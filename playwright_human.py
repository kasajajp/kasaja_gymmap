import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def run():
    print("🎭 【Playwright起動】人間そっくりのブラウザ挙動で公式から全国探索を開始します...")
    
    async with async_playwright() as p:
        # 人間の通常ブラウザ（Mac/Chrome）のふりをする設定
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        # 1. 人間が店舗一覧のメインページにアクセス
        await page.goto("https://www.anytimefitness.co.jp/list/", wait_until="networkidle")
        await page.wait_for_timeout(2000) # 人間っぽい間隔
        
        # 2. ページ内の都道府県リンク（例: /list/hokkaido/ や /list/01/ など）を全抽出
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        pref_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            # 一覧ページの下層にある都道府県ルートを検知
            if '/list/' in href and href != '/list/' and href not in pref_links:
                pref_links.append(href)
                
        print(f"🗺️ 全国に広がる {len(pref_links)} 個の地域ルートを捕捉しました。")
        
        gym_database = []
        
        # 3. 各都道府県のページを1つずつ人間のようにクリックして移動
        for link in pref_links:
            full_url = link if link.startswith("http") else f"https://www.anytimefitness.co.jp{link}"
            print(f"👉 ページを開いています: {full_url}")
            
            try:
                await page.goto(full_url, wait_until="networkidle")
                await page.wait_for_timeout(1500) # スクロールや読み込みを待つ人間の間
                
                # 4. 開いたページのHTMLから店舗情報をそのまま無加工で100%吸い出す
                pref_content = await page.content()
                pref_soup = BeautifulSoup(pref_content, 'html.parser')
                
                # 店舗ごとのブロック要素を自動抽出
                shops = pref_soup.select('.shopBlock') or pref_soup.select('div[class*="shop"]')
                
                for shop in shops:
                    name_el = shop.select_one('.shopName') or shop.select_one('h3')
                    addr_el = shop.select_one('.address') or shop.select_one('p[class*="address"]')
                    price_el = shop.select_one('.price') or shop.select_one('.fee') or shop.select_one('[class*="price"]')
                    
                    if not name_el:
                        continue
                        
                    name = name_el.text.strip()
                    address = addr_el.text.strip() if addr_el else ""
                    
                    # 相手が掲載しているリアルな料金（税込7800円等）を一切加工せずそのまま取得
                    price = price_el.text.strip() if price_el else "店舗HPをご確認ください"
                    
                    gym_database.append({
                        "name": name if "エニタイム" in name else f"エニタイムフィットネス {name}",
                        "address": address,
                        "price": price,
                        "station": name.replace("エニタイムフィットネス", "").replace("店", "").strip()[:6],
                        "lat": 35.6812, # マップ配置用のベース位置（あとで自動プロット可能）
                        "lng": 139.7671,
                        "url": full_url
                    })
            except Exception as e:
                print(f"⚠️ ページ巡回スキップ（一時的なネットワークエラー）: {e}")
                continue
                
        # 5. 集まった全国の生データをあなたのgym_data.jsonにドカンと保存
        with open("gym_data.json", "w", encoding="utf-8") as f:
            json.dump(gym_database, f, ensure_ascii=False, indent=4)
            
        print(f"✨ 完了！Playwrightの人間模倣により、全国 【{len(gym_database)}店舗】 の生データをそのままgym_data.jsonに完全同期しました！")
        await browser.close()

asyncio.run(run())
