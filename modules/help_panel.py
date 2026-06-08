from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.helpers import build_help_keyboard, HELP_TEXTS

HELP_MENU = build_help_keyboard()

async def show_help(client: Client, message: Message):
    await message.reply_text(
        "❓ **راهنمای ربات**\n\n"
        "روی هر گزینه کلیک کن تا توضیحات اون رو ببینی:\n"
        "همچنین می‌تونی بنویسی `راهنما` یا `help`",
        reply_markup=HELP_MENU
    )

async def handle_help_callback(client: Client, callback: CallbackQuery, db):
    data = callback.data

    if data == "help_menu":
        await callback.message.edit_text(
            "❓ **راهنمای ربات**\n\nروی هر گزینه کلیک کن:",
            reply_markup=HELP_MENU
        )
    elif data.startswith("help_"):
        key = data.replace("help_", "")
        text = HELP_TEXTS.get(key, "❌ راهنمایی برای این بخش یافت نشد.")
        await callback.message.edit_text(text, reply_markup=HELP_MENU)
    
    await callback.answer()

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def help_handler(client, message):
        text = message.text or ""
        if text in ["راهنما", "help", "Help", "کمک"]:
            await show_help(client, message)
