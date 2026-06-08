from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
import asyncio

GAME_EMOJIS = ["🎮", "🎯", "🎲", "🎰", "🕹️"]
TYPING_EMOJIS = ["⌨️", "✍️", "📝"]
VIDEO_EMOJIS = ["📺", "🎬", "🎥"]
PHOTO_EMOJIS = ["📸", "📷", "🖼️"]
STICKER_EMOJIS = ["🎭", "😎", "🌟"]
MUSIC_EMOJIS = ["🎵", "🎶", "🎧", "🎼"]

async def set_status(client: Client, status_type: str, text: str = ""):
    me = await client.get_me()
    
    if status_type == "playing":
        await client.update_status(emoji_status=None, is_playing=True)
        await client.send_chat_action(me.id, ChatAction.PLAYING)
    elif status_type == "typing":
        await client.send_chat_action(me.id, ChatAction.TYPING)
    elif status_type == "video":
        await client.update_status(emoji_status=None, is_watching=True)
    elif status_type == "photo":
        pass
    elif status_type == "sticker":
        pass
    elif status_type == "music":
        await client.update_status(emoji_status=None, is_listening=True)

async def handle_status_command(client: Client, message: Message, db):
    text = message.text or ""
    
    status_mapping = {
        "بازی": ("playing", "🎮 درحال بازی"),
        "تایپینگ": ("typing", "⌨️ درحال تایپ"),
        "ویدیو": ("video", "📺 درحال ویدیو دیدن"),
        "عکس": ("photo", "📸 درحال عکس دیدن"),
        "استیکر": ("sticker", "🎭 درحال دیدن استیکر"),
        "اهنگ": ("music" or "آهنگ", "🎵 درحال گوش دادن"),
    }

    for keyword, (stype, display) in status_mapping.items():
        if keyword in text:
            await set_status(client, stype, display)
            await message.reply_text(f"✅ **{display}**")
            return True
    return False

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def status_handler(client, message):
        if message.text:
            await handle_status_command(client, message, db)
