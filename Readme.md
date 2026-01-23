# 程式架構
```
my_line_bot/
├── .env                  (維持不變)
├── run.py                (維持不變)
├── config.py             (維持不變)
├── mydict.txt            (維持不變: 自訂字典檔)
├── delete_words.txt      (維持不變: 停用詞檔案)
├── files/                (📂新增: 專門放置要給機器人學習的文章 .txt 檔案)
├── templates/            (📂新增: Flask 網頁模板資料夾)
│   └── admin.html        (🔥新: 訓練後台的網頁介面 HTML)
└── src/
    ├── __init__.py       (🔄修: 新增註冊 admin 藍圖)
    ├── line_bot_api.py   (維持不變)
    ├── controller.py     (維持不變: 專門處理 Line Webhook 請求)
    ├── admin.py          (🔥新: 專門處理後台網頁邏輯 /admin)
    ├── database.py       (🔄修: 新增「寫入/更新」資料庫的函式)
    ├── ai_client.py      (維持不變: 處理 Gemini AI)
    ├── text_processor.py (🔄修: 新增「批量讀取 files 資料夾」功能)
    ├── intent_matcher.py (維持不變: 處理關鍵字比對)
    └── service.py        (維持不變: 指揮官)
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

1. 核心入口與設定 (Root)

run.py (程式入口)

功能：這是整個網站的啟動按鈕。

職責：它會呼叫 src 資料夾裡的程式來建立網站伺服器 (Flask App)，並開始監聽網路請求。執行它之後，你的機器人與後台網頁才會上線。

config.py (設定檔)

功能：專案的「控制中心」。

職責：負責讀取 .env 檔案裡的機密資訊（如 Line Token、資料庫密碼），讓其他程式可以安全地使用這些變數，而不需要把密碼寫死在程式碼裡。

1. 網站與路由層 (Web Layer)
src/__init__.py (初始化)

功能：Flask 網站的工廠。

職責：負責將所有的模組（Admin 後台、Controller 控制器）組裝起來，變成一個完整的應用程式。

src/controller.py (路由控制器)

功能：對外的「總機櫃檯」。

職責：主要負責接收 Line 官方傳來的 Webhook 訊號 (例如：有人傳訊息給機器人了)，然後將這個訊號轉交給 service.py 去處理。

src/admin.py (後台邏輯)

功能：網頁後台的管理者。

職責：處理 /admin 網頁上的所有操作，例如顯示資料庫裡的關鍵字、接收網頁表單送出的新修飾語，並呼叫 database.py 更新資料庫。

3. 機器人核心邏輯 (Bot Logic Layer)
這是機器人「大腦」運作最關鍵的部分：

src/service.py (服務核心)

功能：機器人的「大腦中樞」。

職責：協調所有工作。當收到訊息時，它會依序命令：

text_processor 進行斷詞。

intent_matcher 找出使用者的意圖（是求助？還是閒聊？）。

ai_client 根據危險指數進行「語句修飾」（加溫暖前綴）。

最後透過 line_bot_api 將組裝好的訊息回傳給使用者。

src/intent_matcher.py (意圖辨識)

功能：機器人的「分類帽」。

職責：比對使用者的斷詞與資料庫裡的關鍵字 (keywords)，判斷這句話最接近哪個意圖 (Intent)，並回傳對應的標準答案與危險指數。

src/ai_client.py (修飾模組) [重要修改]

功能：機器人的「潤飾師」。

職責：原本是 Google AI，現在改為規則式 (Rule-Based)。它負責讀取資料庫的 response_modifiers，根據 service.py 傳來的 level (修飾等級)，在原本生硬的回覆前後加上「同理心前綴」或「支持性後綴」。

4. 資料與工具層 (Data & Tools)
src/database.py (資料庫操作)

功能：資料庫的「管理員」。

職責：專門負責執行 SQL 指令。其他程式不能直接碰資料庫，都要透過它來「新增關鍵字」、「讀取修飾語」或「建立新分類」。

src/text_processor.py (文字處理)

功能：機器人的「翻譯蒟蒻」。

職責：使用 jieba 函式庫將使用者打的一長串句子（如「我想找人聊聊」）切成單詞（['我', '想', '找', '人', '聊聊']），方便比對。

src/line_bot_api.py (Line API 整合)

功能：Line 的「傳令兵」。

職責：負責初始化 Line Bot SDK，提供發送訊息 (reply_message) 的功能。

5. 其他檔案
templates/admin.html：後台網頁的「外觀」，使用 HTML 寫成，讓你可以用瀏覽器操作資料庫。

train_bot.py：一個獨立的工具程式。用來讀取 files/ 資料夾裡的 .txt 文章，分析高頻詞彙並存入資料庫（批次訓練用）。

TEST/keyTest.py：用來測試 Line Token 是否有效的簡單腳本。

init_data.py (新建立)：用來初始化資料庫，寫入預設的修飾語 (如「嗯嗯」、「拍拍」)。