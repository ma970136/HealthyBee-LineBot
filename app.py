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

from lang_text import get_text, format_bp_message, format_steps_message, LANG_ID, check_missing_lang_keys
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

def get_HeartRate(): #field1
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/1.json?results=100"
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        for feed in reversed(feeds):  # 從最新的開始找
            val = feed.get("field1")
            if val:
                heart_rate = float(val)
                if heart_rate == 0:
                    continue  # 如果是 0，繼續檢查下一筆資料
                else:
                    return f"❤️{heart_rate:.1f} bpm"  # 找到非 0 的心率就返回
    except Exception:
        return "⚠️ 讀取心率時發生錯誤。"

    return "目前沒有有效的心率資料。"

def get_Steps(image_path="static/weekly_steps.png", langID=3): #field2
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/2.json?results=1000"
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "⚠️ 無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        if not feeds:
            return "⚠️ 沒有步數資料。"

        # 設定時區為 UTC+8（台灣）
        now = datetime.now(timezone(timedelta(hours=8)))
        week_str = []
        latest_data_everyday = []
        for i in range(7):
            week_str.append((now - timedelta(days=i)).strftime('%Y-%m-%d'))
            latest_data_everyday.append(None)

        for feed in reversed(feeds):  # 從最新資料往前找
            created_at = feed.get("created_at")
            val = feed.get("field2")

            if created_at and val:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                date_str = ts.strftime('%Y-%m-%d')

                for i in range(7):
                    if date_str == week_str[i] and latest_data_everyday[i] is None:
                        latest_data_everyday[i] = int(float(val))

                # 都找到了就不用再找了
        for i in range(7):
            if latest_data_everyday[i] is None:
                latest_data_everyday[i] = 0
        return_result = ""
        for i in range(7):  # 從 0 到 6，共 7 天
            return_result += f"{week_str[i]} 走了 {latest_data_everyday[i]} 步"
            if i != 6:
                return_result += "\n"
        
        result = format_steps_message(langID, week_str, latest_data_everyday)

        # 計算 X 軸與 Y 軸的資料
        x_labels = ([datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d") for d in week_str])[::-1]
        y_values = (latest_data_everyday)[::-1]

        # 畫圖
        plt.figure(figsize=(10, 4))
        bars = plt.bar(x_labels, y_values, width=0.6)
        for bar in bars:
            yval = bar.get_height()
            
            plt.text(bar.get_x() + bar.get_width() / 2, yval,  # 顯示在每個長條上方
                    f'{int(yval)}', ha='center', va='bottom', fontsize=10)  # 調整文字位置和大小
        plt.title('Daily Steps (Last 7 Days)')
        plt.xlabel('Date')
        plt.ylabel('Steps')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(image_path)
        plt.show()
        plt.close()

        print(result)
        return image_path, result
    except Exception as e:
        print(f"⚠️ 資料處理發生錯誤：{e}")
        return f"⚠️ 資料處理發生錯誤：{e}"
# thingspeak_url_test = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/2.json?results=1000"
img_path, message = get_Steps()
# get_Steps()
def get_Cal(image_path="static/weekly_Cal.png"): #field3
    thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/3.json?results=1000"
    response = requests.get(thingspeak_url)
    if response.status_code != 200:
        return "⚠️ 無法從 ThingSpeak 取得資料。"

    try:
        feeds = response.json().get("feeds", [])
        if not feeds:
            return "⚠️ 沒有卡路里資料。"

        # 設定時區為 UTC+8（台灣）
        now = datetime.now(timezone(timedelta(hours=8)))
        week_str = []
        latest_data_everyday = []
        for i in range(7):
            week_str.append((now - timedelta(days=i)).strftime('%Y-%m-%d'))
            latest_data_everyday.append(None)

        for feed in reversed(feeds):  # 從最新資料往前找
            created_at = feed.get("created_at")
            val = feed.get("field3")

            if created_at and val:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                date_str = ts.strftime('%Y-%m-%d')
                # print("R",week_str[1],latest_data_everyday[1])

                for i in range(7):
                    if date_str == week_str[i] and latest_data_everyday[i] is None:
                        latest_data_everyday[i] = int(float(val))

                # 都找到了就不用再找了
        for i in range(7):
            if latest_data_everyday[i] is None:
                latest_data_everyday[i] = 0
        return_result = ""
        for i in range(7):
            return_result += f"{week_str[i]} 消耗了 {latest_data_everyday[i]} cal"
            if i != 6:
                return_result += "\n"


        # 計算 X 軸與 Y 軸的資料
        x_labels = ([datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d") for d in week_str])[::-1]
        y_values = (latest_data_everyday)[::-1]

        # 畫圖
        plt.figure(figsize=(10, 4))
        bars = plt.bar(x_labels, y_values, width=0.6)
        for bar in bars:
            yval = bar.get_height()
            
            plt.text(bar.get_x() + bar.get_width() / 2, yval,  # 顯示在每個長條上方
                    f'{int(yval)}', ha='center', va='bottom', fontsize=10)  # 調整文字位置和大小
        plt.title('Daily Calories (Last 7 Days)')
        plt.xlabel('Date')
        plt.ylabel('Calories(cal)')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig(image_path)
        plt.show()
        plt.close()

        print(return_result)
        return image_path, return_result
    except Exception as e:
        print(f"⚠️ 資料處理發生錯誤：{e}")
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
    user_id = event.source.user_id

    # 嘗試讀取語言設定，若不存在則使用預設語言（繁體中文）
    try:
        with open("user_lang.json", "r", encoding="utf-8") as f:
            lang_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        lang_data = {}  # 若檔案不存在或格式錯誤，使用空字典

    # 嘗試獲取用戶的手機語言設定（默認為繁體中文）
    try:
        user_profile = line_bot_api.get_profile(user_id)
        user_language = user_profile.language  # 這將返回用戶手機語言，例如 "zh-TW", "en", "ja"
    except Exception as e:
        user_language = "en"  # 如果獲取語言失敗，默認使用繁體中文
    
    # 根據用戶手機語言設定來決定語言 ID
    lang_map = {
        "zh-TW": 2,  # 繁體中文
        "zh-CN": 1,  # 簡體中文
        "en": 3,     # 英文
        "ja": 4      # 日文
    }
    lang_id = lang_map.get(user_language, 2)  # 默認為繁體中文

    # 根據語言返回歡迎訊息
    welcome_msg = get_text("welcome", lang_id)  # 從 lang_text.py 中獲取對應語言的歡迎訊息

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_msg)
    )

# 訊息處理邏輯
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()
    # 嘗試讀取語言設定，若不存在則使用預設語言（繁體中文）
    try:
        with open("user_lang.json", "r", encoding="utf-8") as f:
            lang_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        lang_data = {}  # 若檔案不存在或格式錯誤，使用空字典
     
    # 預設語言為繁體中文 (lang_id = 2)
    lang_id = lang_data.get(user_id, 2)

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
    
    lang_id = lang_data.get(user_id, 2)  # 預設為繁體中文

    # ✅ 查詢卡路里
    if "消耗卡路里" in msg:
        img_path, message = get_Cal()
        # 發送圖片與日期時間訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=message),
                ImageSendMessage(
                    original_content_url="https://healthybee-linebot.onrender.com/static/weekly_Cal.png",
                    preview_image_url="https://healthybee-linebot.onrender.com/static/weekly_Cal.png"
                )
            ]
        )
        # result = get_Cal()
        # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result))
        # return

    # ✅ 查步數指令
    if "每日步數" in msg:
        thingspeak_url = f"https://api.thingspeak.com/channels/{THINGSPEAK_CHANNEL_ID}/fields/2.json?results=1000"
        img_path, message = get_Steps(langID=lang_id)
        # 發送圖片與日期時間訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=message),
                ImageSendMessage(
                    original_content_url="https://healthybee-linebot.onrender.com/static/weekly_steps.png",
                    preview_image_url="https://healthybee-linebot.onrender.com/static/weekly_steps.png"
                )
            ]
        )


    # ✅ 查心率指令
    if "查詢心率" in msg:
        result = get_HeartRate()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=get_text("bp_prefix", lang_id) + result))
        return

    # 🟡 未匹配指令
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=get_text("unknown_command", lang_id)))



# 啟動 Flask App
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)