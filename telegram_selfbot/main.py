import os
import sys
import asyncio
import json
import logging

from telethon import TelegramClient, events, Button
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError
from telethon.tl.functions.account import DeleteAccountRequest
from telethon.tl.types import *

sys.path.insert(0, os.path.dirname(__file__))

from config import API_ID, API_HASH, SESSION_NAME, ADMINS, OWNER_ID, BOT_TOKEN, LOG_GROUP_ID, FORCE_JOIN_CHATS
from database import *
from handlers.panel import *
from handlers.selfbot import register_selfbot
from utils.translations import generate_license_key, format_time
from utils.helpers import *

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.makedirs('sessions', exist_ok=True)

bot = None
user_clients = {}

async def get_user_client(user_id):
    if user_id in user_clients and user_clients[user_id].is_connected():
        return user_clients[user_id]
    if is_user_loggedin(user_id):
        session_path = os.path.join('sessions', f'user_{user_id}')
        if os.path.exists(session_path + '.session'):
            try:
                client = TelegramClient(session_path, API_ID, API_HASH)
                await client.connect()
                if await client.is_user_authorized():
                    register_selfbot(client)
                    user_clients[user_id] = client
                    me = await client.get_me()
                    logger.info(f"✅ سشن کاربر {user_id} ({me.first_name}) بازیابی شد!")
                    return client
            except Exception as e:
                logger.error(f"❌ خطا در بازیابی سشن {user_id}: {e}")
    return None

async def reconnect_user_selfbot(user_id):
    if is_user_loggedin(user_id):
        client = await get_user_client(user_id)
        if client:
            status = get_setting(user_id, "selfbot_active", "on")
            if status == "off":
                try:
                    await client.disconnect()
                except:
                    pass
                return
            me = await client.get_me()
            logger.info(f"✅ سلف‌بات کاربر {user_id} ({me.first_name}) دوباره متصل شد!")

async def check_license_and_login(event):
    uid = event.sender_id
    owner_id_val = str(get_setting("config", "owner_id", "0"))
    is_owner = str(uid) == owner_id_val
    is_admin_user = is_admin(uid)

    if not is_owner and not is_admin_user:
        has_lic = check_license(uid)
        lic_key = get_setting(uid, "license_key", None)
        if not has_lic and not lic_key:
            btns = [
                [Button.inline("🔑 فعالسازی لایسنس", "bot_activate_license")],
                [Button.inline("❌ بستن", "bot_close")]
            ]
            await event.reply("🔐 **شما لایسنس ندارید!**\nبرای استفاده از ربات باید لایسنس فعال کنید.", buttons=btns)
            return False

    logged_in = is_user_loggedin(uid)
    if not logged_in:
        btns = [
            [Button.inline("📱 ورود به حساب", "bot_start_login")],
            [Button.inline("🔙 برگشت", "bot_close")]
        ]
        label = "حالا باید شماره تلفن خود را برای فعالسازی سلف‌بات وارد کنید."
        if is_owner or is_admin_user:
            label = "شماره تلفن خود را برای فعالسازی سلف‌بات وارد کنید."
        await event.reply(f"🔐 **ادمین عزیز، {label}**", buttons=btns)
        return False
    client = await get_user_client(uid)
    if not client:
        btns = [
            [Button.inline("📱 ورود مجدد", "bot_start_login")],
            [Button.inline("🔙 برگشت", "bot_close")]
        ]
        await event.reply("❌ **سشن شما منقضی شده!**\nلطفا دوباره وارد شوید.", buttons=btns)
        return False
    return True

async def start_handler(event):
    uid = event.sender_id
    ok = await check_license_and_login(event)
    if ok:
        btns = await get_main_panel_buttons(uid)
        clock_style = get_setting(uid, "clock_style", 1)
        try:
            iran_time = format_time(int(clock_style))
        except:
            iran_time = format_time(1)
        await event.reply(f"**🕐 {iran_time} - پنل اصلی**\nبه پنل ربات خوش آمدید!", buttons=btns)

