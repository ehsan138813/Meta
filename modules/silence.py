import re
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def handle_silence(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if message.chat.type != ChatType.PRIVATE:
        return

    text = message.text or message.caption or ""

    if text.startswith("سکوت"):
        parts = text.split()
        if len(parts) >= 3 and parts[1] == "تایم":
            try:
                minutes = int(parts[2])
                until = time.time() + (minutes * 60)
                db.add_silence(user_id, message.reply_to_message.from_user.id, until)
                await message.reply_text(f"🔇 **سکوت {minutes} دقیقه‌ای شد.**")
            except:
                await message.reply_text("❌ فرمت اشتباه. مثال: `سکوت تایم 5`")
        else:
            if message.reply_to_message:
                target = message.reply_to_message.from_user
                db.add_silence(user_id, target.id, 0)
                await message.reply_text(f"🔇 **{target.first_name} سکوت دائمی شد.**")

    elif text == "لیست سکوت":
        silences = db.get_silence_list(user_id)
        if silences:
            msg = "🔇 **لیست سکوت:**\n\n"
            for target_id, until in silences:
                try:
                    u = await client.get_users(target_id)
                    name = u.first_name
                except:
                    name = str(target_id)
                if until == 0:
                    msg += f"👤 {name} - دائمی\n"
                else:
                    remaining = int(until - time.time())
                    if remaining > 0:
                        msg += f"👤 {name} - {remaining//60} دقیقه باقی\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("✅ لیست سکوت خالی است.")

    elif text.startswith("حذف سکوت"):
        if message.reply_to_message:
            target = message.reply_to_message.from_user
            db.remove_silence(user_id, target.id)
            await message.reply_text(f"✅ **سکوت {target.first_name} برداشته شد.**")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def silence_handler(client, message):
        await handle_silence(client, message, db)

    @app.on_message(filters.private)
    async def silence_check(client, message):
        if message.from_user and message.from_user.id != (client.get_me()).id:
            if db.is_silenced((client.get_me()).id, message.from_user.id):
                await client.delete_messages(message.chat.id, message.id)
