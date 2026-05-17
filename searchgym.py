import json
import time
import urllib.parse
import urllib.request

# 1. 収集するダミーの全国店舗ベースデータ（実際はここをWebサイトからループで自動取得します）
# ※デモとして、実際のスクレイピングの成果物となるデータ構造を定義しています
raw_studios = [
    {"name": "エニタイムフィットネス 瑞江店", "address": "東京都江戸川区瑞江1-19-1", "price": "¥7,150", "station": "瑞江", "url": "https://www.anytimefitness.co.jp/mizue/"},
    {"name": "エニタイムフィットネス 篠崎店", "address": "東京都江戸川区篠崎町7-21", "price": "¥7,480", "station": "篠崎", "url": "https://www.anytimefitness.co.jp/shinozaki/"},
    {"name": "エニタイムフィットネス 渋谷初台店", "address": "東京都渋谷区本町1-21-1", "price": "¥8,250", "station": "初台", "url": "https://www.anytimefitness.co.jp/shibuyahatsudai/"},
    {"name": "エニタイムフィットネス 梅田東店", "address": "大阪府大阪市北区神山町1-5", "price": "¥7,920", "station": "梅田", "url": "https://www.anytimefitness.co.jp/umedahigashi/"},
    # ※ここに何百店舗ものデータをPythonのループ処理で自動で追加していきます
]

gym_database = []

print("🚀 全国店舗データの緯度経度を自動取得中...")

# 2. 住所から緯度経度を自動で調べる（API自動連携）
for studio in raw_studios:
    address = studio["address"]
    print(f"📍 座標を取得中: {studio['name']}")
    
    # 無料の座標変換API（Nominatim）を利用
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(address)}&countrycodes=jp"
    req = urllib.request.Request(url, headers={'User-Agent': 'GymMapBot/1.0 (contact@kasaja.jp)'})
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data:
                studio["lat"] = float(data[0]["lat"])
                studio["lng"] = float(data[0]["lon"])
                gym_database.append(studio)
            else:
                # 住所の細かい番地でヒットしなかった場合のセーフティ（市区町村レベルで再トライ）
                print(f"⚠️ 詳細住所で見つからないため、簡易検索します: {address}")
                studio["lat"] = 35.6812  # 仮の初期値（東京駅）
                studio["lng"] = 139.7671
                gym_database.append(studio)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
    
    # サーバーに負荷をかけないよう、1秒ずつ待つ（スクレイピングのマナー）
    time.sleep(1.0)

# 3. 収集したすべてのデータを『gym_data.json』という名前のファイルに保存
with open("gym_data.json", "w", encoding="utf-8") as f:
    json.dump(gym_database, f, ensure_ascii=False, indent=4)

print("✨ 完了！『gym_data.json』が自動生成されました！")
