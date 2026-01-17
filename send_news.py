import requests
import json
from datetime import datetime
import os

# 1. 直接配置正确的 fakeid（临时测试，后续可改回 Secrets）
APP_ID = os.getenv("WECHAT_APP_ID")
APP_SECRET = os.getenv("WECHAT_APP_SECRET")
FAN_FAKEID = "ozOAi3WZVDFeRSDcDlic5zebBuhc"  # 直接粘贴正确的 fakeid

# 2. 从你的接口获取 News 数据
def get_news_data():
    try:
        api_url = "https://world.20030525.xyz/v2/60s"
        response = requests.get(api_url, timeout=60)
        response.raise_for_status()
        data = response.json()
        news_list = data["data"]["news"]
        return news_list
    except Exception as e:
        print(f"❌ 获取 News 失败：{str(e)}")
        return None

# 3. 获取公众号 Access Token
def get_access_token():
    try:
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
        response = requests.get(token_url, timeout=60)
        response.raise_for_status()
        token_data = response.json()
        
        if "access_token" in token_data:
            print(f"✅ 获取 Access Token 成功：{token_data['access_token'][:20]}...")  # 打印部分 token 验证
            return token_data["access_token"]
        else:
            print(f"❌ 获取 Access Token 失败：{token_data}")
            return None
    except Exception as e:
        print(f"❌ 获取 Access Token 异常：{str(e)}")
        return None

# 4. 简化版纯文字推送（仅给单个 fakeid 发送，排除多余逻辑）
def send_text_news_to_wechat(access_token, news_list):
    if not FAN_FAKEID:
        print("❌ 未配置有效 fakeid")
        return

    # 简化消息内容（避免过长被拦截）
    news_title = f"今日热点 {datetime.now().strftime('%Y-%m-%d')}\n"
    news_content = "\n".join([f"{idx}. {news[:50]}" for idx, news in enumerate(news_list[:5], 1)])  # 只取前5条，每条截断50字
    final_content = news_title + news_content

    try:
        send_url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        send_data = {
            "touser": FAN_FAKEID,  # 直接使用 fakeid
            "msgtype": "text",
            "text": {
                "content": final_content
            }
        }

        response = requests.post(send_url, json=send_data, timeout=60)
        # 打印完整响应（关键！看微信服务器真实反馈）
        print(f"📝 微信服务器完整响应：{response.text}")
        
        response.raise_for_status()
        send_result = response.json()

        if send_result.get("errcode") == 0:
            print(f"✅ 已成功推送给 fakeid：{FAN_FAKEID}")
        else:
            print(f"❌ 推送失败：{send_result}")
    except Exception as e:
        print(f"❌ 推送异常：{str(e)}")

# 主程序入口
if __name__ == "__main__":
    news_list = get_news_data()
    if not news_list:
        exit(1)
    
    access_token = get_access_token()
    if not access_token:
        exit(1)
    
    send_text_news_to_wechat(access_token, news_list)
