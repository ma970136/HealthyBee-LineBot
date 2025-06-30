import json
import os
import requests
import matplotlib.pyplot as plt
from collections import defaultdict
from flask import Flask, request, abort
from dotenv import load_dotenv  # 記得 pip install python-dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
from linebot.models import QuickReply, QuickReplyButton, MessageAction, ImageSendMessage

from lang_text import get_text, format_bp_message, LANG_ID, check_missing_lang_keys
from datetime import datetime, timezone, timedelta
app = Flask(__name__)

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

def get_weekly_steps_chart(thingspeak_url: str, image_path="static/weekly_steps.png"):
    print("🟡 取得資料：", thingspeak_url)
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return None, "❌ 無法取得步數資料"

    feeds = response.json().get("feeds", [])
    if not feeds:
        return None, "⚠️ 沒有步數資料"

    # 台灣時區
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz).date()
    seven_days_ago = today - timedelta(days=6)

    # 每天的最後一筆步數
    daily_data = {}
    for feed in reversed(feeds):  # 從最新的資料找
        created_at = feed.get("created_at")
        val = feed.get("field2")
        if created_at and val:
            try:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                date = ts.date()
                print(f"🟡 取得資料：{created_at} → 台灣時間：{ts} → 日期：{date} → 步數：{val}")

                # if seven_days_ago <= date <= today:
                    # if date not in daily_data:
                daily_data[date] = int(float(val))
            except Exception:
                continue

    # 補足沒有資料的日期（值為 None）
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    daily_steps = []
    prev_val = None
    for d in dates:
        val = daily_data.get(d)
        if val is not None and prev_val is not None:
            daily_steps.append(val - prev_val)
        else:
            daily_steps.append(0 if prev_val is not None else None)
        prev_val = val

    # 畫圖
    x_labels = [d.strftime("%m/%d") for d in dates]
    y_values = [v if v is not None else 0 for v in daily_steps]

    plt.figure(figsize=(10, 4))
    plt.bar(x_labels, y_values, width=0.6)
    plt.title('Daily Steps (Last 7 days)')
    plt.xlabel('Date')
    plt.ylabel('Steps')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    return image_path, None


def get_HeartRate(): #field1
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/1.json?results=10"
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

def get_Steps(): #field2
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/2.json?results=10"
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "⚠️ 無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        if not feeds:
            return "⚠️ 沒有步數資料。"

        # 設定時區為 UTC+8（台灣）
        now = datetime.now(timezone(timedelta(hours=8)))
        today_str = now.strftime('%Y-%m-%d')
        yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')

        latest_today = None
        latest_yesterday = None

        for feed in reversed(feeds):  # 從最新資料往前找
            created_at = feed.get("created_at")
            val = feed.get("field2")

            if created_at and val:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                date_str = ts.strftime('%Y-%m-%d')

                if date_str == today_str and latest_today is None:
                    latest_today = int(float(val))

                elif date_str == yesterday_str and latest_yesterday is None:
                    latest_yesterday = int(float(val))

                # 都找到了就不用再找了
                if latest_today is not None and latest_yesterday is not None:
                    break

        if latest_today is None and latest_yesterday is None:
            return "⚠️ 今天與昨天皆無步數資料。"
        elif latest_today is None:
            return f"⚠️ 今天尚無步數資料。\n📊 昨日累計：{latest_yesterday} 步"
        elif latest_yesterday is None:
            return f"👣 今日總步數為：{latest_today} 步（昨日無資料）"
        else:
            today_steps = latest_today - latest_yesterday
            return f"👟 今日步數：{today_steps} 步\n📊 昨日累計：{latest_yesterday} 步"

    except Exception as e:
        return f"⚠️ 資料處理發生錯誤：{e}"

def get_Cal(): #field3
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/3.json?results=10"
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"
    try:
        feeds = response.json().get("feeds", [])
        if not feeds:
            return "⚠️ 沒有卡路里資料。"

        # 設定時區為 UTC+8（台灣）
        now = datetime.now(timezone(timedelta(hours=8)))
        today_str = now.strftime('%Y-%m-%d')
        yesterday_str = (now - timedelta(days=1)).strftime('%Y-%m-%d')

        latest_today = None
        latest_yesterday = None

        for feed in reversed(feeds):  # 從最新資料往前找
            created_at = feed.get("created_at")
            val = feed.get("field3")

            if created_at and val:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                date_str = ts.strftime('%Y-%m-%d')

                if date_str == today_str and latest_today is None:
                    latest_today = int(float(val))

                elif date_str == yesterday_str and latest_yesterday is None:
                    latest_yesterday = int(float(val))

                # 都找到了就不用再找了
                if latest_today is not None and latest_yesterday is not None:
                    break

        if latest_today is None and latest_yesterday is None:
            return "⚠️ 今天與昨天皆無卡路里資料。"
        elif latest_today is None:
            return f"⚠️ 今天尚無卡路里資料。\n📊 昨日累計：{latest_yesterday} kcal"
        elif latest_yesterday is None:
            return f"🔥 今日消耗卡路里為：{latest_today} kcal（昨日無資料）"
        else:
            today_steps = latest_today - latest_yesterday
            return f"🔥 今日消耗卡路里：{today_steps} kcal\n📊 昨日消耗卡路里：{latest_yesterday} kcal"

    except Exception as e:
        return f"⚠️ 資料處理發生錯誤：{e}"
    
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
    if "消耗卡路里" in msg:
        result = get_Cal()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # ✅ 查步數指令
    # if "每日步數" in msg:
    #     result = get_Steps()
    #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
    #     return
    if "每日步數" in msg:
        thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/2.json?results=100"

        img_path, err = get_weekly_steps_chart(thingspeak_url)
        if err:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=err))
        else:
            img_url = "https://healthybee-linebot.onrender.com/static/weekly_steps.png"
            image_msg = ImageSendMessage(
                original_content_url=img_url,
                preview_image_url=img_url
            )
            line_bot_api.reply_message(event.reply_token, image_msg)
        return



    # ✅ 查心率指令
    if "查詢心率" in msg:
        result = get_HeartRate()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        return

    # 🟡 未匹配指令
    reply_text = "請輸入『查詢心率』或『消耗卡路里』等指令來使用功能。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))



# 啟動 Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)