async def bot_callback_handler(event):
    uid = event.sender_id
    data = event.data.decode()

    if data == "bot_close":
        try:
            await event.delete()
        except:
            await event.edit("❌", buttons=None)
        return

    if data == "bot_activate_license":
        set_login_state(uid, "waiting_license", {})
        await event.edit("🔑 **کد لایسنس** خود را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "bot_start_login":
        set_login_state(uid, "waiting_phone", {})
        await event.edit("📱 **شماره تلفن** خود را به همراه کد کشور وارد کنید:\nمثال: `+989123456789`", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "bot_cancel":
        clear_login_state(uid)
        await event.edit("✅ **لغو شد!**", buttons=[[Button.inline("🏠 شروع", "bot_back_start")]])
        return

    if data == "bot_back_start":
        await start_handler(event)
        return

    # Forward panel callback to existing panel handler
    await bot_panel_handler(event, bot, uid)

async def bot_unified_handler(event):
    if event.sender_id == (await bot.get_me()).id:
        return
    uid = event.sender_id
    text = event.message.text.strip()
    owner_id_val = get_setting("config", "owner_id", "0")
    is_owner_or_admin = str(uid) == owner_id_val or is_admin(uid)

    if hasattr(bot, '_admin_action') and is_owner_or_admin:
        action = bot._admin_action
        if action == "make_license":
            try:
                days = int(text)
                key = generate_license_key()
                add_license(key, days, uid)
                await event.reply(f"🔑 **لایسنس ساخته شد!**\nکد: `{key}`\nروز: {days}")
            except ValueError:
                await event.reply("❌ عدد معتبر وارد کنید!")
            bot._admin_action = None
            return
        if action == "del_account":
            try:
                target_id = int(text)
                if target_id in user_clients:
                    try:
                        await user_clients[target_id].disconnect()
                    except:
                        pass
                    del user_clients[target_id]
                remove_account(target_id)
                await event.reply(f"🗑 **اکانت {target_id} به طور کامل حذف شد!**")
            except:
                await event.reply("❌ آیدی معتبر وارد کنید!")
            bot._admin_action = None
            return
        if action == "add_admin":
            try:
                target_id = int(text)
                perms = {"all": True}
                set_admin_permissions(target_id, perms, uid)
                await event.reply(f"✅ **ادمین {target_id} اضافه شد!**")
            except:
                await event.reply("❌ آیدی معتبر وارد کنید!")
            bot._admin_action = None
            return
        if action == "remove_admin":
            try:
                target_id = int(text)
                remove_admin(target_id)
                await event.reply(f"✅ **ادمین {target_id} حذف شد!**")
            except:
                await event.reply("❌ آیدی معتبر وارد کنید!")
            bot._admin_action = None
            return

    if hasattr(bot, '_payment_action'):
        action = bot._payment_action
        if action == "set_card":
            set_setting(uid, "card_number", text)
            await event.reply(f"✅ **شماره کارت ثبت شد:** {text}")
            bot._payment_action = None
            return
        if action == "send_receipt":
            bot._payment_amount = text
            bot._payment_action = "waiting_receipt"
            await event.reply("📸 **عکس رسید** را ارسال کنید:")
            return

    if event.message.photo and hasattr(bot, '_payment_action') and bot._payment_action == "waiting_receipt":
        amount = getattr(bot, '_payment_amount', "0")
        card = get_setting(uid, "card_number", "نامشخص")
        path = await event.message.download_media()
        add_payment(uid, card, amount, path)
        await event.reply(f"✅ **رسید پرداخت ارسال شد!**\nمنتظر تایید ادمین باشید.")
        bot._payment_action = None
        bot._payment_amount = None
        try:
            await bot.send_message(int(owner_id_val), f"💳 **پرداخت جدید**\nکاربر: {uid}\nمبلغ: {amount}\nشماره کارت: {card}")
        except:
            pass
        return

    if hasattr(bot, '_timed_msg_action') and bot._timed_msg_action:
        save_timed_message(uid, text)
        await event.reply("✅ **پیام تایم دار ذخیره شد!**")
        bot._timed_msg_action = None
        return

    if text.lower() in ["del", "delete"] and event.is_reply and is_owner_or_admin:
        reply = await event.get_reply_message()
        target_id = reply.sender_id
        if str(target_id) == owner_id_val:
            await event.reply("❌ نمیتونی اکانت خودت رو حذف کنی!")
            return
        try:
            if target_id in user_clients:
                uc = user_clients[target_id]
                try:
                    await uc(DeleteAccountRequest("Deleted by admin"))
                    await asyncio.sleep(1)
                except:
                    pass
                try:
                    await uc.disconnect()
                except:
                    pass
                del user_clients[target_id]
        except:
            pass
        remove_account(target_id)
        await event.reply(f"🗑 **اکانت {target_id} حذف شد** ✅")
        return

    step, login_data = get_login_state(uid)

    if step == "waiting_license":
        key = text.strip()
        success = use_license(key, uid)
        if success:
            set_setting(uid, "license_key", key)
            clear_login_state(uid)
            btns = [[Button.inline("📱 ورود به حساب", "bot_start_login")], [Button.inline("❌ بستن", "bot_close")]]
            await event.reply("✅ **لایسنس با موفقیت فعال شد!**\nحالا شماره تلفن خود را وارد کنید.", buttons=btns)
        else:
            await event.reply("❌ **کد لایسنس نامعتبر یا قبلا استفاده شده!**\nدوباره تلاش کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if step == "waiting_phone":
        phone = text.strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        add_login_attempt(uid, phone)
        try:
            session_path = os.path.join('sessions', f'user_{uid}')
            user_cl = TelegramClient(session_path, API_ID, API_HASH)
            await user_cl.connect()
            sent = await user_cl.send_code_request(phone)
            set_login_state(uid, "waiting_code", {
                "phone": phone,
                "phone_code_hash": sent.phone_code_hash,
                "session_path": session_path
            })
            await event.reply("📨 **کد تایید** که در تلگرام براتون اومده رو دقیقا همینجا وارد کنید.\n⚠️ **روی «کد تایید لاگین» در تلگرام کلیک نکنید**\n❌ اگر زدید، لاگین خراب میشه و باید از اول شروع کنید.\n\nکد رو به صورت متن بفرستید (مثلا: 19446)", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        except Exception as e:
            await event.reply(f"❌ **خطا:** {str(e)}\nدوباره تلاش کنید:", buttons=[[Button.inline("🔄 تلاش مجدد", "bot_start_login")]])
        return

    if step == "waiting_code":
        code = text.strip().replace(" ", "").replace(".", "")
        update_login_attempt(uid, code)
        phone = login_data.get("phone", "")
        phone_code_hash = login_data.get("phone_code_hash", "")
        session_path = login_data.get("session_path", "")
        try:
            user_cl = TelegramClient(session_path, API_ID, API_HASH)
            await user_cl.connect()
            try:
                await user_cl.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
            except SessionPasswordNeededError:
                set_login_state(uid, "waiting_2fa", login_data)
                await event.reply("🔐 **رمز عبور دو مرحله‌ای** خود را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
                return
            me = await user_cl.get_me()
            register_selfbot(user_cl)
            user_clients[uid] = user_cl
            add_user_account(uid, phone, session_path, OWNER_ID)
            clear_login_state(uid)
            btns = await get_main_panel_buttons(uid)
            await event.reply(f"✅ **ورود موفقیت‌آمیز!**\nخوش آمدید {me.first_name}!\nحالا میتوانید از دستورات استفاده کنید.", buttons=btns)
        except (PhoneCodeInvalidError, PhoneCodeExpiredError):
            await event.reply("❌ **کد نادرست یا منقضی شده!**\nدوباره تلاش کنید:", buttons=[[Button.inline("🔄 تلاش مجدد", "bot_start_login")]])
        except Exception as e:
            await event.reply(f"❌ **خطا:** {str(e)}", buttons=[[Button.inline("🔄 تلاش مجدد", "bot_start_login")]])
        return

    if step == "waiting_2fa":
        password = text.strip()
        phone = login_data.get("phone", "")
        session_path = login_data.get("session_path", "")
        try:
            user_cl = TelegramClient(session_path, API_ID, API_HASH)
            await user_cl.connect()
            await user_cl.sign_in(password=password)
            me = await user_cl.get_me()
            register_selfbot(user_cl)
            user_clients[uid] = user_cl
            add_user_account(uid, phone, session_path, OWNER_ID)
            clear_login_state(uid)
            btns = await get_main_panel_buttons(uid)
            await event.reply(f"✅ **ورود موفقیت‌آمیز!**\nخوش آمدید {me.first_name}!", buttons=btns)
        except Exception as e:
            await event.reply(f"❌ **خطا:** {str(e)}\nدوباره تلاش کنید:", buttons=[[Button.inline("🔄 تلاش مجدد", "bot_cancel")]])
        return

    ok = await check_license_and_login(event)
    if ok:
        btns = await get_main_panel_buttons(uid)
        clock_style = get_setting(uid, "clock_style", 1)
        try:
            iran_time = format_time(int(clock_style))
        except:
            iran_time = format_time(1)
        await event.reply(f"**🕐 {iran_time} - پنل اصلی**\nبه پنل ربات خوش آمدید!", buttons=btns)

async def bot_panel_handler(event, client, uid):
    data = event.data.decode()

    if data == "back_main":
        btns = await get_main_panel_buttons(uid)
        iran_time = format_time(get_setting(uid, "clock_style", 1))
        await event.edit(f"**🕐 {iran_time} - پنل اصلی**\nبه پنل ربات خوش آمدید!", buttons=btns)
        return

    if data == "trans_menu":
        btns = [
            [Button.inline("🇬🇧 انگلیسی", "trans_en"), Button.inline("🇸🇦 عربی", "trans_ar")],
            [Button.inline("🇨🇳 چینی", "trans_zh"), Button.inline("🇷🇺 روسی", "trans_ru")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("🌍 **منوی ترجمه**\nروی یک زبان کلیک کنید.", buttons=btns)
        return

    if data.startswith("trans_"):
        lang = data.split("_")[1]
        target_map = {"en": "en", "ar": "ar", "zh": "zh-cn", "ru": "ru"}
        target = target_map.get(lang, "en")
        user_client = await get_user_client(uid)
        if user_client:
            async for msg in user_client.iter_messages(event.chat_id, limit=2):
                mid = getattr(event.original_update, 'msg_id', 0) if hasattr(event, 'original_update') else 0
                translated = translate_text(msg.text or msg.message or "", target)
                await event.edit(f"**🌍 ترجمه به {lang}:**\n\n{translated}", buttons=None)
                return
        await event.edit("❌ متنی برای ترجمه یافت نشد!", buttons=None)
        return

    if data == "pm_lock_toggle":
        current = get_setting(uid, "pm_lock", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "pm_lock", new)
        status = "✅ روشن" if new == "on" else "❌ خاموش"
        await event.answer(f"قفل پیوی {status}", alert=True)
        return

    if data == "toggle_clock_bio":
        current = get_setting(uid, "clock_in_bio", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "clock_in_bio", new)
        status = "✅ روشن" if new == "on" else "❌ خاموش"
        await event.answer(f"ساعت در بیو {status}", alert=True)
        btns = await get_main_panel_buttons(uid)
        await event.edit(f"✅ ساعت در بیو: {status}", buttons=btns)
        return

    if data == "toggle_thunder_bio":
        current = get_setting(uid, "thunder_in_bio", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "thunder_in_bio", new)
        status = "✅ روشن" if new == "on" else "❌ خاموش"
        await event.answer(f"رعد در بیو {status}", alert=True)
        btns = await get_main_panel_buttons(uid)
        await event.edit(f"✅ رعد در بیو: {status}", buttons=btns)
        return

    if data == "admin_panel_bot":
        btns = await get_admin_buttons()
        await event.edit("**🛡 پنل ادمین**", buttons=btns)
        return
        btns = await get_main_panel_buttons(uid)
        iran_time = format_time(get_setting(uid, "clock_style", 1))
        await event.edit(f"**🕐 {iran_time} - پنل اصلی**\n🔒 قفل پیوی: {status}", buttons=btns)
        return

    if data == "silence_menu":
        btns = [
            [Button.inline("🤐 سکوت دائمی", "silence_perm"), Button.inline("⏱ سکوت تایم دار", "silence_timed")],
            [Button.inline("✅ حذف سکوت", "unsilence"), Button.inline("📋 لیست سکوت", "silence_list_menu")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**🤐 منوی سکوت**\n(این بخش در سلف‌بات قابل استفاده است)", buttons=btns)
        return

    if data in ["silence_perm", "silence_timed", "unsilence"]:
        await event.answer("⚠️ این قابلیت در سلف‌بات شما قابل استفاده است. پیام مورد نظر را در چت خود ریپلای کنید.", alert=True)
        return

    if data == "silence_list_menu":
        rows = get_silence_list(uid)
        if not rows:
            await event.edit("📋 **لیست سکوت خالی است!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        msg = "**📋 لیست سکوت شما:**\n\n"
        for row in rows:
            until = row[1]
            until_str = "دائمی" if until == "forever" else until
            msg += f"👤 {row[0]} - تا {until_str}\n"
        await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "social_menu":
        btns = [
            [Button.inline("➕ دوست", "add_friend"), Button.inline("➖ حذف دوست", "remove_friend")],
            [Button.inline("➕ دشمن", "add_enemy"), Button.inline("➖ حذف دشمن", "remove_enemy")],
            [Button.inline("➕ کراش", "add_crush"), Button.inline("➖ حذف کراش", "remove_crush")],
            [Button.inline("📋 لیست دوست", "list_friends"), Button.inline("📋 لیست دشمن", "list_enemies")],
            [Button.inline("📋 لیست کراش", "list_crushes")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**👥 منوی اجتماعی**", buttons=btns)
        return

    if data in ["add_friend", "add_enemy", "add_crush", "remove_friend", "remove_enemy", "remove_crush"]:
        await event.answer("⚠️ این قابلیت در سلف‌بات شما قابل استفاده است.", alert=True)
        return

    if data in ["list_friends", "list_enemies", "list_crushes"]:
        typ = data.split("_")[1]
        type_map = {"friends": "friend", "enemies": "enemy", "crushes": "crush"}
        rows = get_list(uid, type_map.get(typ, typ))
        labels = {"friends": "👥 دوستان", "enemies": "👥 دشمنان", "crushes": "👥 کراش‌ها"}
        msg = f"**{labels.get(typ, '')}:**\n\n"
        if not rows:
            msg += "خالی!"
        for r in rows:
            msg += f"👤 {r[1]}\n"
        await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "anim_menu":
        btns = [
            [Button.inline("❤️ قلب", "anim_heart"), Button.inline("🌊 موج", "anim_wave")],
            [Button.inline("💓 ضربان", "anim_beat"), Button.inline("💝 Love", "anim_love")],
            [Button.inline("🌙 ماه", "anim_moon"), Button.inline("🌕 Moon2", "anim_moon2")],
            [Button.inline("🕐 Clock2", "anim_clock2"), Button.inline("⚡ رعد", "anim_thunder")],
            [Button.inline("🌈 قلب رنگی", "anim_color_heart"), Button.inline("🌍 زمین", "anim_earth")],
            [Button.inline("⌨️ تایپینگ", "anim_typing"), Button.inline("📊 پروگرس", "anim_progress")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**✨ منوی انیمیشن**\n(در سلف‌بات خود اجرا کنید)", buttons=btns)
        return

    if data in ["anim_heart", "anim_wave", "anim_beat", "anim_love", "anim_moon", "anim_moon2",
                "anim_clock2", "anim_thunder", "anim_color_heart", "anim_earth", "anim_typing", "anim_progress"]:
        await event.answer("⚠️ انیمیشن را در سلف‌بات خود با دستور مربوطه اجرا کنید.", alert=True)
        return

    if data == "status_menu":
        btns = [
            [Button.inline("🎮 درحال بازی", "set_status_playing"), Button.inline("⌨️ درحال تایپ", "set_status_typing")],
            [Button.inline("📺 درحال ویدیو", "set_status_watching"), Button.inline("🎵 گوش دادن اهنگ", "set_status_music")],
            [Button.inline("📸 درحال عکس", "set_status_photo"), Button.inline("😎 درحال استیکر", "set_status_sticker")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**🎮 منوی وضعیت**\n(در سلف‌بات خود اعمال میشود)", buttons=btns)
        return

    if data in ["set_status_playing", "set_status_typing", "set_status_watching", "set_status_music",
                "set_status_photo", "set_status_sticker"]:
        stypes = {"set_status_playing": "playing", "set_status_typing": "typing", "set_status_watching": "watching",
                  "set_status_music": "music", "set_status_photo": "photo", "set_status_sticker": "sticker"}
        stexts = {"set_status_playing": "🎮 درحال بازی", "set_status_typing": "⌨️ درحال تایپ", "set_status_watching": "📺 درحال ویدیو دیدن",
                  "set_status_music": "🎵 درحال گوش دادن به اهنگ", "set_status_photo": "📸 درحال عکس", "set_status_sticker": "😎 درحال استیکر"}
        stype = stypes.get(data, "playing")
        stext = stexts.get(data, "🎮")
        set_setting(uid, "custom_status_type", stype)
        set_setting(uid, "custom_status_text", stext)
        await event.answer(f"✅ وضعیت به {stext} تغییر کرد!", alert=True)
        btns = await get_main_panel_buttons(uid)
        await event.edit(f"✅ وضعیت تنظیم شد: {stext}", buttons=btns)
        return

    if data == "account_menu":
        btns = [
            [Button.inline("📝 تنظیم نام", "set_name"), Button.inline("📝 تنظیم نام خانوادگی", "set_lastname")],
            [Button.inline("🖼 تنظیم عکس", "set_photo"), Button.inline("🗑 حذف عکس", "del_photo")],
            [Button.inline("🗑 حذف تمام عکس ها", "del_all_photos")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**⚙️ تنظیمات حساب**\n(در سلف‌بات خود اعمال کنید)", buttons=btns)
        return

    if data in ["set_name", "set_lastname", "set_photo", "del_photo", "del_all_photos"]:
        await event.answer("⚠️ از دستورات سلف‌بات خود استفاده کنید.", alert=True)
        return

    if data == "tag_menu":
        btns = [
            [Button.inline("📢 تگ همه", "tag_all"), Button.inline("👤 تگ ادمین ها", "tag_admins")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**📢 منوی تگ**\n(در سلف‌بات خود اجرا کنید)", buttons=btns)
        return

    if data in ["tag_all", "tag_admins"]:
        await event.answer("⚠️ از دستورات سلف‌بات خود استفاده کنید.", alert=True)
        return

    if data == "payment_menu":
        btns = [
            [Button.inline("💳 تنظیم شماره کارت", "set_card")],
            [Button.inline("📸 ارسال رسید", "send_receipt")],
            [Button.inline("💰 درآمدها", "my_income")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        card = get_setting(uid, "card_number", "تنظیم نشده")
        await event.edit(f"**💳 منوی پرداخت**\nشماره کارت شما: {card}", buttons=btns)
        return

    if data == "set_card":
        bot._payment_action = "set_card"
        await event.edit("💳 **شماره کارت** خود را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "send_receipt":
        bot._payment_action = "send_receipt"
        await event.edit("💳 **مبلغ** را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "my_income":
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(CAST(amount AS INTEGER)), 0) FROM payments WHERE user_id=? AND status='approved'", (uid,))
        total = c.fetchone()[0] or 0
        conn.close()
        await event.edit(f"💰 **درآمد کل شما:** {total} تومان", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "secretary_menu":
        btns = [
            [Button.inline("📝 تنظیم پیام‌ها", "set_secretary"), Button.inline("📋 مشاهده پیام‌ها", "view_secretary")],
            [Button.inline("❌ حذف سکرتری", "del_secretary")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**📨 منوی سکرتری**", buttons=btns)
        return

    if data == "set_secretary":
        await event.answer("⚠️ در سلف‌بات خود پیام بنویسید: `/done` و سپس پیام‌ها را ارسال کنید.", alert=True)
        return

    if data == "view_secretary":
        msgs = get_secretary_msgs(uid)
        if not msgs:
            await event.edit("📋 **پیامی تنظیم نشده!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 پیام‌های سکرتری:**\n\n"
        for m in msgs:
            text += f"{m[0]}. {m[1]}\n"
        await event.edit(text, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "del_secretary":
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM secretary_msgs WHERE user_id=?", (uid,))
        conn.commit()
        conn.close()
        await event.edit("✅ سکرتری حذف شد!", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "timed_msg_menu":
        btns = [
            [Button.inline("➕ افزودن پیام تایم دار", "add_timed_msg")],
            [Button.inline("📋 مشاهده پیام‌ها", "view_timed_msgs")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**⏰ منوی پیام تایم دار**", buttons=btns)
        return

    if data == "add_timed_msg":
        bot._timed_msg_action = True
        await event.edit("⏰ **متن پیام تایم دار** را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "view_timed_msgs":
        msgs = get_timed_messages(uid)
        if not msgs:
            await event.edit("📋 **پیامی وجود ندارد!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 پیام‌های تایم دار:**\n\n"
        for m in msgs[:10]:
            text += f"🆔 {m[0]}: {m[2][:50]}...\n"
        await event.edit(text, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "broadcast_menu":
        btns = [
            [Button.inline("📤 ارسال به همه گروه‌ها", "broadcast_all")],
            [Button.inline("📤 ارسال به گروه خاص", "broadcast_specific")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**📤 منوی برودکست**\n(در سلف‌بات خود اجرا کنید)", buttons=btns)
        return

    if data in ["broadcast_all", "broadcast_specific"]:
        await event.answer("⚠️ از سلف‌بات خود استفاده کنید.", alert=True)
        return

    if data == "license_menu":
        btns = [
            [Button.inline("🔑 فعالسازی لایسنس", "bot_activate_license")],
            [Button.inline("📋 وضعیت لایسنس", "license_status_bot")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**🔐 منوی لایسنس**", buttons=btns)
        return

    if data == "license_status_bot":
        exp = get_setting(uid, "license_expiry", "ندارد")
        key = get_setting(uid, "license_key", "ندارد")
        await event.edit(f"**🔐 وضعیت لایسنس:**\nکد: `{key}`\nتاریخ انقضا: {exp}", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "help_menu":
        btns = [
            [Button.inline("🌍 ترجمه", "help_translate"), Button.inline("🔒 قفل پیوی", "help_pm_lock")],
            [Button.inline("🤐 سکوت", "help_silence"), Button.inline("👤 کپی", "help_copy")],
            [Button.inline("🎮 وضعیت", "help_status"), Button.inline("✨ انیمیشن", "help_anim")],
            [Button.inline("👥 اجتماعی", "help_social"), Button.inline("⚙️ حساب", "help_account")],
            [Button.inline("📢 تگ", "help_tag"), Button.inline("💳 پرداخت", "help_payment")],
            [Button.inline("📨 سکرتری", "help_secretary"), Button.inline("⏰ تایم دار", "help_timed")],
            [Button.inline("📤 برودکست", "help_broadcast"), Button.inline("🔐 لایسنس", "help_license")],
            [Button.inline("📥 دانلود", "help_download"), Button.inline("🔁 تکرار", "help_repeat")],
            [Button.inline("❌ بستن", "bot_close")]
        ]
        await event.edit("**📚 راهنما**\nروی هر گزینه کلیک کنید.", buttons=btns)
        return

    help_texts = {
        "help_translate": "🌍 **ترجمه**\nاز پنل ترجمه استفاده کنید یا دستور:\n`.en متن` برای انگلیسی\n`.ar متن` برای عربی",
        "help_pm_lock": "🔒 **قفل پیوی**\n`.pmlock` یا از پنل فعال کنید.",
        "help_silence": "🤐 **سکوت**\nروی کاربر ریپلای کنید و بنویسید `.silence`\n`.silence 5` برای تایم دار\n`.unsilence` برای حذف",
        "help_copy": "👤 **کپی پروفایل**\n`.copy` روشن و `.copyoff` خاموش\nروی کاربر ریپلای کنید تا کپی شود.",
        "help_status": "🎮 **وضعیت**\n`.playing GTA` یا `.watching Movie`\nاز پنل هم میتوانید انتخاب کنید.",
        "help_anim": "✨ **انیمیشن**\n`.heart` `.wave` `.moon` `.thunder` و...",
        "help_social": "👥 **اجتماعی**\nاز پنل دوست/دشمن/کراش را مدیریت کنید.",
        "help_account": "⚙️ **حساب**\n`.setname نام` یا `.setlastname نام خانوادگی`",
        "help_tag": "📢 **تگ**\n`.tagall` برای تگ همه\n`.tagadmins` برای تگ ادمین‌ها",
        "help_payment": "💳 **پرداخت**\nشماره کارت ثبت کنید و رسید ارسال کنید.",
        "help_secretary": "📨 **سکرتری**\nتا 3 متن خوش آمدیدگویی تنظیم کنید.",
        "help_timed": "⏰ **پیام تایم دار**\nمتن را ذخیره کنید و بعدا بفرستید.",
        "help_broadcast": "📤 **برودکست**\nمتن را به همه گروه‌ها یا گروه خاص بفرستید.",
        "help_license": "🔐 **لایسنس**\nبرای استفاده از ربات نیاز به کد لایسنس دارید.",
        "help_download": "📥 **دانلود**\nروی رسانه ریپلای کنید و بنویسید `.download`",
        "help_repeat": "🔁 **تکرار**\n`.repeat 5 متن` متن را 5 بار تکرار میکند.",
    }
    if data in help_texts:
        await event.edit(help_texts[data], buttons=[[Button.inline("🔙 برگشت راهنما", "help_menu"), Button.inline("🏠 خانه", "back_main")]])
        return

    if data == "force_join_menu":
        btns = [
            [Button.inline("➕ افزودن کانال/گروه", "add_force")],
            [Button.inline("➖ حذف", "remove_force")],
            [Button.inline("📋 لیست", "list_force")],
            [Button.inline("🔙 برگشت", "back_main")]
        ]
        await event.edit("**🔒 منوی عضویت اجباری**", buttons=btns)
        return

    if data in ["add_force", "remove_force"]:
        await event.answer("⚠️ این بخش فقط برای ادمین اصلی قابل استفاده است.", alert=True)
        return

    if data == "list_force":
        rows = get_force_joins()
        if not rows:
            await event.edit("📋 **هیچ کانال/گروهی ثبت نشده!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 لیست عضویت اجباری:**\n\n"
        for r in rows:
            text += f"🆔 {r[1]} - {r[2]}\n"
        await event.edit(text, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "toggle_selfbot":
        current = get_setting(uid, "selfbot_active", "on")
        new = "off" if current == "on" else "on"
        set_setting(uid, "selfbot_active", new)
        status = "✅ فعال" if new == "on" else "❌ غیرفعال"
        await event.answer(f"سلف‌بات {status}", alert=True)
        if new == "off" and uid in user_clients:
            try:
                await user_clients[uid].disconnect()
                del user_clients[uid]
            except:
                pass
        elif new == "on" and uid not in user_clients:
            asyncio.ensure_future(reconnect_user_selfbot(uid))
        btns = await get_main_panel_buttons(uid)
        await event.edit(f"✅ وضعیت سلف‌بات: {status}", buttons=btns)
        return

    if data == "toggle_dot":
        current = get_setting(uid, "dot_mode", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "dot_mode", new)
        status = "✅ روشن" if new == "on" else "❌ خاموش"
        await event.answer(f"دات {status}", alert=True)
        btns = await get_main_panel_buttons(uid)
        await event.edit(f"✅ دات: {status}", buttons=btns)
        return

    if data == "ping_panel":
        import time
        start = time.time()
        msg = await event.edit("📶 **پینگ...**")
        end = time.time()
        ping = round((end - start) * 1000)
        await event.edit(f"📶 **پینگ:** `{ping}ms`", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data in ["close_panel", "bot_close"]:
        try:
            await event.delete()
        except:
            await event.edit("❌", buttons=None)
        return

    if data == "admin_login_logs":
        owner = get_setting("config", "owner_id", "0")
        if str(uid) != owner and not is_admin(uid):
            await event.answer("❌ دسترسی ندارید!", alert=True)
            return
        attempts = get_login_attempts(15)
        if not attempts:
            await event.edit("📋 **هیچ لاگینی ثبت نشده!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        msg = "**📋 کدهای ورود اکانت‌ها:**\n\n"
        for a in attempts:
            msg += f"👤 {a[1]} | 📱 {a[2]} | کد: `{a[3] or '⏳'}` | {a[4]}\n"
        msg += "\n🔒 **تمامی اطلاعات کاربران محفوظ است**"
        await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data.startswith("admin_"):
        owner = get_setting("config", "owner_id", "0")
        if str(uid) != owner and not is_admin(uid):
            await event.answer("❌ دسترسی ندارید!", alert=True)
            return
        await bot_admin_handler(event, uid, data)

async def bot_admin_handler(event, uid, data):
    if data == "admin_make_license":
        bot._admin_action = "make_license"
        await event.edit("🔑 **تعداد روز لایسنس** را وارد کنید (مثال: 30):", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "admin_licenses":
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM licenses ORDER BY created_at DESC LIMIT 20")
        rows = c.fetchall()
        conn.close()
        if not rows:
            await event.edit("📋 **هیچ لایسنس ساخته نشده!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 لایسنس ها:**\n\n"
        for r in rows:
            used = f"توسط {r[3]}" if r[3] else "❌ استفاده نشده"
            text += f"🔑 {r[0]} - {r[1]} روز - {used}\n"
        await event.edit(text, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "admin_accounts":
        accounts = get_all_accounts()
        if not accounts:
            await event.edit("📋 **هیچ اکانتی ثبت نشده!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 اکانت ها:**\n\n"
        for a in accounts:
            text += f"👤 {a[0]} - {a[1]} - {'✅' if a[3] else '❌'}\n"
        await event.edit(text, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
        return

    if data == "admin_del_account":
        bot._admin_action = "del_account"
        await event.edit("🗑 **آیدی عددی کاربر** را برای حذف اکانت وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "admin_payments":
        payments = get_pending_payments()
        if not payments:
            await event.edit("📋 **پرداخت در انتظاری وجود ندارد!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return
        text = "**📋 پرداخت های در انتظار:**\n\n"
        for p in payments:
            text += f"🆔 {p[0]} - کاربر: {p[1]} - مبلغ: {p[3]}\n"
        btns = []
        for p in payments:
            btns.append([Button.inline(f"✅ تایید {p[0]}", f"approve_{p[0]}"),
                         Button.inline(f"❌ رد {p[0]}", f"reject_{p[0]}")])
        btns.append([Button.inline("🔙 برگشت", "back_main")])
        await event.edit(text, buttons=btns)
        return

    if data.startswith("approve_"):
        pid = int(data.split("_")[1])
        approve_payment(pid)
        await event.answer("✅ پرداخت تایید شد!", alert=True)
        return

    if data.startswith("reject_"):
        pid = int(data.split("_")[1])
        reject_payment(pid)
        await event.answer("❌ پرداخت رد شد!", alert=True)
        return

    if data == "admin_add_admin":
        bot._admin_action = "add_admin"
        await event.edit("➕ **آیدی عددی کاربر جدید** را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

    if data == "admin_remove_admin":
        bot._admin_action = "remove_admin"
        await event.edit("➖ **آیدی عددی ادمین** را وارد کنید:", buttons=[[Button.inline("❌ انصراف", "bot_cancel")]])
        return

def register_bot_handlers(b):
    b.on(events.NewMessage(pattern=r'^/start$'))(start_handler)
    b.on(events.CallbackQuery)(bot_callback_handler)
    b.on(events.NewMessage())(bot_unified_handler)

async def main():
    global bot

    if not API_ID or not API_HASH:
        print("❌ لطفا API_ID و API_HASH را در config.py تنظیم کنید!")
        print("   از https://my.telegram.org دریافت کنید.")
        return

    if not BOT_TOKEN:
        print("❌ لطفا BOT_TOKEN را در config.py تنظیم کنید!")
        print("   از @BotFather در تلگرام دریافت کنید.")
        return

    set_setting("config", "owner_id", str(OWNER_ID))

    bot = TelegramClient('bot_session', API_ID, API_HASH)
    await bot.start(bot_token=BOT_TOKEN)
    register_bot_handlers(bot)
    bot_me = await bot.get_me()
    print(f"✅ ربات با توکن روشن شد! @{bot_me.username}")

    # Owner must log in through the bot interface

    accounts = get_all_accounts()
    for acc in accounts:
        if acc[3]:
            try:
                session_path = os.path.join('sessions', f'user_{acc[0]}')
                if os.path.exists(session_path + '.session'):
                    client = TelegramClient(session_path, API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        register_selfbot(client)
                        user_clients[acc[0]] = client
                        me = await client.get_me()
                        print(f"✅ سشن کاربر {acc[0]} ({me.first_name}) بازیابی شد!")
            except Exception as e:
                print(f"❌ خطا در بازیابی سشن {acc[0]}: {e}")

    if LOG_GROUP_ID:
        try:
            await bot.send_message(LOG_GROUP_ID, f"✅ **ربات روشن شد!**\nزمان: {format_time(3)}")
        except:
            pass

    print("✅ ربات فعال است...")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
