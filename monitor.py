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
# 👇 你只需要在这里维护你想监控的单品列表 👇
# 格式：{"name": "你自己取的商品备注名", "url": "具体单品链接"}
# ==========================================
TARGETS = [
    {
        "name": "TikTok 重点商品 1",
        "url": "https://vt.tiktok.com/ZSpXtJCoC/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180"
    },
    {
        "name": "TikTok 重点商品 2",
        "url": "https://vt.tiktok.com/ZSpXtN84Q/?page=TikTokShop&utm_campaign=client_share&utm_source=whatsapp&share_app_id=1180"
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
    # 如果以后要加新商品，按上面的格式复制一行粘贴在这里即可（注意上一行末尾要有逗号）
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
    """
    尝试访问页面并提取价格元数据（OpenGraph / Meta 标签）
    注：Shopee 和 TikTok 分享短链在跳转后，部分基础信息会包含在页面源码的 meta 标签中
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # 1. 尝试从标准的电商 og:price:amount 标签读取价格
        price_meta = soup.find("meta", property="og:price:amount") or soup.find("meta", property="product:price:amount")
        if price_meta and price_meta.get("content"):
            return float(price_meta["content"])
            
        # 2. 尝试从页面标题或描述中匹配 RM 价格（例如 RM49.90）
        text_to_search = soup.title.string if soup.title else ""
        desc_meta = soup.find("meta", attrs={"name": "description"})
        if desc_meta and desc_meta.get("content"):
            text_to_search += " " + desc_meta["content"]
            
        match = re.search(r'RM\s*(\d+(?:\.\d{1,2})?)', text_to_search, re.IGNORECASE)
        if match:
            return float(match.group(1))
            
    except Exception as e:
        print(f"抓取页面 {url} 时遇到网络或拦截限制: {e}")
        
    return None

def check_all_prices():
    history = load_history()
    updated_history = {}
    
    for item in TARGETS:
        name = item["name"]
        url = item["url"]
        
        # 尝试抓取真实价格
        fetched_price = fetch_real_price(url)
        
        # 如果因为平台反爬暂时没抓到，保留上次记录的价格（首次运行默认给 50.0 占位）
        last_record = history.get(name, {})
        current_price = fetched_price if fetched_price is not None else last_record.get("price", 50.0)
        old_price = last_record.get("price", current_price)
        
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
            status_text = "（真实抓价成功）" if fetched_price is not None else "（受平台防爬限制，暂沿用历史价）"
            print(f"[{name}] 当前 RM{current_price:.2f}，价格平稳 {status_text}")
            
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
