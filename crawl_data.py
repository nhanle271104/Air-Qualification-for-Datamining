import requests
import csv
import os
from datetime import datetime, timedelta

# ================= API =================
STATION_API = "https://tedp.vn/api/public-data/search/findPublicDataWithValidParentIn?stationType=4&page=0&size=50"
DATA_API = "https://tedp.vn/api/data_hour/search/findByStationIdAndGetTimeBetweenOrderByGetTimeDesc"
DATA_FOLDER = "data"

# ============ LẤY DANH SÁCH TRẠM =============
def fetch_stations():
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    response = requests.get(STATION_API, headers=headers)
    data = response.json()
    stations = data.get("_embedded", {}).get("public-data", [])

    # Lọc trạm Hà Nội
    hanoi_stations = [
        s for s in stations
        if s.get("stationName") and "Hà Nội" in s.get("stationName")
    ]
    return hanoi_stations


# ============ LẤY DỮ LIỆU THEO TRẠM ============
def fetch_station_data(station_id, from_time, to_time):
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    params = {
        "stationId": station_id,
        "from": from_time,
        "to": to_time
    }

    response = requests.get(DATA_API, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Lỗi khi lấy dữ liệu trạm {station_id}")
        return None


# ============ CHUYỂN JSON → ROW CSV ============
def collect_rows(data, station_name):
    rows = []

    if not data or "_embedded" not in data or "data_hour" not in data["_embedded"]:
        return rows

    records = data["_embedded"]["data_hour"]

    for record in records:
        row = {
            "stationId": record.get("stationId", ""),
            "stationName": station_name,
            "getTime": record.get("getTime", "")
        }

        # Thêm toàn bộ dữ liệu cảm biến (thô)
        sensor_data = record.get("data", {})
        for key, value in sensor_data.items():
            row[key] = value

        rows.append(row)

    return rows


# ================== MAIN ==================
if __name__ == "__main__":
    os.makedirs(DATA_FOLDER, exist_ok=True)

    stations = fetch_stations()

    today = datetime.now()
    from_time = (today - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S")
    to_time   = today.strftime("%Y-%m-%dT%H:%M:%S")

    print(f"🔍 Tìm thấy {len(stations)} trạm ở Hà Nội\n")

    all_rows = []
    sensor_columns = set()

    # Lấy dữ liệu từng trạm
    for station in stations:
        station_id = station.get("stationId")
        station_name = station.get("stationName")

        if station_id:
            print(f"📡 Đang lấy dữ liệu: {station_name}")
            data = fetch_station_data(station_id, from_time, to_time)

            rows = collect_rows(data, station_name)
            all_rows.extend(rows)

            for r in rows:
                for k in r.keys():
                    if k not in ["stationId", "stationName", "getTime"]:
                        sensor_columns.add(k)

    # ============ GHI CSV DUY NHẤT ============
    filename = os.path.join(DATA_FOLDER, "raw_air_quality_data.csv")

    fieldnames = ["stationId", "stationName", "getTime"] + sorted(sensor_columns)

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in all_rows:
            writer.writerow(row)

    print(f"\n✅ Hoàn tất! Dữ liệu đã lưu vào {filename}")
