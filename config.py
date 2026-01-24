import os  # 匯入作業系統模組，用來讀取環境變數
from dotenv import load_dotenv  # 匯入 dotenv，用來讀取 .env 檔案

# 載入專案目錄下的 .env 檔案內容到環境變數中
load_dotenv()

class Config:
    """
    設定類別：集中管理所有的 API Key 和資料庫連線資訊
    """
    # 取得 Line Bot 的 Token，如果沒設定則回傳空字串 (使用 .strip() 去除前後空白)
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '').strip()
    
    # 取得 Line Bot 的 Secret
    LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
    
    # 取得程式執行的 Port，預設為 5001
    PORT = os.getenv('PORT', 5001)

    # --- 資料庫設定 ---
    # 資料庫主機位置 (通常是 localhost)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    # 資料庫使用者名稱 (通常是 root)
    DB_USER = os.getenv('DB_USER', 'root')
    # 資料庫密碼 (記得在 .env 設定)
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    # 資料庫名稱 (對應剛剛 SQL 建立的名稱)
    DB_NAME = os.getenv('DB_NAME', 'Aeust')

    # --- Google Gemini AI 設定 ---
    # Google AI 的 API Key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


    AI_CHARACTER_PROMPT = """
    你現在是『暖暖』，一個專門陪伴經歷性創傷或法律困擾的青少年的 AI 樹洞守護者。
    
    請遵守以下【角色守則】：
    1. 溫暖接納：使用溫柔、不帶批判的語氣，讓使用者感到安全。請多用「我感覺到你很...」、「這真的很不容易...」等同理句型。
    2. 專業邊界：你不是律師或心理師。遇到法律問題，提供一般性流程資訊（如：蒐證、通報流程），但必須強調「具體情況請諮詢專業律師」。
    3. 安全優先：若關鍵字涉及自殺、自傷或立即危險，請在回覆中溫柔地置入求助資源（如 113 或 110）。
    4. 回應風格：像一個懂你的大哥哥/大姊姊，字數控制在 150 字以內，不要長篇大論的說教。
    
    現在，使用者的訊息關鍵字是：{keywords}。
    請根據上述設定，生成一段給青少年的建議回覆：
    """