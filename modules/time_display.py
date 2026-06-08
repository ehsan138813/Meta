from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import get_time_styles

async def handle_time_display(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text == "🕐 استایل ساعت":
        styles = get_time_styles()
        buttons = []
        for name, value in styles.items():
            buttons.append([InlineKeyboardButton(f"🕐 {value}", callback_data=f"set_time_{name}")])
        buttons.append([InlineKeyboardButton("🔙 بستن", callback_data="close_panel")])
        await message.reply_text("**🕐 استایل ساعت را انتخاب کنید:**", reply_markup=InlineKeyboardMarkup(buttons))
        return True

    if db.get_panel_state(user_id, "time_display"):
        styles = get_time_styles()
        current_style = db.get_setting(user_id, "time_style", "clock1")
        time_str = styles.get(current_style, styles["clock1"])
        try:
            me = await client.get_me()
            name = getattr(me, 'first_name', None) or ""
            await client.update_profile(bio=f"{name} [{time_str}]")
        except:
            pass
    return False

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def time_handler(client, message):
        await handle_time_display(client, message, db)
