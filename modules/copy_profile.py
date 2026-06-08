from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
import os

async def handle_copy(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text == "کپی روشن":
        db.set_setting(user_id, "copy_target", "awaiting")
        await message.reply_text("📋 **به پیوی فرد مورد نظر برو و ریپلای بزن.**")
        return

    if text == "کپی خاموش":
        db.set_setting(user_id, "copy_target", None)
        await message.reply_text("📋 **کپی خاموش شد.**")
        return

    if db.get_setting(user_id, "copy_target") == "awaiting" and message.reply_to_message:
        target_user = message.reply_to_message.from_user
        if target_user:
            try:
                full_name = target_user.first_name or ""
                if target_user.last_name:
                    full_name += f" {target_user.last_name}"

                await client.update_profile(
                    first_name=target_user.first_name or "",
                    last_name=target_user.last_name or "",
                )

                try:
                    await client.update_profile(bio=getattr(target_user, 'bio', None) or "")
                except:
                    pass

                try:
                    photos = []
                    async for photo in client.get_chat_photos(target_user.id):
                        photos.append(photo)
                    if photos:
                        photo_path = await client.download_media(photos[0].file_id)
                        await client.set_profile_photo(photo=photo_path)
                        os.remove(photo_path)
                except:
                    pass

                db.set_setting(user_id, "copy_target", None)
                await message.reply_text(f"✅ **کپی شد: {full_name}**")
            except Exception as e:
                await message.reply_text(f"❌ خطا: {str(e)[:80]}")
                db.set_setting(user_id, "copy_target", None)

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def copy_handler(client, message):
        await handle_copy(client, message, db)
