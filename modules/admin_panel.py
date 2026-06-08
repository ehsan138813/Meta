from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS, OWNER_ID

async def handle_admin(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""
    me = await client.get_me()

    if user_id not in ADMIN_IDS and user_id != OWNER_ID:
        return

    if text.startswith("غیرفعال"):
        parts = text.split()
        if len(parts) >= 2:
            target = parts[-1]
            try:
                target_id = int(target)
                db.deactivate_user(target_id)
                await message.reply_text(f"✅ **کاربر {target_id} غیرفعال شد.**")
            except:
                await message.reply_text("❌ آیدی نامعتبر.")

    elif text.startswith("حذف اکانت"):
        parts = text.split()
        if len(parts) >= 2:
            target = parts[-1]
            try:
                target_id = int(target)
                db.delete_user(target_id)
                await message.reply_text(f"✅ **اکانت {target_id} حذف شد.**")
            except:
                await message.reply_text("❌ آیدی نامعتبر.")

    elif text == "لیست کاربران" or text == "کاربران":
        users = db.get_all_users()
        if users:
            msg = "👥 **لیست کاربران:**\n\n"
            for uid, phone, active in users:
                status = "✅ فعال" if active else "❌ غیرفعال"
                msg += f"👤 {uid} - {phone} - {status}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("📭 هیچ کاربری ثبت نشده.")

    elif text == "آمار" or text == "amar":
        users = db.get_all_users()
        active = sum(1 for u in users if u[2])
        inactive = sum(1 for u in users if not u[2])
        await message.reply_text(
            f"📊 **آمار ربات:**\n\n"
            f"👥 کل کاربران: {len(users)}\n"
            f"✅ فعال: {active}\n"
            f"❌ غیرفعال: {inactive}"
        )

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def admin_handler(client, message):
        await handle_admin(client, message, db)
