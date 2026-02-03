import pandas as pd
import numpy as np
import os

DATA_FOLDER = "data"
INPUT_FILE = os.path.join(DATA_FOLDER, "clean_air_quality_data.csv")
OUTPUT_FILE = os.path.join(DATA_FOLDER, "aqi_result.csv")

print("📥 Đang đọc dữ liệu sạch...")
df = pd.read_csv(INPUT_FILE)

# =========================
# HÀM TÍNH AQI NỘI SUY
# =========================
def calc_aqi(cp, breakpoints):
    for bp in breakpoints:
        if bp["C_low"] <= cp <= bp["C_high"]:
            return ((bp["I_high"] - bp["I_low"]) /
                    (bp["C_high"] - bp["C_low"])) * (cp - bp["C_low"]) + bp["I_low"]
    return np.nan


# =========================
# NGƯỠNG VN_AQI
# =========================
AQI_LEVELS = [
    {"I_low": 0,   "I_high": 50},
    {"I_low": 51,  "I_high": 100},
    {"I_low": 101, "I_high": 150},
    {"I_low": 151, "I_high": 200},
    {"I_low": 201, "I_high": 300},
    {"I_low": 301, "I_high": 500},
]

BREAKPOINTS = {
    "PM-2-5": [
        {"C_low": 0,   "C_high": 12,   **AQI_LEVELS[0]},
        {"C_low": 12.1,"C_high": 35.4, **AQI_LEVELS[1]},
        {"C_low": 35.5,"C_high": 55.4, **AQI_LEVELS[2]},
        {"C_low": 55.5,"C_high": 150.4,**AQI_LEVELS[3]},
        {"C_low": 150.5,"C_high": 250.4,**AQI_LEVELS[4]},
        {"C_low": 250.5,"C_high": 500, **AQI_LEVELS[5]},
    ],
    "PM-10": [
        {"C_low": 0,   "C_high": 54,   **AQI_LEVELS[0]},
        {"C_low": 55,  "C_high": 154,  **AQI_LEVELS[1]},
        {"C_low": 155, "C_high": 254,  **AQI_LEVELS[2]},
        {"C_low": 255, "C_high": 354,  **AQI_LEVELS[3]},
        {"C_low": 355, "C_high": 424,  **AQI_LEVELS[4]},
        {"C_low": 425, "C_high": 604,  **AQI_LEVELS[5]},
    ],
    "NO2": [
        {"C_low": 0, "C_high": 53,  **AQI_LEVELS[0]},
        {"C_low": 54, "C_high": 100, **AQI_LEVELS[1]},
        {"C_low": 101,"C_high": 360, **AQI_LEVELS[2]},
        {"C_low": 361,"C_high": 649, **AQI_LEVELS[3]},
        {"C_low": 650,"C_high": 1249,**AQI_LEVELS[4]},
        {"C_low": 1250,"C_high": 2049,**AQI_LEVELS[5]},
    ],
    "SO2": [
        {"C_low": 0, "C_high": 35,  **AQI_LEVELS[0]},
        {"C_low": 36,"C_high": 75,  **AQI_LEVELS[1]},
        {"C_low": 76,"C_high": 185, **AQI_LEVELS[2]},
        {"C_low": 186,"C_high": 304,**AQI_LEVELS[3]},
        {"C_low": 305,"C_high": 604,**AQI_LEVELS[4]},
        {"C_low": 605,"C_high": 1004,**AQI_LEVELS[5]},
    ],
    "O3": [
        {"C_low": 0, "C_high": 54,  **AQI_LEVELS[0]},
        {"C_low": 55,"C_high": 70,  **AQI_LEVELS[1]},
        {"C_low": 71,"C_high": 85,  **AQI_LEVELS[2]},
        {"C_low": 86,"C_high": 105, **AQI_LEVELS[3]},
        {"C_low": 106,"C_high": 200,**AQI_LEVELS[4]},
    ],
    "CO": [
        {"C_low": 0.0,"C_high": 4.4, **AQI_LEVELS[0]},
        {"C_low": 4.5,"C_high": 9.4, **AQI_LEVELS[1]},
        {"C_low": 9.5,"C_high": 12.4,**AQI_LEVELS[2]},
        {"C_low": 12.5,"C_high": 15.4,**AQI_LEVELS[3]},
        {"C_low": 15.5,"C_high": 30.4,**AQI_LEVELS[4]},
        {"C_low": 30.5,"C_high": 50.4,**AQI_LEVELS[5]},
    ]
}

# =========================
# TÍNH AQI TỪNG CHẤT
# =========================
pollutants = [c for c in BREAKPOINTS.keys() if c in df.columns]

for pol in pollutants:
    print(f"🔎 Tính AQI cho {pol}")
    df[f"AQI_{pol}"] = df[pol].apply(lambda x: calc_aqi(x, BREAKPOINTS[pol]) if pd.notna(x) else np.nan)

# =========================
# AQI TỔNG = MAX
# =========================
aqi_cols = [f"AQI_{p}" for p in pollutants]
df["AQI"] = df[aqi_cols].max(axis=1)

# =========================
# PHÂN LOẠI
# =========================
def classify_aqi(aqi):
    if aqi <= 50: return "Tốt"
    if aqi <= 100: return "Trung bình"
    if aqi <= 150: return "Kém"
    if aqi <= 200: return "Xấu"
    if aqi <= 300: return "Rất xấu"
    return "Nguy hại"

df["Level"] = df["AQI"].apply(classify_aqi)

# =========================
# LƯU FILE
# =========================
os.makedirs(DATA_FOLDER, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("✅ Đã tính AQI xong →", OUTPUT_FILE)
