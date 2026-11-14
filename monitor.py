import os
import json
import requests
from bs4 import BeautifulSoup

# 从环境变量读取配置
BARK_URL = os.environ.get("BARK_URL")
DATA_FILE = "prices.json"

def send_bark_notification(title, body, url=""):
    if not BARK_URL:
        print("错误: 未配置 BARK_URL 环境变量")
        return
    
    # 拼接 Bark 推送地址（加上 url 参数实现点击通知直接跳转网页）
    base_url = BARK_URL.rstrip('/')
    target_url = f"{base_url}/{title}/{body}"
    if url:
        target_url += f"?url={url}"
        
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
        except:
            return {}
    return {}

def save_history(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def check_prices():
    # 模拟你要监控的商品数据（后续可替换为真实的 Shopee/TikTok 抓取逻辑）
    product_name = "示例 Shopee 热门商品"
    product_url = "https://your-netlify-site.netlify.app"  # 你的网页端链接
    current_price = 70.0  # 当前抓取到的价格
    
    history = load_history()
    old_price = history.get(product_name, {}).get("price", 100.0) # 默认上次是 100
    
    print(f"商品: {product_name} | 上次价格: RM{old_price} | 当前价格: RM{current_price}")
    
    # 对比价格
    if current_price < old_price:
        drop_amount = old_price - current_price
        drop_percent = (drop_amount / old_price) * 100
        
        title = "🔥 发现降价！"
        body = f"【{product_name}】\n现价: RM{current_price:.2f} (原价: RM{old_price:.2f})\n🎉 跌幅 {drop_percent:.1f}% (省了 RM{drop_amount:.2f})"
        
        print(body)
        send_bark_notification(title, body, url=product_url)
    else:
        print("价格无优惠，暂不推送。")
        
    # 更新历史记录并保存，供网页端读取展示
    history[product_name] = {
        "price": current_price,
        "old_price": old_price,
        "update_time": "2026-11-14"
    }
    save_history(history)

if __name__ == "__main__":
    check_prices()
