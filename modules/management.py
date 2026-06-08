from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
import asyncio

async def handle_management(client: Client, message: Message, db):
    text = message.text or ""
    chat = message.chat

    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    if text == "تگ همه" or text == "@all" or text == "@everyone":
        members = []
        async for member in client.get_chat_members(chat.id):
            if not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)
        
        mentions = " ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in members])
        batch_size = 50
        for i in range(0, len(members), batch_size):
            batch = members[i:i+batch_size]
            chunk = " ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in batch])
            await message.reply_text(f"📢 **تگ همه:**\n{chunk}")
            await asyncio.sleep(1)

    elif text == "تگ ادمین" or text == "@admin":
        admins = []
        async for member in client.get_chat_members(chat.id, filter="administrators"):
            if not member.user.is_bot:
                admins.append(member.user)
        
        mentions = " ".join([f"[{u.first_name}](tg://user?id={u.id})" for u in admins])
        await message.reply_text(f"👮 **ادمین‌ها:**\n{mentions}")

    elif text == "حذف چت دوطرفه":
        if chat.type == ChatType.PRIVATE:
            await client.delete_user_history(chat.id)
            await message.reply_text("✅ **چت دوطرفه حذف شد.**")

    elif text == "پاک کردن" or text == "حذف پیام من":
        if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            async for msg in client.get_chat_history(chat.id, limit=100):
                if msg.from_user and msg.from_user.id == (await client.get_me()).id:
                    try:
                        await msg.delete()
                        await asyncio.sleep(0.5)
                    except:
                        pass
            await message.reply_text("✅ **پیام‌های شما حذف شد.**")

def register(app: Client, db):
    @app.on_message(filters.text)
    async def management_handler(client, message):
        await handle_management(client, message, db)
