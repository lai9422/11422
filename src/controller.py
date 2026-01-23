from flask import Blueprint, request, abort
from linebot.exceptions import InvalidSignatureError
from src.line_bot_api import handler
import src.service 

webhook_blueprint = Blueprint('webhook', __name__)

@webhook_blueprint.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        return '伺服器正常運作中！'

    if request.method == 'POST':
        signature = request.headers.get('X-Line-Signature')
        body = request.get_data(as_text=True)

        print("收到 LINE 請求:", body)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            print("❌ 錯誤：Channel Secret 填錯了，或簽章驗證失敗")
            abort(400)
        except Exception as e:
            print(f"❌ 未知錯誤：{e}")
            abort(500)

        return 'OK'