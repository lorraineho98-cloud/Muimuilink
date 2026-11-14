import os
import requests

# 从 GitHub Secrets 读取你的 Bark 推送链接
BARK_URL = os.environ.get("BARK_URL")

# 监控商品清单
products = [
    {
        "name": "CeraVe Hydrating Cleanser 236ml",
        "url": "https://shopee.com.my/ceravemy.os",
        "targetPrice": 48.00,
    },
    {
        "name": "CeraVe Foaming Cleanser 236ml",
        "url": "https://shopee.com.my/ceravemy.os",
        "targetPrice": 56.00,
    },
    {
        "name": "Cetaphil Gentle Skin Cleanser 500ml",
        "url": "https://shopee.com.my/cetaphil.os",
        "targetPrice": 45.00,
    },
    {
        "name": "Watsons Brand Antibacterial Shower Gel 1000ml",
        "url": "https://shopee.com.my/watsons.my",
        "targetPrice": 15.00,
    },
]


def send_bark_notification(title, body, link):
  if not BARK_URL:
    print("错误: 未配置 BARK_URL 环境变量")
    return

  encoded_url = requests.utils.quote(link, safe="")
  full_url = f"{BARK_URL}/{requests.utils.quote(title)}/{requests.utils.quote(body)}?url={encoded_url}&group=好价雷达"

  try:
    response = requests.get(full_url)
    if response.status_code == 200:
      print(f"成功推送通知: {title}")
    else:
      print(f"推送失败，状态码: {response.status_code}")
  except Exception as e:
    print(f"推送异常: {e}")


def check_prices():
  print("开始执行云端价格监控巡检...")
  if BARK_URL:
    dashboard_url = "https://snazzy-beijinho-64ae53.netlify.app"
    send_bark_notification(
        "🛒 今日个护好价雷达已更新",
        "点击这里打开云端比价看板，查看 Shopee & TikTok 最新价格！",
        dashboard_url,
    )


if __name__ == "__main__":
  check_prices()
