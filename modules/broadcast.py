import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

BROADCAST_RUNNING = {}

async def handle_broadcast(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text.startswith("افزودن گروه تبلیغ"):
        group_id_str = text.replace("افزودن گروه تبلیغ", "").strip()
        if group_id_str:
            try:
                chat_id = int(group_id_str) if group_id_str.isdigit() else group_id_str
                chat = await client.get_chat(chat_id)
                db.add_broadcast_group(user_id, chat.id, chat.title or "بدون نام")
                await message.reply_text(f"✅ **گروه {chat.title} به لیست تبلیغ اضافه شد.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)}")

    elif text.startswith("حذف گروه تبلیغ"):
        group_id_str = text.replace("حذف گروه تبلیغ", "").strip()
        if group_id_str:
            try:
                chat_id = int(group_id_str) if group_id_str.isdigit() else group_id_str
                db.remove_broadcast_group(user_id, chat_id)
                await message.reply_text("✅ **حذف شد.**")
            except:
                pass

    elif text == "لیست گروه‌های تبلیغ":
        groups = db.get_broadcast_groups(user_id)
        if groups:
            msg = "📢 **گروه‌های تبلیغ:**\n\n"
            for gid, title in groups:
                msg += f"👥 {title} (`{gid}`)\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("📭 هیچ گروهی ثبت نشده.")

    elif text.startswith("شروع تبلیغ"):
        if user_id in BROADCAST_RUNNING and BROADCAST_RUNNING[user_id]:
            await message.reply_text("⚠️ **تبلیغ در حال اجراست!**")
            return
        
        reply = message.reply_to_message
        if not reply:
            await message.reply_text("❌ روی یک پیام ریپلای کن.")
            return
        
        groups = db.get_broadcast_groups(user_id)
        if not groups:
            await message.reply_text("❌ هیچ گروهی برای تبلیغ ثبت نشده.")
            return
        
        BROADCAST_RUNNING[user_id] = True
        await message.reply_text(f"📢 **تبلیغ شروع شد به {len(groups)} گروه...**")
        
        try:
            while BROADCAST_RUNNING.get(user_id):
                for gid, title in groups:
                    if not BROADCAST_RUNNING.get(user_id):
                        break
                    try:
                        await reply.copy(gid)
                        await asyncio.sleep(5)
                    except:
                        continue
                if BROADCAST_RUNNING.get(user_id):
                    await asyncio.sleep(1)
        except:
            pass
        
        BROADCAST_RUNNING[user_id] = False
        await message.reply_text("✅ **تبلیغ متوقف شد.**")

    elif text == "توقف تبلیغ":
        if user_id in BROADCAST_RUNNING:
            BROADCAST_RUNNING[user_id] = False
            await message.reply_text("⏹️ **تبلیغ متوقف شد.**")
        else:
            await message.reply_text("❌ تبلیغی در حال اجرا نیست.")

BROAD_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("➕ افزودن گروه", callback_data="broad_add")],
    [InlineKeyboardButton("📋 لیست گروه‌ها", callback_data="broad_list")],
    [InlineKeyboardButton("▶️ شروع تبلیغ", callback_data="broad_start")],
    [InlineKeyboardButton("⏹️ توقف تبلیغ", callback_data="broad_stop")],
    [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")],
])

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def broadcast_handler(client, message):
        await handle_broadcast(client, message, db)
