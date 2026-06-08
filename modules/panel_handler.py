from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import build_panel_keyboard, get_panel_modules, build_main_menu, get_time_styles
from database.models import Database
from modules.animations import ANIM_MENU, handle_animation_callback
from modules.social import SOCIAL_MENU
from modules.secretary import SEC_MENU
from modules.broadcast import BROAD_MENU
from modules.payment import PAY_MENU, handle_payment_callback
from modules.help_panel import handle_help_callback
from modules.force_join import check_force_join
import asyncio

PANEL_MESSAGE = {}

async def show_panel(client: Client, message: Message, db):
    user_id = message.from_user.id if message.from_user else message.sender_chat.id
    modules = get_panel_modules()
    
    states = {}
    for mod_name in modules:
        states[mod_name] = db.get_panel_state(user_id, mod_name)
    
    modules_state = {
        "order": [(name, modules[name]["emoji_on"], modules[name]["emoji_off"], modules[name]["label"]) 
                  for name in modules],
        "states": states
    }
    
    keyboard = build_panel_keyboard(modules_state, user_id)
    msg = await message.reply_text(
        "📋 **پنل مدیریت ربات**\n"
        "هر قابلیت رو با کلیک روشن/خاموش کن:\n"
        "🟢 = روشن | 🔴 = خاموش",
        reply_markup=keyboard
    )
    PANEL_MESSAGE[user_id] = msg.id

async def toggle_module(client: Client, callback: CallbackQuery, db):
    user_id = callback.from_user.id
    module = callback.data.replace("toggle_", "")
    
    state = db.toggle_panel_state(user_id, module)
    modules = get_panel_modules()
    
    if module in modules:
        emoji = modules[module]["emoji_on"] if state else modules[module]["emoji_off"]
        await callback.answer(f"{emoji} {modules[module]['label']}: {'روشن' if state else 'خاموش'}")
    
    states = {}
    for mod_name in modules:
        states[mod_name] = db.get_panel_state(user_id, mod_name)
    
    modules_state = {
        "order": [(name, modules[name]["emoji_on"], modules[name]["emoji_off"], modules[name]["label"]) 
                  for name in modules],
        "states": states
    }
    
    keyboard = build_panel_keyboard(modules_state, user_id)
    await callback.message.edit_reply_markup(keyboard)

