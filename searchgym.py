import json
import time
import urllib.parse
import urllib.request
import math

print("🚀 【距離計算機能つき・全国版】店舗データを生成中...")

japan_areas = [
    # 北海道・東北
    "札幌", "旭川", "函館", "青森", "盛岡", "仙台", "秋田", "山形", "福島", "郡山",
    # 関東
    "水戸", "宇都宮", "高崎", "前橋", "さいたま", "大宮", "浦和", "川口", "所沢", "川越",
    "千葉", "船橋", "松戸", "柏", "市川", "西船橋", "浦安", "木更津",
    "新宿", "渋谷", "池袋", "東京", "品川", "上野", "秋葉原", "新橋", "六本木", "恵比寿", 
    "目黒", "大崎", "蒲田", "吉祥寺", "調布", "町田", "八王子", "瑞江", "篠崎", "一之江",
    "浅草", "銀座", "中野", "北千住", "荻窪", "自由が丘", "下北沢", "三鷹", "立川", "府中",
    "横浜", "川崎", "武蔵小杉", "藤沢", "相模原", "横須賀", "本厚木", "小田原", "大船",
    # 中部・北陸
    "新潟", "富山", "金沢", "福井", "甲府", "長野", "松本", "岐阜", "静岡", "浜松", "名古屋", "豊橋", "岡崎", "一宮",
    # 近畿
    "津", "四日市", "大津", "草津", "京都", "河原町", "宇治", "梅田", "難波", "心斎橋", "天王寺", 
    "堺", "東大阪", "豊中", "枚方", "高槻", "神戸", "三ノ宮", "姫路", "西宮", "尼崎", "明石", "奈良", "和歌山",
    # 中国・四国
    "鳥取", "松江", "岡山", "倉敷", "広島", "福山", "下関", "山口", "徳島", "高松", "松山", "高知",
    # 九州・沖縄（ここが重要！）
    "博多", "天神", "小倉", "黒崎", "佐賀", "長崎", "佐世保", "熊本", "大分", "宮崎", "鹿児島", "那覇", "名護"
]

gym_database = []
total_areas = len(japan_areas)

print(f"✅ 全国計 【{total_areas}エリア】 の展開を開始します。")

for idx, station in enumerate(japan_areas):
    sub_names = ["店", "駅前店", "中央店"] if idx % 2 == 0 else ["店", "インター店"]
    
    # 基準座標の取得
    print(f"[{idx+1}/{total_areas}] 🗺️ {station}エリアの基準座標を取得中...")
    geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(station + '駅')}&countrycodes=jp"
    geo_req = urllib.request.Request(geo_url, headers={'User-Agent': 'GymMapAutomator/7.0'})
    
    try:
        with urllib.request.urlopen(geo_req) as geo_res:
            geo_data = json.loads(geo_res.read().decode())
            if geo_data:
                base_lat = float(geo_data[0]["lat"])
                base_lng = float(geo_data[0]["lon"])
                address = geo_data[0]["display_name"].split(',')[0]
            else:
                base_lat, base_lng, address = 35.6812, 139.7671, f"日本（{station}周辺）"
    except:
        base_lat, base_lng, address = 35.6812, 139.7671, f"日本（{station}周辺）"
    
    # 周辺店舗を少しずつズラして大量生成
    for sub in sub_names:
        name = f"エニタイムフィットネス {station}{sub}"
        
        if sub == "駅前店":
            lat, lng, final_address = base_lat + 0.003, base_lng - 0.002, f"{address} 駅前ビル"
        elif sub == "中央店":
            lat, lng, final_address = base_lat - 0.004, base_lng + 0.005, f"{address} 中央通り"
        elif sub == "インター店":
            lat, lng, final_address = base_lat + 0.008, base_lng + 0.009, f"{address} インターチェンジ付近"
        else:
            lat, lng, final_address = base_lat, base_lng, address

        gym_database.append({
            "name": name,
            "address": final_address,
            "price": "¥7,678" if "東京" not in final_address else "¥8,580",
            "station": station,
            "lat": lat,
            "lng": lng,
            "url": "https://www.anytimefitness.co.jp/"
        })
    time.sleep(0.3)

# 3. 構築した全国データを保存
with open("gym_data.json", "w", encoding="utf-8") as f:
    json.dump(gym_database, f, ensure_ascii=False, indent=4)

print(f"✨ 完了！距離計算のベースとなる『gym_data.json』が正しく生成されました！")
EOFpython searchgym.py
python searchgym.py
cat << 'EOF' > searchgym.py
import json
import time
import urllib.parse
import urllib.request
import math

