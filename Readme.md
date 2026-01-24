# 程式架構
```
11422 (專案根目錄)
├── run.py                 # 🚀 程式啟動入口 (Entry Point)
├── config.py              # ⚙️ 設定檔 (讀取 .env 環境變數)
├── .env                   # 🔑 敏感資訊 (API Key, DB 密碼，需自行建立)
├── requirements.txt       # (推測) 套件依賴清單
├── files/                 # 📂 放置文本資料的資料夾 (用於分析高頻詞)
│   └── a.txt              # ...
├── templates/             # 🎨 前端 HTML 模板 (Flask Template)
│   ├── admin.html         # 後台儀表板
│   ├── review.html        # 訊息審核頁面
│   ├── history.html       # 歷史紀錄頁面
│   └── ...
└── src/                   # 🧠 核心程式碼邏輯包
    ├── __init__.py        # Flask App 工廠模式 (註冊 Blueprint)
    ├── admin.py           # 🔧 後台管理邏輯 (Dashboard, Review, Gemini API)
    ├── ai_client.py       # 🤖 回覆修飾模組 (加上語氣詞、前綴後綴)
    ├── controller.py      # 🌐 LINE Webhook 入口 (驗證簽章)
    ├── database.py        # 🗄️ 資料庫操作 (MySQL 連線, CRUD)
    ├── intent_matcher.py  # 🔍 意圖比對邏輯 (關鍵字匹配)
    ├── line_bot_api.py    # 📲 初始化 LINE Bot API 物件
    ├── service.py         # ⚙️ 核心業務邏輯 (決定自動回覆或轉人工)
    ├── test_chat.py       # 🧪 網頁版聊天測試介面
    └── text_processor.py  # ✂️ 斷詞處理 (Jieba, 停用詞過濾)
```

# 函式安裝  
Anaconda Navigator
https://drive.google.com/file/d/1Wi1gUjaOv2A06M0gK8xqLiAIjOv1lbpD/view?usp=sharing

`pip install line-bot-sdk`

`pip install flask line-bot-sdk python-dotenv`

`"C:/Users/USER/AppData/Local/Programs/Python/Python313/python.exe" -m pip install flask`

`pip install jieba`

`pip install google-genai`

`pip install mysql2`

`pip install mysql-connector-python`

`pip uninstall mysql-connector`

`pip install mysql-connector`

`pip install flask line-bot-sdk python-dotenv jieba mysql-connector-python requests`

# 伺服器啟動
ngrok下載 https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip

金鑰設定
ngrok config add-authtoken 38H

ngrok http http://127.0.0.1:5001/

# 資料庫
密碼統一aeust

```
CREATE DATABASE IF NOT EXISTS Aeust CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE Aeust;

-- 建立 'bot_intents' 資料表，用來存機器人的意圖與回覆
CREATE TABLE IF NOT EXISTS bot_intents (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '唯一編號 (自動遞增)',
    category VARCHAR(50) NOT NULL COMMENT '意圖分類 (例如：緊急求助)',
    keywords JSON NOT NULL COMMENT '關鍵字列表 (存成 JSON 陣列格式)',
    danger INT DEFAULT 0 COMMENT '危險指數 (0-5，越高越危險)',
    response TEXT NOT NULL COMMENT '機器人的標準回覆內容',
    action VARCHAR(50) DEFAULT 'NONE' COMMENT '後續動作代碼 (用來觸發按鈕)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '資料建立時間'
);

CREATE TABLE IF NOT EXISTS response_modifiers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '唯一編號',
    category VARCHAR(50) NOT NULL COMMENT '對應 bot_intents 的分類，或 "default" (通用)',
    mod_type VARCHAR(20) NOT NULL COMMENT '類型：prefix(前綴), suffix(後綴), particle(語氣詞)',
    content TEXT NOT NULL COMMENT '修飾語內容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '建立時間'
);


CREATE TABLE IF NOT EXISTS pending_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    user_message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- 狀態: pending (待審), replied (已回)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS chat_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 記錄是誰說的：'user' (使用者) 或 'bot' (機器人/管理員)
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
# 示範資料
```
INSERT INTO bot_intents (category, keywords, danger, response, action) VALUES 
(
    '緊急求助', 
    '["死", "自殺", "割腕", "消失", "頂樓"]', 
    5, 
    '同學，請先停下來，我們很重視你的安全。👇 請點擊下方按鈕，有人會馬上聽你說。', 
    'SHOW_CRISIS_MENU'
),
(
    '身體界線', 
    '["摸", "不舒服", "性騷擾"]', 
    3, 
    '這可能涉及性騷擾，你的感覺很重要。你想了解如何保護自己嗎？', 
    'LINK_LEGAL_INFO'
),
(
    '打招呼', 
    '["嗨", "你好", "哈囉"]', 
    0, 
    '嗨！我在這裡陪你，有什麼想說的嗎？', 
    'SHOW_MAIN_MENU'
);

