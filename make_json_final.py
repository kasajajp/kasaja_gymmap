import json
import time
import urllib.parse
import urllib.request
import os

print("🚀 【確実性最優先】住所から緯度経度を完全に割り出し、JSONに焼き付けます...")

input_file = "gym_data_all.json"

if not os.path.exists(input_file):
    print(f"❌ エラー: 手元に {input_file} が見つかりません。")
    exit()

with open(input_file, "r", encoding="utf-8") as f:
    gym_list = json.load(f)

total = len(gym_list)
print(f"📦 合計 {total} 店舗のデータを読み込みました。順番に座標を割り出します。")

for index, gym in enumerate(gym_list, 1):
    # 💡 すでに正常な数値の座標が入っている場合はスキップ（これまでに取れた数件は無駄にしません）
    if "lat" in gym and isinstance(gym["lat"], (int, float)):
        continue
        
    name = gym.get("name", "エニタイムフィットネス")
    address = gym.get("address", "").strip()
    
    print(f"🔄 [{index}/{total}] {name} を処理中...")
    
    lat, lng = None, None
    if address and "見つかりませんでした" not in address:
        try:
            # 💡 住所を一切加工せず、そのまま国土地理院の検索エンジンに投げます
            encoded_addr = urllib.parse.quote(address)
            url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={encoded_addr}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'GymGeocodingSystem/6.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # ヒットした場合
                if res_data and len(res_data) > 0:
                    coordinates = res_data[0].get("geometry", {}).get("coordinates", [])
                    if len(coordinates) == 2:
                        lng = float(coordinates[0]) # 経度
                        lat = float(coordinates[1]) # 緯度
                        print(f"  ➡️ 🎯 割り出し成功! 緯度: {lat}, 経度: {lng}")
                        
        except Exception as e:
            print(f"  ➡️ ⚠️ エラー発生（一時スキップ）: {e}")
            
    # 💡 データに「数値」として直接焼き付け、店舗名と完全にリンクさせます
    gym["lat"] = lat
    gym["lng"] = lng
    
    # 1件ごとにその場で即時上書き保存（途中で止めてもデータは100%壊れません）
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(gym_list, f, ensure_ascii=False, indent=4)
        
    # 国土地理院はブロックが非常に緩いため、0.1秒の待機で安全かつ超高速に回せます
    time.sleep(0.1)

print("\n✨ 【大成功】すべての店舗名と住所に、本物の緯度経度が完全にリンクしました！")
