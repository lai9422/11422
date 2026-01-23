from flask import Blueprint, render_template, request, jsonify
# 引入與 service.py 相同的核心模組
from src.database import get_intents
from src.ai_client import ai_service
from src.text_processor import segment_text
from src.intent_matcher import find_best_match

test_chat_blueprint = Blueprint('test_chat', __name__)

@test_chat_blueprint.route('/test', methods=['GET'])
def test_page():
    """顯示測試網頁"""
    return render_template('test_chat.html')

@test_chat_blueprint.route('/test/api/send', methods=['POST'])
def test_send_message():
    """處理測試訊息，模擬 service.py 的邏輯"""
    data = request.json
    user_msg = data.get('message', '').strip()
    
    if not user_msg:
        return jsonify({'response': '請輸入訊息', 'action': 'NONE'})

    # --- 以下邏輯複製自 src/service.py (略過去除 LINE API 部分) ---

    # 1. 取得資料
    intents = get_intents()

    # 2. 斷詞
    seg_list = segment_text(user_msg)

    # 3. 判斷意圖
    matched_intent = find_best_match(seg_list, intents)

    # 4. 決策與規則式修飾
    final_response_text = ""
    action_code = "NONE"

    if matched_intent:
        # 命中意圖
        danger_level = matched_intent.get('danger', 0)
        
        polish_level = 2  # 預設 Level 2
        if danger_level >= 4:
            polish_level = 3  # 高危險 -> Level 3
        
        # 呼叫 AI 修飾
        final_response_text = ai_service.polish_response(
            user_text=user_msg, 
            base_response=matched_intent['response'], 
            category=matched_intent['category'],
            level=polish_level 
        )
        action_code = matched_intent['action']
        
    else:
        # 未命中 -> 閒聊
        default_text = "我不太確定你的意思，但我在這裡陪你。你可以多說一點嗎？"
        final_response_text = ai_service.polish_response(
            user_text=user_msg, 
            base_response=default_text, 
            category="閒聊", 
            level=2
        )
        action_code = "SHOW_MAIN_MENU"

    # --- 回傳結果給網頁，而不是呼叫 LINE API ---
    return jsonify({
        'response': final_response_text,
        'action': action_code,
        'debug_intent': matched_intent['category'] if matched_intent else '未命中'
    })