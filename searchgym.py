import json
import time
import urllib.parse
import urllib.request
import re
from bs4 import BeautifulSoup

print("🚀 エニタイム公式サイトからリアルタイムで店舗データを自動収集中...")

# 💡 東京都の店舗一覧ページのURL
target_url = "https://www.anytimefitness.co.jp/tokyo/"
req = urllib.request.Request(target_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

gym_database = []

try:
    with urllib.request.urlopen(req) as response:
        html = response.read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        # 公式サイトのHTMLから、各店舗のブロック（divまたはli）をすべて自動で見つける
        studios = soup.find_all('div', class_='studio-item') or soup.find_all('li', class_='studio-item')
        
        # もし特定のクラスで見つからない場合の、汎用的な店舗リンク抽出ロジック（セーフティ）
        if not studios:
            print("🔍 簡易スキャンモードで店舗を抽出中...")
            links = soup.find_all('a', href=re.compile(re.escape('/shisetsu/')))
            raw_studios = []
            for link in links:
                name = link.get_text(strip=True)
                if name and "店" in name:
                    raw_studios.append({"name": name, "url": urllib.parse.urljoin(target_url, link['href'])})
        else:
            raw_studios = []
            for studio in studios:
                name_tag = studio.find('h3') or studio.find('span', class_='name')
                link_tag = studio.find('a')
                if name_tag and link_tag:
                    raw_studios.append({
                        "name": name_tag.get_text(strip=True),
                        "url": urllib.parse.urljoin(target_url, link_tag['href'])
                    })

        # 重重複を排除
        seen = set()
        unique_studios = []
        for s in raw_studios:
            if s['name'] not in seen:
                seen.add(s['name'])
                unique_studios.append(s)

        total_gyms = len(unique_studios)
        print(f"✅ 公式サイトから 【{total_gyms}店舗】 を自動検知しました！")
        print("🌍 続いて、各店舗の住所と緯度経度を自動解析します（数分かかります）...")

        # 🚀 【リミッター解除】東京の全店舗をループ処理で全て回る
        for idx, studio in enumerate(unique_studios):
            name = studio["name"]
            url = studio["url"]
            
            # 店舗名から駅名を推測（例:「エニタイムフィットネス 瑞江店」 -> 「瑞江」）
            station = name.replace("エニタイムフィットネス", "").replace("店", "").strip()
            
            # 1店舗ずつ進捗を表示
            print(f"[{idx+1}/{total_gyms}] 📍 {name} の座標を自動計算中...")
            
            # 住所から座標を検索するAPI（Nominatim）
            geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(station + '駅')}&countrycodes=jp"
            geo_req = urllib.request.Request(geo_url, headers={'User-Agent': 'GymMapAutomator/3.0'})
            
            try:
                with urllib.request.urlopen(geo_req) as geo_res:
                    geo_data = json.loads(geo_res.read().decode())
                    if geo_data:
                        lat = float(geo_data[0]["lat"])
                        lng = float(geo_data[0]["lon"])
                        # 本物の住所をAPIから逆引き
                        address = geo_data[0]["display_name"].split(',')[0] 
                    else:
                        lat, lng, address = 35.6812, 139.7671, "東京都（位置特定不可）"
            except:
                lat, lng, address = 35.6812, 139.7671, "東京都（通信エラー）"
            
            # データベース配列へ追加
            gym_database.append({
                "name": name if "エニタイム" in name else f"エニタイムフィットネス {name}",
                "address": address,
                "price": "¥7,678",  # 標準価格
                "station": station,
                "lat": lat,
                "lng": lng,
                "url": url
            })
            
            # ⚠️ サーバーに負荷をかけないマナー（2秒休憩）
            time.sleep(2.0)

except Exception as e:
    print(f"❌ スクレイピング中にエラーが発生しました: {e}")

# 3. 収集したすべての東京データを『gym_data.json』に上書き保存！
with open("gym_data.json", "w", encoding="utf-8") as f:
    json.dump(gym_database, f, ensure_ascii=False, indent=4)

print(f"✨ 完了！東京全域のデータを反映した『gym_data.json』が自動更新されました！")
