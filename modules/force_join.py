from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import UserNotParticipant

async def check_force_join(client: Client, user_id: int, db):
    force_joins = db.get_force_joins(user_id)
    if not force_joins:
        return True
    
    for chat_id, chat_title in force_joins:
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.BANNED]:
                return False
        except:
            return False
    return True

async def handle_force_join(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if message.chat.type != ChatType.PRIVATE:
        return

    if text.startswith("عضویت اجباری"):
        chat_id_str = text.replace("عضویت اجباری", "").strip()
        if chat_id_str:
            try:
                chat_id = int(chat_id_str) if chat_id_str.isdigit() else chat_id_str
                chat = await client.get_chat(chat_id)
                db.add_force_join(user_id, chat.id, chat.title or "بدون نام")
                await message.reply_text(f"✅ **عضویت اجباری در {chat.title} فعال شد.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)}")

    elif text.startswith("حذف عضویت اجباری"):
        chat_id_str = text.replace("حذف عضویت اجباری", "").strip()
        if chat_id_str:
            try:
                chat_id = int(chat_id_str) if chat_id_str.isdigit() else chat_id_str
                db.remove_force_join(user_id, chat_id)
                await message.reply_text("✅ **حذف شد.**")
            except:
                pass

    elif text == "لیست عضویت اجباری":
        joins = db.get_force_joins(user_id)
        if joins:
            msg = "📋 **لیست عضویت اجباری:**\n\n"
            for cid, title in joins:
                msg += f"👥 {title} (`{cid}`)\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("✅ لیست خالی است.")

def register(app: Client, db):
    @app.on_message(filters.private)
    async def force_join_handler(client, message):
        sender = message.from_user
        if sender and sender.id != (await client.get_me()).id:
            if not await check_force_join(client, sender.id, db):
                force_joins = db.get_force_joins((await client.get_me()).id)
                msg = "⚠️ **برای استفاده از ربات باید در کانال/گروه‌های زیر عضو شوید:**\n\n"
                for cid, title in force_joins:
                    msg += f"👥 {title}\n"
                buttons = []
                for cid, title in force_joins:
                    buttons.append([InlineKeyboardButton(f"👥 {title}", url=f"https://t.me/{title}")])
                buttons.append([InlineKeyboardButton("✅ عضو شدم", callback_data="check_join")])
                await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
                return True
        return False

    @app.on_message(filters.text & filters.private)
    async def force_handler(client, message):
        await handle_force_join(client, message, db)
