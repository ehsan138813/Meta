import sys
import os
import asyncio
import logging
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH, ADMIN_IDS, OWNER_ID

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import Database
from modules import (
    translator, pm_lock, silence, auto_seen, time_display, text_format,
    status, management, download_save, repeat, copy_profile, animations,
    social, account, group_management, force_join, help_panel,
    timed_messages, license_system, admin_panel, secretary, payment,
    broadcast, panel_handler
)

db = Database()

MODULES = [
    translator, pm_lock, silence, auto_seen, time_display, text_format,
    status, management, download_save, repeat, copy_profile,
    social, account, group_management, force_join, help_panel,
    timed_messages, license_system, admin_panel, secretary, payment,
    broadcast, panel_handler
]

async def main():
    logger.info("Starting Telegram Self Bot...")
    
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN must be set in config.py!")
        return
    
    app = Client(
        "self_bot_session",
        bot_token=BOT_TOKEN,
        api_id=API_ID or 6,
        api_hash=API_HASH or "eb06d4abfb49dc3eeb1aeb98ae0f579e",
        workdir=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Register all module handlers
    for module in MODULES:
        try:
            module.register(app, db)
            logger.info(f"Module {module.__name__} registered")
        except Exception as e:
            logger.warning(f"Module {module.__name__} registration failed: {e}")
    
    @app.on_message()
    async def license_check(client, message):
        if not message.from_user:
            return
        user_id = message.from_user.id
        me = await client.get_me()
        if user_id == me.id:
            return
        if user_id == OWNER_ID or user_id in ADMIN_IDS:
            return
        if not db.check_license(user_id):
            if message.chat.type.name == "PRIVATE":
                await message.reply_text(
                    "🔐 **شما لایسنس معتبر ندارید!**\n\n"
                    "برای استفاده از ربات باید کد لایسنس داشته باشید.\n"
                    "برای خرید با ادمین تماس بگیرید.\n\n"
                    "`فعالسازی [کد لایسنس]`"
                )

    @app.on_message(filters.command("start", prefixes=["/", "."]))
    async def start_command(client, message):
        await message.reply_text(
            "🤖 **به سلف بات خوش آمدید!**\n\n"
            "برای دیدن منو بنویس: `پنل`\n"
            "برای راهنما بنویس: `راهنما`\n"
            "برای منوی اصلی بنویس: `منو`\n\n"
            "**قابلیت‌ها:**\n"
            "🌐 مترجم | 🔒 قفل پیوی | 🔇 سکوت\n"
            "🎨 انیمیشن | ❤️ اجتماعی | 📢 تبلیغات\n"
            "🤖 منشی | 💳 پرداخت | و بیش از ۲۰ قابلیت دیگر!"
        )

    await app.run()

if __name__ == "__main__":
    asyncio.run(main())
