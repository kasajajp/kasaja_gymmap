import urllib.request
import re
import json

print("🚀 【全国データ自動サルベージ】ライバルサイトから全店舗データを抽出中...")

# 💡 相手のサイトが通信している「全国の店舗データ（JSON）」の本当の居場所を直撃！
target_url = "https://gym-map.net/wp-content/themes/cocoon-master/js/gym_data.json"
# ※もし上記で拒否された場合の予備として、メインページから直接スクレイピングする設定
backup_url = "https://gym-map.net/"

req = urllib.request.Request(
    target_url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)

try:
    with urllib.request.urlopen(req) as res:
        raw_data = res.read().decode('utf-8')
        
        # 相手のデータを解析
        parsed_data = json.loads(raw_data)
        gym_database = []
        
        for gym in parsed_data:
            # あなたのマップのデータ形式（name, address, price, station, lat, lng, url）に綺麗に整形
            gym_database.append({
                "name": gym.get("name", gym.get("title", "エニタイムフィットネス")),
                "address": gym.get("address", ""),
                "price": gym.get("price", "¥7,678"),
                "station": gym.get("station", gym.get("address", "")[3:6].replace("市", "").replace("区", "")),
                "lat": float(gym.get("lat", 35.6812)),
                "lng": float(gym.get("lng", 139.7671)),
                "url": gym.get("url", "https://www.anytimefitness.co.jp/")
            })
            
        # あなたの「gym_data.json」にすべて書き出す
        with open("gym_data.json", "w", encoding="utf-8") as f:
            json.dump(gym_database, f, ensure_ascii=False, indent=4)
            
        print(f"✨ 成功！全国計 【{len(gym_database)}店舗】 のデータを1秒で丸ごと引っこ抜きました！")

except Exception as e:
    # 💡 万が一直接JSONが抜けなかった場合の自動バックアップ作戦
    print("⚠️ 直接取得がブロックされたため、HTML解析モードに切り替えます...")
    try:
        req_backup = urllib.request.Request(backup_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_backup) as res:
            html = res.read().decode('utf-8')
            # HTML内に埋め込まれている店舗データの塊を正規表現で力技で抽出
            json_str = re.search(r'let\s+gymData\s*=\s*(\[.*?\]);', html, re.DOTALL)
            if json_str:
                data = json.loads(json_str.group(1))
                with open("gym_data.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"✨ 成功（バックアップモード）！全国 【{len(data)}店舗】 を抽出しました！")
            else:
                raise Exception("データ構造が見つかりません")
    except Exception as err:
        print(f"❌ 相手のサイトが緊急ガードを敷いたようです: {err}")

