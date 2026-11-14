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

if __name__ == "__main__":
    print("正在发送测试推送...")
    # 强制发送一条测试通知，看手机能不能收到
    send_bark_notification(
        "🔥 价格监控系统测试", 
        "【Shopee 示例商品】\n现价: RM50.00 (原价: RM60.00)\n🎉 直降 16.7% (省 RM10.00)", 
        url=NETLIFY_URL
    )
