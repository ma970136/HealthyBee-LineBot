import json
import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv  # 記得 pip install python-dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 設定 JSON 檔案路徑
passport_file = "user_passport.json"

# 確保 json 檔存在
if not os.path.exists(passport_file):
    with open(passport_file, "w") as f:
        json.dump({}, f)

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

# 綁定護照號碼的函式
def bind_passport_id(user_id, text):
    try:
        # 檢查格式：護照號碼:123456789
        if not text.startswith("護照號碼:"):
            return "請用正確格式輸入，例如：護照號碼:123456789"

        passport_number = text.replace("護照號碼:", "").strip()
        
        # 驗證是否為 9 碼數字
        if not passport_number.isdigit() or len(passport_number) != 9:
            return "護照號碼格式錯誤，請輸入 9 碼數字"

        # 讀取 json
        with open(passport_file, "r", encoding="utf-8") as f:
            user_dict = json.load(f)

        # 更新使用者資料
        user_dict[user_id] = passport_number

        # 寫入 json
        with open(passport_file, "w", encoding="utf-8") as f:
            json.dump(user_dict, f, ensure_ascii=False, indent=2)

        return f"✅ 綁定成功！您的護照號碼為：{passport_number}"
    
    except Exception as e:
        return f"❌ 綁定失敗：{str(e)}"
    
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
        return f"您的體溫為：{avg:.2f} °C"
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
from linebot.models import FollowEvent

@handler.add(FollowEvent)
def handle_follow(event):
    welcome_msg = "🐝 歡迎加入 HealthyBee！\n"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg)
    )

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
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    # 綁定流程啟動（使用者點選 "我要綁定"）
    if msg == "我要綁定":
        reply_text = "🐝 請輸入護照號碼（共數字 9 碼）："
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    # 綁定護照號碼（9 碼純數字）
    if msg.isdigit() and len(msg) == 9:
        # 儲存到 JSON 檔案
        with open("user_passport.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        data[user_id] = msg
        with open("user_passport.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        reply_text = f"✅ 已成功綁定護照號碼：{msg}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    # 若有其他訊息未匹配，保留給語言查詢等
    ...
@app.route("/", methods=["GET"])
def home():
    return "HealthyBee is running 🐝"

# 啟動 Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)