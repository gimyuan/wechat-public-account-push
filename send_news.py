import requests
import json
from datetime import datetime
import os

# 1. 从 GitHub Secrets 读取配置参数（支持多 OpenID）
APP_ID = os.getenv("WECHAT_APP_ID")
APP_SECRET = os.getenv("WECHAT_APP_SECRET")
FAN_OPENIDS_STR = os.getenv("WECHAT_FAN_OPENID")  # 读取逗号分隔的 OpenID 字符串

# 拆分多 OpenID 为列表（处理空值、去重）
FAN_OPENID_LIST = [openid.strip() for openid in FAN_OPENIDS_STR.split(",") if openid.strip()] if FAN_OPENIDS_STR else []

# 2. 从你的接口获取 News 数据
def get_news_data():
    try:
        api_url = "https://world.20030525.xyz/v2/60s"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
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

# 4. 纯文字消息推送（支持多 OpenID 循环发送，个人订阅号可用）
def send_text_news_to_wechat(access_token, news_list):
    if not FAN_OPENID_LIST:
        print("❌ 未配置有效粉丝 OpenID，无法发送消息")
        return

    # 文字内容排版（清晰易读）
    news_title = f"今日热点 News {datetime.now().strftime('%Y-%m-%d')}\n\n"
    news_content = ""
    for idx, news in enumerate(news_list, 1):
        news_content += f"{idx}. {news}\n"
    final_content = news_title + news_content + "\n✨ 自动推送 by GitHub Actions"

    # 循环给每个 OpenID 发送消息
    for openid in FAN_OPENID_LIST:
        try:
            # 个人号可用的客服消息接口
            send_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
            send_data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": final_content
                }
            }

            response = requests.post(send_url, json=send_data, timeout=30)
            response.raise_for_status()
            send_result = response.json()

            if send_result.get("errcode") == 0:
                print(f"✅ 已成功推送给 OpenID：{openid}")
            else:
                print(f"❌ 推送给 OpenID {openid} 失败：{send_result}")
        except Exception as e:
            print(f"❌ 推送给 OpenID {openid} 异常：{str(e)}")

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
    
    # 步骤3：批量发送纯文字消息（多粉丝核心）
    send_text_news_to_wechat(access_token, news_list)
