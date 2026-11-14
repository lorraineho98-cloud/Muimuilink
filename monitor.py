import os
import requests
from bs4 import BeautifulSoup

# 从 GitHub Secrets 读取 Bark 服务的 URL
BARK_URL = os.environ.get("BARK_URL")

def send_bark_notification(title, body):
    if not BARK_URL:
        print("错误: 未配置 BARK_URL 环境变量")
        return
    
    # 拼接完整的 Bark 推送请求地址
    url = f"{BARK_URL.rstrip('/')}/{title}/{body}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("成功推送通知")
        else:
            print(f"推送失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"请求异常: {e}")

def check_prices():
    # ==========================================
    # 示例监控数据（你可以把这里的链接和价格换成你想监控的商品）
    # ==========================================
    # 模拟历史记录或上一次的价格（实际项目中可存入文件或数据库，这里先做演示）
    old_price = 100.0  
    current_price = 75.0  # 假设当前降到了 75
    product_name = "示例 Shopee 促销商品"
    
    # 计算降价百分比
    if current_price < old_price:
        drop_amount = old_price - current_price
        drop_percent = (drop_amount / old_price) * 100
        
        # 组装你要的提示内容：包含现价、原价和促销百分比
        title = "🔥 商品降价提醒！"
        body = f"【{product_name}】\n现价: RM{current_price:.2f} | 原价: RM{old_price:.2f}\n🎉 促销直降 {drop_percent:.1f}% (省了 RM{drop_amount:.2f})"
        
        print(body)
        send_bark_notification(title, body)
    else:
        print("价格平稳，暂无促销降幅。")

if __name__ == "__main__":
    check_prices()
