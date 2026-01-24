# src/service.py

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, 
    QuickReply, QuickReplyButton, MessageAction
)
from linebot.exceptions import LineBotApiError

# 引入專案模組
from src.line_bot_api import line_bot_api, handler
from src.database import get_intents, save_pending_message # 同時需要讀取意圖與存檔
from src.ai_client import ai_service
from src.text_processor import segment_text
from src.intent_matcher import find_best_match
# ... 引入 log_chat
from src.database import get_intents, save_pending_message, log_chat
# from src.database import save_pending_message, log_chat

# ==========================================
# 輔助函式：產生回覆物件 (沿用原本的設計)
# ==========================================
def get_reply_object(reply_text, action):
    if action == "SHOW_CRISIS_MENU":
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="撥打 113", text="撥打 113")),
                QuickReplyButton(action=MessageAction(label="撥打 110", text="撥打 110"))
            ])
        )
    elif action == "SHOW_MAIN_MENU":
        return TextSendMessage(
            text=reply_text,
            quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="心情不好", text="心情不好")),
                QuickReplyButton(action=MessageAction(label="關於我", text="關於我"))
            ])
        )
    else:
        return TextSendMessage(text=reply_text)

# ==========================================
# Line Bot 主要處理邏輯 (混合模式)
# ==========================================
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    user_id = event.source.user_id
    print(f"📩 收到訊息: {user_msg}")

#     # 1. 【新增】先記錄使用者的發言到歷史紀錄表
    log_chat(user_id, 'user', user_msg)

#     # ==========================================
#     # 第一階段：嘗試自動匹配 (Auto-Pilot)
#     # ==========================================
    
    # 1. 取得目前已學會的所有意圖
    intents = get_intents()

    # 2. 斷詞
    seg_list = segment_text(user_msg)

    # 3. 判斷是否命中已知的知識
    matched_intent = find_best_match(seg_list, intents)

    # 設定一個信心門檻 (如果完全沒沾上邊，就不要硬回)
    # 這裡假設 find_best_match 會回傳 None 如果完全不匹配
    
    if matched_intent:
        print(f"✅ 命中已知案例: {matched_intent['category']}")
        
        # 取得資料庫中的標準答案
        base_response = matched_intent['response']
        danger_level = matched_intent.get('danger', 0)
        action_code = matched_intent.get('action', 'NONE')

        # 進行語氣修飾 (AI Polish)
        polish_level = 2
        if danger_level >= 4: polish_level = 3
        
        final_response_text = ai_service.polish_response(
            user_text=user_msg, 
            base_response=base_response, 
            category=matched_intent['category'],
            level=polish_level 
        )

        # 直接回覆使用者 (不用人工審核)
        try:
            reply_obj = get_reply_object(final_response_text, action_code)
            line_bot_api.reply_message(event.reply_token, reply_obj)
            print("🚀 自動回覆成功")
            return # 結束函式，不進入第二階段
        except LineBotApiError as e:
            print(f"❌ Line API 錯誤: {e}")

#     # ==========================================
#     # 第二階段：未知案例，進入人工審核 (Human-in-the-loop)
#     # ==========================================
    print("🤷‍♂️ 未命中已知案例，轉交人工審核...")

    # 1. 存入待審核資料庫
    save_success = save_pending_message(user_id, user_msg)

    # 2. 告知使用者稍後回覆
    # (為了避免使用者覺得被已讀不回，還是要傳一個制式訊息)
    fallback_text = "【系統自動回覆】\n這個問題我需要請教一下社工老師，會盡快由專人回覆您，請稍候。"
    
    try:
        if save_success:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=fallback_text))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="系統繁忙中。"))
    except LineBotApiError as e:
        print(f"❌ Line API 回覆錯誤: {e}")

# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     user_msg = event.message.text.strip()
#     user_id = event.source.user_id
    
#     print(f"📩 收到 {user_id} 訊息: {user_msg}")

#     # 1. 【關鍵】記錄使用者的話到歷史紀錄 (供未來參考)
#     log_chat(user_id, 'user', user_msg)

#     # 2. 存入待審核區 (供後台人工處理)
#     save_pending_message(user_id, user_msg)

#     # 3. 回覆等待訊息
#     try:
#         reply_text = "【系統收到】您的訊息已送達，我們將盡快回覆您。"
#         line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
#     except LineBotApiError as e:
#         print(f"Line Error: {e}")