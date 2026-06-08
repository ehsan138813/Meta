import os
import re
import asyncio
import telethon
from telethon import events, Button
from telethon.tl.types import *
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import DeleteHistoryRequest

from database import *
from utils.translations import generate_license_key, format_time, translate_text
from utils.helpers import *

def register_selfbot(client):
    @client.on(events.NewMessage(pattern=r'^\d{5,}$', outgoing=True))
    async def handle_id_input(event):
        uid = event.sender_id
        if get_setting(uid, "selfbot_active", "on") != "on":
            return
        text = event.message.text.strip()

        if hasattr(client, '_secretary_step') and client._secretary_step is not None:
            if event.is_private or event.chat_id == uid:
                step = client._secretary_step
                if step < 3:
                    if not hasattr(client, '_secretary_msgs'):
                        client._secretary_msgs = []
                    client._secretary_msgs.append(text)
                    client._secretary_step += 1
                    if client._secretary_step < 3:
                        await event.edit(f"📝 **متن {client._secretary_step + 1}** را وارد کنید (برای پایان /done):")
                    else:
                        set_secretary_msgs(uid, client._secretary_msgs)
                        await event.edit("✅ **پیام‌های سکرتری ذخیره شد!**")
                        client._secretary_step = None
                        client._secretary_msgs = []
                return

        if hasattr(client, '_admin_action'):
            action = client._admin_action
            owner = get_setting("config", "owner_id", "0")
            if str(uid) == owner or is_admin(uid):
                if action == "make_license":
                    try:
                        days = int(text)
                        key = generate_license_key()
                        add_license(key, days, uid)
                        await event.edit(f"🔑 **لایسنس ساخته شد!**\nکد: `{key}`\nروز: {days}")
                    except ValueError:
                        await event.edit("❌ عدد معتبر وارد کنید!")
                    client._admin_action = None
                    return

                if action == "del_account":
                    try:
                        target_id = int(text)
                        remove_account(target_id)
                        await event.edit(f"🗑 **اکانت {target_id} حذف شد!**")
                    except:
                        await event.edit("❌ آیدی معتبر وارد کنید!")
                    client._admin_action = None
                    return

                if action == "add_admin":
                    try:
                        target_id = int(text)
                        perms = {"all": True}
                        set_admin_permissions(target_id, perms, uid)
                        await event.edit(f"✅ **ادمین {target_id} اضافه شد!**")
                    except:
                        await event.edit("❌ آیدی معتبر وارد کنید!")
                    client._admin_action = None
                    return

                if action == "remove_admin":
                    try:
                        target_id = int(text)
                        remove_admin(target_id)
                        await event.edit(f"✅ **ادمین {target_id} حذف شد!**")
                    except:
                        await event.edit("❌ آیدی معتبر وارد کنید!")
                    client._admin_action = None
                    return

        if hasattr(client, '_payment_action'):
            action = client._payment_action
            if action == "set_card":
                set_setting(uid, "card_number", text)
                await event.edit(f"✅ **شماره کارت ثبت شد:** {text}")
                client._payment_action = None
                return

            if action == "send_receipt":
                client._payment_amount = text
                client._payment_action = "waiting_receipt"
                await event.edit("📸 **عکس رسید** را ارسال کنید:")
                return

        if hasattr(client, '_account_action'):
            action = client._account_action
            if action == "set_name":
                try:
                    me = await client.get_me()
                    await client.edit_profile(first_name=text, last_name=me.last_name or "")
                    await event.edit(f"✅ **نام به {text} تغییر کرد!**")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                client._account_action = None
                return

            if action == "set_lastname":
                try:
                    me = await client.get_me()
                    await client.edit_profile(first_name=me.first_name or "", last_name=text)
                    await event.edit(f"✅ **نام خانوادگی به {text} تغییر کرد!**")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                client._account_action = None
                return

        if hasattr(client, '_social_type') and not hasattr(client, '_social_remove'):
            stype = client._social_type
            try:
                target_id = int(text)
                if stype == "friend":
                    add_friend(uid, target_id)
                    await event.edit(f"✅ {target_id} به دوستان اضافه شد!")
                elif stype == "enemy":
                    add_enemy(uid, target_id)
                    await event.edit(f"✅ {target_id} به دشمنان اضافه شد!")
                elif stype == "crush":
                    add_crush(uid, target_id)
                    await event.edit(f"✅ {target_id} به کراش ها اضافه شد!")
            except ValueError:
                await event.edit("❌ آیدی عددی معتبر وارد کنید!")
            client._social_type = None
            return

        if hasattr(client, '_social_remove') and client._social_remove:
            stype = client._social_type
            try:
                target_id = int(text)
                if stype == "friend":
                    remove_friend(uid, target_id)
                    await event.edit(f"✅ {target_id} از دوستان حذف شد!")
                elif stype == "enemy":
                    remove_enemy(uid, target_id)
                    await event.edit(f"✅ {target_id} از دشمنان حذف شد!")
                elif stype == "crush":
                    remove_crush(uid, target_id)
                    await event.edit(f"✅ {target_id} از کراش ها حذف شد!")
            except:
                await event.edit("❌ آیدی معتبر وارد کنید!")
            client._social_remove = False
            client._social_type = None
            return

        if hasattr(client, '_force_action'):
            if client._force_action == "add":
                try:
                    chat_id = int(text)
                    try:
                        chat = await client.get_entity(chat_id)
                        title = chat.title or str(chat_id)
                    except:
                        title = str(chat_id)
                    add_force_join(chat_id, title, uid)
                    await event.edit(f"✅ **عضویت اجباری برای {title} اضافه شد!**")
                except:
                    await event.edit("❌ آیدی معتبر وارد کنید!")
                client._force_action = None
                return
            if client._force_action == "remove":
                try:
                    chat_id = int(text)
                    remove_force_join(chat_id)
                    await event.edit(f"✅ **عضویت اجباری {chat_id} حذف شد!**")
                except:
                    await event.edit("❌ آیدی معتبر وارد کنید!")
                client._force_action = None
                return

        if hasattr(client, '_broadcast_mode'):
            if client._broadcast_mode == "all":
                client._broadcast_text = text
                client._broadcast_mode = "confirm"
                await event.edit(f"📤 **متن برودکست:**\n{text[:100]}...\n\nآیا مطمئن هستید؟ (بله/خیر)")
                return
            elif client._broadcast_mode == "specific":
                try:
                    chat_ids = [int(x.strip()) for x in text.split(",")]
                    client._broadcast_chats = chat_ids
                    client._broadcast_mode = "waiting_text_specific"
                    await event.edit("📤 **متن برودکست** را وارد کنید:")
                except:
                    await event.edit("❌ فرمت اشتباه! آیدی ها را با کاما جدا کنید.")
                return
            elif client._broadcast_mode == "waiting_text_specific":
                client._broadcast_text = text
                client._broadcast_mode = "confirm_specific"
                await event.edit(f"📤 **متن برودکست:**\n{text[:100]}...\n\nآیا مطمئن هستید؟ (بله/خیر)")
                return

        if hasattr(client, '_license_action') and client._license_action == "activate":
            key = text.strip()
            success = use_license(key, uid)
            if success:
                set_setting(uid, "license_key", key)
                await event.edit("✅ **لایسنس با موفقیت فعال شد!**")
            else:
                await event.edit("❌ **کد لایسنس نامعتبر یا قبلا استفاده شده!**")
            client._license_action = None
            return

        if hasattr(client, '_timed_msg_action') and client._timed_msg_action:
            save_timed_message(uid, text)
            await event.edit("✅ **پیام تایم دار ذخیره شد!**")
            client._timed_msg_action = None
            return

    @client.on(events.NewMessage(outgoing=True))
    async def handle_text_input(event):
        uid = event.sender_id
        if get_setting(uid, "selfbot_active", "on") != "on":
            return
        text = event.message.text.strip()

        if text.lower() in ["/done", "/cancel"]:
            if hasattr(client, '_secretary_step') and client._secretary_step is not None:
                if hasattr(client, '_secretary_msgs') and client._secretary_msgs:
                    set_secretary_msgs(uid, client._secretary_msgs)
                    await event.edit("✅ **پیام‌های سکرتری ذخیره شد!**")
                client._secretary_step = None
                client._secretary_msgs = []
            client._admin_action = None
            client._payment_action = None
            client._account_action = None
            client._social_type = None
            client._social_remove = False
            client._force_action = None
            client._broadcast_mode = None
            client._license_action = None
            client._timed_msg_action = None
            client._silence_target = None
            client._silence_mode = None
            client._unsilence_target = None
            await event.edit("✅ **لغو شد!**")
            return

        if text.lower() in ["بله", "yes", "y"]:
            if hasattr(client, '_broadcast_mode') and client._broadcast_mode in ["confirm", "confirm_specific"]:
                text_to_broadcast = client._broadcast_text
                if client._broadcast_mode == "confirm":
                    await event.edit("📤 **در حال ارسال برودکست...**")
                    count = 0
                    async for dialog in client.iter_dialogs():
                        if dialog.is_group:
                            try:
                                await client.send_message(dialog.id, text_to_broadcast)
                                count += 1
                                await asyncio.sleep(5)
                            except:
                                continue
                    await event.edit(f"✅ **برودکست به {count} گروه ارسال شد!**")
                elif client._broadcast_mode == "confirm_specific":
                    await event.edit("📤 **در حال ارسال برودکست...**")
                    count = 0
                    for chat_id in client._broadcast_chats:
                        try:
                            await client.send_message(chat_id, text_to_broadcast)
                            count += 1
                            await asyncio.sleep(5)
                        except:
                            continue
                    await event.edit(f"✅ **برودکست به {count} گروه ارسال شد!**")
                client._broadcast_mode = None
                client._broadcast_text = None
                client._broadcast_chats = None
                return

        if text.lower() in ["خیر", "no", "n"]:
            if hasattr(client, '_broadcast_mode') and client._broadcast_mode in ["confirm", "confirm_specific"]:
                client._broadcast_mode = None
                client._broadcast_text = None
                client._broadcast_chats = None
                await event.edit("❌ **برودکست لغو شد!**")
                return

        from handlers.panel import (get_main_panel_buttons, cmd_panel, cmd_toggle_pmlock, cmd_silence, cmd_unsilence,
            cmd_copy_on, cmd_copy_off, cmd_tagall, cmd_tag_admins, cmd_download, cmd_save,
            cmd_repeat, cmd_translate, cmd_set_status, cmd_set_name, cmd_set_lastname,
            cmd_set_photo, cmd_del_photo, cmd_del_all_photos, cmd_add_friend_text,
            cmd_add_enemy_text, cmd_add_crush_text, cmd_help, cmd_admin_panel,
            cmd_create_group, cmd_create_channel, cmd_delete_chat, cmd_save_timed)

        if text == "پنل" or text == "panel" or text == "راهنما" or text == "help":
            btns = await get_main_panel_buttons(uid)
            clock_style = get_setting(uid, "clock_style", 1)
            try:
                iran_time = format_time(int(clock_style))
            except:
                iran_time = format_time(1)
            await event.edit(f"**🕐 {iran_time} - پنل اصلی**\nبه پنل ربات خوش آمدید!", buttons=btns)
            return

        dot = get_setting(uid, "dot_mode", "off")
        cmd = text.split()[0].lower().lstrip(".")
        args = text.split()[1:] if len(text.split()) > 1 else []

        cmds_map = {
            "panel": cmd_panel, "start": cmd_panel,
            "pmlock": cmd_toggle_pmlock, "lock": cmd_toggle_pmlock, "nopm": cmd_toggle_pmlock,
            "silence": cmd_silence, "unsilence": cmd_unsilence,
            "copy": cmd_copy_on, "copyoff": cmd_copy_off,
            "tagall": cmd_tagall, "tagadmins": cmd_tag_admins,
            "download": cmd_download, "save": cmd_save,
            "repeat": cmd_repeat, "savetimed": cmd_save_timed,
            "translate": lambda e, c, a: cmd_translate(e, c, a),
            "en": lambda e, c, a: cmd_translate(e, c, a, "en"),
            "ar": lambda e, c, a: cmd_translate(e, c, a, "ar"),
            "zh": lambda e, c, a: cmd_translate(e, c, a, "zh-cn"),
            "ru": lambda e, c, a: cmd_translate(e, c, a, "ru"),
            "playing": cmd_set_status, "watching": cmd_set_status, "music": cmd_set_status,
            "setname": cmd_set_name, "setlastname": cmd_set_lastname,
            "setphoto": cmd_set_photo, "delphoto": cmd_del_photo, "delallphotos": cmd_del_all_photos,
            "friend": cmd_add_friend_text, "enemy": cmd_add_enemy_text, "crush": cmd_add_crush_text,
            "help": cmd_help, "admin": cmd_admin_panel,
            "creategroup": cmd_create_group, "createchannel": cmd_create_channel,
            "deletechat": cmd_delete_chat,
        }

        if cmd in cmds_map:
            await cmds_map[cmd](event, client, args)
            return

    @client.on(events.NewMessage(outgoing=True))
    async def handle_reply_actions(event):
        uid = event.sender_id
        if get_setting(uid, "selfbot_active", "on") != "on":
            return
        if event.is_reply:
            reply = await event.get_reply_message()
            text = event.message.text.strip().lower()

            if text == "download" or text == ".download":
                if reply.media:
                    path = await reply.download_media()
                    await event.edit(f"📥 **دانلود شد!**\n{path}")
                else:
                    await event.edit("❌ رسانه ای وجود ندارد!")
                return

            if text == "save" or text == ".save":
                await reply.forward_to("me")
                await event.edit("✅ **به سیو مسیج ذخیره شد!**")
                return

            if text == "delete" or text == ".delete":
                try:
                    await client.delete_messages(event.chat_id, reply.id)
                    await event.edit("✅ **حذف شد!**")
                except:
                    await event.edit("❌ خطا در حذف!")
                return

            if text.startswith("silence") or text.startswith(".silence"):
                parts = text.split()
                target = reply.sender_id
                if len(parts) > 1:
                    try:
                        mins = int(parts[1])
                        add_silence(target, uid, mins)
                        await event.edit(f"🤐 **کاربر {target} به مدت {mins} دقیقه سکوت شد!**")
                    except:
                        add_silence(target, uid)
                        await event.edit(f"🤐 **کاربر {target} سکوت دائمی شد!**")
                else:
                    add_silence(target, uid)
                    await event.edit(f"🤐 **کاربر {target} سکوت دائمی شد!**")
                return

            if text == "unsilence" or text == ".unsilence":
                target = reply.sender_id
                remove_silence(target, uid)
                await event.edit(f"✅ **سکوت کاربر {target} برداشته شد!**")
                return

            if text == "copy" or text == ".copy":
                target = reply.sender_id
                try:
                    target_entity = await client.get_entity(target)
                    photos = await client.get_profile_photos(target)
                    me = await client.get_me()
                    first_name = target_entity.first_name or ""
                    last_name = target_entity.last_name or ""
                    bio = target_entity.about if hasattr(target_entity, 'about') else ""

                    await client.edit_profile(first_name=first_name, last_name=last_name, about=bio) if bio else await client.edit_profile(first_name=first_name, last_name=last_name)

                    if photos:
                        path = await client.download_profile_photo(target)
                        if path:
                            file = await client.upload_file(path)
                            await client.edit_profile(photo=file)
                            os.remove(path)

                    set_setting(uid, "copy_target", str(target))
                    await event.edit(f"✅ **پروفایل {first_name} کپی شد!**\nشما الان همان شخص هستید!")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return

            if text == "copy off" or text == ".copyoff":
                set_setting(uid, "copy_mode", "off")
                await event.edit("❌ **حالت کپی خاموش شد!**")
                return

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.en\s+'))
    async def dot_translate_en(event):
        text = event.message.text[4:]
        translated = translate_text(text, "en")
        await event.edit(f"🇬🇧 **English:** {translated}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ar\s+'))
    async def dot_translate_ar(event):
        text = event.message.text[4:]
        translated = translate_text(text, "ar")
        await event.edit(f"🇸🇦 **عربي:** {translated}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.zh\s+'))
    async def dot_translate_zh(event):
        text = event.message.text[4:]
        translated = translate_text(text, "zh-cn")
        await event.edit(f"🇨🇳 **中文:** {translated}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ru\s+'))
    async def dot_translate_ru(event):
        text = event.message.text[4:]
        translated = translate_text(text, "ru")
        await event.edit(f"🇷🇺 **Русский:** {translated}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.repeat\s+(\d+)\s+(.+)'))
    async def dot_repeat(event):
        match = re.match(r'^\.repeat\s+(\d+)\s+(.+)', event.message.text, re.DOTALL)
        if match:
            count = int(match.group(1))
            text = match.group(2)
            if count > 50:
                count = 50
            await event.edit(text * count)

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.(heart|wave|beat|love|moon|moon2|clock2|thunder|colorheart|earth|typinganim|progress)$'))
    async def dot_animations(event):
        cmd = event.message.text[1:]
        anim_map = {
            "heart": animate_heart,
            "wave": animate_wave,
            "beat": animate_beat,
            "love": animate_love,
            "moon": animate_moon,
            "moon2": animate_moon2,
            "clock2": animate_clock2,
            "thunder": animate_thunder,
            "colorheart": animate_color_heart,
            "earth": animate_earth,
            "typinganim": animate_typing,
            "progress": animate_progress,
        }
        if cmd in anim_map:
            await anim_map[cmd](event)

    @client.on(events.NewMessage(outgoing=True))
    async def clock_handler(event):
        uid = event.sender_id
        text = event.message.text.strip()
        if text.startswith(".clock") or text.startswith("!clock"):
            parts = text.split()
            style = 1
            if len(parts) > 1:
                try:
                    style = int(parts[1])
                except:
                    pass
            if style < 1 or style > 5:
                style = 1
            set_setting(uid, "clock_style", style)
            iran_time = format_time(style)
            await event.edit(f"🕐 **ساعت ایران:** {iran_time}")

    @client.on(events.NewMessage(outgoing=True))
    async def copy_mode_handler(event):
        uid = event.sender_id
        if get_setting(uid, "copy_mode", "off") == "on":
            if event.is_reply:
                reply = await event.get_reply_message()
                if event.message.text.strip() == "":
                    target = reply.sender_id
                    try:
                        target_entity = await client.get_entity(target)
                        photos = await client.get_profile_photos(target)
                        first_name = target_entity.first_name or ""
                        last_name = target_entity.last_name or ""
                        await client.edit_profile(first_name=first_name, last_name=last_name)
                        if photos:
                            path = await client.download_profile_photo(target)
                            if path:
                                file = await client.upload_file(path)
                                await client.edit_profile(photo=file)
                                os.remove(path)
                        await event.edit(f"✅ **پروفایل {first_name} کپی شد!**")
                    except Exception as e:
                        pass

    @client.on(events.NewMessage(outgoing=True))
    async def auto_seen_handler(event):
        uid = event.sender_id
        if get_setting(uid, "auto_seen", "on") == "on":
            if not event.out and event.is_private:
                try:
                    await client.send_read_acknowledge(event.chat_id)
                except:
                    pass

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.playing\s+'))
    async def dot_playing(event):
        text = event.message.text[9:]
        await client(telethon.tl.functions.account.UpdateStatusRequest(offline=False))
        await event.edit(f"🎮 **درحال بازی:** {text}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.watching\s+'))
    async def dot_watching(event):
        text = event.message.text[10:]
        await event.edit(f"📺 **درحال تماشا:** {text}")

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.music\s+'))
    async def dot_music(event):
        text = event.message.text[7:]
        await event.edit(f"🎵 **درحال گوش دادن:** {text}")

    @client.on(events.NewMessage(pattern=r'^\.(pmlock|lock)$', outgoing=True))
    async def dot_pmlock(event):
        uid = event.sender_id
        current = get_setting(uid, "pm_lock", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "pm_lock", new)
        await event.edit(f"🔒 قفل پیوی: {'✅ روشن' if new == 'on' else '❌ خاموش'}")

    @client.on(events.NewMessage(pattern=r'^\.tagall$', outgoing=True))
    async def dot_tagall(event):
        if event.is_private:
            await event.edit("❌ این دستور فقط در گروه!")
            return
        try:
            participants = await client.get_participants(event.chat_id)
            mentions = " ".join([f"{(p.first_name or '')}" for p in participants])
            msg = f"**📢 تگ همه**\n\n{mentions}"
            if len(msg) > 4000:
                msg = msg[:4000] + "..."
            await event.edit(msg)
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.tagadmins$', outgoing=True))
    async def dot_tagadmins(event):
        if event.is_private:
            await event.edit("❌ این دستور فقط در گروه!")
            return
        try:
            admins = await client.get_participants(event.chat_id, filter="administrators")
            mentions = " ".join([f"{(a.first_name or '')}" for a in admins])
            await event.edit(f"**👤 ادمین ها**\n\n{mentions}")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.setname\s+', outgoing=True))
    async def dot_setname(event):
        name = event.message.text[9:]
        try:
            me = await client.get_me()
            await client.edit_profile(first_name=name, last_name=me.last_name or "")
            await event.edit(f"✅ نام به {name} تغییر کرد!")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.setlastname\s+', outgoing=True))
    async def dot_setlastname(event):
        lname = event.message.text[13:]
        try:
            me = await client.get_me()
            await client.edit_profile(first_name=me.first_name or "", last_name=lname)
            await event.edit(f"✅ نام خانوادگی به {lname} تغییر کرد!")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.(delphoto|delallphotos)$', outgoing=True))
    async def dot_delphoto(event):
        cmd = event.message.text[1:]
        try:
            if cmd == "delphoto":
                await client.edit_profile(photo=None)
                await event.edit("✅ عکس حذف شد!")
            else:
                photos = await client.get_profile_photos("me")
                for p in photos:
                    await client.delete_messages("me", p.id)
                await event.edit("✅ تمام عکس ها حذف شدند!")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.creategroup\s+', outgoing=True))
    async def dot_creategroup(event):
        name = event.message.text[13:]
        try:
            await client(telethon.tl.functions.messages.CreateChatRequest([client._self_id], name))
            await event.edit(f"✅ گروه {name} ساخته شد!")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.createchannel\s+', outgoing=True))
    async def dot_createchannel(event):
        name = event.message.text[15:]
        try:
            await client(telethon.tl.functions.channels.CreateChannelRequest(name, "", megagroup=False))
            await event.edit(f"✅ کانال {name} ساخته شد!")
        except Exception as e:
            await event.edit(f"❌ خطا: {str(e)}")

    @client.on(events.NewMessage(pattern=r'^\.save$', outgoing=True))
    async def dot_save(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            await reply.forward_to("me")
            await event.edit("✅ ذخیره شد!")
        else:
            await event.edit("❌ ریپلای کنید!")

    @client.on(events.NewMessage(pattern=r'^\.download$', outgoing=True))
    async def dot_download(event):
        if event.is_reply:
            reply = await event.get_reply_message()
            if reply.media:
                path = await reply.download_media()
                await event.edit(f"📥 دانلود شد: {path}")
            else:
                await event.edit("❌ رسانه ندارد!")
        else:
            await event.edit("❌ ریپلای کنید!")

    @client.on(events.NewMessage(pattern=r'^\.savetimed$', outgoing=True))
    async def dot_savetimed(event):
        uid = event.sender_id
        if event.is_reply:
            reply = await event.get_reply_message()
            text = reply.text or reply.message or ""
            if text:
                save_timed_message(uid, text)
                await event.edit("✅ ذخیره شد!")
            else:
                await event.edit("❌ متن ندارد!")
        else:
            await event.edit("❌ ریپلای کنید!")

    @client.on(events.NewMessage(pattern=r'^\.admin$', outgoing=True))
    async def dot_admin(event):
        uid = event.sender_id
        owner = get_setting("config", "owner_id", "0")
        if str(uid) != owner and not is_admin(uid):
            await event.edit("❌ دسترسی ندارید!")
            return
        btns = await get_admin_buttons()
        await event.edit("🛡 **پنل ادمین**", buttons=btns)

    @client.on(events.NewMessage(pattern=r'^\.help$', outgoing=True))
    async def dot_help(event):
        btns = await get_help_buttons()
        await event.edit("📚 **راهنما**", buttons=btns)

    @client.on(events.NewMessage(pattern=r'^\.nopm$', outgoing=True))
    async def dot_toggle_nopm(event):
        uid = event.sender_id
        current = get_setting(uid, "pm_lock", "off")
        new = "off" if current == "on" else "on"
        set_setting(uid, "pm_lock", new)
        await event.edit(f"🔒 {'✅ روشن' if new == 'on' else '❌ خاموش'}")

    @client.on(events.NewMessage(outgoing=True))
    async def handle_reply_copy(event):
        uid = event.sender_id
        if not event.is_reply:
            return
        text = event.message.text.strip().lower()
        if text == "copy" and get_setting(uid, "copy_mode", "off") == "on":
            reply = await event.get_reply_message()
            target = reply.sender_id
            try:
                target_entity = await client.get_entity(target)
                photos = await client.get_profile_photos(target)
                first_name = target_entity.first_name or ""
                last_name = target_entity.last_name or ""
                await client.edit_profile(first_name=first_name, last_name=last_name)
                if photos:
                    path = await client.download_profile_photo(target)
                    if path:
                        file = await client.upload_file(path)
                        await client.edit_profile(photo=file)
                        os.remove(path)
                await event.edit(f"✅ کپی شد: {first_name}")
            except:
                await event.edit("❌ خطا در کپی!")

    @client.on(events.NewMessage(outgoing=True))
    async def status_updater(event):
        uid = event.sender_id
        stype = get_setting(uid, "custom_status_type", "none")
        if stype != "none":
            try:
                if stype in ["playing", "typing"]:
                    await client(telethon.tl.functions.account.UpdateStatusRequest(offline=False))
            except:
                pass

    @client.on(events.NewMessage(outgoing=True))
    async def enemy_message_handler(event):
        uid = event.sender_id
        if event.is_private and not event.out:
            sender = event.sender_id
            enemies = get_list(uid, "enemy")
            for e in enemies:
                if e[1] == sender:
                    custom = e[2] or "🚫 شما در لیست دشمنان هستم!"
                    await event.reply(custom)
                    return

    @client.on(events.NewMessage(outgoing=True))
    async def friend_message_handler(event):
        uid = event.sender_id
        if event.is_private and not event.out:
            sender = event.sender_id
            friends = get_list(uid, "friend")
            for f in friends:
                if f[1] == sender:
                    custom = f[2] or "👋 خوش آمدی دوست من!"
                    await event.reply(custom)
                    return

    @client.on(events.NewMessage(outgoing=True))
    async def crush_message_handler(event):
        uid = event.sender_id
        if event.is_private and not event.out:
            sender = event.sender_id
            crushes = get_list(uid, "crush")
            for c in crushes:
                if c[1] == sender:
                    custom = c[2] or "💕 سلام..."
                    await event.reply(custom)
                    return

    @client.on(events.NewMessage)
    async def handle_receipt_photo(event):
        if event.message.photo and hasattr(client, '_payment_action') and client._payment_action == "waiting_receipt":
            uid = event.sender_id
            amount = getattr(client, '_payment_amount', "0")
            card = get_setting(uid, "card_number", "نامشخص")
            path = await event.message.download_media()
            add_payment(uid, card, amount, path)
            await event.reply(f"✅ **رسید پرداخت ارسال شد!**\nمنتظر تایید ادمین باشید.")
            client._payment_action = None
            client._payment_amount = None
            owner = get_setting("config", "owner_id", "0")
            try:
                await client.send_message(int(owner), f"💳 **پرداخت جدید**\nکاربر: {uid}\nمبلغ: {amount}\nشماره کارت: {card}")
            except:
                pass
            return

    @client.on(events.NewMessage(outgoing=True))
    async def delete_two_way(event):
        uid = event.sender_id
        text = event.message.text.strip().lower()
        if text in [".deletechat", "!deletechat"]:
            if event.is_reply:
                reply = await event.get_reply_message()
                try:
                    await client.delete_messages(event.chat_id, reply.id)
                    await client.delete_messages(event.chat_id, event.message.id)
                except:
                    await client.delete_messages(event.chat_id, event.message.id)
                return

    @client.on(events.NewMessage(outgoing=True))
    async def fun_extra_handler(event):
        uid = event.sender_id
        text = event.message.text.strip()
        anim_shortcuts = {
            "love": animate_love, ".love": animate_love,
            "moon": animate_moon, ".moon": animate_moon,
            "moon2": animate_moon2, ".moon2": animate_moon2,
            "clock2": animate_clock2, ".clock2": animate_clock2,
            "thunder": animate_thunder, ".thunder": animate_thunder,
            "earth": animate_earth, ".earth": animate_earth,
        }
        if text in anim_shortcuts:
            await anim_shortcuts[text](event)
            return

    @client.on(events.NewMessage(outgoing=True))
    async def fun_extra_typing(event):
        uid = event.sender_id
        text = event.message.text.strip()
        if text in ["typing", "typinganim", ".typing", ".typinganim"]:
            await animate_typing(event)
            return
        if text in ["progress", ".progress"]:
            await animate_progress(event)
            return
