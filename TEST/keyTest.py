import requests

# ==========================================
# 把你那串 s1jqKWheyc... 開頭的 Token 貼在這裡
# ==========================================
token = '2SgcahcCOJ4jtvz5AhPVI13LLMNt2hoZzRSeizr5Oa34A6e8eymrt+glR/PeXBlV/KAtaAgGZqpuR3gMQfNakO VyoaXELWHRz26EtlvmwPXH8yB18cHqepg8/xprc4ggS2b0t5wHSaRtYhi6GlnUoQdB04t89/1O/w1cDnyilFU='
# 1. 自動去除前後空白 (這一步常常能解決問題！)
token = token.strip() 

print(f"測試 Token: {token[:10]}... (長度: {len(token)})")
print("正在連線 LINE 伺服器進行驗證...")

# 2. 直接發送測試請求給 LINE
headers = {"Authorization": f"Bearer {token}"}
url = "https://api.line.me/v2/bot/info"

try:
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        print("\n✅ 恭喜！這個 Token 是有效的！")
        print("機器人名稱:", response.json().get('displayName'))
        print(">> 請回到原本的 b.py，把這一串有效的 Token 貼上去 (記得用 .strip() 處理)")
    elif response.status_code == 401:
        print("\n❌ 驗證失敗 (401)！")
        print("原因：Token 無效。")
        print("解決：請回到 LINE 後台，確定按下了 [Reissue] 按鈕，並且複製了「新的」那一串。")
    else:
        print(f"\n⚠️ 其他錯誤 ({response.status_code})")
        print(response.text)

except Exception as e:
    print("連線發生錯誤:", e)