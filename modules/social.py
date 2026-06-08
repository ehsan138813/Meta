from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatType

async def handle_social(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""
    chat = message.chat

    if text == "تنظیم دشمن":
        db.set_setting(user_id, "social_action", "enemy")
        await message.reply_text("👤 **آیدی عددی فرد مورد نظر رو بفرست:**")
    elif text == "تنظیم دوست":
        db.set_setting(user_id, "social_action", "friend")
        await message.reply_text("👤 **آیدی عددی فرد مورد نظر رو بفرست:**")
    elif text == "تنظیم کراش":
        db.set_setting(user_id, "social_action", "crush")
        await message.reply_text("👤 **آیدی عددی فرد مورد نظر رو بفرست:**")
    elif text == "لیست دشمن":
        enemies = db.get_list(user_id, "enemy")
        if enemies:
            msg = "👤 **لیست دشمن:**\n\n"
            for target_id, txt in enemies:
                try:
                    u = await client.get_users(target_id)
                    name = u.first_name
                except:
                    name = str(target_id)
                msg += f"❌ {name} - {txt or 'بدون متن'}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("✅ لیست دشمن خالی است.")
    elif text == "لیست دوست":
        friends = db.get_list(user_id, "friend")
        if friends:
            msg = "👤 **لیست دوست:**\n\n"
            for target_id, txt in friends:
                try:
                    u = await client.get_users(target_id)
                    name = u.first_name
                except:
                    name = str(target_id)
                msg += f"✅ {name} - {txt or 'بدون متن'}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("✅ لیست دوست خالی است.")
    elif text == "لیست کراش":
        crushes = db.get_list(user_id, "crush")
        if crushes:
            msg = "👤 **لیست کراش:**\n\n"
            for target_id, txt in crushes:
                try:
                    u = await client.get_users(target_id)
                    name = u.first_name
                except:
                    name = str(target_id)
                msg += f"💕 {name} - {txt or 'بدون متن'}\n"
            await message.reply_text(msg)
        else:
            await message.reply_text("✅ لیست کراش خالی است.")
    elif text.startswith("حذف دشمن") or text.startswith("حذف دوست") or text.startswith("حذف کراش"):
        parts = text.split()
        if len(parts) >= 2:
            action = parts[0]
            target_id = parts[1]
            try:
                target_id = int(target_id)
                list_type = {"حذف‌دشمن": "enemy", "حذف‌دوست": "friend", "حذف‌کراش": "crush"}
                type_map = {"حذف‌دشمن": "enemy", "حذف‌دوست": "friend", "حذف‌کراش": "crush"}
                action_clean = action.replace(" ", "")
                if action_clean in type_map:
                    getattr(db, f"remove_{type_map[action_clean]}") (user_id, target_id)
                    await message.reply_text(f"✅ **با موفقیت حذف شد.**")
            except:
                pass
    else:
        social_action = db.get_setting(user_id, "social_action")
        if social_action and text.isdigit():
            target_id = int(text)
            if social_action == "enemy":
                db.add_enemy(user_id, target_id)
            elif social_action == "friend":
                db.add_friend(user_id, target_id)
            elif social_action == "crush":
                db.add_crush(user_id, target_id)
            db.set_setting(user_id, "social_action", None)
            await message.reply_text(f"✅ **تنظیم شد.**")

    # Enemy text trigger
    if message.chat.type == ChatType.PRIVATE:
        sender = message.from_user
        if sender and sender.id != user_id:
            enemies = db.get_list(user_id, "enemy")
            for e_id, txt in enemies:
                if e_id == sender.id and txt:
                    await message.reply_text(txt)

SOCIAL_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❌ تنظیم دشمن", callback_data="social_enemy"),
     InlineKeyboardButton("✅ تنظیم دوست", callback_data="social_friend")],
    [InlineKeyboardButton("💕 تنظیم کراش", callback_data="social_crush"),
     InlineKeyboardButton("📋 لیست دشمن", callback_data="list_enemy")],
    [InlineKeyboardButton("📋 لیست دوست", callback_data="list_friend"),
     InlineKeyboardButton("📋 لیست کراش", callback_data="list_crush")],
    [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")],
])

def register(app: Client, db):
    pass
