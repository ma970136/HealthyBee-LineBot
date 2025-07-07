# lang_text.py

# 语言编号映射
LANG_ID = {
    1: "zh-CN",  # 简体中文
    2: "zh-TW",  # 繁體中文
    3: "en",     # English
    4: "ja"      # 日本語
}

# 文案主文本库
TEXT_GROUP = {
    # 🟦 欢迎
    "welcome": {
        1: "欢迎使用HealthyBee！",
        2: "歡迎使用HealthyBee！",
        3: "Welcome to HealthyBee!",
        4: "HealthyBee へようこそ！"
    },

    "set_lang_success": {
        1: "✅ 语言设置成功：简体中文",
        2: "✅ 語言設置成功：繁體中文",
        3: "✅ Language set to English",
        4: "✅ 言語は日本語に設定されました。"
    },

    "help": {
        1: "您可以使用以下命令：\n1. 查询血压\n2. 设置提醒\n3. 更换语言",
        2: "您可以使用以下指令：\n1. 查詢血壓\n2. 設定提醒\n3. 更換語言",
        3: "You can use the following commands:\n1. Check blood pressure\n2. Set reminder\n3. Change language",
        4: "次のコマンドが使えます：\n1. 血圧確認\n2. リマインダー設定\n3. 言語変更"
    },

    # 🟨 血压文案
    "bp_prefix": {
        1: "📊 最新测量到的血压值是：",
        2: "📊 最新測量到的血壓值是：",
        3: "📊 The latest blood pressure reading is:",
        4: "📊 最新の血圧測定値は："
    },

    "bp_normal": {
        1: "✅ 血压正常，请继续保持良好生活习惯。",
        2: "✅ 血壓正常，請繼續保持良好生活習慣。",
        3: "✅ Your blood pressure is normal. Keep up the healthy habits!",
        4: "✅ 血圧は正常です。良い生活習慣を続けてください。"
    },

    "bp_high": {
        1: "⚠️ 血压略高，请注意休息和持续观察，必要时请就医检查。",
        2: "⚠️ 血壓略高，請注意休息並持續觀察，必要時請就醫檢查。",
        3: "⚠️ Blood pressure is slightly high. Please rest, monitor your condition, and consult a doctor if needed.",
        4: "⚠️ 血圧はやや高めです。休息と経過観察を行い、必要に応じて医師に相談してください。"
    },
# 通用 - 未知命令
"unknown_command": {
    1: "❓ 抱歉，我不理解您的指令。",
    2: "❓ 抱歉，我無法理解您的指令。",
    3: "❓ Sorry, I didn't understand your command.",
    4: "❓ 申し訳ありません。コマンドを理解できませんでした。"
},

# 系统错误
"server_error": {
    1: "⚠️ 系统出现了一点小问题，请稍后再试。",
    2: "⚠️ 系統出現了一點小問題，請稍後再試。",
    3: "⚠️ Oops! Something went wrong. Please try again later.",
    4: "⚠️ システムに問題が発生しました。しばらくしてからもう一度お試しください。"
},

# 设置提醒
"reminder_set": {
    1: "🔔 已为您设置提醒。",
    2: "🔔 已為您設定提醒。",
    3: "🔔 Reminder has been set.",
    4: "🔔 リマインダーを設定しました。"
},

# 取消提醒
"reminder_cancel": {
    1: "🔕 已取消提醒。",
    2: "🔕 已取消提醒。",
    3: "🔕 Reminder has been canceled.",
    4: "🔕 リマインダーをキャンセルしました。"
},

# 提醒时间到
"reminder_upcoming": {
    1: "⏰ 提醒时间到了，请注意查看。",
    2: "⏰ 提醒時間到了，請注意查看。",
    3: "⏰ It's time! Please check.",
    4: "⏰ リマインダーの時間です。ご確認ください。"
},

# 提醒已过期
"reminder_missed": {
    1: "⚠️ 您错过了一个提醒。",
    2: "⚠️ 您錯過了一個提醒。",
    3: "⚠️ You missed a reminder.",
    4: "⚠️ リマインダーを逃しました。"
},

# 没有历史记录
"history_empty": {
    1: "暂无历史记录。",
    2: "暫無歷史記錄。",
    3: "No history available.",
    4: "履歴はありません。"
},

# 历史记录单项模板（如: 时间 + 值）
"history_item": {
    1: "📅 {time} - 血压：{value}",
    2: "📅 {time} - 血壓：{value}",
    3: "📅 {time} - BP: {value}",
    4: "📅 {time} - 血圧: {value}"
},

# 建议就医
"suggest_checkup": {
    1: "💡 如果不适持续，请及时前往医院进行更详细的检查。",
    2: "💡 如果不適持續，請及時前往醫院進行更詳細的檢查。",
    3: "💡 If you feel unwell, please visit a hospital for a detailed checkup.",
    4: "💡 体調が優れない場合は、病院で詳しく検査を受けてください。"
},

# 已是最新数据
"already_latest": {
    1: "✅ 当前已是最新数据，无需更新。",
    2: "✅ 目前已是最新資料，無需更新。",
    3: "✅ This is the latest data, no update needed.",
    4: "✅ これが最新のデータです。更新は不要です。"
},

# 切换语言提示
"change_lang": {
    1: "🌐 您可以输入数字 1~4 来选择新的语言。",
    2: "🌐 您可以輸入數字 1~4 來選擇新的語言。",
    3: "🌐 You can enter a number (1~4) to select a new language.",
    4: "🌐 数字 1〜4 を入力して新しい言語を選択できます。"
},

# 是/否
"confirm_yes": {
    1: "是",
    2: "是",
    3: "Yes",
    4: "はい"
},
"confirm_no": {
    1: "否",
    2: "否",
    3: "No",
    4: "いいえ"
},
"走了": {
    1: "走了",        # 简体中文
    2: "走了",        # 繁體中文
    3: "walked",      # 英文
    4: "歩いた"       # 日本語
},
"步": {
    1: "步",          # 简体中文
    2: "步",          # 繁體中文
    3: "steps",       # 英文
    4: "歩"           # 日本語
},
# 早安
"greeting_morning": {
    1: "🌅 早安！祝您一天好心情～",
    2: "🌅 早安！祝您一天好心情～",
    3: "🌅 Good morning! Have a nice day!",
    4: "🌅 おはようございます！良い一日を！"
},

# 晚安
"greeting_evening": {
    1: "🌙 晚安！记得好好休息。",
    2: "🌙 晚安！記得好好休息。",
    3: "🌙 Good night! Have a restful sleep.",
    4: "🌙 おやすみなさい！ゆっくり休んでください。"
}

}

