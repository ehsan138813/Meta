"""
ربات تلگرامی حرفه‌ای با دکمه‌های شیشه‌ای (Inline Keyboard)
نصب: pip install python-telegram-bot==20.7
اجرا: python bot.py
"""
import logging
import random
import datetime
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# ====== تنظیمات ======
TOKEN = "YOUR_BOT_TOKEN_HERE"  # توکن رباتت رو از BotFather بگیر
ADMIN_ID = 123456789  # آیدی عددی خودت

# ====== لاگ ======
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ====== دیتابیس ساده JSON ======
DB_FILE = "users_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== منوی اصلی ======
def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("ℹ️ درباره من", callback_data="about"),
            InlineKeyboardButton("📊 آمار", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🎲 تاس بنداز", callback_data="dice"),
            InlineKeyboardButton("🎯 شانس", callback_data="luck")
        ],
        [
            InlineKeyboardButton("📅 تاریخ و ساعت", callback_data="datetime"),
            InlineKeyboardButton("😂 جوک", callback_data="joke")
        ],
        [
            InlineKeyboardButton("💎 حقایق جالب", callback_data="fact"),
            InlineKeyboardButton("🌍 ترجمه", callback_data="translate")
        ],
        [
            InlineKeyboardButton("📞 تماس با سازنده", url="https://t.me/your_username"),
            InlineKeyboardButton("⚙️ تنظیمات", callback_data="settings")
        ],
        [
            InlineKeyboardButton("❌ بستن", callback_data="close")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ====== دستور /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = load_data()

    # ذخیره اطلاعات کاربر
    user_id = str(user.id)
    if user_id not in data:
        data[user_id] = {
            "name": user.first_name,
            "username": user.username,
            "join_date": str(datetime.datetime.now()),
            "messages": 0,
            "language": "fa"
        }
        save_data(data)

    welcome_text = f"""
✨ سلام {user.first_name} عزیز! ✨

به ربات حرفه‌ای من خوش اومدی! 🎉

از منوی زیر یکی از گزینه‌ها رو انتخاب کن:
    """
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

# ====== دستور /help ======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📚 **راهنمای ربات:**

🔹 /start - شروع و نمایش منو
🔹 /help - نمایش این راهنما
🔹 /menu - نمایش منوی اصلی
🔹 /id - دریافت آیدی شما
🔹 /echo [متن] - تکرار پیام

یا از دکمه‌های منو استفاده کن!
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

# ====== دستور /menu ======
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 منوی اصلی:", reply_markup=main_menu_keyboard())

# ====== دستور /id ======
async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"🆔 آیدی شما: `{user_id}`", parse_mode='Markdown')

# ====== دستور /echo ======
async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(f"🔊 {text}")
    else:
        await update.message.reply_text("⚠️ لطفاً یک متن بعد از دستور بنویس!\nمثال: `/echo سلام`", parse_mode='Markdown')

