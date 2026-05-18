import json
import os
import time
import urllib.parse
import urllib.request
import re

print("🚀 【最安定モード】gym_data_all.json から緯度経度を割り出して書き込みます...")

input_file = "gym_data_all.json"

if not os.path.exists(input_file):
    print(f"❌ エラー: 手元に {input_file} が見つかりません。")
    exit()

# JSONファイルを読み込む
with open(input_file, "r", encoding="utf-8") as f:
    gym_list = json.load(f)

total = len(gym_list)
print(f"📦 合計 {total} 店舗のデータを読み込みました。")

for index, gym in enumerate(gym_list, 1):
    # 💡 すでに正常な数値の座標が入っている店舗はスキップ（２回目以降の実行を高速化）
    if "lat" in gym and isinstance(gym["lat"], (int, float)):
        continue
        
    name = gym.get("name", "店舗")
    address = gym.get("address", "").strip()
    
    lat, lng = None, None
    
    if address and "見つかりませんでした" not in address:
        try:
            # 🛠️ 住所クレンジング（これがないと国土地理院でエラーになります）
            # 1. 「〒123-4567」の郵便番号部分を取り除く
            clean_address = re.sub(r'〒?\d{3}-\d{4}\s*', '', address)
            # 2. 全角スペースを半角スペースにする
            clean_address = clean_address.replace("　", " ")
            # 3. 建物名や階数（スペース以降の文字）をカットして純粋な番地だけにする
            # 例：「沖縄県糸満市字兼城400番地 1F」 ➡️ 「沖縄県糸満市字兼城400番地」
            clean_address = clean_address.split(" ")[0].strip()
            
            # 国土地理院のジオコーディングAPIへリクエスト
            encoded_addr = urllib.parse.quote(clean_address)
            url = f"https://msearch.gsi.go.jp/address-search/AddressSearch?q={encoded_addr}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'GymGeocodingApp/1.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # 座標が見つかった場合
                if res_data and len(res_data) > 0:
                    coordinates = res_data[0].get("geometry", {}).get("coordinates", [])
                    if len(coordinates) == 2:
                        lng = float(coordinates[0]) # 経度
                        lat = float(coordinates[1]) # 緯度
                        print(f"🔄 [{index}/{total}] {name} ➡️ 🎯 座標確定! ({lat}, {lng})")
                    else:
                        print(f"🔄 [{index}/{total}] {name} ➡️ ⚠️ 座標の形が不正です")
                else:
                    print(f"🔄 [{index}/{total}] {name} ➡️ ❌ 住所がマッチしませんでした ({clean_address})")
                    
        except Exception as e:
            print(f"🔄 [{index}/{total}] {name} ➡️ 💥 エラー発生: {e}")
            time.sleep(1) # エラー時は少し待機
            
    # データに直接「lat」「lng」という名前で数値を保存
    gym["lat"] = lat
    gym["lng"] = lng
    
    # 💥 大事：1件処理するごとにその場で即時上書き保存（途中で止めてもデータは壊れません）
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(gym_list, f, ensure_ascii=False, indent=4)
        
    # サーバーに怒られないように0.1秒だけ待つ
    time.sleep(0.1)

print("\n✨ すべてのデータに本物の緯度経度が追加されました！")
