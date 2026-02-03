import pandas as pd
import numpy as np
import os

DATA_FOLDER = "data"
INPUT_FILE = os.path.join(DATA_FOLDER, "raw_air_quality_data.csv")
OUTPUT_FILE = os.path.join(DATA_FOLDER, "clean_air_quality_data.csv")

print("📥 Đang đọc dữ liệu...")
df = pd.read_csv(INPUT_FILE)
print("Ban đầu:", len(df))

# ==================================================
# 1️⃣ Chuẩn hóa thời gian
# ==================================================
df["getTime"] = pd.to_datetime(df["getTime"], errors="coerce")
df = df.dropna(subset=["getTime"])
df = df.sort_values(["stationId", "getTime"])

# ==================================================
# 2️⃣ Giữ các cột cần cho AQI
# ==================================================
pollutants = ["PM-2-5", "PM-10", "NO2", "SO2", "O3", "CO"]
base_cols = ["stationId", "stationName", "getTime"]

existing_cols = [c for c in pollutants if c in df.columns]
df = df[base_cols + existing_cols]

# ==================================================
# 3️⃣ Chuyển sang số (không nội suy toàn bộ)
# ==================================================
for col in existing_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

print("\nNaN sau khi ép số:")
print(df[existing_cols].isna().sum())

# ==================================================
# 4️⃣ Loại giá trị vô lý (không clip, mà loại hẳn)
# ==================================================
limits = {
    "PM-2-5": (0, 500),
    "PM-10": (0, 800),
    "NO2": (0, 1000),
    "SO2": (0, 1000),
    "O3": (0, 800),
    "CO": (0, 50)
}

for col, (low, high) in limits.items():
    if col in df.columns:
        df.loc[(df[col] < low) | (df[col] > high), col] = np.nan

# ==================================================
# 5️⃣ KHÔNG nội suy dài — chỉ giữ dữ liệu gốc
# ==================================================
# VN_AQI sẽ xử lý bằng NOWCAST sau
# Ta chỉ cần loại dòng không có bất kỳ chất nào

df["valid_pollutants"] = df[existing_cols].notna().sum(axis=1)
df = df[df["valid_pollutants"] > 0]
df = df.drop(columns=["valid_pollutants"])

print("Sau khi bỏ dòng không có chất nào:", len(df))

# ==================================================
# 6️⃣ Gộp về dữ liệu giờ (nếu crawl nhiều lần/giờ)
# ==================================================
df["hour"] = df["getTime"].dt.floor("H")

df = (
    df.groupby(["stationId", "stationName", "hour"], as_index=False)
      .mean(numeric_only=True)
)

df = df.rename(columns={"hour": "getTime"})

print("Sau khi gom về giờ:", len(df))

# ==================================================
# 7️⃣ Lưu file sạch
# ==================================================
os.makedirs(DATA_FOLDER, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("✅ File sẵn sàng cho tính VN_AQI:", OUTPUT_FILE)
