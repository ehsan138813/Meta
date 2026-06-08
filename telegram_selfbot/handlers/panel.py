from telethon import events, Button
from telethon.tl.types import MessageEntityBold, MessageEntityUnderline
import datetime
import asyncio
import os
import sys

from database import *
from utils.translations import translate_text, format_time, TRANSLATION_TARGETS
from utils.helpers import *

async def get_main_panel_buttons(user_id):
    dot = get_setting(user_id, "dot_mode", "off")
    dot_status = "✅ روشن" if dot == "on" else "❌ خاموش"
    dots = "❌" if dot == "on" else "✅"
    buttons = [
        [Button.inline("🌍 ترجمه", "trans_menu"), Button.inline("🔒 قفل پیوی", "pm_lock_toggle")],
        [Button.inline("🤐 سکوت", "silence_menu"), Button.inline("👤 کپی پروفایل", "copy_toggle")],
        [Button.inline("🎮 وضعیت", "status_menu"), Button.inline("✨ انیمیشن", "anim_menu")],
        [Button.inline("👥 دوست/دشمن/کراش", "social_menu"), Button.inline("⚙️ تنظیمات حساب", "account_menu")],
        [Button.inline("📢 اعضا/ادمین", "tag_menu"), Button.inline("💳 پرداخت", "payment_menu")],
        [Button.inline("📨 سکرتری", "secretary_menu"), Button.inline("⏰ پیام تایم دار", "timed_msg_menu")],
        [Button.inline("📋 لیست سکوت", "silence_list_menu"), Button.inline("📤 برودکست", "broadcast_menu")],
        [Button.inline("🔐 لایسنس", "license_menu"), Button.inline("📚 راهنما", "help_menu")],
        [Button.inline(f"{dots} دات {dot_status}", "toggle_dot")],
        [Button.inline("❌ بستن", "close_panel")]
    ]
    return buttons