# ====== مدیریت کلیک روی دکمه‌ها ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = load_data()
    user_id = str(user.id)

    # آپدیت تعداد پیام‌ها
    if user_id in data:
        data[user_id]["messages"] += 1
        save_data(data)

    # ====== درباره من ======
    if query.data == "about":
        about_text = """
🤖 **درباره ربات:**

📌 نام: ربات حرفه‌ای تلگرام
📌 نسخه: 2.0
📌 سازنده: @your_username
📌 زبان: Python

✨ قابلیت‌ها:
• دکمه‌های شیشه‌ای
• ذخیره اطلاعات کاربران
• آمارگیری
• و کلی چیز دیگه!
        """
        keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]]
        await query.edit_message_text(about_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== آمار ======
    elif query.data == "stats":
        if user_id in data:
            user_data = data[user_id]
            stats_text = f"""
📊 **آمار شما:**

👤 نام: {user_data.get('name', 'نامشخص')}
📅 تاریخ عضویت: {user_data.get('join_date', 'نامشخص')[:10]}
💬 تعداد پیام‌ها: {user_data.get('messages', 0)}
🆔 آیدی: `{user.id}`
            """
        else:
            stats_text = "⚠️ اطلاعاتی یافت نشد. /start رو بزن."
        keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]]
        await query.edit_message_text(stats_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== تاس ======
    elif query.data == "dice":
        dice = random.randint(1, 6)
        dice_emojis = {1: "⚀", 2: "⚁", 3: "⚂", 4: "⚃", 5: "⚄", 6: "⚅"}
        text = f"🎲 تاس ریخته شد!\n\nنتیجه: {dice_emojis[dice]} عدد {dice}"

        keyboard = [
            [
                InlineKeyboardButton("🔄 دوباره", callback_data="dice"),
                InlineKeyboardButton("🔙 منو", callback_data="back_to_menu")
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== شانس ======
    elif query.data == "luck":
        luck = random.randint(0, 100)
        if luck > 80:
            message = "🍀 شانست خیلی بالاست! امروز روز توئه!"
        elif luck > 50:
            message = "😊 شانست خوبه! ادامه بده!"
        elif luck > 20:
            message = "😐 شانست متوسطه. تلاش کن!"
        else:
            message = "😔 شانست کمه. ناامید نشو!"

        text = f"🎯 درصد شانس شما: {luck}%\n\n{message}"
        keyboard = [
            [
                InlineKeyboardButton("🔄 دوباره", callback_data="luck"),
                InlineKeyboardButton("🔙 منو", callback_data="back_to_menu")
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== تاریخ و ساعت ======
    elif query.data == "datetime":
        now = datetime.datetime.now()
        persian_date = now.strftime("%Y/%m/%d")
        time = now.strftime("%H:%M:%S")
        weekday = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یکشنبه"][now.weekday()]

        text = f"""
📅 **تاریخ و ساعت:**

📆 تاریخ: {persian_date}
🕐 ساعت: {time}
📌 روز: {weekday}
        """
        keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== جوک ======
    elif query.data == "joke":
        jokes = [
            "😂 یه روز یه مورچه رفت سفر، یه کفش خرید، کفشش تنگ بود، مورچه شد 🐜",
            "😄 معلم: چرا دیر اومدی؟\nشاگرد: چون خواب بودم\nمعلم: پس چرا بیدار نشدی؟\nشاگرد: چون خواب بودم!",
            "🤣 یه بچه فیل به مامانش میگه: چرا من گوشام انقدر بزره؟\nمامان فیل: برای اینکه گوش ندی چی گفتم!",
            "😂 شوهر: زنم گفت برو نون بگیر، نگفت کی بیا!",
            "😆 معلم: اگه ۵ تا سیب داشته باشی و ۳ تاش رو بخوری، چند تا میمونه؟\nدانش‌آموز: ۵ تا! چون نمیدونم کی سیب خریدم که!",
            "🤣 یه مرد رفت دکتر، دکتر گفت: چی شده؟\nمرد: انقدر خندیدم که دلم درد گرفت!",
            "😄 پدر: پسرم چرا نمره ریاضیت ۱۰ شده؟\nپسر: بابا چون معلم ۱۰ تا سوال داد، من همه رو خالی گذاشتم!"
        ]
        text = random.choice(jokes)
        keyboard = [
            [
                InlineKeyboardButton("🔄 جوک بعدی", callback_data="joke"),
                InlineKeyboardButton("🔙 منو", callback_data="back_to_menu")
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== حقایق جالب ======
    elif query.data == "fact":
        facts = [
            "💎 اختاپوس ۳ قلب دارد!",
            "💎 موز یک نوع توت است، ولی توت فرنگی توت نیست!",
            "💎 روز ۱۰ ساعت تقریباً ۱.۴ برابر بلندتر از روز ۲۴ ساعت در مریخ است.",
            "💎 زنبور عسل می‌تواند فضای انسان را تشخیص دهد.",
            "💎 گوجه فرنگی در اصل یک میوه است، نه سبزی.",
            "💎 کرگدن شاخش از مو ساخته شده!",
            "💎 دلفین‌ها با اسم همدیگه رو صدا می‌زنن!",
            "💎 عسل هرگز فاسد نمی‌شود! حتی هزاران سال بعد!"
        ]
        text = random.choice(facts)
        keyboard = [
            [
                InlineKeyboardButton("🔄 بعدی", callback_data="fact"),
                InlineKeyboardButton("🔙 منو", callback_data="back_to_menu")
            ]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== ترجمه ======
    elif query.data == "translate":
        text = """
🌍 **سرویس ترجمه:**

برای ترجمه از دستور زیر استفاده کن:
`/translate [متن]`

مثال: `/translate Hello world`
        """
        keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== تنظیمات ======
    elif query.data == "settings":
        text = """
⚙️ **تنظیمات:**

🔹 زبان: فارسی 🇮🇷
🔹 نوتیفیکیشن: فعیل 🔔
🔹 حالت شب: غیرفعال 🌙

برای تغییر روی گزینه‌ها بزن:
        """
        keyboard = [
            [
                InlineKeyboardButton("🇮🇷 فارسی", callback_data="lang_fa"),
                InlineKeyboardButton("🇬🇧 انگلیسی", callback_data="lang_en")
            ],
            [
                InlineKeyboardButton("🔔 نوتیفیکیشن", callback_data="notif"),
                InlineKeyboardButton("🌙 شب", callback_data="night")
            ],
            [InlineKeyboardButton("🔙 برگشت", callback_data="back_to_menu")]
        ]
        await query.edit_message_text(text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== تغییر زبان ======
    elif query.data.startswith("lang_"):
        lang = "فارسی 🇮🇷" if query.data == "lang_fa" else "English 🇬🇧"
        text = f"✅ زبان به {lang} تغییر کرد!"
        keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="settings")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # ====== بستن ======
    elif query.data == "close":
        await query.delete_message()

    # ====== برگشت به منو ======
    elif query.data == "back_to_menu":
        await query.edit_message_text("📋 منوی اصلی:", reply_markup=main_menu_keyboard())

# ====== مدیریت پیام‌های عادی ======
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id in data:
        data[user_id]["messages"] += 1
        save_data(data)

    keyboard = [
        [
            InlineKeyboardButton("🎲 تاس", callback_data="dice"),
            InlineKeyboardButton("😂 جوک", callback_data="joke")
        ],
        [InlineKeyboardButton("📋 منوی اصلی", callback_data="back_to_menu")]
    ]

    await update.message.reply_text(
        f"پیام شما دریافت شد: «{text}»\n\nیکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ====== اجرای ربات ======
def main():
    print("🤖 ربات در حال راه‌اندازی...")
    app = Application.builder().token(TOKEN).build()

    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu_command))
    app.add_handler(CommandHandler("id", id_command))
    app.add_handler(CommandHandler("echo", echo_command))

    # دکمه‌ها
    app.add_handler(CallbackQueryHandler(button_handler))

    # پیام‌های عادی
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ ربات فعال شد!")
    app.run_polling()

if __name__ == "__main__":
    main()
