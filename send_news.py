import requests
import json
from datetime import datetime
import os

# 1. 从 GitHub Secrets 读取公众号配置参数（避免硬编码泄露）
APP_ID = os.getenv("WECHAT_APP_ID")
APP_SECRET = os.getenv("WECHAT_APP_SECRET")
THUMB_MEDIA_ID = os.getenv("WECHAT_THUMB_MEDIA_ID")


# 2. 从你的接口获取 news 数据
def get_news_data():
    try:
        api_url = "https://world.20030525.xyz/v2/60s"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # 抛出请求错误
        data = response.json()
        return data["data"]["news"]
    except Exception as e:
        print(f"获取 News 失败：{str(e)}")
        return None


# 3. 获取公众号 access_token（有效期 2 小时，每次运行重新获取）
def get_access_token():
    try:
        token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"
        response = requests.get(token_url, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        if "access_token" in token_data:
            return token_data["access_token"]
        else:
            print(f"获取 Access Token 失败：{token_data}")
            return None
    except Exception as e:
        print(f"获取 Access Token 异常：{str(e)}")
        return None


# 4. 排版公众号图文内容并上传素材
def upload_news_material(access_token, news_list):
    try:
        # 图文标题和内容排版
        title = f"今日热点 News {datetime.now().strftime('%Y-%m-%d')}"
        content = "<h2>今日速览</h2><ul>"
        for idx, news in enumerate(news_list, 1):
            content += f"<li>{idx}. {news}</li>"
        content += "</ul><p>自动推送 by GitHub Actions</p>"

        # 上传图文素材接口
        upload_url = f"https://api.weixin.qq.com/cgi-bin/media/uploadnews?access_token={access_token}"
        upload_data = {
            "articles": [
                {
                    "title": title,
                    "content": content,
                    "content_source_url": "",  # 原文链接（可选，留空即可）
                    "thumb_media_id": THUMB_MEDIA_ID,
                    "show_cover_pic": 1,  # 是否显示封面图（1=显示，0=不显示）
                    "digest": "每日热点自动推送，速看！"  # 图文摘要（可选）
                }
            ]
        }

        response = requests.post(upload_url, json=upload_data, timeout=30)
        response.raise_for_status()
        upload_result = response.json()
        if "media_id" in upload_result:
            return upload_result["media_id"]
        else:
            print(f"上传图文素材失败：{upload_result}")
            return None
    except Exception as e:
        print(f"上传图文素材异常：{str(e)}")
        return None


# 5. 触发公众号群发
def send_news_to_wechat(access_token, media_id):
    try:
        send_url = f"https://api.weixin.qq.com/cgi-bin/message/mass/sendall?access_token={access_token}"
        send_data = {
            "filter": {
                "is_to_all": True  # 发送给全部粉丝（True=是，False=按标签筛选）
            },
            "mpnews": {
                "media_id": media_id
            },
            "msgtype": "mpnews",  # 消息类型（图文消息=mpnews）
            "send_ignore_reprint": 0
        }

        response = requests.post(send_url, json=send_data, timeout=30)
        response.raise_for_status()
        send_result = response.json()
        if send_result.get("errcode") == 0:
            print("✅ News 已成功群发至公众号！")
        else:
            print(f"群发失败：{send_result}")
    except Exception as e:
        print(f"群发异常：{str(e)}")


# 主程序入口
if __name__ == "__main__":
    # 步骤1：获取 News 数据
    news_list = get_news_data()
    if not news_list:
        exit(1)

    # 步骤2：获取 Access Token
    access_token = get_access_token()
    if not access_token:
        exit(1)

    # 步骤3：上传图文素材
    media_id = upload_news_material(access_token, news_list)
    if not media_id:
        exit(1)

    # 步骤4：群发消息
    send_news_to_wechat(access_token, media_id)
