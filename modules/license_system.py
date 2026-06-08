import time
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMIN_IDS, OWNER_ID
from utils.helpers import generate_license_code

async def handle_license(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text.startswith("ساخت لایسنس"):
        if user_id not in ADMIN_IDS and user_id != OWNER_ID:
            await message.reply_text("❌ **شما دسترسی ادمین ندارید.**")
            return
        parts = text.split()
        if len(parts) >= 3:
            duration_type = parts[1]
            count = 1
            if len(parts) >= 3 and parts[-1].isdigit():
                count = int(parts[-1])
                duration_type = parts[1]
            
            duration_map = {
                "ماه": 30,
                "ماهانه": 30,
                "روز": 1,
                "20": 20,
                "30": 30,
                "دلخواه": 0
            }
            
            days = duration_map.get(duration_type, 0)
            if days == 0 and duration_type.isdigit():
                days = int(duration_type)

            if days > 0 or duration_type == "دلخواه":
                codes = []
                for _ in range(count):
                    code = generate_license_code()
                    dur = days if days > 0 else 365
                    db.add_license(code, dur, user_id)
                    codes.append(code)
                
                result = f"✅ **{count} کد لایسنس ساخته شد:**\n\n"
                result += "\n".join([f"🔑 `{c}` - {dur} روز" for c in codes])
                await message.reply_text(result)
            else:
                await message.reply_text("❌ نوع دوره نامعتبر. مثال: `ساخت لایسنس ماه 5`")

    elif text.startswith("فعالسازی"):
        code = text.replace("فعالسازی", "").strip()
        if code:
            if db.activate_license(code, user_id):
                await message.reply_text("✅ **لایسنس با موفقیت فعال شد!**")
            else:
                await message.reply_text("❌ **کد لایسنس نامعتبر یا قبلا استفاده شده.**")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def license_handler(client, message):
        await handle_license(client, message, db)
