import os
import json
import re
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BARK_URL = os.environ.get("BARK_URL")
DATA_FILE = "prices.json"
NETLIFY_URL = "https://snazzy-beijinho-64ae53.netlify.app/"

# ==========================================
# 🎯 核心监控清单（6大商铺与精选商品）
# ==========================================
TARGETS = [
    {
        "id": "preset_cetaphil_baby_1",
        "name": "Cetaphil Baby Gentle Wash & Shampoo 400ml (婴儿无泪二合一洗发沐浴露)",
        "url": "https://shopee.com.my/CETAPHIL-BABY-GENTLE-WASH-SHAMPOO-400ML-i.368170152.15806038963",
        "default_price": 47.90
    },
    {
        "id": "preset_cetaphil_baby_2",
        "name": "Cetaphil Baby Gentle Wash & Shampoo (230ml / 400ml / 400ml × 2 双瓶囤货装)",
        "url": "https://shopee.com.my/CETAPHIL-Baby-Gentle-Wash-Shampoo-(230ml-400ml-400ml-%C3%97-2)-i.23935614.361910647",
        "default_price": 88.90
    },
    {
        "id": "preset_cetaphil_baby_3",
        "name": "Cetaphil Baby Shampoo With Natural Chamomile 200ml (洋甘菊温和婴儿洗发水)",
        "url": "https://shopee.com.my/Cetaphil-Baby-Shampoo-200ml-%E2%80%93-Gentle-Cleansing-Soothes-Scalp-Maintains-Skin-Barrier-i.112778093.1743149418",
        "default_price": 31.04
    },
    {
        "id": "tiktok_shop_1",
        "name": "TikTok 精选商铺 #1 (ZSpXtJCoC)",
        "url": "https://vt.tiktok.com/ZSpXtJCoC/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180",
        "default_price": 89.00
    },
    {
        "id": "tiktok_shop_2",
        "name": "TikTok 精选商铺 #2 (ZSpXtN84Q)",
        "url": "https://vt.tiktok.com/ZSpXtN84Q/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180",
        "default_price": 99.00
    },
    {
        "id": "tiktok_watsons",
        "name": "Watsons Malaysia (@watsonsmy)",
        "url": "https://www.tiktok.com/@watsonsmy?_r=1&_t=ZS-9BOFIksEr8I",
        "default_price": 32.90
    },
    {
        "id": "shopee_cerave",
        "name": "CeraVe Official Store (MY)",
        "url": "https://my.shp.ee/q4a3R5si",
        "default_price": 73.60
    },
    {
        "id": "shopee_watsons",
        "name": "Watsons Malaysia Official Store",
        "url": "https://my.shp.ee/vpZKAcGS",
        "default_price": 49.90
    }
]

def send_bark_notification(title, body, url=""):
    if not BARK_URL:
        print("错误: 未配置 BARK_URL 环境变量")
        return
    
    safe_title = urllib.parse.quote(title)
    safe_body = urllib.parse.quote(body)
    base_url = BARK_URL.rstrip('/')
    target_url = f"{base_url}/{safe_title}/{safe_body}"
    
    if url:
        target_url += f"?url={urllib.parse.quote(url)}"
        
    try:
        response = requests.get(target_url, timeout=10)
        if response.status_code == 200:
            print(f"成功推送通知: {title}")
        else:
            print(f"推送失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")

def load_history():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_real_price(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        if not resp.url.startswith("http"):
            return None
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        price_meta = soup.find("meta", property="og:price:amount") or soup.find("meta", property="product:price:amount")
        if price_meta and price_meta.get("content"):
            return float(price_meta["content"])
            
        text_to_search = soup.title.string if soup.title else ""
        desc_meta = soup.find("meta", attrs={"name": "description"})
        if desc_meta and desc_meta.get("content"):
            text_to_search += " " + desc_meta["content"]
            
        match = re.search(r'RM\s*(\d+(?:\.\d{1,2})?)', text_to_search, re.IGNORECASE)
        if match:
            return float(match.group(1))
            
    except Exception as e:
        print(f"抓取页面 {url} 异常: {e}")
        
    return None

def check_all_prices():
    history = load_history()
    updated_history = {}
    
    for item in TARGETS:
        item_id = item["id"]
        name = item["name"]
        url = item["url"]
        default_price = item["default_price"]
        
        fetched_price = fetch_real_price(url)
        
        last_record = history.get(item_id) or history.get(name) or {}
        current_price = fetched_price if fetched_price is not None else last_record.get("price", default_price)
        old_price = last_record.get("price", current_price)
        
        drop_amount = 0.0
        drop_percent = 0.0
        
        # 仅当价格真正下跌时才触发 Bark 通知
        if current_price < old_price:
            drop_amount = old_price - current_price
            drop_percent = (drop_amount / old_price) * 100
            
            title = f"🔥 【降价提醒】{name[:20]}..."
            body = f"现价: RM{current_price:.2f} (原价: RM{old_price:.2f})\n🎉 直降 {drop_percent:.1f}% (省 RM{drop_amount:.2f})"
            print(body)
            send_bark_notification(title, body, url=NETLIFY_URL)
        else:
            status_text = "（真实抓价成功）" if fetched_price is not None else "（受平台限制，沿用基准价）"
            print(f"[{name[:25]}] 当前 RM{current_price:.2f}，价格平稳 {status_text}")
            
        updated_history[item_id] = {
            "name": name,
            "price": current_price,
            "old_price": old_price,
            "drop_amount": round(drop_amount, 2),
            "drop_percent": round(drop_percent, 1),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "product_url": url
        }
        
    save_history(updated_history)

if __name__ == "__main__":
    check_all_prices()
