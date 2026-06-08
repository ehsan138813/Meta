import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import time

async def handle_timed_messages(client: Client, message: Message, db):
    text = message.text or ""
    user_id = message.from_user.id if message.from_user else message.sender_chat.id

    if text.startswith("تایم ") or text.startswith("زمان‌دار "):
        parts = text.split()
        if len(parts) >= 3:
            try:
                seconds = int(parts[1])
                msg_text = " ".join(parts[2:])
                await message.reply_text(f"⏰ **پیام زمان‌دار در {seconds} ثانیه ارسال میشه.**")
                await asyncio.sleep(seconds)
                await client.send_message("me", f"⏰ **پیام زمان‌دار:**\n\n{msg_text}")
                await client.send_message(message.chat.id, f"⏰ **پیام ارسال شد به سیو مسیج.**")
            except ValueError:
                await message.reply_text("❌ فرمت: `تایم 10 متن تو`")

    if text == "ذخیره پیام" and message.reply_to_message:
        await message.reply_to_message.forward("me")
        await message.reply_text("✅ **در سیو مسیج ذخیره شد.**")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def timed_handler(client, message):
        await handle_timed_messages(client, message, db)
