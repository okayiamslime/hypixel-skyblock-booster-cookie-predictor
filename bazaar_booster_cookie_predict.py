# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import plotly.graph_objects as go

# ==========================================
# 1. 重新讀取原始資料
# ==========================================
print("📥 正在讀取資料庫...")
# 確保每次執行都是從最原始的檔案開始，不怕把資料改壞
df = pd.read_csv('/content/drive/MyDrive/Bazaar_Prediction_Project/bazaar_history.csv')

# ==========================================
# 2. 指定物品並修復時間間隔
# ==========================================
print("🧹 正在過濾物品與修復時間間隔...")
TARGET_ITEM = 'BOOSTER_COOKIE'  # 🌟 你可以在這裡改成你要預測的物品 (例如 BOOSTER_COOKIE)

# 只留下該物品的資料
df = df[df['item_id'] == TARGET_ITEM].copy()
# 刪除文字欄位，避免後續數學計算報錯
df = df.drop(columns=['item_id'])

# 將字串轉換為時間格式並設為索引
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

# 重採樣為 1 小時 (1h) 並用平均值合併，接著用插值法補齊缺漏
df = df.resample('5min').mean()
df = df.interpolate(method='time')

# 恢復索引並清除無法填補的極端空值
df = df.reset_index()
df = df.dropna()

cols = ['buy_price', 'sell_price', 'buy_volume', 'sell_volume']
df[cols] = df[cols].round(0).astype(int)

print(f"✅ 【{TARGET_ITEM}】 資料清洗完成！前五筆資料如下：")
display(df.head())

# 特徵工程

print("正在進行特徵工程...")

# 創造新特徵：買賣價差 (Spread)
df['spread'] = df['sell_price'] - df['buy_price']

# 創造目標變數 Y：五分鐘後的買單價格 (將價格往上平移一格)
df['future_buy_price'] = df['buy_price'].shift(-1)

# 清除最後一筆因為平移而產生空值 (NaN) 的資料
df = df.dropna()

cols = ['buy_price', 'sell_price', 'buy_volume', 'sell_volume']
df[cols] = df[cols].round(0).astype(int)

print("✅ 特徵工程完成！右側已新增 spread 與 future_buy_price 欄位：")
display(df.head())

# 準備資料並訓練模型

print("正在切分資料與訓練模型...")

# 設定特徵變數 X (當下狀態) 與 目標變數 Y (未來價格)
X = df[['buy_price', 'buy_volume', 'spread']]
y = df['future_buy_price']

# 切分訓練集 (80%) 與測試集 (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 建立並訓練線性迴歸模型
reg = LinearRegression()
reg.fit(X_train, y_train)

print("✅ 模型訓練完成！")

# 模型評估與特徵影響力 (係數)

# 1. 評估模型準確度
y_pred = reg.predict(X_test)
score = r2_score(y_test, y_pred)
print(f"🎯 模型的 R2-score: {score:.4f} (越接近1代表解釋程度越好)")

# 2. 找出截距與特徵係數
print(f"\n📌 模型的截距 (Intercept): {reg.intercept_:.4f}")
print("📌 各特徵的權重係數 (Coefficient):")

# 將係數整理成 DataFrame 顯示，方便閱讀
coeff_df = pd.DataFrame(reg.coef_, X.columns, columns=['Coefficient'])
display(coeff_df)

# 3D 互動式資料視覺化 (Plotly)

print("📊 正在生成 3D 視覺化圖表...")

# 為了繪製 3D 迴歸平面，我們額外訓練一個只有兩個特徵的小模型
X_3d = df[['buy_price', 'buy_volume']]
reg_3d = LinearRegression()
reg_3d.fit(X_3d, y)

# 產生網格點 (用來畫出預測平面)
x_surf = np.linspace(df['buy_price'].min(), df['buy_price'].max(), 20)
y_surf = np.linspace(df['buy_volume'].min(), df['buy_volume'].max(), 20)
x_surf, y_surf = np.meshgrid(x_surf, y_surf)
z_surf = reg_3d.intercept_ + (reg_3d.coef_[0] * x_surf) + (reg_3d.coef_[1] * y_surf)

# 繪製真實數據點 (散佈圖)
scatter = go.Scatter3d(
    x=df['buy_price'],
    y=df['buy_volume'],
    z=df['future_buy_price'],
    mode='markers',
    marker=dict(size=4, color=df['future_buy_price'], colorscale='Viridis', opacity=0.8),
    name='真實歷史數據'
)

# 繪製預測平面 (迴歸面)
surface = go.Surface(
    x=x_surf,
    y=y_surf,
    z=z_surf,
    colorscale='Reds',
    opacity=0.5,
    name='預測迴歸平面'
)

# 設定圖表版面與標籤
layout = go.Layout(
    title='Hypixel Bazaar: 當下價格、交易量 與 未來價格預測模型',
    scene=dict(
        xaxis_title='當下買單價格 (Buy Price)',
        yaxis_title='當下交易量 (Buy Volume)',
        zaxis_title='預測五分鐘後價格 (Future Price)'
    ),
    width=900,
    height=700
)

# 顯示圖表
fig = go.Figure(data=[scatter, surface], layout=layout)
fig.show()