# ✅ 文本获取函数
def get_text(key: str, lang_id: int) -> str:
    return TEXT_GROUP.get(key, {}).get(lang_id, "[⚠️ 文本缺失]")

# ✅ 血压文案组合函数
def format_bp_message(lang_id: int, value_str: str, level: str) -> str:
    """
    参数:
        lang_id: 语言编号 (1~4)
        value_str: 例如 "135/88 mmHg"
        level: 可选 "normal" / "high"
    """
    prefix = get_text("bp_prefix", lang_id)
    body = get_text(f"bp_{level}", lang_id)
    return f"{prefix} {value_str}\n{body}"

def format_steps_message(lang_id: int, dates: list, steps: list) -> str:
    """
    生成七天步數查詢結果
    参数:
        lang_id: 语言编号 (1~4)
        dates: 日期列表，例如 ["2025-07-07", "2025-07-06", ...]
        steps: 步數列表，例如 [0, 0, 20, 0, 0, 40]
    
    返回:
        返回完整的步數查詢訊息，包含翻譯後的文字
    """
    result = ""
    
    # 翻譯 "走了" 和 "步" 兩個字
    walked_text = get_text("走了", lang_id)  # 這裡會根據語言返回 "走了"、"歩いた"、"walked"
    step_text = get_text("步", lang_id)      # 這裡會根據語言返回 "步"、"歩"、"steps"
    
    # 迴圈組合結果
    for date, step in zip(dates, steps):
        result += f"{date} {walked_text} {step} {step_text}\n"
    
    return result.strip()  # 去除最後的換行符

# ✅ 检查是否缺失某语言的文案
def check_missing_lang_keys():
    for key, values in TEXT_GROUP.items():
        for lang_num in LANG_ID:
            if lang_num not in values:
                print(f"[缺失] 文案“{key}”缺少语言 {LANG_ID[lang_num]}（lang_id={lang_num}）")