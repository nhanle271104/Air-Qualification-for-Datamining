import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score

print("📥 Đọc dữ liệu AQI...")
df = pd.read_csv("data/aqi_result.csv")

# ===== CHỌN CỘT CẦN =====
df = df[["getTime", "PM-2-5", "AQI_PM-2-5"]]

df["PM-2-5"] = pd.to_numeric(df["PM-2-5"], errors="coerce")
df["AQI_PM-2-5"] = pd.to_numeric(df["AQI_PM-2-5"], errors="coerce")

df = df.dropna()

# ===== TIME =====
df["getTime"] = pd.to_datetime(df["getTime"])
df = df.sort_values("getTime")

# ===== LẤY TRUNG BÌNH THEO NGÀY (CHỈ CỘT SỐ) =====
daily = df.resample("D", on="getTime")[["PM-2-5", "AQI_PM-2-5"]].mean()

print("Số ngày dữ liệu:", len(daily))

# ===== FEATURE MỞ RỘNG (QUAN TRỌNG) =====
daily["AQI_today"] = daily["AQI_PM-2-5"]          # AQI hôm nay
daily["PM25_yesterday"] = daily["PM-2-5"].shift(1) # PM2.5 hôm qua

# ===== TẠO BÀI TOÁN HÔM NAY → NGÀY MAI =====
daily["AQI_tomorrow"] = daily["AQI_PM-2-5"].shift(-1)
daily = daily.dropna()

print("Sau tạo cặp hôm nay → ngày mai:", len(daily))

X = daily[["PM-2-5"]]
y = daily["AQI_tomorrow"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)} | Test: {len(X_test)}")

# ===== RANDOM FOREST =====
rf = RandomForestRegressor(n_estimators=200, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)

# ===== LINEAR REGRESSION =====
lr = LinearRegression()
lr.fit(X_train, y_train)
lr_pred = lr.predict(X_test)

# ===== SO SÁNH =====
print("\n🔎 SO SÁNH DỰ BÁO AQI NGÀY MAI")

print("\n📊 Random Forest")
print("MAE:", round(mean_absolute_error(y_test, rf_pred), 2))
print("R2 :", round(r2_score(y_test, rf_pred), 3))

print("\n📊 Linear Regression")
print("MAE:", round(mean_absolute_error(y_test, lr_pred), 2))
print("R2 :", round(r2_score(y_test, lr_pred), 3))

