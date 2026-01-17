import requests
import json
from datetime import datetime
import os

# 1. 从 GitHub Secrets 读取配置参数（个人号专用）
APP_ID = os.getenv("WECHAT_APP_ID")
APP_SECRET = os.getenv("WECHAT_APP_SECRET")
FAN_OPENID = os.getenv("WECHAT_FAN_OPENID")  # 新增：粉丝 OpenID

# 2. 从你的接口获取 News 数据
def get_news_data():
    try:
        api_url = "https://world.20030525.xyz/v2/60s"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # 抛出请求错误（4xx/5xx）
        data = response.json()
        news_list = data["data"]["news"]
        return news_list
    except Exception as e:
        print(f"❌ 获取 News 失败：{str(e)}")
        return None

# 3. 获取公众号 Access Token（个人号可用，有效期2小时）
def get_access_token():
    try:
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
        response = requests.get(token_url, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        
        if "access_token" in token_data:
            return token_data["access_token"]
        else:
            print(f"❌ 获取 Access Token 失败：{token_data}")
            return None
    except Exception as e:
        print(f"❌ 获取 Access Token 异常：{str(e)}")
        return None

# 4. 纯文字消息推送（个人订阅号可用，客服消息接口）
def send_text_news_to_wechat(access_token, news_list):
    if not FAN_OPENID:
        print("❌ 未配置粉丝 OpenID，无法发送消息")
        return

    try:
        # 文字内容排版（清晰易读）
        news_title = f"今日热点 News {datetime.now().strftime('%Y-%m-%d')}\n\n"
        news_content = ""
        for idx, news in enumerate(news_list, 1):
            news_content += f"{idx}. {news}\n"
        final_content = news_title + news_content + "\n✨ 自动推送 by GitHub Actions"

        # 个人号可用的客服消息接口（仅能给关注的粉丝发送）
        send_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        send_data = {
            "touser": FAN_OPENID,  # 接收消息的粉丝 OpenID
            "msgtype": "text",     # 消息类型：纯文字
            "text": {
                "content": final_content  # 排版后的新闻内容
            }
        }

        response = requests.post(send_url, json=send_data, timeout=30)
        response.raise_for_status()
        send_result = response.json()

        if send_result.get("errcode") == 0:
            print("✅ 纯文字 News 已成功推送到公众号粉丝！")
        else:
            print(f"❌ 推送失败：{send_result}")
    except Exception as e:
        print(f"❌ 推送异常：{str(e)}")

# 主程序入口（执行流程）
if __name__ == "__main__":
    # 步骤1：获取 News 数据
    news_list = get_news_data()
    if not news_list:
        print("❌ 无有效 News 数据，终止推送")
        exit(1)
    
    # 步骤2：获取 Access Token
    access_token = get_access_token()
    if not access_token:
        print("❌ 无有效 Access Token，终止推送")
        exit(1)
    
    # 步骤3：发送纯文字消息（个人号核心）
    send_text_news_to_wechat(access_token, news_list)
