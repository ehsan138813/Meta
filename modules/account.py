import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import PeerIdInvalid

async def handle_account(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text.startswith("تنظیم نام"):
        name = text.replace("تنظیم نام", "").strip()
        if name:
            try:
                me = await client.get_me()
                await client.update_profile(first_name=name, last_name=getattr(me, 'last_name', None) or "")
                await message.reply_text(f"✅ **نام به {name} تغییر یافت.**")
            except Exception as e:
                await message.reply_text(f"❌ ربات‌ها نمی‌توانند نام را تغییر دهند: {str(e)[:50]}")

    elif text.startswith("تنظیم نام خانوادگی"):
        lname = text.replace("تنظیم نام خانوادگی", "").strip()
        if lname:
            try:
                me = await client.get_me()
                await client.update_profile(first_name=getattr(me, 'first_name', None) or "", last_name=lname)
                await message.reply_text(f"✅ **نام خانوادگی به {lname} تغییر یافت.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)[:50]}")

    elif text.startswith("تنظیم بیو"):
        bio = text.replace("تنظیم بیو", "").strip()
        if bio:
            try:
                await client.update_profile(bio=bio)
                await message.reply_text(f"✅ **بیو تنظیم شد.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)[:50]}")

    elif text == "تنظیم عکس" and message.reply_to_message:
        if message.reply_to_message.photo:
            try:
                photo_path = await message.reply_to_message.download()
                await client.set_profile_photo(photo=photo_path)
                os.remove(photo_path)
                await message.reply_text("✅ **عکس پروفایل تنظیم شد.**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)[:50]}")

    elif text == "حذف عکس پروفایل":
        try:
            photos = []
            async for photo in client.get_chat_photos("me"):
                photos.append(photo)
            if photos:
                await client.delete_profile_photos(photos[0].file_id)
                await message.reply_text("✅ **عکس پروفایل حذف شد.**")
            else:
                await message.reply_text("❌ عکسی وجود ندارد.")
        except Exception as e:
            await message.reply_text(f"❌ خطا: {str(e)[:50]}")

    elif text == "حذف تمامی عکس ها":
        try:
            photos = []
            async for photo in client.get_chat_photos("me"):
                photos.append(photo)
            if photos:
                await client.delete_profile_photos([p.file_id for p in photos])
                await message.reply_text(f"✅ **{len(photos)} عکس حذف شد.**")
            else:
                await message.reply_text("❌ عکسی وجود ندارد.")
        except Exception as e:
            await message.reply_text(f"❌ خطا: {str(e)[:50]}")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def account_handler(client, message):
        await handle_account(client, message, db)
