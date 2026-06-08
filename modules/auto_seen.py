from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def handle_auto_seen(client: Client, message: Message, db):
    me = await client.get_me()
    if message.outgoing:
        return
    if message.chat.type == ChatType.PRIVATE:
        user_id = me.id
        if db.get_panel_state(user_id, "auto_seen"):
            try:
                await client.read_chat_history(message.chat.id)
            except:
                pass

def register(app: Client, db):
    @app.on_message(filters.private & ~filters.outgoing)
    async def seen_handler(client, message):
        await handle_auto_seen(client, message, db)
