# src/admin.py
<<<<<<< HEAD
=======
# ========================================================
# 整合功能：
# 1. 關鍵字訓練與意圖管理
# 2. 語氣修飾語管理
# 3. 訊息審核 (Human-in-the-loop)
# 4. AI 輔助回覆生成 (Google Gemini)
# 5. 對話紀錄查詢與匯出
# ========================================================

>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response
from linebot.models import TextSendMessage
import google.generativeai as genai

<<<<<<< HEAD
=======
# 引入專案模組
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
from src.line_bot_api import line_bot_api
from src.text_processor import analyze_folder_words, segment_text
from src.database import (
    Config,
    get_intents, update_keywords_in_db, insert_new_category, 
    get_all_modifiers, add_modifier, delete_modifier,
    get_pending_messages, update_message_status,
    log_chat, get_chat_history_by_user
)

admin_blueprint = Blueprint('admin', __name__)

# ==========================================
<<<<<<< HEAD
# 1. Dashboard & Settings
=======
# 1. 主控台 Dashboard (訓練與修飾語)
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
# ==========================================
@admin_blueprint.route('/admin', methods=['GET'])
def admin_dashboard():
    intents = get_intents()
<<<<<<< HEAD
    top_words = analyze_folder_words(folder_path='./files', top_n=30)
=======
    # 2. 分析文章詞頻
    top_words = analyze_folder_words(folder_path='./files', top_n=30)
    # 3. 取得修飾語
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
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

<<<<<<< HEAD
=======
# --- 修飾語管理 ---
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
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
<<<<<<< HEAD
# 2. Review (審核) - 頁面與 API
# ==========================================
@admin_blueprint.route('/admin/review', methods=['GET'])
def review_page():
    # 這是給瀏覽器直接打開用的，會回傳完整網頁 (外殼 + 內容)
    pending_msgs = get_pending_messages()
    for msg in pending_msgs:
        msg['segmented_words'] = segment_text(msg['user_message'])
    return render_template('review.html', pending_msgs=pending_msgs)

@admin_blueprint.route('/admin/api/review_content')
def api_review_content():
    # 🔥 這是給 JS 自動更新用的，只回傳「review_content.html」
    pending_msgs = get_pending_messages()
    for msg in pending_msgs:
        msg['segmented_words'] = segment_text(msg['user_message'])
    return render_template('review_content.html', pending_msgs=pending_msgs)

=======
# 2. 訊息審核 (Human-in-the-loop)
# ==========================================
@admin_blueprint.route('/admin/review', methods=['GET'])
def review_page():
    # 取得所有待處理訊息
    pending_msgs = get_pending_messages()
    
    # 預先對每一則訊息進行斷詞，讓前端可以顯示 checkbox
    for msg in pending_msgs:
        msg['segmented_words'] = segment_text(msg['user_message'])
        
    return render_template('review.html', pending_msgs=pending_msgs)

>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
@admin_blueprint.route('/admin/process_reply', methods=['POST'])
def process_reply():
    msg_id = request.form.get('msg_id')
    user_id = request.form.get('user_id')
    final_response = request.form.get('final_response')
<<<<<<< HEAD
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
=======
    selected_keywords = request.form.getlist('selected_keywords') # 這些是被勾選的去識別化關鍵字
    save_to_db = request.form.get('save_to_db')

    # A. 透過 Line Push API 主動回覆使用者
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=final_response))
        print(f"✅ 已人工回覆使用者 {user_id}")
        
        # 【記錄】記錄機器人(管理員)的回覆到歷史紀錄表
        log_chat(user_id, 'bot', final_response)
        
    except Exception as e:
        print(f"❌ Push Message 失敗: {e}")
        return "發送失敗，請檢查 Line Channel Access Token 是否正確", 500

    # B. 更新訊息狀態為 'replied'
    update_message_status(msg_id, 'replied')

    # C. 如果勾選「存入資料庫」，則讓機器人學會這次的對話
    if save_to_db and selected_keywords:
        category_name = f"Learned_Case_{msg_id}"
        
        insert_new_category(
            category=category_name,
            danger=0, 
            response=final_response,
            action="NONE",
            keywords=selected_keywords
        )
        print(f"📚 機器人已學習新案例: {selected_keywords} -> {final_response}")
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97

    return redirect(url_for('admin.review_page'))


