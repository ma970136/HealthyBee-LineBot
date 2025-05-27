import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv  # 記得 pip install python-dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 載入 .env 環境變數
load_dotenv()

# 初始化 Flask 應用
app = Flask(__name__)

# 讀取環境變數
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
THINGSPEAK_CHANNEL_ID = os.environ.get("THINGSPEAK_CHANNEL_ID")
THINGSPEAK_API_KEY = os.environ.get("THINGSPEAK_API_KEY")  # 可選，如果你設成 private 才需要

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 抓 ThingSpeak 資料並計算平均
def fetch_thingspeak_data():
    url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/1.json?results=10"
    
    response = requests.get(url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"

    data = response.json()
    temps = []
    for feed in data["feeds"]:
        val = feed.get("field1")
        if val:
            try:
                temps.append(float(val))
            except ValueError:
                pass

    if temps:
        avg = sum(temps) / len(temps)
        return f"最近 10 筆溫度平均為：{avg:.2f} °C"
    else:
        return "目前沒有有效的溫度資料。"

# LINE webhook endpoint
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 訊息處理邏輯
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    if "查溫度" in user_text:
        result = fetch_thingspeak_data()
    else:
        result = "請輸入『查溫度』來查詢資料。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=result)
    )

# 啟動 Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)