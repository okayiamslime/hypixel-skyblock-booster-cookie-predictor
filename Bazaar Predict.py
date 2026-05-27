import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import os

def fetch_bazaar_data():
    print("正在呼叫 Hypixel API...")
    url = "https://api.hypixel.net/skyblock/bazaar"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if not data.get('success'):
            print("❌ API 請求失敗")
            return
            
        products = data['products']
        
        # 你想追蹤的物品清單
        TARGET_ITEMS = ['BOOSTER_COOKIE']
        
        records = []

        tz_tw = timezone(timedelta(hours=8))
        timestamp = datetime.now(tz_tw).strftime('%Y-%m-%d %H:%M:%S')
        
        for item_id in TARGET_ITEMS:
            if item_id in products:
                prod = products[item_id]
                qs = prod['quick_status']
                records.append({
                    'timestamp': timestamp,
                    'item_id': item_id,
                    'buy_price': qs['buyPrice'],
                    'sell_price': qs['sellPrice'],
                    'buy_volume': qs['buyVolume'],
                    'sell_volume': qs['sellVolume']
                })


        df = pd.DataFrame(records)
        
        cols = ['buy_price', 'sell_price', 'buy_volume', 'sell_volume']
        df[cols] = df[cols].round(0).astype(int)
        
        # 使 GitHub 機器人正確存檔
        file_name = 'bazaar_history.csv'
        
        if not os.path.isfile(file_name):
            df.to_csv(file_name, index=False)
            print(f"✨ 建立新資料庫並寫入 {len(records)} 筆資料")
        else:
            df.to_csv(file_name, mode='a', header=False, index=False)
            print(f"✅ 成功將 {len(records)} 筆新資料更新至資料庫 ({timestamp})")
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    fetch_bazaar_data()
