import os
import json
import mysql.connector
import jieba
from config import Config  # 讀取設定檔

# ==========================================
# 1. 資料庫連線工具
# ==========================================
def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def load_existing_categories():
    """ 撈出目前資料庫裡所有的意圖分類 """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, category, danger, response FROM bot_intents")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_keywords(cat_id, new_words):
    """ 更新舊有的分類 (把新詞加進去) """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 先讀取舊的 keywords
    cursor.execute("SELECT keywords FROM bot_intents WHERE id = %s", (cat_id,))
    row = cursor.fetchone()
    
    # 解析 JSON
    if isinstance(row['keywords'], str):
        current_keywords = json.loads(row['keywords'])
    else:
        current_keywords = row['keywords'] # 若 connector 自動轉好了
        
    # 合併並去重複
    updated_set = set(current_keywords)
    for w in new_words:
        updated_set.add(w)
    
    final_list = list(updated_set)
    final_json = json.dumps(final_list, ensure_ascii=False)
    
    # 寫回資料庫
    cursor.execute("UPDATE bot_intents SET keywords = %s WHERE id = %s", (final_json, cat_id))
    conn.commit()
    conn.close()
    print(f"✅ 更新成功！目前關鍵字庫: {final_list}")

def create_new_category(category, danger, response, action, keywords):
    """ 插入全新的分類 """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    keywords_json = json.dumps(keywords, ensure_ascii=False)
    
    sql = """
    INSERT INTO bot_intents (category, danger, response, action, keywords)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (category, danger, response, action, keywords_json))
    conn.commit()
    conn.close()
    print(f"✅ 新分類「{category}」建立成功！")

# ==========================================
# 2. 斷詞邏輯 (你原本的程式碼整合)
# ==========================================
def analyze_files():
    # 初始化設定
    dict_path = 'mydict.txt'
    if os.path.exists(dict_path):
        jieba.load_userdict(dict_path)

    del_words_path = 'delete_words.txt'
    del_words_list = set()
    if os.path.exists(del_words_path):
        with open(del_words_path, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                del_words_list.add(line.strip())

    # 讀取 files 資料夾
    src_file_path = './files'
    if not os.path.exists(src_file_path):
        print("❌ 找不到 files 資料夾，請先建立並放入文章。")
        return []

    all_article = ''
    for article in os.listdir(src_file_path):
        if article.endswith('.txt'):
            path = os.path.join(src_file_path, article)
            with open(path, 'r', encoding='utf-8') as f:
                all_article += f.read()

    # 斷詞
    print("✂️ 正在分析文章...")
    words = jieba.cut(all_article)
    word_count = {}
    
    for w in words:
        w = w.strip()
        if len(w) > 1 and w not in del_words_list:
            word_count[w] = word_count.get(w, 0) + 1
            
    # 排序並回傳前 20 名
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:20]]

# ==========================================
# 3. 主程式：互動介面
# ==========================================
if __name__ == "__main__":
    print("🤖 歡迎使用機器人訓練工具 (模組化版)")
    print("-" * 30)
    
    # 1. 執行斷詞
    top_words = analyze_files()
    if not top_words:
        print("⚠️ 沒有分析出足夠的詞彙，程式結束。")
        exit()
        
    print(f"\n📊 分析出的高頻詞彙 (前20名): {top_words}")
    print("-" * 30)
    
    # 2. 讓使用者選擇要加入哪些詞
    input_str = input("👉 請輸入要新增的詞 (用空白分隔，例如 '心情 憂鬱')，或直接按 Enter 全部加入: ")
    
    selected_words = []
    if input_str.strip():
        selected_words = input_str.split()
    else:
        selected_words = top_words
        
    print(f"準備新增詞彙: {selected_words}")
    
    # 3. 撈出資料庫現況
    categories = load_existing_categories()
    
    print("\n📂 目前資料庫中的分類：")
    for idx, row in enumerate(categories):
        print(f"  [{idx+1}] {row['category']} (危險度: {row['danger']}) -> 回覆: {row['response'][:15]}...")
    
    print(f"  [{len(categories)+1}] ✨ 建立一個全新的分類")
    
    # 4. 決定去處
    choice = input(f"\n🤔 請問要把這些詞加到哪裡？請輸入數字 (1-{len(categories)+1}): ")
    
    try:
        choice_idx = int(choice) - 1
        
        if 0 <= choice_idx < len(categories):
            # === 加入現有分類 ===
            target = categories[choice_idx]
            print(f"\n🔄 正在將詞彙加入現有的「{target['category']}」分類...")
            update_keywords(target['id'], selected_words)
            
        elif choice_idx == len(categories):
            # === 建立新分類 ===
            print("\n✨ 開始建立新分類設定 (請依照指示輸入)")
            new_cat_name = input("   分類名稱 (例如: 學業壓力): ")
            new_danger = input("   危險等級 (0=安全, 5=最危險): ")
            new_response = input("   機器人回覆內容: ")
            
            # 簡單的 Action 選擇
            print("   觸發動作: [1] 無 (NONE)  [2] 顯示求助選單 (SHOW_CRISIS_MENU)  [3] 顯示主選單 (SHOW_MAIN_MENU)")
            act_choice = input("   請選擇動作 (預設1): ")
            new_action = "NONE"
            if act_choice == "2": new_action = "SHOW_CRISIS_MENU"
            if act_choice == "3": new_action = "SHOW_MAIN_MENU"
            
            create_new_category(new_cat_name, int(new_danger), new_response, new_action, selected_words)
            
        else:
            print("❌ 輸入無效，取消操作。")
            
    except ValueError:
        print("❌ 輸入格式錯誤，請輸入數字。")
#ngrok config add-authtoken 38HkZGAIVLfaCKZZVIcJkem9nK9_3KeMcMJGCFbaUZQrC7fxN
# ngrok http http://127.0.0.1:5001/