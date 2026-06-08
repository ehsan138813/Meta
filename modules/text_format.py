from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from pyrogram import enums

async def handle_text_format(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or message.caption or ""

    if message.text and not message.text.startswith("/"):
        if db.get_panel_state(user_id, "bold_mode"):
            await message.edit_text(f"**{text}**")
        elif db.get_panel_state(user_id, "quote_mode"):
            await message.edit_text(f"> {text}")
        elif db.get_panel_state(user_id, "underline_mode"):
            await message.edit_text(f"<u>{text}</u>")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private & ~filters.command(""))
    async def format_handler(client, message):
        await handle_text_format(client, message, db)
