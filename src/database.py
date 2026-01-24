# src/database.py
import mysql.connector
import json
from config import Config

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST, user=Config.DB_USER,
        password=Config.DB_PASSWORD, database=Config.DB_NAME
    )

# --- 核心功能: 意圖管理 ---
def get_intents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bot_intents")
        rows = cursor.fetchall()
        for row in rows:
            if isinstance(row['keywords'], str):
                try: row['keywords'] = json.loads(row['keywords'])
                except: row['keywords'] = []
        return rows
    except Exception as e:
        print(f"DB Error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def update_keywords_in_db(category_id, new_keywords):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT keywords FROM bot_intents WHERE id = %s", (category_id,))
        row = cursor.fetchone()
        current = json.loads(row['keywords']) if row and isinstance(row['keywords'], str) else (row['keywords'] if row else [])
        updated = list(set(current + new_keywords))
        cursor.execute("UPDATE bot_intents SET keywords = %s WHERE id = %s", (json.dumps(updated, ensure_ascii=False), category_id))
        conn.commit()
    except Exception as e:
        print(f"Update Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def insert_new_category(category, danger, response, action, keywords):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO bot_intents (category, danger, response, action, keywords) VALUES (%s, %s, %s, %s, %s)", 
                       (category, danger, response, action, json.dumps(keywords, ensure_ascii=False)))
        conn.commit()
    except Exception as e:
        print(f"Insert Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

# --- 修飾語管理 ---
def get_all_modifiers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM response_modifiers ORDER BY category, mod_type")
        return cursor.fetchall()
    except: return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def add_modifier(category, mod_type, content):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO response_modifiers (category, mod_type, content) VALUES (%s, %s, %s)", (category, mod_type, content))
        conn.commit()
    except: pass
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def delete_modifier(mod_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM response_modifiers WHERE id = %s", (mod_id,))
        conn.commit()
    except: pass
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

# ==========================================
# 🔥 審核與歷史紀錄功能 (重點修改區)
# ==========================================

def save_pending_message(user_id, user_message):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # 確保表格存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                user_message TEXT,
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("INSERT INTO pending_messages (user_id, user_message) VALUES (%s, %s)", (user_id, user_message))
        conn.commit()
        return True
    except Exception as e:
        print(f"Save Pending Error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_pending_messages(user_id=None):
    """ 取得待審核訊息 (支援 User ID 搜尋) """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = "SELECT * FROM pending_messages WHERE status = 'pending'"
        params = []
        
        if user_id:
            sql += " AND user_id = %s"
            params.append(user_id)
            
        sql += " ORDER BY created_at DESC"
        
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    except Exception as e:
        print(f"Get Pending Error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def update_message_status(msg_id, status):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE pending_messages SET status = %s WHERE id = %s", (status, msg_id))
        conn.commit()
    except: pass
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

# --- 對話歷史紀錄 (Chat Logs) ---

def log_chat(user_id, role, message):
    """ 記錄每句對話 """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                role VARCHAR(20),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("INSERT INTO chat_logs (user_id, role, message) VALUES (%s, %s, %s)", (user_id, role, message))
        conn.commit()
    except Exception as e:
        print(f"Log Chat Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_chat_history_by_user(user_id):
    """ 取得全部歷史 (給 History 頁面用) """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chat_logs WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
        return cursor.fetchall()
    except: return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()

def get_recent_chat_history(user_id, limit=5):
    """ 取得最近 N 筆歷史 (給 Review 頁面 AI 參考用) """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # 先抓最新的 N 筆 (DESC)，再轉回時間正序 (ASC)
        sql = f"""
            SELECT * FROM (
                SELECT * FROM chat_logs WHERE user_id = %s ORDER BY id DESC LIMIT %s
            ) sub ORDER BY id ASC
        """
        cursor.execute(sql, (user_id, limit))
        return cursor.fetchall()
    except Exception as e:
        print(f"Get Recent History Error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected(): conn.close()