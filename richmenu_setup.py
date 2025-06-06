from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuArea, RichMenuBounds, MessageAction
from dotenv import load_dotenv
import os

# 載入 .env 的 Channel Access Token
load_dotenv()
channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

if not channel_token:
    print("❌ 未讀取到 LINE_CHANNEL_ACCESS_TOKEN，請檢查 .env 設定")
    exit()

line_bot_api = LineBotApi(channel_token)

try:
    # Step 1: 建立 Rich Menu 設定
    rich_menu = RichMenu(
        size={"width": 2500, "height": 843},
        selected=True,
        name="HealthyBee Main Menu",
        chat_bar_text="📋 開啟主選單",
        areas=[
            RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=1250, height=421),
                         action=MessageAction(label="我要綁定", text="我要綁定")),
            RichMenuArea(bounds=RichMenuBounds(x=1250, y=0, width=1250, height=421),
                         action=MessageAction(label="選擇語言", text="選擇語言")),
            RichMenuArea(bounds=RichMenuBounds(x=0, y=421, width=1250, height=422),
                         action=MessageAction(label="查詢體溫", text="查詢體溫")),
            RichMenuArea(bounds=RichMenuBounds(x=1250, y=421, width=1250, height=422),
                         action=MessageAction(label="使用說明", text="教學")),
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
