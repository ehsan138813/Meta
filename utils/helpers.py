import time
import random
import string
import asyncio
from datetime import datetime
import pytz
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import TIMEZONE

def get_iran_time():
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    return now

def get_time_styles():
    now = get_iran_time()
    styles = {
        "clock1": now.strftime("%H:%M"),
        "clock2": now.strftime("%H:%M:%S"),
        "clock3": now.strftime("%I:%M %p"),
        "clock4": now.strftime("%H:%M - %Y/%m/%d"),
        "clock5": now.strftime("%d %B %Y - %H:%M"),
    }
    return styles

def generate_license_code():
    chars = string.ascii_uppercase + string.digits
    return "SELF-" + "-".join(''.join(random.choices(chars, k=4)) for _ in range(4))

def build_panel_keyboard(modules_state, user_id):
    buttons = []
    row = []
    for module, emoji_on, emoji_off, label in modules_state["order"]:
        state = modules_state["states"].get(module, 0)
        emoji = emoji_on if state else emoji_off
        btn = InlineKeyboardButton(f"{emoji} {label}", callback_data=f"toggle_{module}")
        row.append(btn)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("📋 بستن پنل", callback_data="close_panel")])
    return InlineKeyboardMarkup(buttons)

def get_panel_modules():
    return {
        "translator": {"emoji_on": "✅", "emoji_off": "❌", "label": "مترجم"},
        "pm_lock": {"emoji_on": "🔒", "emoji_off": "🔓", "label": "قفل پیوی"},
        "auto_seen": {"emoji_on": "👁️", "emoji_off": "🚫", "label": "خودکار دیده"},
        "copy_mode": {"emoji_on": "📋", "emoji_off": "🚫", "label": "کپی"},
        "silence": {"emoji_on": "🔇", "emoji_off": "🔊", "label": "سکوت"},
        "time_display": {"emoji_on": "🕐", "emoji_off": "🚫", "label": "ساعت"},
        "bold_mode": {"emoji_on": "𝐁", "emoji_off": "🚫", "label": "بولد"},
        "quote_mode": {"emoji_on": "💬", "emoji_off": "🚫", "label": "نقل قول"},
        "underline_mode": {"emoji_on": "𝐔", "emoji_off": "🚫", "label": "زیر خط"},
    }

def build_help_keyboard():
    buttons = [
        [InlineKeyboardButton("🔰 راهنمای پنل", callback_data="help_panel")],
        [InlineKeyboardButton("🌐 مترجم", callback_data="help_translator")],
        [InlineKeyboardButton("🔒 قفل پیوی", callback_data="help_pmlock")],
        [InlineKeyboardButton("🔇 سکوت", callback_data="help_silence")],
        [InlineKeyboardButton("🎭 وضعیت", callback_data="help_status")],
        [InlineKeyboardButton("📋 کپی", callback_data="help_copy")],
        [InlineKeyboardButton("🎨 انیمیشن", callback_data="help_animation")],
        [InlineKeyboardButton("❤️ لیست اجتماعی", callback_data="help_social")],
        [InlineKeyboardButton("⚙️ تنظیمات اکانت", callback_data="help_account")],
        [InlineKeyboardButton("💳 پرداخت", callback_data="help_payment")],
        [InlineKeyboardButton("📢 تبلیغات", callback_data="help_broadcast")],
        [InlineKeyboardButton("🤖 منشی", callback_data="help_secretary")],
        [InlineKeyboardButton("🔐 لایسنس", callback_data="help_license")],
        [InlineKeyboardButton("📊 مدیریت", callback_data="help_management")],
        [InlineKeyboardButton("👤 ادمین", callback_data="help_admin")],
        [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")]
    ]
    return InlineKeyboardMarkup(buttons)

def build_main_menu():
    buttons = [
        [InlineKeyboardButton("📋 پنل اصلی", callback_data="main_panel")],
        [InlineKeyboardButton("🎨 انیمیشن", callback_data="anim_menu")],
        [InlineKeyboardButton("❤️ لیست اجتماعی", callback_data="social_menu")],
        [InlineKeyboardButton("🤖 منشی", callback_data="sec_menu")],
        [InlineKeyboardButton("📢 تبلیغات", callback_data="broad_menu")],
        [InlineKeyboardButton("💳 پرداخت", callback_data="pay_menu")],
        [InlineKeyboardButton("🔐 اطلاعات حساب", callback_data="acc_menu")],
        [InlineKeyboardButton("❓ راهنما", callback_data="help_menu")],
        [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")]
    ]
    return InlineKeyboardMarkup(buttons)

HELP_TEXTS = {
    "panel": "📋 **پنل اصلی**\nاز این پنل می‌تونی همه قابلیت‌ها رو روشن/خاموش کنی.",
    "translator": "🌐 **مترجم**\nمتون فارسی رو به انگلیسی، عربی، چینی و روسی ترجمه کن.",
    "pmlock": "🔒 **قفل پیوی**\nوقتی روشن باشه، هیچکس نمیتونه بهت پیام بده.",
    "silence": "🔇 **سکوت**\nبا ریپلای روی پیام کسی و زدن 'سکوت'، اون شخص سکوت میشه.\n`سکوت تایم 5` = سکوت ۵ دقیقه‌ای\n`سکوت` = سکوت دائمی",
    "status": "🎭 **وضعیت**\n`درحال بازی` | `درحال تایپینگ` | `درحال ویدیو دیدن` | `درحال گوش دادن`",
    "copy": "📋 **کپی**\nبا زدن 'کپی روشن' پروفایل فرد مقابل کپی میشه روی اکانتت.",
    "animation": "🎨 **انیمیشن**\nانیمیشن‌های مختلف: قلب ❤️ | موج 🌊 | ضربان 💓 | ماه 🌙 | ساعت 🕐 | رعد ⚡ | زمین 🌍",
    "social": "❤️ **لیست اجتماعی**\nدوست، دشمن و کراش خودتو تنظیم کن.",
    "account": "⚙️ **تنظیمات اکانت**\nتغییر نام، نام‌خانوادگی، بیو، عکس پروفایل.",
    "payment": "💳 **پرداخت**\nشماره کارتت رو ثبت کن و رسید پرداخت رو ارسال کن.",
    "broadcast": "📢 **تبلیغات**\nارسال خودکار متن/عکس به گروه‌های انتخاب شده.",
    "secretary": "🤖 **منشی**\nپیام‌های خوش‌آمدگویی تنظیم کن (تا ۳ تا).",
    "license": "🔐 **لایسنس**\nبرای استفاده از ربات باید کد لایسنس معتبر داشته باشی.",
    "management": "📊 **مدیریت**\nتگ همه | تگ ادمین‌ها | حذف چت دوطرفه | حذف پیام خود در گروه",
    "admin": "👤 **ادمین**\nساخت لایسنس | غیرفعال کردن کاربر | حذف اکانت | مشاهده آمار",
}
