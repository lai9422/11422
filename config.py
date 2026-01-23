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