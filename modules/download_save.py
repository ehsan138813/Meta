from pyrogram import Client, filters
from pyrogram.types import Message
import os

async def handle_download_save(client: Client, message: Message, db):
    if not message.reply_to_message:
        return

    text = message.text or ""
    reply = message.reply_to_message

    if text == "دانلود":
        if reply.document or reply.video or reply.audio or reply.photo or reply.voice or reply.video_note:
            file_path = await reply.download()
            await message.reply_document(file_path, caption="📥 **رسانه دانلود شد**")
            os.remove(file_path)

    elif text == "ذخیره" or text == "ذخیر":
        await reply.forward("me")
        await message.reply_text("✅ **در سیو مسیج ذخیره شد.**")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def download_handler(client, message):
        await handle_download_save(client, message, db)