# ==========================================
<<<<<<< HEAD
# 3. AI API
=======
# 3. AI 輔助生成 API (Google Gemini)
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
# ==========================================
@admin_blueprint.route('/admin/api/generate', methods=['POST'])
def ai_generate():
    data = request.json
    keywords = data.get('keywords', [])
<<<<<<< HEAD
    if not keywords: return jsonify({"suggestion": "請先勾選關鍵字..."})
    if not Config.GEMINI_API_KEY: return jsonify({"suggestion": "❌ 未設定 API Key"})
         
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        prompt = (
            f"你是一個溫暖的輔導機器人。使用者訊息關鍵字：{', '.join(keywords)}。"
            f"請生成一段溫暖、同理且簡短的回覆建議(100字內)。"
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
=======
    
    if not keywords:
        return jsonify({"suggestion": "請先勾選關鍵字，AI 才能依照重點生成回覆。"})

    # 1. 檢查 API Key
    if not Config.GEMINI_API_KEY:
         return jsonify({"suggestion": "❌ 錯誤：尚未設定 GEMINI_API_KEY，請檢查 .env 檔案。"})
         
    try:
        # 2. 設定 Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

        # 3. 組合提示詞 (Prompt)
        prompt = (
            f"你是一個協助處理青少年性創傷與法律問題的溫暖機器人。"
            f"使用者傳來的訊息中包含了這些關鍵字：{', '.join(keywords)}。"
            f"請根據這些關鍵字，生成一段溫暖、不帶批判性、且具備同理心的回覆草稿。"
            f"字數控制在 100 字以內。請直接給出建議的回覆內容即可，不要包含開頭的確認語。"
        )

        # 4. 呼叫 Google AI
        response = model.generate_content(prompt)
        ai_reply = response.text

        return jsonify({"suggestion": ai_reply})

    except Exception as e:
        print(f"❌ Gemini API 錯誤: {e}")
        return jsonify({"suggestion": f"AI 連線發生錯誤 (請檢查 Key 或網路): {e}"})


# ==========================================
# 4. 歷史紀錄查詢與匯出
# ==========================================
@admin_blueprint.route('/admin/history', methods=['GET', 'POST'])
def history_page():
    chat_history = []
    target_user_id = ""
    
    if request.method == 'POST':
        target_user_id = request.form.get('user_id', '').strip()
        if target_user_id:
            chat_history = get_chat_history_by_user(target_user_id)
            
    return render_template('history.html', history=chat_history, user_id=target_user_id)

@admin_blueprint.route('/admin/history/export/<user_id>')
def export_history(user_id):
    rows = get_chat_history_by_user(user_id)
    
    if not rows:
        return "無資料可匯出"

    # 組合文字內容
    content = f"User ID: {user_id}\n匯出時間: {rows[-1]['created_at'] if rows else 'N/A'}\n"
    content += "=" * 50 + "\n\n"
    
    for row in rows:
        time_str = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        role_str = "👤 使用者" if row['role'] == 'user' else "🤖 機器人"
        content += f"[{time_str}] {role_str}:\n{row['message']}\n"
        content += "-" * 30 + "\n"
        
    # 製作成檔案下載回應
    response = make_response(content)
    # 設定下載檔名 (防止中文檔名亂碼，這裡用 user_id)
    response.headers["Content-Disposition"] = f"attachment; filename=history_{user_id}.txt"
    response.headers["Content-type"] = "text/plain; charset=utf-8"
    return response
>>>>>>> 023a5a7f251de2f2f52a56b38e048cf831210f97
