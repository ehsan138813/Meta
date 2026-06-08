from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio

async def handle_repeat(client: Client, message: Message, db):
    text = message.text or ""
    if not message.reply_to_message:
        return

    if text.startswith("تکرار"):
        parts = text.split()
        if len(parts) >= 2:
            try:
                count = int(parts[1])
                if 1 <= count <= 100:
                    for i in range(count):
                        await message.reply_to_message.copy(message.chat.id)
                        await asyncio.sleep(0.3)
                    await message.reply_text(f"✅ **{count} بار تکرار شد.**")
                else:
                    await message.reply_text("❌ عدد باید بین 1 تا 100 باشد.")
            except ValueError:
                await message.reply_text("❌ عدد معتبر وارد کن.")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def repeat_handler(client, message):
        await handle_repeat(client, message, db)
