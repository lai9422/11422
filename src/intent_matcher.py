def find_best_match(seg_list, intents):
    """
    比對斷詞結果與意圖庫
    回傳: 危險指數最高的意圖物件 (若無命中則回傳 None)
    """
    found_intents = []
    
    # 轉成 set 加速比對
    user_keywords = set(seg_list)

    # 比對所有意圖
    for intent in intents:
        # 取交集：只要有任何一個關鍵字命中就算
        if set(intent["keywords"]) & user_keywords:
            found_intents.append(intent)
    
    # 若有命中，選出危險度最高的一個
    if found_intents:
        # sort key: 依照 danger 欄位降序排列
        found_intents.sort(key=lambda x: x["danger"], reverse=True)
        best_match = found_intents[0]
        print(f"🎯 命中意圖: {best_match['category']} (危險度: {best_match['danger']})")
        return best_match
    
    return None