from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, MessageAction
from dotenv import load_dotenv
import os
from lang_text import get_text, format_steps_message, format_calories_message, LANG_ID, check_missing_lang_keys
import json
# 載入 .env 的 Channel Access Token
load_dotenv()
channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_token:
    print("❌ 未讀取到 LINE_CHANNEL_ACCESS_TOKEN，請檢查 .env 設定")
    exit()

line_bot_api = LineBotApi(channel_token)
# 讀取用戶的語言設定
def get_user_language(user_id: str) -> int:
    try:
        with open("user_lang.json", "r", encoding="utf-8") as f:
            lang_data = json.load(f)
        return lang_data.get(user_id, 2)  # 如果找不到該用戶的設定，預設為繁體中文 (lang_id = 2)
    except (FileNotFoundError, json.JSONDecodeError):
        return 2  # 如果檔案不存在或讀取錯誤，預設為繁體中文
# user_id = event.source.user_id
lang_id = 4
try:
    # Step 1: 建立 Rich Menu 設定
    rich_menu = RichMenu(
        size={"width": 2500, "height": 1686},
        selected=True,
        name="HealthyBee Main Menu",
        chat_bar_text="📋 開啟主選單",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                        action=MessageAction(label=get_text("get_steps", lang_id), text=get_text("get_steps", lang_id))),
            RichMenuArea(bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
                        action=MessageAction(label=get_text("get_calories", lang_id), text=get_text("get_calories", lang_id))),
            RichMenuArea(bounds=RichMenuBounds(x=0, y=843, width=1250, height=843),
                        action=MessageAction(label=get_text("get_heartrate", lang_id), text=get_text("get_heartrate", lang_id))),
            RichMenuArea(bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
                        action=MessageAction(label=get_text("choose_language", lang_id), text=get_text("choose_language", lang_id))),
        ]
    )

    # Step 2: 建立 Rich Menu 並取得 ID
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu)
    print("✅ Rich Menu 已建立，ID：", rich_menu_id)

    # Step 3: 上傳圖片
    with open("richmenu.png", "rb") as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
        print("✅ 圖片已上傳")

    # Step 4: 設為預設 Rich Menu
    line_bot_api.set_default_rich_menu(rich_menu_id)
    print("✅ Rich Menu 已設為預設並啟用成功！")

except Exception as e:
    print("❌ 發生錯誤：", str(e))
