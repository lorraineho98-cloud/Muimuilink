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

TARGETS = [
    {
        "name": "TikTok 重点商品 1",
        "url": "https://vt.tiktok.com/ZSpXtJCoC/"
    },
    {
        "name": "TikTok 重点商品 2",
        "url": "https://vt.tiktok.com/ZSpXtN84Q/"
    },
    {
        "name": "Shopee 重点商品 1",
        "url": "https://my.shp.ee/ngy4Hpb4"
    },
    {
        "name": "Shopee 重点商品 2",
        "url": "https://my.shp.ee/q4a3R5si"
    },
    {
        "name": "Shopee 重点商品 3",
        "url": "https://my.shp.ee/vpZKAcGS"
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
        # 加上 allow_redirects=True 让它自动跟随网页重定向
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        # 如果最终跳转到了特殊协议，直接跳过解析
        if not resp.url.startswith("http"):
            return None
            
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 尝试提取价格
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
        name = item["name"]
        url = item["url"]
        
        fetched_price = fetch_real_price(url)
        
        last_record = history.get(name, {})
        current_price = fetched_price if fetched_price is not None else last_record.get("price", 50.0)
        old_price = last_record.get("price", 60.0) # 设一个比现价高的原价，用来测试通知
        
        # 为了测试通知，我们在这里主动制造一个“降价”效果，确保手机能立刻收到推送
        if current_price >= old_price:
            old_price = current_price + 10.0
            
        drop_amount = old_price - current_price
        drop_percent = (drop_amount / old_price) *