INSERT INTO response_modifiers (category, mod_type, content) VALUES 
# (分類, 類型, 內容)
            ('default', 'prefix', '嗯嗯，'),
            ('default', 'prefix', '我知道了，'),
            ('default', 'prefix', '原來是這樣，'),
            ('default', 'suffix', ' (拍拍')),
            ('default', 'suffix', ' 我們會在這裡陪你。'),
            ('default', 'particle', '～'),
            ('default', 'particle', '喔！'),
            ('default', 'particle', '❤️'),
            
            ('緊急求助', 'prefix', '請先深呼吸，'),
            ('緊急求助', 'prefix', '親愛的請聽我說，'),
            ('緊急求助', 'suffix', ' 請讓我們幫助你好嗎？'),
            ('緊急求助', 'suffix', ' 你的安全對我們最重要。'),
            
            ('閒聊', 'prefix', '嘿嘿，'),
            ('閒聊', 'suffix', ' 隨時歡迎找我聊聊！'),
            ('閒聊', 'particle', '呀～'),
            
            ('打招呼', 'prefix', '嗨嗨！'),
            ('打招呼', 'prefix', '你好呀！');
```

# 資料庫更新
http://127.0.0.1:5001/admin


# AI說明
以下為您詳細解釋每個檔案的功能與職責：

🧩 各模組詳細功能說明
1. 啟動與設定層
run.py:

負責啟動 Flask Server。

會在 Console 印出後台管理連結 (/admin)。

config.py:

集中管理環境變數 (LINE_CHANNEL_SECRET, DB_PASSWORD 等)。

定義 AI_CHARACTER_PROMPT (雖然目前主要用在 admin.py 的 Gemini 生成建議)。

2. 網路介面層 (Controllers)
src/controller.py:

處理 LINE 平台傳來的 Webhook 請求。

負責驗證簽章 (X-Line-Signature)。

將合法請求交給 handler 處理。

src/admin.py:

提供網頁後台功能。

儀表板: 顯示熱門關鍵字、管理意圖與修飾語。

審核功能 (/review): 讓管理者查看「未命中」的訊息，並手動撰寫回覆或存入知識庫。

AI 建議: 呼叫 Google Gemini API 產生回覆建議。

3. 業務邏輯層 (Service / Business Logic)
src/service.py (大腦):

這是機器人的核心流程控制中心。

流程：收到訊息 -> text_processor 斷詞 -> intent_matcher 比對意圖。

自動駕駛 (Auto-Pilot): 若命中意圖且危險度低 -> 呼叫 ai_client 修飾語句 -> 直接回覆。

人工介入 (Human-in-the-loop): 若未命中 -> 存入 pending_messages 資料庫 -> 回覆「請稍候」。

src/intent_matcher.py:

單純負責演算法邏輯：比對「使用者斷詞」與「資料庫意圖關鍵字」，找出危險指數最高的匹配項目。

4. 工具與資料層 (Utils & Data)
src/database.py:

負責所有 MySQL SQL 指令。

管理：bot_intents (意圖庫), response_modifiers (修飾語), pending_messages (待審核), chat_logs (對話紀錄)。

src/text_processor.py:

使用 jieba 進行中文斷詞。

載入 mydict.txt (自訂詞典) 和 delete_words.txt (停用詞)。

分析 files/ 資料夾內的高頻詞彙。

src/ai_client.py:

注意：這個檔案目前主要負責「規則式修飾」(Rule-based polishing)，從資料庫讀取前綴、後綴、語氣詞來包裝回覆，而非直接呼叫 LLM (LLM 是在 admin.py 裡呼叫的)。

🔄 資料流向 (Data Flow)
使用者傳訊 ➡️ LINE Server ➡️ controller.py (Webhook)

➡️ line_bot_api.py (Handler) ➡️ service.py (handle_message)

➡️ 斷詞 (text_processor.py) ➡️ 比對 (intent_matcher.py + database.py)

分支 A (命中): ➡️ ai_client.py (修飾) ➡️ line_bot_api (回覆使用者)。

分支 B (未命中): ➡️ database.py (存入 pending) ➡️ line_bot_api (回覆罐頭訊息) ➡️ 管理者 (在 admin.py 介面審核並回覆)。