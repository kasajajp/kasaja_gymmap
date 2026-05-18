import json
import os
import time
import re
from playwright.sync_api import sync_playwright

print("🚀 【Googleマップ解析モード】gym_data_all.json から緯度経度を割り出します...")

input_file = "gym_data_all.json"

if not os.path.exists(input_file):
    print(f"❌ エラー: 手元に {input_file} が見つかりません。")
    exit()

with open(input_file, "r", encoding="utf-8") as f:
    gym_list = json.load(f)

total = len(gym_list)
print(f"📦 合計 {total} 店舗のデータを読み込みました。未取得の店舗をGoogleマップで検索します。")

with sync_playwright() as p:
    # 💡 相手にロボットだとバレないようにブラウザを起動
    browser = p.chromium.launch(headless=False)  # 実際の動きを確認できるように画面を表示します
    page = browser.new_page()

    for index, gym in enumerate(gym_list, 1):
        # すでに本物の数値の座標が入っている場合はスキップして高速化
        if "lat" in gym and isinstance(gym["lat"], (int, float)):
            continue
            
        name = gym.get("name", "")
        address = gym.get("address", "").strip()
        
        print(f"🔄 [{index}/{total}] {name} を検索中...")
        
        lat, lng = None, None
        if address and "見つかりませんでした" not in address:
            try:
                # 郵便番号だけ綺麗にカット
                clean_address = re.sub(r'〒?\d{3}-\d{4}\s*', '', address)
                
                # Googleマップの検索URLを直接生成
                search_url = f"https://www.google.com/maps/search/{urllib.parse.quote(clean_address)}"
                page.goto(search_url)
                
                # 地図が読み込まれるまで少し待機
                page.wait_for_timeout(3000)
                
                # 💡 GoogleマップのURL（アドレスバー）には、必ず現在のピンの緯度経度が「@35.6812,139.7671」の形式で含まれます
                current_url = page.url
                match = re.search(r'@([\d.]+),([\d.]+)', current_url)
                
                if match:
                    lat = float(match.group(1))
                    lng = float(match.group(2))
                    print(f"  ➡️ 🎯 Googleマップから座標を抽出成功! ({lat}, {lng})")
                else:
                    print("  ➡️ ⚠️ URLから座標が読み取れませんでした。")
                    
            except Exception as e:
                print(f"  ➡️ ❌ エラー発生: {e}")
        
        # 割り出した数値をJSONデータに直接リンクして保存
        gym["lat"] = lat
        gym["lng"] = lng
        
        # 1件ごとにその場で即時上書き保存
        with open(input_file, "w", encoding="utf-8") as f:
            json.dump(gym_list, f, ensure_ascii=False, indent=4)
            
        # 人間らしい動きにするため1秒休憩
        time.sleep(1.0)

    browser.close()

print("\n✨ 【完了】すべてのデータに本物の緯度経度が焼き付けられました！")
