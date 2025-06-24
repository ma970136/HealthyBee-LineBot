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
        4: "HealthyBeeへようこそ！"
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

# ✅ 检查是否缺失某语言的文案
def check_missing_lang_keys():
    for key, values in TEXT_GROUP.items():
        for lang_num in LANG_ID:
            if lang_num not in values:
                print(f"[缺失] 文案“{key}”缺少语言 {LANG_ID[lang_num]}（lang_id={lang_num}）")