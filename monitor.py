import os
import json
import urllib.parse
from datetime import datetime
import requests

BARK_URL = os.environ.get("BARK_URL")
DATA_FILE = "prices.json"
NETLIFY_URL = "https://snazzy-beijinho-64ae53.netlify.app/"

def send_bark_notification(title, body, url=""):
    if not BARK_URL:
        print("错误: 未配置 BARK_URL 环境变量")
        return
    
    # 对中文和特殊字符进行 URL 编码，防止链接参数截断或发送失败
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

def check_prices():
    # 测试商品数据（后续替换为你真实的 Shopee/TikTok 抓取逻辑）
    product_name = "Shopee 热门护肤套装"
    current_price = 68.0
    
    history = load_history()
    # 如果没有历史记录，默认原价为 100.0 以便触发首次演示
    old_price = history.get(product_name, {}).get("price", 100.0)
    
    drop_amount = 0.0
    drop_percent = 0.0
    
    if current_price < old_price:
        drop_amount = old_price - current_price
        drop_percent = (drop_amount / old_price) * 100
        
        title = "🔥 发现降价促销！"
        body = f"【{product_name}】\n现价: RM{current_price:.2f} (原价: RM{old_price:.2f})\n🎉 直降 {drop_percent:.1f}% (省 RM{drop_amount:.2f})"
        
        print(body)
        send_bark_notification(title, body, url=NETLIFY_URL)
    else:
        print("价格平稳，暂不推送。")
        
    # 保存最新比价数据供网页端展示
    history[product_name] = {
        "price": current_price,
        "old_price": old_price,
        "drop_amount": round(drop_amount, 2),
        "drop_percent": round(drop_percent, 1),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_history(history)

if __name__ == "__main__":
    check_prices()
