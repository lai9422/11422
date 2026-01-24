import json
import random

# 1. 定義資料庫欄位結構與基礎資料庫
# 這裡我們預設一些針對你專案主題 (青少年/性創傷/法律/情緒) 的分類模版
# 透過 random.choice 或組合的方式來產生大量變化

data_templates = [
    {
        "category": "緊急求助",
        "danger": 5,
        "action": "SHOW_CRISIS_MENU",
        "response_pool": [
            "同學，請先停下來，我們很重視你的安全。👇 請點擊下方按鈕，有人會馬上聽你說。",
            "深呼吸，你現在不孤單。我們有專業的人員可以協助你，請看下面的資源。",
            "我知道現在很痛苦，但請給我們一個機會幫助你。👇",
            "你的生命很重要，請讓我們協助你度過這個時刻。"
        ],
        "keywords_pool": [
            ["死", "自殺", "不想活"],
            ["割腕", "流血", "痛"],
            ["消失", "再見", "絕望"],
            ["跳樓", "頂樓", "危險"],
            ["藥", "吞", "過量"]
        ]
    },
    {
        "category": "身體界線",
        "danger": 3,
        "action": "LINK_LEGAL_INFO",
        "response_pool": [
            "這聽起來可能涉及性騷擾，你的感覺很重要。你想了解如何保護自己嗎？",
            "對方這樣的行為是不對的。如果你感到不舒服，那是因為你的界線被侵犯了。",
            "這可能已經觸犯了法律中的性騷擾防治法。需要我為你解釋相關權益嗎？",
            "發生這樣的事不是你的錯。我們可以一起看看有哪些法律途徑可以協助你。"
        ],
        "keywords_pool": [
            ["摸", "大腿", "胸部"],
            ["強吻", "擁抱", "不舒服"],
            ["性騷擾", "變態", "噁心"],
            ["脫", "裸照", "外流"],
            ["強迫", "做愛", "發生關係"]
        ]
    },
    {
        "category": "情緒支持",
        "danger": 1,
        "action": "AI_EMPATHY_RESPONSE",  # 假設這會觸發你的 AI 生成回覆
        "response_pool": [
            "聽起來你最近壓力很大，願意多跟我說一點嗎？",
            "這種感覺真的很難受，不過我在這裡陪你。",
            "你可以把這裡當作樹洞，說出來心裡或許會好受一些。",
            "沒關係的，想哭就哭出來，情緒需要出口。"
        ],
        "keywords_pool": [
            ["難過", "哭", "傷心"],
            ["壓力", "好大", "崩潰"],
            ["寂寞", "沒人理", "邊緣"],
            ["生氣", "憤怒", "不爽"],
            ["焦慮", "睡不著", "失眠"]
        ]
    },
    {
        "category": "打招呼與閒聊",
        "danger": 0,
        "action": "SHOW_MAIN_MENU",
        "response_pool": [
            "嗨！我在這裡陪你，有什麼想說的嗎？",
            "哈囉！今天過得還好嗎？",
            "嗨嗨，我是你的小助手，隨時都可以找我聊聊喔。",
            "你好呀！有什麼我可以幫你的嗎？"
        ],
        "keywords_pool": [
            ["嗨", "你好", "哈囉"],
            ["早安", "午安", "晚安"],
            ["在嗎", "有人嗎", "test"],
            ["你是誰", "機器人", "介紹"],
            ["無聊", "聊天", "講笑話"]
        ]
    },
    {
        "category": "法律諮詢",
        "danger": 2,
        "action": "SEARCH_LEGAL_DB",
        "response_pool": [
            "關於法律問題，建議保留證據是第一步。你想知道怎麼蒐證嗎？",
            "這可能涉及刑法或性平法。我可以幫你查找相關條文。",
            "遇到這種法律問題，你是未成年人嗎？法律對未成年人有特別保護。",
            "我們可以協助你尋找法律扶助資源，需要嗎？"
        ],
        "keywords_pool": [
            ["法律", "告他", "警察"],
            ["證據", "截圖", "錄音"],
            ["提告", "法院", "判刑"],
            ["未成年", "保護令", "社工"],
            ["律師", "諮詢", "費用"]
        ]
    }
]

def generate_sql_file(filename="insert_intents.sql", num_rows=100):
    with open(filename, "w", encoding="utf-8") as f:
        # 寫入 SQL 檔頭
        f.write("INSERT INTO bot_intents (category, keywords, danger, response, action) VALUES \n")
        
        values_list = []
        
        # 為了產生 "上百種"，我們使用組合生成法
        # 這裡示範如何透過混和關鍵字來擴充資料量
        
        count = 0
        while count < num_rows:
            # 1. 隨機選一個分類模版
            template = random.choice(data_templates)
            
            # 2. 隨機選一組基礎關鍵字 (例如 ["摸", "不舒服"])
            base_keywords = random.choice(template["keywords_pool"])
            
            # 3. 為了增加變異性，隨機混入一些同義詞或擴充詞，讓關鍵字組合不同
            # 這樣資料庫才會有豐富的匹配模式
            modifiers = ["現在", "真的", "覺得", "好", "一直", "突然"]
            extra_word = random.choice(modifiers)
            
            # 組合出新的關鍵字列表，例如 ["摸", "不舒服", "真的"]
            # 注意：Python 的 list 傳遞是 reference，要 copy
            final_keywords = base_keywords.copy()
            if random.random() > 0.5: # 50% 機率加入修飾詞
                final_keywords.append(extra_word)
                
            # 4. 選一個回應
            response_text = random.choice(template["response_pool"])
            
            # 5. 構建 SQL Value 字串
            # 注意：keywords 欄位在 SQL 裡通常存成 JSON 字串，需要用 json.dumps 處理中文編碼
            keywords_json = json.dumps(final_keywords, ensure_ascii=False)
            
            # 使用 Python f-string 格式化 SQL
            # SQL 字串需要跳脫單引號，這裡簡單處理將內容中的單引號代換掉
            sql_val = f"('{template['category']}', '{keywords_json}', {template['danger']}, '{response_text}', '{template['action']}')"
            
            values_list.append(sql_val)
            count += 1

        # 將所有 VALUES 用逗號連接，並加上分號結尾
        f.write(",\n".join(values_list))
        f.write(";\n")

    print(f"✅ 成功生成 {num_rows} 筆資料至 {filename}")

# 執行生成函數，產生 200 筆資料
if __name__ == "__main__":
    generate_sql_file("insert_intents.sql", 200)