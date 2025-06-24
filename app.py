import json
import os
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv  # 記得 pip install python-dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from linebot.models import QuickReply, QuickReplyButton, MessageAction

from lang_text import get_text, format_bp_message, LANG_ID, check_missing_lang_keys
from datetime import datetime, timezone, timedelta

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
thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/1.json?results=10"

def get_HeartRate():
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        for feed in reversed(feeds):  # 從最新的開始找
            val = feed.get("field1")
            if val:
                return f"❤️ 最新心率為：{float(val):.1f} bpm"
    except Exception:
        return "⚠️ 讀取心率時發生錯誤。"

    return "目前沒有有效的心率資料。"

def get_Steps():  # field2 為步數欄位
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        
        # 取得今天日期（UTC+8）
        now = datetime.now(timezone(timedelta(hours=8)))
        today_str = now.strftime('%Y-%m-%d')

        total_steps = 0
        for feed in feeds:
            created_at = feed.get("created_at")
            val = feed.get("field2")

            if created_at and val:
                # 解析時間並轉換為 +8 時區
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                if ts.strftime('%Y-%m-%d') == today_str:
                    try:
                        total_steps += int(float(val))
                    except ValueError:
                        pass

        if total_steps > 0:
            return f"👟 今日累積步數：{total_steps} 步"
        else:
            return "今天還沒有任何步數資料。"

    except Exception as e:
        return f"⚠️ 讀取步數時發生錯誤：{e}"

def get_Cal(): #field3
    
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"
    data = response.json()
    HeartRate = []
    for feed in data["feeds"]:
        val = feed.get("field1")
        if val:
            try:
                HeartRate.append(float(val))
            except ValueError:
                pass
    if HeartRate:
        return f"您的心率為：{HeartRate[-10:]/10}/min"
    else:
        return "目前沒有有效的心率資料。"
    
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

@app.route("/", methods=["GET"])
def home():
    return "HealthyBee is running 🐝"

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
    user_id = event.source.user_id
    msg = event.message.text.strip()

    # ✅ 選擇語言
    if msg == "選擇語言":
        reply_text = "🌐 請選擇語言："
        quick_reply = QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="繁體中文", text="語言：繁體中文")),
            QuickReplyButton(action=MessageAction(label="简体中文", text="語言：简体中文")),
            QuickReplyButton(action=MessageAction(label="English", text="語言：English")),
            QuickReplyButton(action=MessageAction(label="日本語", text="語言：日本語")),
        ])
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text, quick_reply=quick_reply)
        )
        return
    # 儲存語言設定
    lang_map = {
        "語言：简体中文": 1,
        "語言：繁體中文": 2,
        "語言：English": 3,
        "語言：日本語": 4,
    }
    if msg in lang_map:
        lang_id = lang_map[msg]

        # 👉 嘗試讀取原本 JSON，如果不存在就建立空的
        try:
            with open("user_lang.json", "r", encoding="utf-8") as f:
                lang_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            lang_data = {}

        # 👉 更新語言設定
        lang_data[user_id] = lang_id
        with open("user_lang.json", "w", encoding="utf-8") as f:
            json.dump(lang_data, f, indent=2, ensure_ascii=False)

        # 👉 使用 lang_text.py 提供回應文字
        reply_text = get_text("set_lang_success", lang_id)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return
    
    # ✅ 查詢卡路里

    

    # ✅ 查步數指令
    if "每日步數" in msg:
        result = get_Steps()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return
    # ✅ 查心率指令
    if "查詢心率" in msg:
        result = get_HeartRate()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 🟡 未匹配指令
    reply_text = "請輸入『查心率』或『我要綁定』來使用功能。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))



# 啟動 Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)