async def handle_callbacks(client: Client, callback: CallbackQuery, db):
    data = callback.data
    user_id = callback.from_user.id
    
    if data == "close_panel":
        await callback.message.delete()
        await callback.answer()
        return
    
    if data == "main_panel":
        await show_panel(client, callback.message, db)
        await callback.answer()
        return
    
    if data == "anim_menu":
        await callback.message.edit_text(
            "🎨 **انیمیشن‌ها**\nانیمیشن مورد نظرت رو انتخاب کن:",
            reply_markup=ANIM_MENU
        )
        await callback.answer()
        return
    
    if data.startswith("anim_"):
        await handle_animation_callback(client, callback, db)
        return
    
    if data == "social_menu":
        await callback.message.edit_text(
            "❤️ **مدیریت اجتماعی**\n"
            "دوست، دشمن و کراش خودتو مدیریت کن:",
            reply_markup=SOCIAL_MENU
        )
        await callback.answer()
        return
    
    if data == "sec_menu":
        await callback.message.edit_text(
            "🤖 **منشی ربات**\n"
            "تا ۳ پیغام خوش‌آمدگویی تنظیم کن:",
            reply_markup=SEC_MENU
        )
        await callback.answer()
        return
    
    if data == "broad_menu":
        await callback.message.edit_text(
            "📢 **تبلیغات**\n"
            "گروه‌ها رو اضافه کن و تبلیغتو شروع کن:",
            reply_markup=BROAD_MENU
        )
        await callback.answer()
        return
    
    if data == "pay_menu":
        await callback.message.edit_text(
            "💳 **پرداخت**\n"
            "شماره کارت و درآمدهای خودتو مدیریت کن:",
            reply_markup=PAY_MENU
        )
        await callback.answer()
        return
    
    if data.startswith("pay_"):
        await handle_payment_callback(client, callback, db)
        return
    
    if data.startswith("help_"):
        await handle_help_callback(client, callback, db)
        return
    
    if data.startswith("toggle_"):
        await toggle_module(client, callback, db)
        return
    
    if data == "check_join":
        if await check_force_join(client, user_id, db):
            await callback.answer("✅ عضویت تایید شد!")
            await callback.message.delete()
        else:
            await callback.answer("❌ هنوز عضو نشدی!", show_alert=True)
        return

    if data.startswith("list_"):
        list_type = data.replace("list_", "")
        if list_type == "enemy":
            enemies = db.get_list(user_id, "enemy")
            if enemies:
                msg = "👤 **لیست دشمن:**\n\n"
                for tid, txt in enemies:
                    try:
                        u = await client.get_users(tid)
                        name = u.first_name
                    except:
                        name = str(tid)
                    msg += f"❌ {name} - {txt or 'بدون متن'}\n"
                await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="social_menu")]]))
            else:
                await callback.answer("✅ لیست خالی است")
        elif list_type == "friend":
            friends = db.get_list(user_id, "friend")
            if friends:
                msg = "👤 **لیست دوست:**\n\n"
                for tid, txt in friends:
                    try:
                        u = await client.get_users(tid)
                        name = u.first_name
                    except:
                        name = str(tid)
                    msg += f"✅ {name} - {txt or 'بدون متن'}\n"
                await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="social_menu")]]))
            else:
                await callback.answer("✅ لیست خالی است")
        elif list_type == "crush":
            crushes = db.get_list(user_id, "crush")
            if crushes:
                msg = "👤 **لیست کراش:**\n\n"
                for tid, txt in crushes:
                    try:
                        u = await client.get_users(tid)
                        name = u.first_name
                    except:
                        name = str(tid)
                    msg += f"💕 {name} - {txt or 'بدون متن'}\n"
                await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="social_menu")]]))
            else:
                await callback.answer("✅ لیست خالی است")
        await callback.answer()
        return
    
    if data.startswith("social_"):
        action = data.replace("social_", "")
        db.set_setting(user_id, "social_action", action)
        await callback.message.edit_text(f"👤 **آیدی عددی فرد مورد نظر رو بفرست:**\n(مثال: `123456789`)")
        await callback.answer()
        return

    if data.startswith("sec_set_"):
        order = data.replace("sec_set_", "")
        db.set_setting(user_id, "sec_set_order", order)
        await callback.message.edit_text(f"📝 **متن منشی {order} رو بفرست:**")
        await callback.answer()
        return
    
    if data == "sec_view":
        msgs = db.get_secretary(user_id)
        if msgs:
            msg = "🤖 **پیام‌های منشی:**\n\n"
            for order, txt in msgs:
                msg += f"{order}. {txt}\n"
            await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="sec_menu")]]))
        else:
            await callback.answer("📭 منشی تنظیم نشده")
        await callback.answer()
        return
    
    if data == "acc_menu":
        me = await client.get_me()
        await callback.message.edit_text(
            f"👤 **اطلاعات حساب**\n\n"
            f"نام: {me.first_name or '---'}\n"
            f"نام خانوادگی: {me.last_name or '---'}\n"
            f"بیو: {me.bio or '---'}\n"
            f"آیدی: `{me.id}`\n"
            f"شماره: `{me.phone_number or '---'}`\n\n"
            f"**دستورات:**\n"
            f"`تنظیم نام [نام]`\n"
            f"`تنظیم نام خانوادگی [نام]`\n"
            f"`تنظیم بیو [متن]`\n"
            f"`تنظیم عکس` (ریپلای روی عکس)\n"
            f"`حذف عکس پروفایل`\n"
            f"`حذف تمامی عکس ها`",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بستن", callback_data="close_panel")]])
        )
        await callback.answer()
        return

    if data.startswith("set_time_"):
        style = data.replace("set_time_", "")
        db.set_setting(user_id, "time_style", style)
        await callback.answer(f"✅ استایل ساعت تنظیم شد: {style}")
        return

    if data == "broad_add":
        await callback.message.edit_text("📢 **آیدی گروه رو بفرست:**\nمثال: `-100123456789`")
        await callback.answer()
        return
    
    if data == "broad_list":
        groups = db.get_broadcast_groups(user_id)
        if groups:
            msg = "📢 **گروه‌های تبلیغ:**\n\n"
            for gid, title in groups:
                msg += f"👥 {title} (`{gid}`)\n"
            await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="broad_menu")]]))
        else:
            await callback.answer("📭 لیست خالی است")
        await callback.answer()
        return
    
    if data == "broad_start":
        await callback.message.edit_text("📢 **روی پیام مورد نظر ریپلای کن و بنویس `شروع تبلیغ`**")
        await callback.answer()
        return
    
    if data == "broad_stop":
        from modules.broadcast import BROADCAST_RUNNING
        BROADCAST_RUNNING[user_id] = False
        await callback.answer("⏹️ توقف شد")
        return

    if data == "pay_card":
        await callback.message.edit_text("💳 **شماره کارتت رو بفرست:**\nمثال: `شماره کارت 1234-5678-9012-3456`")
        await callback.answer()
        return
    
    if data == "pay_income":
        payments = db.get_payments(user_id)
        if payments:
            msg = "💰 **درآمدها:**\n\n"
            total = 0
            for p in payments:
                s = "✅" if p[5] == "confirmed" else "⏳" if p[5] == "pending" else "❌"
                msg += f"{s} {p[3]} - {p[5]}\n"
                if p[5] == "confirmed":
                    total += p[3] or 0
            msg += f"\n💵 مجموع: {total}"
            await callback.message.edit_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙", callback_data="pay_menu")]]))
        else:
            await callback.answer("📭 هیچ تراکنشی نیست")
        await callback.answer()
        return

    if data == "help_menu":
        from utils.helpers import build_help_keyboard
        await callback.message.edit_text(
            "❓ **راهنمای ربات**\n\nروی هر گزینه کلیک کن:",
            reply_markup=build_help_keyboard()
        )
        await callback.answer()
        return

def register(app: Client, db):
    @app.on_message(filters.text & filters.private)
    async def panel_trigger(client, message):
        text = message.text or ""
        if text.strip() == "پنل":
            await show_panel(client, message, db)
        elif text.strip() == "منو" or text.strip() == "منوی اصلی":
            await message.reply_text("🏠 **منوی اصلی**", reply_markup=build_main_menu())

    @app.on_callback_query()
    async def callback_handler(client, callback):
        await handle_callbacks(client, callback, db)
