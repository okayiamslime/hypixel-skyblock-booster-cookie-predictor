import requests
import pandas as pd
from datetime import datetime
import pytz
import os

# ==========================================
# 1. 基本設定
# ==========================================
# API 網址
URL = "https://api.hypixel.net/v2/skyblock/bazaar"

# 設定你想抓取的物品 ID (必須是大寫與底線)
# 你可以在這裡自由新增或刪減你想觀察的物品
TARGET_ITEMS = [
    "BOOSTER_COOKIE"
]

# 設定本機存檔路徑 (這裡預設存在與這個 .py 檔同一個資料夾)
# 你也可以寫絕對路徑，例如 "C:/SkyblockProject/bazaar_history.csv"
CSV_FILE_NAME = "bazaar_history.csv"

# ==========================================
# 2. 爬蟲主程式
# ==========================================
def fetch_bazaar_data():
    try:
        # 發送請求獲取資料
        response = requests.get(URL, timeout=10)
        data = response.json()

        if data.get("success"):
            bazaar_data = data["products"]
            records = []
            
            # 取得當下台灣時間
            tw_tz = pytz.timezone('Asia/Taipei')
            current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
            
            # 提取目標物品的數據
            for item in TARGET_ITEMS:
                if item in bazaar_data:
                    quick_status = bazaar_data[item]["quick_status"]
                    
                    record = {
                        "timestamp": current_time,
                        "item_id": quick_status["productId"],
                        "buy_price": int(quick_status["buyPrice"]),   # 轉為整數，避免科學記號 e+05
                        "sell_price": int(quick_status["sellPrice"]), # 轉為整數
                        "buy_volume": quick_status["buyVolume"],
                        "sell_volume": quick_status["sellVolume"]
                    }
                    records.append(record)
            
            # 如果有抓到資料，則進行存檔
            if records:
                df = pd.DataFrame(records)
                
                # 檢查檔案是否已存在，決定是否寫入標題列 (header)
                file_exists = os.path.isfile(CSV_FILE_NAME)
                
                # mode='a' 代表附加 (Append)，不會覆蓋舊資料
                df.to_csv(CSV_FILE_NAME, mode='a', header=not file_exists, index=False)
                
                # 寫入簡單的 Log，方便你未來檢查排程有沒有乖乖跑
                with open("scraper_log.txt", "a", encoding="utf-8") as log:
                    log.write(f"[{current_time}] 成功記錄 {len(records)} 筆資料。\n")
                    
        else:
            write_error_log("API 回傳 success 為 False")
            
    except Exception as e:
        write_error_log(str(e))

def write_error_log(error_msg):
    # 紀錄錯誤訊息
    tw_tz = pytz.timezone('Asia/Taipei')
    current_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
    with open("scraper_log.txt", "a", encoding="utf-8") as log:
        log.write(f"[{current_time}] 發生錯誤: {error_msg}\n")

# ==========================================
# 3. 執行程式
# ==========================================
if __name__ == "__main__":
    fetch_bazaar_data()