# src/admin.py
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response
from linebot.models import TextSendMessage
import google.generativeai as genai
import time # 用於防止快取或其他時間處理
from src.database import get_recent_chat_history, log_chat

from src.line_bot_api import line_bot_api
from src.text_processor import analyze_folder_words, segment_text
from src.database import (
    Config,
    get_intents, update_keywords_in_db, insert_new_category, 
    get_all_modifiers, add_modifier, delete_modifier,
    get_pending_messages, update_message_status,
    log_chat, get_chat_history_by_user, get_recent_chat_history
)

admin_blueprint = Blueprint('admin', __name__)

# ==========================================
# 1. Dashboard & Settings
# ==========================================
@admin_blueprint.route('/admin', methods=['GET'])
def admin_dashboard():
    intents = get_intents()
    top_words = analyze_folder_words(folder_path='./files', top_n=30)
    modifiers = get_all_modifiers()
    return render_template('admin.html', intents=intents, top_words=top_words, modifiers=modifiers)

@admin_blueprint.route('/admin/submit', methods=['POST'])
def admin_submit():
    selected_words = request.form.getlist('selected_words')
    mode = request.form.get('mode') 
    if mode == 'existing':
        cat_id = request.form.get('category_id')
        if selected_words: update_keywords_in_db(cat_id, selected_words)
    elif mode == 'new':
        new_cat = request.form.get('new_category_name')
        danger = request.form.get('danger_level')
        response = request.form.get('response_text')
        action = request.form.get('action_code')
        if new_cat: insert_new_category(new_cat, int(danger), response, action, selected_words)
    return redirect(url_for('admin.admin_dashboard'))

@admin_blueprint.route('/admin/modifier/add', methods=['POST'])
def add_modifier_route():
    category = request.form.get('category')
    mod_type = request.form.get('mod_type')
    content = request.form.get('content')
    if category and mod_type and content:
        add_modifier(category, mod_type, content)
    return redirect(url_for('admin.admin_dashboard'))

@admin_blueprint.route('/admin/modifier/delete', methods=['POST'])
def delete_modifier_route():
    mod_id = request.form.get('mod_id')
    if mod_id:
        delete_modifier(mod_id)
    return redirect(url_for('admin.admin_dashboard'))


# ==========================================
# 2. Review (審核) - 頁面與 API
# ==========================================
@admin_blueprint.route('/admin/review', methods=['GET'])
def review_page():
    # 接收搜尋參數
    target_user_id = request.args.get('user_id', '').strip()
    
    # 傳入 user_id 進行過濾
    pending_msgs = get_pending_messages(user_id=target_user_id if target_user_id else None)
    
    # 斷詞處理 + 載入歷史紀錄
    for msg in pending_msgs:
        msg['segmented_words'] = segment_text(msg['user_message'])
        
        # 取得該用戶最近 5 筆歷史 (不包含當前這則 pending 的)
        history_rows = get_recent_chat_history(msg['user_id'], limit=5)
        
        # 對歷史紀錄也進行斷詞
        for h_row in history_rows:
            h_row['segmented_words'] = segment_text(h_row['message'])
            
        msg['history_context'] = history_rows

    return render_template('review.html', pending_msgs=pending_msgs, user_id=target_user_id)

@admin_blueprint.route('/admin/api/review_content')
def api_review_content():
    # 接收搜尋參數 (給 AJAX 用)
    target_user_id = request.args.get('user_id', '').strip()
    
    pending_msgs = get_pending_messages(user_id=target_user_id if target_user_id else None)
    
    for msg in pending_msgs:
        msg['segmented_words'] = segment_text(msg['user_message'])
        
        # 載入歷史
        history_rows = get_recent_chat_history(msg['user_id'], limit=5)
        for h_row in history_rows:
            h_row['segmented_words'] = segment_text(h_row['message'])
        msg['history_context'] = history_rows
        
    return render_template('review_content.html', pending_msgs=pending_msgs)

@admin_blueprint.route('/admin/process_reply', methods=['POST'])
def process_reply():
    msg_id = request.form.get('msg_id')
    user_id = request.form.get('user_id')
    final_response = request.form.get('final_response')
    selected_keywords = request.form.getlist('selected_keywords')
    save_to_db = request.form.get('save_to_db')

    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=final_response))
        log_chat(user_id, 'bot', final_response)
    except Exception as e:
        print(f"Push Error: {e}")
        return "發送失敗", 500

    update_message_status(msg_id, 'replied')

    if save_to_db and selected_keywords:
        insert_new_category(f"Learned_Case_{msg_id}", 0, final_response, "NONE", selected_keywords)

    return redirect(url_for('admin.review_page'))


# ==========================================
# 3. AI API
# ==========================================

# 2. 更新：AI 生成 API (接收前後文)
@admin_blueprint.route('/admin/api/generate', methods=['POST'])
def ai_generate():
    data = request.json
    current_keywords = data.get('keywords', [])
    history_keywords = data.get('history_keywords', [])

    if not current_keywords and not history_keywords:
        return jsonify({"suggestion": "請至少勾選一些關鍵字(當前或歷史)。"})
    
    if not Config.GEMINI_API_KEY: 
        return jsonify({"suggestion": "❌ 未設定 API Key"})
         
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        
        # 組合 Prompt
        context_str = "、".join(history_keywords)
        current_str = "、".join(current_keywords)
        
        # 這裡可以加入您之前設定的「暖暖」人設
        prompt = (
            f"你是一個溫暖的輔導機器人「暖暖」。\n"
            f"【前情提要 (去識別化關鍵字)】：{context_str}\n"
            f"【使用者目前訊息 (去識別化關鍵字)】：{current_str}\n\n"
            f"請根據以上脈絡，生成一段溫暖、同理、不帶批判性的回覆建議 (100字內)。"
        )
        response = model.generate_content(prompt)
        return jsonify({"suggestion": response.text})
    except Exception as e:
        return jsonify({"suggestion": f"AI Error: {e}"})

# ==========================================
# 4. History (歷史紀錄) - 頁面與 API
# ==========================================
@admin_blueprint.route('/admin/history', methods=['GET', 'POST'])
def history_page():
    # 這是完整網頁
    chat_history = []
    target_user_id = request.args.get('user_id') or request.form.get('user_id', '').strip()
    
    if target_user_id:
        chat_history = get_chat_history_by_user(target_user_id)
            
    return render_template('history.html', history=chat_history, user_id=target_user_id)

@admin_blueprint.route('/admin/api/history_content')
def api_history_content():
    # 🔥 這是給 JS 自動更新用的，只回傳「history_content.html」
    target_user_id = request.args.get('user_id', '').strip()
    chat_history = []
    
    if target_user_id:
        chat_history = get_chat_history_by_user(target_user_id)
    
    return render_template('history_content.html', history=chat_history, user_id=target_user_id)

@admin_blueprint.route('/admin/history/export/<user_id>')
def export_history(user_id):
    rows = get_chat_history_by_user(user_id)
    if not rows: return "無資料"
    content = f"User: {user_id}\nTime: {rows[-1]['created_at'] if rows else ''}\n{'='*30}\n"
    for row in rows:
        role = "👤" if row['role'] == 'user' else "🤖"
        content += f"[{row['created_at']}] {role}: {row['message']}\n{'-'*20}\n"
    resp = make_response(content)
    resp.headers["Content-Disposition"] = f"attachment; filename=history_{user_id}.txt"
    resp.headers["Content-type"] = "text/plain; charset=utf-8"
    return resp