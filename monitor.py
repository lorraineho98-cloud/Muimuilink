import os
import requests

# 直接从环境获取
BARK_URL = os.environ.get("BARK_URL")

def test_push():
    print(f"当前读取到的 BARK_URL 是: {BARK_URL}")
    
    if not BARK_URL:
        print("❌ 致命错误: BARK_URL 环境变量为空！说明你在 GitHub Secrets 里的名字写错了，或者根本没配成功。")
        return

    # 强制拼一个最简单的测试链接
    target_url = f"{BARK_URL.rstrip('/')}/价格监控终极测试/GitHub云端连通成功！"
    
    try:
        response = requests.get(target_url, timeout=10)
        print(f"Bark 服务器响应状态码: {response.status_code}")
        print(f"Bark 服务器返回内容: {response.text}")
        if response.status_code == 200:
            print("✅ 理论上手机应该已经响了！")
        else:
            print("❌ Bark 服务器拒绝了请求，请检查 Key 是否正确。")
    except Exception as e:
        print(f"❌ 请求发生异常: {e}")

if __name__ == "__main__":
    test_push()
