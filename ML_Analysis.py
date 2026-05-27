import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import plotly.graph_objects as go

# ==========================================
# 1. 讀取資料與清洗 (Data Cleaning)
# ==========================================
print("📥 正在讀取資料庫...")
df = pd.read_csv('bazaar_history.csv')

# 設定要預測的目標物品
TARGET_ITEM = 'BOOSTER_COOKIE'
df = df[df['item_id'] == TARGET_ITEM].copy()
df = df.drop(columns=['item_id'])

# 修復時間間隔與補漏 (Time-Series Resampling & Interpolation)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)
df = df.resample('1h').mean()
df = df.interpolate(method='time')
df = df.reset_index()
df = df.dropna()

# 強制轉為乾淨的整數
cols = ['buy_price', 'sell_price', 'buy_volume', 'sell_volume']
df[cols] = df[cols].round(0).astype(int)

# ==========================================
# 2. 特徵工程 (Feature Engineering)
# ==========================================
# 創造價差 (Spread)
df['spread'] = df['sell_price'] - df['buy_price']
# 創造預測目標 (下一小時的買價)
df['future_buy_price'] = df['buy_price'].shift(-1)
df = df.dropna()

# ==========================================
# 3. 訓練線性迴歸模型 (Model Training)
# ==========================================
# 🌟 排除 sell_price 以避免共線性 (Multicollinearity)
X = df[['buy_price', 'buy_volume', 'spread']]
y = df['future_buy_price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

reg = LinearRegression()
reg.fit(X_train, y_train)

# ==========================================
# 4. 模型評估 (Evaluation)
# ==========================================
score = r2_score(y_test, reg.predict(X_test))
print(f"\n🎯 模型的 R2-score: {score:.4f}")
print(f"📌 模型的截距 (Intercept): {reg.intercept_:.4f}")

print("\n📌 各特徵的權重係數 (Coefficient):")
coeff_df = pd.DataFrame(reg.coef_, X.columns, columns=['Coefficient'])
display(coeff_df)

# ==========================================
# 5. 3D 視覺化 (Data Visualization)
# ==========================================
print("\n📊 正在生成 3D 視覺化圖表...")

# 為了畫 3D 平面，使用兩個主要特徵
X_3d = df[['buy_price', 'buy_volume']]
reg_3d = LinearRegression()
reg_3d.fit(X_3d, y)

x_surf = np.linspace(df['buy_price'].min(), df['buy_price'].max(), 20)
y_surf = np.linspace(df['buy_volume'].min(), df['buy_volume'].max(), 20)
x_surf, y_surf = np.meshgrid(x_surf, y_surf)
z_surf = reg_3d.intercept_ + (reg_3d.coef_[0] * x_surf) + (reg_3d.coef_[1] * y_surf)

scatter = go.Scatter3d(
    x=df['buy_price'], y=df['buy_volume'], z=df['future_buy_price'],
    mode='markers', marker=dict(size=4, color=df['future_buy_price'], colorscale='Viridis', opacity=0.8),
    name='真實數據'
)
surface = go.Surface(
    x=x_surf, y=y_surf, z=z_surf, colorscale='Reds', opacity=0.5, name='預測面'
)

layout = go.Layout(
    title=f'Hypixel Bazaar: {TARGET_ITEM} 價格預測模型',
    scene=dict(
        xaxis_title='當下買單價格 (Buy Price)',
        yaxis_title='當下交易量 (Buy Volume)',
        zaxis_title='預測下一小時價格 (Future Price)'
    ),
    width=900, height=700
)

fig = go.Figure(data=[scatter, surface], layout=layout)
fig.show()
