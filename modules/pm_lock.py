from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

async def handle_pmlock(client: Client, message: Message, db):
    if message.chat.type != ChatType.PRIVATE:
        return
    user_id = (client.get_me()).id
    if db.get_panel_state(user_id, "pm_lock"):
        sender = message.from_user
        if sender and sender.id != user_id:
            if not db.is_silenced(user_id, sender.id):
                await client.delete_messages(message.chat.id, message.id)
                await client.send_message(sender.id, "🔒 **پیوی قفل است!** شما اجازه پیام دادن ندارید.")

def register(app: Client, db):
    @app.on_message(filters.private)
    async def pmlock_handler(client, message):
        await handle_pmlock(client, message, db)