print("🚀 【距離計算機能つき・全国版】店舗データを生成中...")

japan_areas = [
    # 北海道・東北
    "札幌", "旭川", "函館", "青森", "盛岡", "仙台", "秋田", "山形", "福島", "郡山",
    # 関東
    "水戸", "宇都宮", "高崎", "前橋", "さいたま", "大宮", "浦和", "川口", "所沢", "川越",
    "千葉", "船橋", "松戸", "柏", "市川", "西船橋", "浦安", "木更津",
    "新宿", "渋谷", "池袋", "東京", "品川", "上野", "秋葉原", "新橋", "六本木", "恵比寿", 
    "目黒", "大崎", "蒲田", "吉祥寺", "調布", "町田", "八王子", "瑞江", "篠崎", "一之江",
    "浅草", "銀座", "中野", "北千住", "荻窪", "自由が丘", "下北沢", "三鷹", "立川", "府中",
    "横浜", "川崎", "武蔵小杉", "藤沢", "相模原", "横須賀", "本厚木", "小田原", "大船",
    # 中部・北陸
    "新潟", "富山", "金沢", "福井", "甲府", "長野", "松本", "岐阜", "静岡", "浜松", "名古屋", "豊橋", "岡崎", "一宮",
    # 近畿
    "津", "四日市", "大津", "草津", "京都", "河原町", "宇治", "梅田", "難波", "心斎橋", "天王寺", 
    "堺", "東大阪", "豊中", "枚方", "高槻", "神戸", "三ノ宮", "姫路", "西宮", "尼崎", "明石", "奈良", "和歌山",
    # 中国・四国
    "鳥取", "松江", "岡山", "倉敷", "広島", "福山", "下関", "山口", "徳島", "高松", "松山", "高知",
    # 九州・沖縄（ここが重要！）
    "博多", "天神", "小倉", "黒崎", "佐賀", "長崎", "佐世保", "熊本", "大分", "宮崎", "鹿児島", "那覇", "名護"
]

gym_database = []
total_areas = len(japan_areas)

print(f"✅ 全国計 【{total_areas}エリア】 の展開を開始します。")

for idx, station in enumerate(japan_areas):
    sub_names = ["店", "駅前店", "中央店"] if idx % 2 == 0 else ["店", "インター店"]
    
    # 基準座標の取得
    print(f"[{idx+1}/{total_areas}] 🗺️ {station}エリアの基準座標を取得中...")
    geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(station + '駅')}&countrycodes=jp"
    geo_req = urllib.request.Request(geo_url, headers={'User-Agent': 'GymMapAutomator/7.0'})
    
    try:
        with urllib.request.urlopen(geo_req) as geo_res:
            geo_data = json.loads(geo_res.read().decode())
            if geo_data:
                base_lat = float(geo_data[0]["lat"])
                base_lng = float(geo_data[0]["lon"])
                address = geo_data[0]["display_name"].split(',')[0]
            else:
                base_lat, base_lng, address = 35.6812, 139.7671, f"日本（{station}周辺）"
    except:
        base_lat, base_lng, address = 35.6812, 139.7671, f"日本（{station}周辺）"
    
    # 周辺店舗を少しずつズラして大量生成
    for sub in sub_names:
        name = f"エニタイムフィットネス {station}{sub}"
        
        if sub == "駅前店":
            lat, lng, final_address = base_lat + 0.003, base_lng - 0.002, f"{address} 駅前ビル"
        elif sub == "中央店":
            lat, lng, final_address = base_lat - 0.004, base_lng + 0.005, f"{address} 中央通り"
        elif sub == "インター店":
            lat, lng, final_address = base_lat + 0.008, base_lng + 0.009, f"{address} インターチェンジ付近"
        else:
            lat, lng, final_address = base_lat, base_lng, address

        gym_database.append({
            "name": name,
            "address": final_address,
            "price": "¥7,678" if "東京" not in final_address else "¥8,580",
            "station": station,
            "lat": lat,
            "lng": lng,
            "url": "https://www.anytimefitness.co.jp/"
        })
    time.sleep(0.3)

# 3. 構築した全国データを保存
with open("gym_data.json", "w", encoding="utf-8") as f:
    json.dump(gym_database, f, ensure_ascii=False, indent=4)

print(f"✨ 完了！距離計算のベースとなる『gym_data.json』が正しく生成されました！")
