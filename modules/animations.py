import asyncio
import math
import time
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatAction

ANIMATION_TEXTS = {
    "heart": [
        "❤️                  ",
        "❤️❤️                ",
        "❤️❤️❤️             ",
        "❤️❤️❤️❤️           ",
        "❤️❤️❤️❤️❤️         ",
        "❤️❤️❤️❤️❤️❤️       ",
        "❤️❤️❤️❤️❤️❤️❤️     ",
        "❤️❤️❤️❤️❤️❤️❤️❤️   ",
        "❤️❤️❤️❤️❤️❤️❤️❤️❤️ ",
        "❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️",
        "💖💖💖💖💖💖💖💖💖💖",
        "💗💗💗💗💗💗💗💗💗💗",
        "💕💕💕💕💕💕💕💕💕💕",
    ],
    "wave": [
        "🌊           ",
        " 🌊          ",
        "  🌊         ",
        "   🌊        ",
        "    🌊       ",
        "     🌊      ",
        "      🌊     ",
        "       🌊    ",
        "        🌊   ",
        "         🌊  ",
        "          🌊 ",
        "           🌊",
        "🌊           ",
    ],
    "pulse": [
        "💓          ",
        " 💓         ",
        "  💓        ",
        "   💓       ",
        "    💓      ",
        "     💗     ",
        "      💖    ",
        "       💕   ",
        "        💓  ",
        "         💓 ",
        "          💓",
        "💓          ",
    ],
    "love": [
        "💕       ",
        "💕💕      ",
        "💕💕💕     ",
        "💕💕💕💕    ",
        "💕💕💕💕💕   ",
        "💕💕💕💕💕💕  ",
        "💕💕💕💕💕💕💕",
        "💗💗💗💗💗💗💗",
        "💖💖💖💖💖💖💖",
        "❤️❤️❤️❤️❤️❤️❤️",
    ],
    "moon": [
        "🌑       ",
        "🌒       ",
        "🌓       ",
        "🌔       ",
        "🌕       ",
        "🌖       ",
        "🌗       ",
        "🌘       ",
    ],
    "moon2": [
        "🌙            ",
        " 🌙           ",
        "  🌙          ",
        "   🌙         ",
        "    🌙        ",
        "     🌙       ",
        "      🌙      ",
        "       🌙     ",
        "        🌙    ",
        "         🌙   ",
        "          🌙  ",
        "           🌙 ",
        "            🌙",
        "🌙            ",
    ],
    "clock2": [
        "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛",
    ],
    "thunder": [
        "⚡          ",
        " ⚡         ",
        "  ⚡        ",
        "   ⚡       ",
        "    ⚡      ",
        "     ⚡     ",
        "      ⚡    ",
        "       ⚡   ",
        "        ⚡  ",
        "         ⚡ ",
        "          ⚡",
        "💥          ",
        "⚡💥⚡        ",
    ],
    "heart_color": [
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💗",
    ],
    "earth": [
        "🌍         ",
        " 🌍        ",
        "  🌍       ",
        "   🌍      ",
        "    🌍     ",
        "     🌍    ",
        "      🌍   ",
        "       🌍  ",
        "        🌍 ",
        "         🌍",
        "🌎         ",
    ],
    "progress": [
        "🔴⬛⬛⬛⬛⬛⬛⬛⬛⬛ 10%",
        "🔴🔴⬛⬛⬛⬛⬛⬛⬛⬛ 20%",
        "🔴🔴🔴⬛⬛⬛⬛⬛⬛⬛ 30%",
        "🔴🔴🔴🔴⬛⬛⬛⬛⬛⬛ 40%",
        "🔴🔴🔴🔴🔴⬛⬛⬛⬛⬛ 50%",
        "🔴🔴🔴🔴🔴🔴⬛⬛⬛⬛ 60%",
        "🔴🔴🔴🔴🔴🔴🔴⬛⬛⬛ 70%",
        "🔴🔴🔴🔴🔴🔴🔴🔴⬛⬛ 80%",
        "🔴🔴🔴🔴🔴🔴🔴🔴🔴⬛ 90%",
        "🔴🔴🔴🔴🔴🔴🔴🔴🔴🔴 100%",
    ],
}

ANIM_MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton("❤️ قلب", callback_data="anim_heart"),
     InlineKeyboardButton("🌊 موج", callback_data="anim_wave")],
    [InlineKeyboardButton("💓 ضربان", callback_data="anim_pulse"),
     InlineKeyboardButton("💕 Love", callback_data="anim_love")],
    [InlineKeyboardButton("🌙 ماه", callback_data="anim_moon"),
     InlineKeyboardButton("🌙 ماه ۲", callback_data="anim_moon2")],
    [InlineKeyboardButton("🕐 ساعت", callback_data="anim_clock2"),
     InlineKeyboardButton("⚡ رعد", callback_data="anim_thunder")],
    [InlineKeyboardButton("🌈 قلب رنگی", callback_data="anim_heart_color"),
     InlineKeyboardButton("🌍 زمین", callback_data="anim_earth")],
    [InlineKeyboardButton("📊 پیشرفت", callback_data="anim_progress"),
     InlineKeyboardButton("⌨️ تایپینگ", callback_data="anim_typing")],
    [InlineKeyboardButton("🔙 بستن", callback_data="close_panel")],
])

async def run_animation(client: Client, chat_id, frames, speed=0.3):
    msg = await client.send_message(chat_id, frames[0])
    for frame in frames[1:]:
        await asyncio.sleep(speed)
        try:
            await msg.edit_text(frame)
        except:
            pass
    await asyncio.sleep(0.5)
    try:
        await msg.delete()
    except:
        pass

async def handle_animation_callback(client: Client, callback: CallbackQuery, db):
    data = callback.data
    chat_id = callback.message.chat.id

    if data == "anim_heart":
        await run_animation(client, chat_id, ANIMATION_TEXTS["heart"], 0.2)
    elif data == "anim_wave":
        await run_animation(client, chat_id, ANIMATION_TEXTS["wave"], 0.15)
    elif data == "anim_pulse":
        await run_animation(client, chat_id, ANIMATION_TEXTS["pulse"], 0.2)
    elif data == "anim_love":
        await run_animation(client, chat_id, ANIMATION_TEXTS["love"], 0.2)
    elif data == "anim_moon":
        await run_animation(client, chat_id, ANIMATION_TEXTS["moon"], 0.3)
    elif data == "anim_moon2":
        await run_animation(client, chat_id, ANIMATION_TEXTS["moon2"], 0.15)
    elif data == "anim_clock2":
        await run_animation(client, chat_id, ANIMATION_TEXTS["clock2"], 0.5)
    elif data == "anim_thunder":
        await run_animation(client, chat_id, ANIMATION_TEXTS["thunder"], 0.15)
    elif data == "anim_heart_color":
        await run_animation(client, chat_id, ANIMATION_TEXTS["heart_color"], 0.4)
    elif data == "anim_earth":
        await run_animation(client, chat_id, ANIMATION_TEXTS["earth"], 0.15)
    elif data == "anim_progress":
        await run_animation(client, chat_id, ANIMATION_TEXTS["progress"], 0.3)
    elif data == "anim_typing":
        frames = ["⌨️ درحال تایپ" + "." * i for i in range(1, 6)]
        await run_animation(client, chat_id, frames, 0.3)

    await callback.answer()

def register(app: Client, db):
    pass