async def get_animation_buttons():
    buttons = [
        [Button.inline("❤️ قلب", "anim_heart"), Button.inline("🌊 موج", "anim_wave")],
        [Button.inline("💓 ضربان", "anim_beat"), Button.inline("💝 Love", "anim_love")],
        [Button.inline("🌙 ماه", "anim_moon"), Button.inline("🌕 Moon2", "anim_moon2")],
        [Button.inline("🕐 Clock2", "anim_clock2"), Button.inline("⚡ رعد", "anim_thunder")],
        [Button.inline("🌈 قلب رنگی", "anim_color_heart"), Button.inline("🌍 زمین", "anim_earth")],
        [Button.inline("⌨️ تایپینگ", "anim_typing"), Button.inline("📊 پروگرس", "anim_progress")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_status_buttons():
    buttons = [
        [Button.inline("🎮 درحال بازی", "set_status_playing"), Button.inline("⌨️ درحال تایپ", "set_status_typing")],
        [Button.inline("📺 درحال ویدیو", "set_status_watching"), Button.inline("🎵 گوش دادن اهنگ", "set_status_music")],
        [Button.inline("📸 درحال عکس", "set_status_photo"), Button.inline("😎 درحال استیکر", "set_status_sticker")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_social_buttons():
    buttons = [
        [Button.inline("➕ دوست", "add_friend"), Button.inline("➖ حذف دوست", "remove_friend")],
        [Button.inline("➕ دشمن", "add_enemy"), Button.inline("➖ حذف دشمن", "remove_enemy")],
        [Button.inline("➕ کراش", "add_crush"), Button.inline("➖ حذف کراش", "remove_crush")],
        [Button.inline("📋 لیست دوست", "list_friends"), Button.inline("📋 لیست دشمن", "list_enemies")],
        [Button.inline("📋 لیست کراش", "list_crushes")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_tag_buttons():
    buttons = [
        [Button.inline("📢 تگ همه", "tag_all"), Button.inline("👤 تگ ادمین ها", "tag_admins")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_account_buttons():
    buttons = [
        [Button.inline("📝 تنظیم نام", "set_name"), Button.inline("📝 تنظیم نام خانوادگی", "set_lastname")],
        [Button.inline("🖼 تنظیم عکس", "set_photo"), Button.inline("🗑 حذف عکس", "del_photo")],
        [Button.inline("🗑 حذف تمام عکس ها", "del_all_photos")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_admin_buttons():
    buttons = [
        [Button.inline("➕ ساخت لایسنس", "admin_make_license"), Button.inline("📋 لایسنس ها", "admin_licenses")],
        [Button.inline("👥 اکانت ها", "admin_accounts"), Button.inline("🗑 حذف اکانت", "admin_del_account")],
        [Button.inline("📊 پرداخت ها", "admin_payments"), Button.inline("➕ ادمن جدید", "admin_add_admin")],
        [Button.inline("➖ حذف ادمن", "admin_remove_admin"), Button.inline("🤐 لیست سکوت", "silence_list_menu")],
        [Button.inline("📤 برودکست", "broadcast_menu"), Button.inline("🔒 عضویت اجباری", "force_join_menu")],
        [Button.inline("🔙 برگشت", "back_main")]
    ]
    return buttons

async def get_help_buttons():
    buttons = [
        [Button.inline("🌍 ترجمه", "help_translate"), Button.inline("🔒 قفل پیوی", "help_pm_lock")],
        [Button.inline("🤐 سکوت", "help_silence"), Button.inline("👤 کپی", "help_copy")],
        [Button.inline("🎮 وضعیت", "help_status"), Button.inline("✨ انیمیشن", "help_anim")],
        [Button.inline("👥 اجتماعی", "help_social"), Button.inline("⚙️ حساب", "help_account")],
        [Button.inline("📢 تگ", "help_tag"), Button.inline("💳 پرداخت", "help_payment")],
        [Button.inline("📨 سکرتری", "help_secretary"), Button.inline("⏰ تایم دار", "help_timed")],
        [Button.inline("📤 برودکست", "help_broadcast"), Button.inline("🔐 لایسنس", "help_license")],
        [Button.inline("📥 دانلود", "help_download"), Button.inline("🔁 تکرار", "help_repeat")],
        [Button.inline("❌ بستن", "close_panel")]
    ]
    return buttons

def register_panel(client):
    client.add_event_handler(lambda e: panel_handler(e))

async def panel_handler(event):
    if isinstance(event, events.CallbackQuery.Event):
        data = event.data.decode()
        user_id = event.sender_id
        uid = event.query.user_id

        if data == "close_panel":
            try:
                await event.delete()
            except:
                await event.edit("❌", buttons=None)
            return

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
            await event.edit("🌍 **منوی ترجمه**\nروی یک زبان کلیک کنید تا متن آخرین پیام ترجمه شود.", buttons=btns)
            return

        if data.startswith("trans_"):
            lang = data.split("_")[1]
            target = TRANSLATION_TARGETS.get(lang, "en")
            await event.edit(f"🔄 در حال ترجمه به {lang}...")
            async for msg in client.iter_messages(event.chat_id, limit=2):
                if msg.id != event.original_update.msg_id:
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
            await event.edit("**🤐 منوی سکوت**\nروی کاربر مورد نظر ریپلای کنید و گزینه مناسب را بزنید.", buttons=btns)
            return

        if data == "silence_perm":
            await event.edit("🔄 روی کاربر مورد نظر ریپلای کنید و دوباره این گزینه را بزنید...")
            client._silence_target = uid
            client._silence_mode = "perm"
            await event.edit("✅ آماده است! روی کاربر ریپلای کنید و دوباره دکمه را بزنید.", buttons=None)
            return

        if data == "silence_timed":
            await event.edit("⏱ تعداد دقیقه را وارد کنید:", buttons=None)
            client._silence_target = uid
            client._silence_mode = "timed"
            return

        if data == "unsilence":
            await event.edit("🔄 روی کاربر مورد نظر ریپلای کنید و دوباره این گزینه را بزنید...")
            client._unsilence_target = uid
            await event.edit("✅ آماده است! روی کاربر ریپلای کنید و دوباره دکمه را بزنید.", buttons=None)
            return

        if data == "silence_list_menu":
            rows = get_silence_list(uid)
            if not rows:
                await event.edit("📋 **لیست سکوت خالی است!**", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
                return
            msg = "**📋 لیست سکوت شما:**\n\n"
            for row in rows:
                until = row[1]
                if until == "forever":
                    until_str = "دائمی"
                else:
                    try:
                        dt = datetime.datetime.fromisoformat(until)
                        until_str = dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        until_str = until
                msg += f"👤 {row[0]} - تا {until_str}\n"
            await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "social_menu":
            btns = await get_social_buttons()
            await event.edit("**👥 منوی اجتماعی**\nمدیریت دوستان، دشمنان و کراش ها", buttons=btns)
            return

        if data in ["add_friend", "add_enemy", "add_crush"]:
            typ = data.split("_")[1]
            client._social_type = typ
            await event.edit(f"🔄 آیدی عددی یا یوزرنیم مورد نظر را ارسال کنید.\nریپلای هم میتوانید بزنید.", buttons=None)
            return

        if data in ["remove_friend", "remove_enemy", "remove_crush"]:
            typ = data.split("_")[1]
            client._social_type = typ
            client._social_remove = True
            await event.edit(f"🔄 آیدی عددی فرد مورد نظر را ارسال کنید.", buttons=None)
            return

        if data == "list_friends":
            rows = get_list(uid, "friend")
            msg = "**👥 لیست دوستان:**\n\n"
            if not rows:
                msg += "خالی!"
            for r in rows:
                msg += f"👤 {r[1]}\n"
            await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "list_enemies":
            rows = get_list(uid, "enemy")
            msg = "**👥 لیست دشمنان:**\n\n"
            if not rows:
                msg += "خالی!"
            for r in rows:
                msg += f"👤 {r[1]}\n"
            await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "list_crushes":
            rows = get_list(uid, "crush")
            msg = "**👥 لیست کراش ها:**\n\n"
            if not rows:
                msg += "خالی!"
            for r in rows:
                msg += f"👤 {r[1]}\n"
            await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "anim_menu":
            btns = await get_animation_buttons()
            await event.edit("**✨ منوی انیمیشن**\nانیمیشن مورد نظر خود را انتخاب کنید.", buttons=btns)
            return

        animation_map = {
            "anim_heart": animate_heart,
            "anim_wave": animate_wave,
            "anim_beat": animate_beat,
            "anim_love": animate_love,
            "anim_moon": animate_moon,
            "anim_moon2": animate_moon2,
            "anim_clock2": animate_clock2,
            "anim_thunder": animate_thunder,
            "anim_color_heart": animate_color_heart,
            "anim_earth": animate_earth,
            "anim_typing": animate_typing,
            "anim_progress": animate_progress
        }
        if data in animation_map:
            await animation_map[data](event)
            btns = await get_main_panel_buttons(uid)
            await event.edit("✅ انیمیشن تمام شد!", buttons=btns)
            return

        if data == "status_menu":
            btns = await get_status_buttons()
            await event.edit("**🎮 منوی وضعیت**\nوضعیت مورد نظر خود را انتخاب کنید.", buttons=btns)
            return

        status_map = {
            "set_status_playing": ("playing", "🎮 درحال بازی"),
            "set_status_typing": ("typing", "⌨️ درحال تایپ"),
            "set_status_watching": ("watching", "📺 درحال ویدیو دیدن"),
            "set_status_music": ("music", "🎵 درحال گوش دادن به اهنگ"),
            "set_status_photo": ("photo", "📸 درحال عکس"),
            "set_status_sticker": ("sticker", "😎 درحال استیکر")
        }
        if data in status_map:
            stype, stext = status_map[data]
            set_setting(uid, "custom_status_type", stype)
            set_setting(uid, "custom_status_text", stext)
            await event.answer(f"✅ وضعیت به {stext} تغییر کرد!", alert=True)
            btns = await get_main_panel_buttons(uid)
            await event.edit(f"✅ وضعیت تنظیم شد: {stext}", buttons=btns)
            return

        if data == "account_menu":
            btns = await get_account_buttons()
            await event.edit("**⚙️ تنظیمات حساب**", buttons=btns)
            return

        if data == "set_name":
            client._account_action = "set_name"
            await event.edit("📝 نام جدید را وارد کنید:", buttons=None)
            return

        if data == "set_lastname":
            client._account_action = "set_lastname"
            await event.edit("📝 نام خانوادگی جدید را وارد کنید:", buttons=None)
            return

        if data == "set_photo":
            client._account_action = "set_photo"
            await event.edit("🖼 یک عکس برای پروفایل ارسال کنید:", buttons=None)
            return

        if data == "del_photo":
            try:
                await client.edit_profile(photo=None)
                await event.edit("✅ عکس پروفایل حذف شد!", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            except Exception as e:
                await event.edit(f"❌ خطا: {str(e)}", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "del_all_photos":
            try:
                photos = await client.get_profile_photos("me")
                for p in photos:
                    await client.delete_messages("me", p.id)
                await event.edit("✅ تمام عکس ها حذف شدند!", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            except Exception as e:
                await event.edit(f"❌ خطا: {str(e)}", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "tag_menu":
            btns = await get_tag_buttons()
            await event.edit("**📢 منوی تگ**", buttons=btns)
            return

        if data == "tag_all":
            if event.chat_id == uid:
                await event.answer("❌ این دستور فقط در گروه کار میکند!", alert=True)
                return
            try:
                participants = await client.get_participants(event.chat_id)
                mentions = " ".join([f"{(p.first_name or '')}" for p in participants])
                msg = f"**📢 تگ همه اعضا**\n\n{mentions}"
                if len(msg) > 4000:
                    msg = msg[:4000] + "..."
                await event.edit(msg, buttons=[[Button.inline("🔙 برگشت", "tag_menu")]])
            except Exception as e:
                await event.edit(f"❌ خطا: {str(e)}")
            return

        if data == "tag_admins":
            if event.chat_id == uid:
                await event.answer("❌ این دستور فقط در گروه کار میکند!", alert=True)
                return
            try:
                admins = await client.get_participants(event.chat_id, filter="administrators")
                mentions = " ".join([f"{(a.first_name or '')}" for a in admins])
                await event.edit(f"**👤 تگ ادمین ها**\n\n{mentions}", buttons=[[Button.inline("🔙 برگشت", "tag_menu")]])
            except Exception as e:
                await event.edit(f"❌ خطا: {str(e)}")
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
            client._payment_action = "set_card"
            await event.edit("💳 شماره کارت خود را وارد کنید:", buttons=None)
            return

        if data == "send_receipt":
            client._payment_action = "send_receipt"
            await event.edit("💳 مبلغ را وارد کنید:", buttons=None)
            return

        if data == "my_income":
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT SUM(amount) FROM payments WHERE user_id=? AND status='approved'", (uid,))
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
            await event.edit("**📨 منوی سکرتری**\nتا 3 متن خوش آمدیدگویی تنظیم کنید.", buttons=btns)
            return

        if data == "set_secretary":
            client._secretary_step = 0
            client._secretary_msgs = []
            await event.edit("📝 **متن اول** را وارد کنید (برای لغو /cancel):", buttons=None)
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
            client._timed_msg_action = True
            await event.edit("⏰ **متن پیام تایم دار** را وارد کنید:", buttons=None)
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
            await event.edit("**📤 منوی برودکست**\nپیام به تمام گروه‌ها ارسال میشود.", buttons=btns)
            return

        if data == "broadcast_all":
            client._broadcast_mode = "all"
            await event.edit("📤 **متن برودکست** را وارد کنید:", buttons=None)
            return

        if data == "broadcast_specific":
            client._broadcast_mode = "specific"
            await event.edit("📤 **آیدی گروه‌ها** را با کاما جدا وارد کنید (مثال: -123456,-789):", buttons=None)
            return

        if data == "license_menu":
            btns = [
                [Button.inline("🔑 فعالسازی لایسنس", "activate_license")],
                [Button.inline("📋 وضعیت لایسنس", "license_status")],
                [Button.inline("🔙 برگشت", "back_main")]
            ]
            await event.edit("**🔐 منوی لایسنس**", buttons=btns)
            return

        if data == "activate_license":
            client._license_action = "activate"
            await event.edit("🔑 **کد لایسنس** را وارد کنید:", buttons=None)
            return

        if data == "license_status":
            exp = get_setting(uid, "license_expiry", "ندارد")
            await event.edit(f"**🔐 وضعیت لایسنس:**\nتاریخ انقضا: {exp}", buttons=[[Button.inline("🔙 برگشت", "back_main")]])
            return

        if data == "help_menu":
            btns = await get_help_buttons()
            await event.edit("**📚 راهنما**\nروی هر گزینه کلیک کنید تا راهنمایی مربوطه را ببینید.", buttons=btns)
            return

        help_texts = {
            "help_translate": "🌍 **راهنمای ترجمه**\nکافیه یک پیام بنویسید و در ابتدای آن زبان مقصد رو مشخص کنید.\nمثال: `.en hello` یا `.ar سلام`\nهمچنین میتوانید از پنل ترجمه استفاده کنید.",
            "help_pm_lock": "🔒 **قفل پیوی**\nبا فعال کردن این گزینه، هیچ کس نمیتواند به شما پیام خصوصی بدهد.\nدستور: `.pmlock`",
            "help_silence": "🤐 **راهنمای سکوت**\nروی کاربر ریپلای کنید و بنویسید `.silence` تا سکوت دائمی شود.\nبرای سکوت تایم دار: `.silence 5` (5 دقیقه)\nبرای حذف: `.unsilence`",
            "help_copy": "👤 **راهنمای کپی**\nبا `.copy` روشن و با `.copyoff` خاموش میشود.\nوقتی روشن باشد، پروفایل شخص مورد نظر کپی میشود.",
            "help_status": "🎮 **راهنمای وضعیت**\nوضعیت دلخواه خود را از پنل انتخاب کنید.\nمثال: `.playing GTA` یا `.watching Movie`",
            "help_anim": "✨ **راهنمای انیمیشن**\nاز پنل انیمیشن ها را انتخاب کرده و اجرا کنید.\nیا دستورات:\n`.heart` `.wave` `.moon` `.thunder` و...",
            "help_social": "👥 **راهنمای اجتماعی**\nاز پنل دوست/دشمن/کراش میتوانید افراد را مدیریت کنید.\nمتن دلخواه نیز میتوانید برای هر کدام تنظیم کنید.",
            "help_account": "⚙️ **راهنمای حساب**\nاز این بخش میتوانید نام، نام خانوادگی و عکس پروفایل خود را تغییر دهید.",
            "help_tag": "📢 **راهنمای تگ**\n`.tagall` برای تگ همه اعضا\n`.tagadmins` برای تگ ادمین‌ها",
            "help_payment": "💳 **راهنمای پرداخت**\nشماره کارت خود را ثبت کنید.\nکاربران رسید پرداخت ارسال میکنند و شما تایید یا رد میکنید.",
            "help_secretary": "📨 **راهنمای سکرتری**\nمیتوانید تا 3 متن خوش آمدیدگویی تنظیم کنید.\nهر کاربر جدید به ترتیب پیام‌ها را دریافت میکند.",
            "help_timed": "⏰ **راهنمای پیام تایم دار**\nمیتوانید پیام‌ها را ذخیره کنید و بعدا به سیو مسیج بفرستید.",
            "help_broadcast": "📤 **راهنمای برودکست**\nیک متن را به تمام گروه‌های خود یا گروه‌های مشخص ارسال کنید.",
            "help_license": "🔐 **راهنمای لایسنس**\nبرای استفاده از ربات نیاز به کد لایسنس دارید.\nاز ادمین کد لایسنس دریافت کنید و فعال کنید.",
            "help_download": "📥 **راهنمای دانلود**\nروی یک رسانه ریپلای کنید و بنویسید `.download` تا دانلود شود.\nبا `.save` به سیو مسیج ذخیره میشود.",
            "help_repeat": "🔁 **راهنمای تکرار**\n`.repeat 5 متن شما`\nمتن شما را 5 بار تکرار میکند.",
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

        if data == "add_force":
            client._force_action = "add"
            await event.edit("🔒 **آیدی عددی کانال/گروه** را ارسال کنید:", buttons=None)
            return

        if data == "remove_force":
            client._force_action = "remove"
            await event.edit("🔒 **آیدی عددی** را برای حذف ارسال کنید:", buttons=None)
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

        if data == "toggle_dot":
            current = get_setting(uid, "dot_mode", "off")
            new = "off" if current == "on" else "on"
            set_setting(uid, "dot_mode", new)
            status = "✅ روشن" if new == "on" else "❌ خاموش"
            await event.answer(f"دات {status}", alert=True)
            btns = await get_main_panel_buttons(uid)
            await event.edit(f"✅ دات: {status}", buttons=btns)
            return

        if data.startswith("admin_"):
            if not is_admin(uid) and uid != int(get_setting("config", "owner_id", "0")):
                await event.answer("❌ شما دسترسی ادمین ندارید!", alert=True)
                return
            await handle_admin_callback(event, data, uid)

        return

    if isinstance(event, events.NewMessage.Event):
        await handle_message(event, client)

async def handle_admin_callback(event, data, uid):
    if data == "admin_make_license":
        client._admin_action = "make_license"
        await event.edit("🔑 **تعداد روز لایسنس** را وارد کنید (مثال: 30):", buttons=None)
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
        client._admin_action = "del_account"
        await event.edit("🗑 **آیدی عددی کاربر** را برای حذف اکانت وارد کنید:", buttons=None)
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
        client._admin_action = "add_admin"
        await event.edit("➕ **آیدی عددی کاربر جدید** برای ادمین شدن را وارد کنید:", buttons=None)
        return

    if data == "admin_remove_admin":
        client._admin_action = "remove_admin"
        await event.edit("➖ **آیدی عددی ادمین** را برای حذف وارد کنید:", buttons=None)
        return

async def handle_message(event, client):
    uid = event.sender_id
    if not event.out and event.is_private:
        owner_id_val = get_setting("config", "owner_id", "0")
        try:
            owner_id = int(owner_id_val)
        except:
            owner_id = 0
        if uid != owner_id:
            if get_setting(owner_id, "pm_lock", "off") == "on":
                await event.reply("🔒 **پیوی قفل است!** اجازه ارسال پیام ندارید.")
                return
            if is_silenced(uid, owner_id):
                await event.reply("🤐 **شما سکوت شده اید!**")
                return
            force_list = get_force_joins()
            for f in force_list:
                try:
                    participant = await client.get_participant(f[1], uid)
                except:
                    chat = await client.get_entity(f[1])
                    await event.reply(f"🔒 برای ارسال پیام باید عضو {chat.title} شوید.")
                    return
            msgs = get_secretary_msgs(owner_id)
            counter_key = f"sec_count_{uid}"
            count = int(get_setting(owner_id, counter_key, "0"))
            if msgs and count < len(msgs):
                await event.reply(msgs[count][1])
                set_setting(owner_id, counter_key, str(count + 1))
            if msgs and count >= len(msgs):
                set_setting(owner_id, counter_key, "0")

    if event.out:
        text = event.message.text or event.message.message or ""
        if not text:
            return

        dot = get_setting(uid, "dot_mode", "off")
        is_command = text.startswith(".") or (dot == "off" and not text.startswith("."))

        if is_command:
            await handle_commands(event, client, text, dot)

async def handle_commands(event, client, text, dot):
    parts = text.split()
    cmd = parts[0].lower()
    if dot == "on" and not cmd.startswith("."):
        return
    if dot == "on":
        cmd = cmd[1:] if cmd.startswith(".") else cmd
    args = parts[1:]

    cmds = {
        "panel": cmd_panel,
        "pmlock": cmd_toggle_pmlock,
        "lock": cmd_toggle_pmlock,
        "silence": cmd_silence,
        "unsilence": cmd_unsilence,
        "copy": cmd_copy_on,
        "copyoff": cmd_copy_off,
        "tagall": cmd_tagall,
        "tagadmins": cmd_tag_admins,
        "download": cmd_download,
        "save": cmd_save,
        "repeat": cmd_repeat,
        "translate": cmd_translate,
        "en": lambda e, c, a: cmd_translate(e, c, a, "en"),
        "ar": lambda e, c, a: cmd_translate(e, c, a, "ar"),
        "zh": lambda e, c, a: cmd_translate(e, c, a, "zh-cn"),
        "ru": lambda e, c, a: cmd_translate(e, c, a, "ru"),
        "heart": lambda e, c, a: animate_heart(e),
        "wave": lambda e, c, a: animate_wave(e),
        "beat": lambda e, c, a: animate_beat(e),
        "love": lambda e, c, a: animate_love(e),
        "moon": lambda e, c, a: animate_moon(e),
        "moon2": lambda e, c, a: animate_moon2(e),
        "clock2": lambda e, c, a: animate_clock2(e),
        "thunder": lambda e, c, a: animate_thunder(e),
        "colorheart": lambda e, c, a: animate_color_heart(e),
        "earth": lambda e, c, a: animate_earth(e),
        "typinganim": lambda e, c, a: animate_typing(e),
        "progress": lambda e, c, a: animate_progress(e),
        "playing": cmd_set_status,
        "watching": cmd_set_status,
        "music": cmd_set_status,
        "setname": cmd_set_name,
        "setlastname": cmd_set_lastname,
        "setphoto": cmd_set_photo,
        "delphoto": cmd_del_photo,
        "delallphotos": cmd_del_all_photos,
        "friend": cmd_add_friend_text,
        "enemy": cmd_add_enemy_text,
        "crush": cmd_add_crush_text,
        "help": cmd_help,
        "start": cmd_panel,
        "admin": cmd_admin_panel,
        "creategroup": cmd_create_group,
        "createchannel": cmd_create_channel,
        "deletechat": cmd_delete_chat,
        "savetimed": cmd_save_timed,
    }

    if cmd in cmds:
        await cmds[cmd](event, client, args)
        return

    if cmd == "repeat" and args:
        try:
            count = int(args[0])
            msg_text = " ".join(args[1:])
            if count > 20:
                count = 20
            await event.edit(msg_text * count)
        except:
            await event.edit("❌ فرمت: .repeat تعداد متن")

async def cmd_panel(event, client, args):
    uid = event.sender_id
    btns = await get_main_panel_buttons(uid)
    clock_style = get_setting(uid, "clock_style", 1)
    try:
        iran_time = format_time(int(clock_style))
    except:
        iran_time = format_time(1)
    await event.edit(f"**🕐 {iran_time} - پنل اصلی**\nبه پنل ربات خوش آمدید!", buttons=btns)

async def cmd_toggle_pmlock(event, client, args):
    uid = event.sender_id
    current = get_setting(uid, "pm_lock", "off")
    new = "off" if current == "on" else "on"
    set_setting(uid, "pm_lock", new)
    await event.edit(f"🔒 قفل پیوی: {'✅ روشن' if new == 'on' else '❌ خاموش'}")

async def cmd_silence(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        target = reply.sender_id
        if args:
            try:
                mins = int(args[0])
                add_silence(target, uid, mins)
                await event.edit(f"🤐 کاربر {target} به مدت {mins} دقیقه سکوت شد!")
            except:
                await event.edit("❌ فرمت: .silence 5 (دقیقه)")
        else:
            add_silence(target, uid)
            await event.edit(f"🤐 کاربر {target} سکوت دائمی شد!")
    else:
        await event.edit("❌ روی کاربر ریپلای کنید!")

async def cmd_unsilence(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        target = reply.sender_id
        remove_silence(target, uid)
        await event.edit(f"✅ سکوت کاربر {target} برداشته شد!")
    else:
        await event.edit("❌ روی کاربر ریپلای کنید!")

async def cmd_copy_on(event, client, args):
    uid = event.sender_id
    set_setting(uid, "copy_mode", "on")
    await event.edit("✅ **کپی روشن شد!**\nروی هر کاربر ریپلای کنید تا پروفایلش کپی شود.")

async def cmd_copy_off(event, client, args):
    uid = event.sender_id
    set_setting(uid, "copy_mode", "off")
    await event.edit("❌ **کپی خاموش شد!**")

async def cmd_tagall(event, client, args):
    if event.is_private:
        await event.edit("❌ این دستور فقط در گروه قابل استفاده است!")
        return
    try:
        participants = await client.get_participants(event.chat_id)
        mentions = " ".join([f"{(p.first_name or '')}" for p in participants])
        msg = f"**📢 تگ همه اعضا**\n\n{mentions}"
        if len(msg) > 4000:
            msg = msg[:4000] + "..."
        await event.edit(msg)
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_tag_admins(event, client, args):
    if event.is_private:
        await event.edit("❌ این دستور فقط در گروه قابل استفاده است!")
        return
    try:
        admins = await client.get_participants(event.chat_id, filter="administrators")
        mentions = " ".join([f"{(a.first_name or '')}" for a in admins])
        await event.edit(f"**👤 تگ ادمین ها**\n\n{mentions}")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_download(event, client, args):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.media:
            path = await reply.download_media()
            await event.edit(f"📥 **دانلود شد!**\nمسیر: {path}")
        else:
            await event.edit("❌ این پیام رسانه ندارد!")
    else:
        await event.edit("❌ روی یک رسانه ریپلای کنید!")

async def cmd_save(event, client, args):
    if event.is_reply:
        reply = await event.get_reply_message()
        await reply.forward_to("me")
        await event.edit("✅ **به سیو مسیج ذخیره شد!**")
    else:
        await event.edit("❌ روی یک پیام ریپلای کنید!")

async def cmd_repeat(event, client, args):
    if len(args) < 2:
        await event.edit("❌ فرمت: .repeat تعداد متن")
        return
    try:
        count = int(args[0])
        text = " ".join(args[1:])
        if count > 50:
            count = 50
        await event.edit(text * count)
    except:
        await event.edit("❌ فرمت: .repeat تعداد متن")

async def cmd_translate(event, client, args, target="en"):
    reply = await event.get_reply_message() if event.is_reply else None
    text = " ".join(args) if args else (reply.text or reply.message if reply else None)
    if not text:
        await event.edit("❌ متنی برای ترجمه وجود ندارد!")
        return
    translated = translate_text(text, target)
    await event.edit(f"**🌍 ترجمه:**\n\n{translated}")

async def cmd_set_status(event, client, args):
    uid = event.sender_id
    cmd = event.message.text.split()[0].lower().lstrip(".")
    text = " ".join(args) if args else ""
    status_map = {
        "playing": "🎮", "watching": "📺", "music": "🎵",
    }
    emoji = status_map.get(cmd, "🎮")
    set_setting(uid, "custom_status_type", cmd)
    set_setting(uid, "custom_status_text", text or cmd)
    await event.edit(f"{emoji} **وضعیت به {cmd} {text} تغییر کرد!**")

async def cmd_set_name(event, client, args):
    if not args:
        await event.edit("❌ نام را وارد کنید!")
        return
    name = " ".join(args)
    try:
        me = await client.get_me()
        await client.edit_profile(first_name=name, last_name=me.last_name or "")
        await event.edit(f"✅ **نام به {name} تغییر کرد!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_set_lastname(event, client, args):
    if not args:
        await event.edit("❌ نام خانوادگی را وارد کنید!")
        return
    lname = " ".join(args)
    try:
        me = await client.get_me()
        await client.edit_profile(first_name=me.first_name or "", last_name=lname)
        await event.edit(f"✅ **نام خانوادگی به {lname} تغییر کرد!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_set_photo(event, client, args):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.photo:
            path = await reply.download_media()
            file = await client.upload_file(path)
            await client.edit_profile(photo=file)
            await event.edit("✅ **عکس پروفایل تغییر کرد!**")
            os.remove(path)
        else:
            await event.edit("❌ روی یک عکس ریپلای کنید!")
    else:
        await event.edit("❌ روی یک عکس ریپلای کنید!")

async def cmd_del_photo(event, client, args):
    try:
        await client.edit_profile(photo=None)
        await event.edit("✅ **عکس پروفایل حذف شد!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_del_all_photos(event, client, args):
    try:
        photos = await client.get_profile_photos("me")
        for p in photos:
            await client.delete_messages("me", p.id)
        await event.edit("✅ **تمام عکس ها حذف شدند!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_add_friend_text(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        target = reply.sender_id
        custom = " ".join(args) if args else ""
        add_friend(uid, target, custom)
        await event.edit(f"✅ {target} به لیست دوستان اضافه شد!")
    else:
        await event.edit("❌ روی کاربر ریپلای کنید!")

async def cmd_add_enemy_text(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        target = reply.sender_id
        custom = " ".join(args) if args else ""
        add_enemy(uid, target, custom)
        await event.edit(f"✅ {target} به لیست دشمنان اضافه شد!")
    else:
        await event.edit("❌ روی کاربر ریپلای کنید!")

async def cmd_add_crush_text(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        target = reply.sender_id
        custom = " ".join(args) if args else ""
        add_crush(uid, target, custom)
        await event.edit(f"✅ {target} به لیست کراش ها اضافه شد!")
    else:
        await event.edit("❌ روی کاربر ریپلای کنید!")

async def cmd_help(event, client, args):
    btns = await get_help_buttons()
    await event.edit("**📚 راهنمای ربات**\nروی گزینه ها کلیک کنید.", buttons=btns)

async def cmd_admin_panel(event, client, args):
    uid = event.sender_id
    owner = get_setting("config", "owner_id", "0")
    if str(uid) != owner and not is_admin(uid):
        await event.edit("❌ شما دسترسی ادمین ندارید!")
        return
    btns = await get_admin_buttons()
    await event.edit("**🛡 پنل ادمین**", buttons=btns)

async def cmd_create_group(event, client, args):
    if not args:
        await event.edit("❌ اسم گروه را وارد کنید!")
        return
    name = " ".join(args)
    try:
        group = await client(telethon.tl.functions.messages.CreateChatRequest([client._self_id], name))
        await event.edit(f"✅ **گروه {name} ساخته شد!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_create_channel(event, client, args):
    if not args:
        await event.edit("❌ اسم کانال را وارد کنید!")
        return
    name = " ".join(args)
    try:
        channel = await client(telethon.tl.functions.channels.CreateChannelRequest(name, "", megagroup=False))
        await event.edit(f"✅ **کانال {name} ساخته شد!**")
    except Exception as e:
        await event.edit(f"❌ خطا: {str(e)}")

async def cmd_delete_chat(event, client, args):
    if event.is_reply:
        reply = await event.get_reply_message()
        try:
            await client.delete_messages(event.chat_id, reply.id)
            await event.edit("✅ **پیام حذف شد!**")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")
    else:
        await event.edit("❌ روی پیام ریپلای کنید!")

async def cmd_save_timed(event, client, args):
    uid = event.sender_id
    if event.is_reply:
        reply = await event.get_reply_message()
        text = reply.text or reply.message or ""
        if text:
            save_timed_message(uid, text)
            conn = get_conn()
            c = conn.cursor()
            c.execute("SELECT last_insert_rowid()")
            mid = c.fetchone()[0]
            conn.close()
            await event.edit(f"✅ **پیام تایم دار ذخیره شد!** (آیدی: {mid})")
        else:
            await event.edit("❌ پیام متنی ندارد!")
    else:
        await event.edit("❌ روی یک پیام ریپلای کنید!")

def register_handlers(client):
    register_panel(client)
