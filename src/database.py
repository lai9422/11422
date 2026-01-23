import json
import mysql.connector
from config import Config

def get_intents():
    """
    從 MySQL 讀取意圖。若失敗則回傳備用資料。
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            connect_timeout=3
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bot_intents")
        rows = cursor.fetchall()

        intents = []
        for row in rows:
            # 解析 keywords JSON 字串
            if isinstance(row['keywords'], str):
                try:
                    row['keywords'] = json.loads(row['keywords'])
                except:
                    row['keywords'] = []
            intents.append(row)

        cursor.close()
        conn.close()

        if not intents:
            raise Exception("Database Empty")
        
        return intents

    except Exception as e:
        print(f"⚠️ 資料庫讀取失敗 ({e})，切換至備用資料")
        return [
            {
                "category": "緊急求助 (備用)",
                "keywords": ["死", "自殺", "頂樓"],
                "danger": 5,
                "response": "1系統連線中，請先冷靜。我們很關心你，請撥打 113。",
                "action": "SHOW_CRISIS_MENU"
            }
        ]

def update_keywords_in_db(category_id, new_keywords):
    """ 更新現有分類的關鍵字 (讀取舊的 -> 合併 -> 寫回) """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)

        # 1. 查出舊的
        cursor.execute("SELECT keywords FROM bot_intents WHERE id = %s", (category_id,))
        row = cursor.fetchone()
        
        current_keywords = []
        if row and row['keywords']:
            # 判斷是字串還是已經是 list (視 driver 版本而定)
            if isinstance(row['keywords'], str):
                current_keywords = json.loads(row['keywords'])
            else:
                current_keywords = row['keywords']

        # 2. 合併 (使用 set 去重複)
        updated_set = set(current_keywords)
        for w in new_keywords:
            updated_set.add(w)
        
        final_json = json.dumps(list(updated_set), ensure_ascii=False)

        # 3. 更新
        cursor.execute("UPDATE bot_intents SET keywords = %s WHERE id = %s", (final_json, category_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB 更新錯誤: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def insert_new_category(category, danger, response, action, keywords):
    """ 插入全新的分類 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        keywords_json = json.dumps(keywords, ensure_ascii=False)
        
        sql = """
        INSERT INTO bot_intents (category, danger, response, action, keywords)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (category, danger, response, action, keywords_json))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ DB 新增錯誤: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def get_all_modifiers():
    """ 取得所有修飾語 (供後台顯示用) """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM response_modifiers ORDER BY category, mod_type")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"❌ 讀取修飾語失敗: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def add_modifier(category, mod_type, content):
    """ 新增一條修飾語 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        sql = "INSERT INTO response_modifiers (category, mod_type, content) VALUES (%s, %s, %s)"
        cursor.execute(sql, (category, mod_type, content))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 新增修飾語失敗: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def delete_modifier(mod_id):
    """ 刪除一條修飾語 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("DELETE FROM response_modifiers WHERE id = %s", (mod_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 刪除修飾語失敗: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()



# [請將這段程式碼加到 src/database.py 的最下方]

def save_pending_message(user_id, user_message):
    """ 儲存使用者的訊息到待審核區 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        sql = "INSERT INTO pending_messages (user_id, user_message) VALUES (%s, %s)"
        cursor.execute(sql, (user_id, user_message))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 儲存待審訊息失敗: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_pending_messages():
    """ 取得所有狀態為 'pending' 的訊息 """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pending_messages WHERE status = 'pending' ORDER BY created_at DESC")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"❌ 讀取待審訊息失敗: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def update_message_status(msg_id, status):
    """ 更新訊息狀態 (例如改為 'replied') """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("UPDATE pending_messages SET status = %s WHERE id = %s", (status, msg_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ 更新狀態失敗: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()


# [請加到 src/database.py 最下方]

def log_chat(user_id, role, message):
    """ 記錄一筆對話 (User 或 Bot) """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor()
        sql = "INSERT INTO chat_logs (user_id, role, message) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user_id, role, message))
        conn.commit()
    except Exception as e:
        print(f"❌ 記錄對話失敗: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_chat_history_by_user(user_id):
    """ 取得指定 User 的完整對話紀錄 (依時間排序) """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST, user=Config.DB_USER,
            password=Config.DB_PASSWORD, database=Config.DB_NAME
        )
        cursor = conn.cursor(dictionary=True)
        # 依時間先後排序，這樣才能還原前後文
        sql = "SELECT * FROM chat_logs WHERE user_id = %s ORDER BY created_at ASC"
        cursor.execute(sql, (user_id,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print(f"❌ 查詢對話失敗: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()