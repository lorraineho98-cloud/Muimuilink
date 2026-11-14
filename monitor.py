import os
import json
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup

BARK_URL = os.environ.get("BARK_URL")
DATA_FILE = "prices.json"
NETLIFY_URL = "https://snazzy-beijinho-64ae53.netlify.app/"

# 你提供的 6 个监控目标
TARGETS = [
    {
        "name": "TikTok 商品 1",
        "url": "https://vt.tiktok.com/ZSpXtJCoC/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180",
        "platform": "tiktok"
    },
    {
        "name": "TikTok 商品 2",
        "url": "https://vt.tiktok.com/ZSpXtN84Q/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180",
        "platform": "tiktok"
    },
    {
        "name": "Watsons TikTok 店铺",
        "url": "https://www.tiktok.com/@watsonsmy?_r=1&_t=ZS-9BOFIksEr8I",
        "platform": "tiktok_shop"
    },
    {
        "name": "Shopee 商品 1",
        "url": "https://my.shp.ee/ngy4Hpb4",
        "platform": "shopee"
    },
    {
        "name": "Shopee 商品 2",
        "url": "https://my.shp.ee/q4a3R5si",
        "platform": "shopee"
    },
    {
        "name": "Shopee 商品 3",
        "url": "https://my.shp.ee/vpZKAcGS",
        "platform": "shopee"
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
            print("成功推送通知")
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

def fetch_price(target):
    # 此处为演示框架：由于 Shopee/TikTok 存在反爬或动态渲染，
    # 我们先以默认模拟价格运行，确保多商品循环与网页看板全部打通。
    # 后续我们可以针对具体商品页面的 HTML 标签进行精准抓取。
    return 50.0 

def check_all_prices():
    history = load_history()
    updated_history = {}
    
    for item in TARGETS:
        name = item["name"]
        url = item["url"]
        
        # 获取当前价格（演示中赋予基础对比价）
        current_price = fetch_price(item)
        
        # 获取历史价格（如果没有则设为 60.0 以便触发降价演示）
        old_price = history.get(name, {}).get("price", 60.0)
        
        drop_amount = 0.0
        drop_percent = 0.0
        
        if current_price < old_price:
            drop_amount = old_price - current_price
            drop_percent = (drop_amount / old_price) * 100
            
            title = f"🔥 【{name}】降价提醒！"
            body = f"现价: RM{current_price:.2f} (原价: RM{old_price:.2f})\n🎉 直降 {drop_percent:.1f}% (省 RM{drop_amount:.2f})"
            print(body)
            send_bark_notification(title, body, url=NETLIFY_URL)
        else:
            print(f"[{name}] 价格平稳，暂不推送。")
            
        updated_history[name] = {
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
