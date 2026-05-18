import asyncio
import json
import re
import os
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def generate_perfect_json():
    prefectures = [
        "hokkaido", "aomori", "iwate", "miyagi", "akita", "yamagata", "fukushima",
        "ibaraki", "tochigi", "gunma", "saitama", "chiba", "tokyo", "kanagawa",
        "niigata", "toyama", "ishikawa", "fukui", "yamanashi", "nagano", "gifu", "shizuoka", "aichi",
        "mie", "shiga", "kyoto", "osaka", "hyogo", "nara", "wakayama",
        "tottori", "shimane", "okayama", "hiroshima", "yamaguchi",
        "tokushima", "kagawa", "ehime", "kochi",
        "fukuoka", "saga", "nagasaki", "kumamoto", "oita", "miyazaki", "kagoshima", "okinawa"
    ]
    
    # 🔥 レポジトリの既存ファイルと同じ「gym_data.json」という名前で出力します
    output_json = "gym_data.json"
    
    # 途中で止まった時のために、すでに保存済みのデータがあれば最初に読み込む（なければ空リスト）
    if os.path.exists(output_json):
        try:
            with open(output_json, "r", encoding="utf-8") as f:
                all_shops_data = json.load(f)
            print(f"📂 既存の {output_json} を読み込みました。現在 {len(all_shops_data)} 店舗保存されています。")
        except:
            all_shops_data = []
    else:
        all_shops_data = []
        
    saved_shop_ids = {shop["id"] for shop in all_shops_data if "id" in shop}
    
    print("🚀 【GitHub地図完全同期モード】スクレイピングを開始します...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ja-JP"
        )
        page = await context.new_page()
        
        try:
            for index, pref in enumerate(prefectures, 1):
                pref_url = f"https://www.anytimefitness.co.jp/shop_category/{pref}/"
                print(f"🗺️  [{index}/47] {pref.upper()} を探索中...")
                
                await page.goto(pref_url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                
                button_selector = "text=店舗ページ"
                total_buttons = await page.locator(button_selector).count()
                
                for b_idx in range(total_buttons):
                    try:
                        target_button = page.locator(button_selector).nth(b_idx)
                        await target_button.scroll_into_view_if_needed()
                        await page.wait_for_timeout(400)
                        
                        # 🔥 1. 店舗ページに移動
                        await target_button.click(force=True)
                        
                        opened_successfully = False
                        for _ in range(25):
                            await page.wait_for_timeout(200)
                            current_url = page.url
                            if pref_url != current_url and "shop_category" not in current_url:
                                opened_successfully = True
                                break
                        
                        # 🔥 2. 移動成功したら詳細を解析
                        if opened_successfully:
                            shop_url = page.url
                            parts = [p for p in shop_url.split('/') if p]
                            
                            if len(parts) >= 3:
                                shop_id = parts[2].strip()
                                
                                exclude_words = ["shop", "recruit", "search", "contact", "shop_category", "prefectures", "blogs"]
                                if shop_id not in exclude_words and shop_id not in prefectures and re.match(r'^[a-zA-Z0-9_-]+$', shop_id):
                                    
                                    # すでに保存済みならスキップ
                                    if shop_id in saved_shop_ids:
                                        await page.goto(pref_url, wait_until="networkidle")
                                        await page.wait_for_timeout(500)
                                        continue
                                        
                                    soup = BeautifulSoup(await page.content(), 'html.parser')
                                    full_text_clean = " ".join(soup.get_text(separator=" ").split())
                                    
                                    # 店舗名取得
                                    shop_name = "エニタイムフィットネス"
                                    h1_text = soup.find('h1')
                                    if h1_text:
                                        shop_name = h1_text.get_text().strip()
                                    
                                    # 住所の抽出
                                    address_text = "住所が見つかりませんでした"
                                    addr_match = re.search(r'〒\d{3}-\d{4}.*?(?=(?:アクセス|東京メトロ|電話番号|店舗情報|スタッフ紹介))', full_text_clean)
                                    if addr_match:
                                        address_text = addr_match.group(0).replace("地図", "").strip()
                                    
                                    # 料金の抽出
                                    price_text = "料金情報が見つかりませんでした"
                                    price_match = re.search(r'¥[\d,]+\s*[（\(].*?[）\)]', full_text_clean)
                                    if price_match:
                                        price_text = price_match.group(0).strip()
                                    else:
                                        price_backup = re.search(r'¥[\d,]+.*?(?=初期費用)', full_text_clean)
                                        if price_backup:
                                            price_text = price_backup.group(0).strip()
                                    
                                    # 💡 地図サイト（葛西店テスト時）と完全に一致するJSON構造
                                    shop_item = {
                                        "id": shop_id,
                                        "name": shop_name,
                                        "address": address_text,
                                        "price": price_text,
                                        "url": shop_url
                                    }
                                    
                                    all_shops_data.append(shop_item)
                                    saved_shop_ids.add(shop_id)
                                    
                                    # その場で gym_data.json をリアルタイム更新
                                    with open(output_json, "w", encoding="utf-8") as json_file:
                                        json.dump(all_shops_data, json_file, ensure_ascii=False, indent=4)
                                        
                                    print(f"    ➡️  【保存成功】 [{pref.upper()}] {shop_name}")
                            
                            # 🔥 3. 開き直して手前に戻る
                            await page.goto(pref_url, wait_until="networkidle", timeout=20000)
                            await page.wait_for_timeout(1000)
                            
                    except Exception as btn_error:
                        try:
                            await page.goto(pref_url, wait_until="networkidle")
                            await page.wait_for_timeout(1000)
                        except:
                            pass
                        continue
                        
                print(f"  🏁 {pref.upper()} 完了。（累計: {len(all_shops_data)} 店舗保存中）")
                print("-" * 60)
                
        except Exception as e:
            print(f"❌ エラー発生: {e}")
        finally:
            await browser.close()
            
    print(f"\n🎉 完了しました！新しくできた『{output_json}』と『make_json_final.py』をGitHubにアップロードしてください！")

if __name__ == "__main__":
    asyncio.run(generate_perfect_json())
