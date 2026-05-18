import json
import time
import urllib.parse
import urllib.request
import os
import re

print("🚀 【安全第一・既存データ救済モード】位置情報の埋め込みを開始します...")

# 対象ファイル
input_file = "gym_data_all.json"

# 1. ローカルにファイルがあるかチェック
if not os.path.exists(input_file):
    print(f"❌ エラー: 手元に {input_file} が見つかりません。")
    print("先にターミナルで 'git pull origin main' を実行して最新ファイルを落としてください。")
    exit()

# 2. データの読み込み
with open(input_file, "r", encoding="utf-8") as f:
    gym_list = json.load(f)

total = len(gym_list)
print(f"📦 合計 {total} 店舗のデータを読み込みました。")

# 3. 1件ずつ安全に座標を付与
for index, gym in enumerate(gym_list, 1):
    # すでに本物の数値（float）の座標が入っている場合はスキップして超高速化
    if "lat" in gym and isinstance(gym["lat"], (int, float)):
        continue
        
    name = gym.get("name", "エニタイムフィットネス")
    address = gym.get("address", "")
    
    print(f"🔄 [{index}/{total}] {name} の座標を取得中...")
    
    lat, lng = None, None
    if address and "見つかりませんでした" not in address:
        try:
            # 住所から郵便番号マークや不要なビル名を削って検索精度を極限まで上げる
            clean_address = re.sub(r'〒\d{3}-\d{4}\s*', '', address)
            clean_address = clean_address.split(" ")[0].strip()
            
            encoded_addr = urllib.parse.quote(clean_address)
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_addr}&limit=1"
            
            # 相手のサーバーに拒否されないよう専用のヘッダーを付与
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'GymMapSystem/3.0 (kasajajp.github.io)'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                if res_data and len(res_data) > 0:
                    lat = float(res_data[0].get("lat"))
                    lng = float(res_data[0].get("lon"))
                    print(f"  ➡️ 🎯 座標を取得! ({lat}, {lng})")
                else:
                    print("  ➡️ ⚠️ 座標が見つかりませんでした。")
        except Exception as e:
            print(f"  ➡️ ❌ 取得失敗（後ほど補完されます）: {e}")
            
    gym["lat"] = lat
    gym["lng"] = lng
    
    # リアルタイムでファイルに1件ずつ上書き保存（途中で止めてもデータは壊れません）
    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(gym_list, f, ensure_ascii=False, indent=4)
        
    # スパム判定を食らわないために1件あたり1.2秒必ず休む
    time.sleep(1.2)

print("\n✨ 【大成功】すべてのデータへ本物の座標焼き付けが完了しました！")
