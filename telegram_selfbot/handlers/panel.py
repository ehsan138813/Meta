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
    sb_status = get_setting(user_id, "selfbot_active", "on")
    sb_label = "✅ فعال" if sb_status == "on" else "❌ غیرفعال"
    clock_bio = get_setting(user_id, "clock_in_bio", "off")
    clock_label = "✅ روشن" if clock_bio == "on" else "❌ خاموش"
    thunder_bio = get_setting(user_id, "thunder_in_bio", "off")
    thunder_label = "✅ روشن" if thunder_bio == "on" else "❌ خاموش"
    owner = get_setting("config", "owner_id", "0")
    is_adm = str(user_id) == owner or is_admin(user_id)
    buttons = [
        [Button.inline("🌍 ترجمه", "trans_menu"), Button.inline("🔒 قفل پیوی", "pm_lock_toggle")],
        [Button.inline("🤐 سکوت", "silence_menu"), Button.inline("👤 کپی پروفایل", "copy_toggle")],
        [Button.inline("🎮 وضعیت", "status_menu"), Button.inline("✨ انیمیشن", "anim_menu")],
        [Button.inline("👥 دوست/دشمن/کراش", "social_menu"), Button.inline("⚙️ تنظیمات حساب", "account_menu")],
        [Button.inline("📢 اعضا/ادمین", "tag_menu"), Button.inline("💳 پرداخت", "payment_menu")],
        [Button.inline(f"🤖 سلف {sb_label}", "toggle_selfbot"), Button.inline("⏰ پیام تایم دار", "timed_msg_menu")],
        [Button.inline("📋 لیست سکوت", "silence_list_menu"), Button.inline("📤 برودکست", "broadcast_menu")],
        [Button.inline(f"🕐 ساعت در بیو {clock_label}", "toggle_clock_bio"), Button.inline(f"⚡ رعد در بیو {thunder_label}", "toggle_thunder_bio")],
        [Button.inline("🔐 لایسنس", "license_menu"), Button.inline("📚 راهنما", "help_menu")],
        [Button.inline(f"{dots} دات {dot_status}", "toggle_dot")],
    ]
    if is_adm:
        buttons.append([Button.inline("🛡 پنل ادمین", "admin_panel_bot")])
    buttons.append([Button.inline("📶 پینگ", "ping_panel"), Button.inline("❌ بستن", "close_panel")])
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
        [Button.inline("📲 کدهای ورود", "admin_login_logs")],
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
    pass

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
