# debug_setup.py
import mysql.connector
from config import Config

def init_db_and_test():
    print("🚀 開始檢測資料庫連線...")
    
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        print("✅ 資料庫連線成功！")

        # 1. 檢查並建立 pending_messages 表格
        print("🔧 檢查 pending_messages 表格...")
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS pending_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_sql)
        print("✅ 表格檢查/建立完成。")

        # 2. 插入一筆測試資料
        print("📝 嘗試插入一筆測試訊息...")
        insert_sql = "INSERT INTO pending_messages (user_id, user_message, status) VALUES (%s, %s, %s)"
        cursor.execute(insert_sql, ("TEST_USER_001", "這是一則測試訊息，如果你看到這行字，代表系統運作正常！", "pending"))
        conn.commit()
        print("✅ 測試資料插入成功！")

        # 3. 讀取測試
        cursor.execute("SELECT count(*) FROM pending_messages WHERE status='pending'")
        count = cursor.fetchone()[0]
        print(f"📊 目前待審核訊息數量: {count} 筆")

        conn.close()
        print("\n🎉 修復完成！請重新啟動 run.py 並打開網頁 /admin/review 查看。")

    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        print("請檢查 config.py 的資料庫帳號密碼是否正確。")

if __name__ == "__main__":
    init_db_and_test()