from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def handle_group_management(client: Client, message: Message, db):
    text = message.text or ""
    user_id = message.from_user.id if message.from_user else message.sender_chat.id

    if text.startswith("ساخت گروه"):
        name = text.replace("ساخت گروه", "").strip()
        if name:
            try:
                group = await client.create_group(name, (await client.get_me()).id)
                await message.reply_text(f"✅ **گروه {name} ساخته شد.**\nآیدی: `{group.id}`")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)}")

    elif text.startswith("ساخت کانال"):
        name = text.replace("ساخت کانال", "").strip()
        if name:
            try:
                channel = await client.create_channel(name, "")
                await message.reply_text(f"✅ **کانال {name} ساخته شد.**\nآیدی: `{channel.id}`")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)}")

    elif text.startswith("حذف گروه") or text.startswith("حذف کانال"):
        parts = text.split()
        if len(parts) >= 2:
            identifier = parts[-1]
            try:
                chat_id = int(identifier) if identifier.isdigit() else identifier
                await client.leave_chat(chat_id)
                await message.reply_text(f"✅ **خروج از چت انجام شد.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)}")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def group_handler(client, message):
        await handle_group_management(client, message, db)
