from pyrogram import Client, filters
from pyrogram.types import Message
from googletrans import Translator
from config import SUPPORTED_LANGUAGES

translator = Translator()

LANG_MAP = {
    "en": "english",
    "ar": "arabic",
    "zh-cn": "chinese",
    "ru": "russian"
}

async def handle_translate(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    if not db.is_silenced(user_id, user_id):
        if db.get_panel_state(user_id, "translator"):
            if message.text:
                for lang_code, lang_name in SUPPORTED_LANGUAGES.items():
                    if lang_code == "fa":
                        continue
                    try:
                        translated = translator.translate(message.text, dest=lang_code)
                        await message.reply_text(
                            f"🌐 **{lang_name}**\n\n{translated.text}",
                            reply_to_message_id=message.id
                        )
                    except:
                        pass

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def translate_handler(client, message):
        await handle_translate(client, message, db)
