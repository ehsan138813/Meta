from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

SECRETARY_COUNT = {}

async def handle_secretary(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text.startswith("تنظیم منشی"):
        parts = text.split(maxsplit=1)
        if len(parts) >= 2:
            rest = parts[1]
            if rest.startswith("1"):
                msg = rest[1:].strip()
                if msg:
                    db.set_secretary(user_id, 1, msg)
                    await message.reply_text("✅ **پیام اول منشی تنظیم شد.**")
            elif rest.startswith("2"):
                msg = rest[1:].strip()
                if msg:
                    db.set_secretary(user_id, 2, msg)
                    await message.reply_text("✅ **پیام دوم منشی تنظیم شد.**")
            elif rest.startswith("3"):
                msg = rest[1:].strip()
                if msg:
                    db.set_secretary(user_id, 3, msg)
                    await message.reply_text("✅ **پیام سوم منشی تنظیم شد.**")

    elif text == "دیدن منشی":
        msgs = db.get_secretary(user_id)
        if msgs:
            msg = "🤖 **پیام‌های منشی:**\n\n"
            for order, txt in msgs:
                msg += f"{order}. {txt}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("📭 منشی تنظیم نشده.")

    # Auto-reply for new users
    if message.chat.type == ChatType.PRIVATE:
        sender = message.from_user
        if sender and sender.id != user_id:
            if sender.id not in SECRETARY_COUNT:
                SECRETARY_COUNT[sender.id] = 0
            SECRETARY_COUNT[sender.id] += 1
            
            msgs = db.get_secretary(user_id)
            if msgs:
                for order, txt in msgs:
                    if SECRETARY_COUNT[sender.id] == order:
                        await message.reply_text(txt)
                        break

SEC_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("📝 تنظیم منشی ۱", callback_data="sec_set_1")],
    [InlineKeyboardButton("📝 تنظیم منشی ۲", callback_data="sec_set_2")],
    [InlineKeyboardButton("📝 تنظیم منشی ۳", callback_data="sec_set_3")],
    [InlineKeyboardButton("📋 دیدن منشی", callback_data="sec_view")],
    [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")],
])

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def secretary_handler(client, message):
        await handle_secretary(client, message, db)
