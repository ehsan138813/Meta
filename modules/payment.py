from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

async def handle_payment(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    text = message.text or ""

    if text.startswith("شماره کارت"):
        card = text.replace("شماره کارت", "").strip()
        if card:
            db.set_setting(user_id, "card_number", card)
            await message.reply_text(f"✅ **شماره کارت ثبت شد:** {card}")

    elif text == "درآمد" or text == "درامد":
        payments = db.get_payments(user_id)
        if payments:
            msg = "💰 **درآمدهای شما:**\n\n"
            total = 0
            for p in payments:
                status_emoji = "✅" if p[5] == "confirmed" else "⏳" if p[5] == "pending" else "❌"
                msg += f"{status_emoji} مبلغ: {p[3]} - وضعیت: {p[5]}\n"
                if p[5] == "confirmed":
                    total += p[3] if p[3] else 0
            msg += f"\n💵 **مجموع: {total}**"
            await message.reply_text(msg)
        else:
            await message.reply_text("📭 هیچ تراکنشی ثبت نشده.")

    # Handle receipt photo
    if message.photo and message.caption and "رسید" in (message.caption or ""):
        sender_id = message.from_user.id
        card = db.get_setting(user_id, "card_number", "ثبت نشده")
        photo = message.photo.file_id
        pay_id = db.add_payment(user_id, card, 0, photo)
        
        await message.reply_text("✅ **رسید پرداخت ثبت شد. در انتظار تایید...**")
        
        admin_id = db.get_setting(user_id, "admin_id", user_id)
        try:
            admin_user = await client.get_users(admin_id)
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ تایید", callback_data=f"pay_confirm_{pay_id}"),
                 InlineKeyboardButton("❌ رد", callback_data=f"pay_reject_{pay_id}")]
            ])
            await client.send_photo(
                admin_id, photo,
                caption=f"💳 **درخواست پرداخت جدید**\n👤 کاربر: {user_id}\n💰 مبلغ: مشخص نشده\n🆔 شناسه: {pay_id}",
                reply_markup=buttons
            )
        except:
            pass

PAY_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("💳 ثبت شماره کارت", callback_data="pay_card")],
    [InlineKeyboardButton("💰 درآمدها", callback_data="pay_income")],
    [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")],
])

async def handle_payment_callback(client: Client, callback, db):
    data = callback.data
    if data.startswith("pay_confirm_"):
        pay_id = int(data.split("_")[2])
        db.update_payment_status(pay_id, "confirmed")
        await callback.message.edit_caption(callback.message.caption + "\n\n✅ **تایید شد**")
        await callback.answer("✅ پرداخت تایید شد")
    elif data.startswith("pay_reject_"):
        pay_id = int(data.split("_")[2])
        db.update_payment_status(pay_id, "rejected")
        await callback.message.edit_caption(callback.message.caption + "\n\n❌ **رد شد**")
        await callback.answer("❌ پرداخت رد شد")

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def payment_handler(client, message):
        await handle_payment(client, message, db)
