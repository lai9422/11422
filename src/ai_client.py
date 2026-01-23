import random
from src.database import get_all_modifiers

class AIClient:
    def __init__(self):
        print("🔄 AIClient 正在初始化，準備載入修飾語...")
        self.reload_modifiers()

    def reload_modifiers(self):
        """ 從資料庫重新載入修飾語到記憶體 """
        rows = get_all_modifiers()
        
        self.prefixes = {}
        self.suffixes = {}
        self.particles = []

        for row in rows:
            cat = row['category']
            typ = row['mod_type']
            content = row['content']

            if typ == 'prefix':
                if cat not in self.prefixes: self.prefixes[cat] = []
                self.prefixes[cat].append(content)
            elif typ == 'suffix':
                if cat not in self.suffixes: self.suffixes[cat] = []
                self.suffixes[cat].append(content)
            elif typ == 'particle':
                self.particles.append(content)
        
        # === Debug 訊息 ===
        count_p = sum(len(v) for v in self.prefixes.values())
        if count_p == 0 and not self.particles:
            print("⚠️ [警告] 資料庫中沒有任何修飾語！請確認你有執行 INSERT SQL 指令。")
        else:
            print(f"✅ 修飾語載入成功：前綴 {count_p} 個, 後綴 {sum(len(v) for v in self.suffixes.values())} 個, 語氣詞 {len(self.particles)} 個")

    def _get_random_text(self, dictionary, category):
        # 優先找該分類，找不到找 default
        pool = dictionary.get(category, dictionary.get("default", []))
        if pool:
            return random.choice(pool)
        return "" # 如果資料庫沒資料，回傳空字串

    def polish_response(self, user_text, base_response, category, level=2):
        try:
            base_response = base_response.strip()

            # === Debug: 印出現在的狀態 ===
            print(f"🔧 [修飾中] 分類: {category} | 等級: {level} | 原句: {base_response}")

            if level == 0: 
                return base_response

            if level == 1:
                # 簡單語氣詞
                part = random.choice(self.particles) if self.particles else "～"
                if base_response and base_response[-1] not in ["。", "！", "？", "!", "?"]:
                    return f"{base_response}{part}"
                return base_response

            # 取得前綴與後綴
            prefix = self._get_random_text(self.prefixes, category)
            suffix = self._get_random_text(self.suffixes, category)
            
            # 如果資料庫是空的，prefix 會是 ""，這裡手動加一個 fallback 測試用
            if not prefix and not self.prefixes:
                prefix = "(測試前綴) "

            final_text = base_response
            if level == 2:
                final_text = f"{prefix}{base_response}"
            elif level == 3:
                final_text = f"{prefix}{base_response}{suffix}"

            print(f"➡️ [結果] {final_text}")
            return final_text

        except Exception as e:
            print(f"❌ 修飾錯誤: {e}")
            return base_response

# 建立實例
ai_service = AIClient()