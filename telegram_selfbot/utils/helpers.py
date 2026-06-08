from telethon.tl.types import MessageEntityBold, MessageEntityItalic, MessageEntityUnderline, MessageEntityCode, MessageEntityTextUrl
from telethon import events
import asyncio
import random

def parse_text_style(text):
    entities = []
    parts = []
    i = 0
    while i < len(text):
        if text[i:i+2] == "**":
            end = text.find("**", i+2)
            if end != -1:
                parts.append(("bold", text[i+2:end]))
                i = end + 2
                continue
        elif text[i:i+2] == "__":
            end = text.find("__", i+2)
            if end != -1:
                parts.append(("underline", text[i+2:end]))
                i = end + 2
                continue
        elif text[i:i+2] == "~~":
            end = text.find("~~", i+2)
            if end != -1:
                parts.append(("italic", text[i+2:end]))
                i = end + 2
                continue
        elif text[i:i+1] == "`":
            end = text.find("`", i+1)
            if end != -1:
                parts.append(("code", text[i+1:end]))
                i = end + 1
                continue
        elif text[i:i+1] == ">":
            end = text.find("\n", i)
            if end == -1:
                end = len(text)
            parts.append(("quote", text[i+1:end].strip()))
            i = end + 1
            continue
        else:
            j = i
            while j < len(text) and text[j] not in ["*", "_", "~", "`", ">"]:
                j += 1
            if j > i:
                parts.append(("text", text[i:j]))
            i = j
            continue
        break
    if not parts:
        parts.append(("text", text))
    return parts

def build_entities(parts):
    offset = 0
    entities = []
    final_text = ""
    for ptype, ptext in parts:
        if ptype == "bold":
            ent = MessageEntityBold(offset=offset, length=len(ptext))
        elif ptype == "underline":
            ent = MessageEntityUnderline(offset=offset, length=len(ptext))
        elif ptype == "italic":
            ent = MessageEntityItalic(offset=offset, length=len(ptext))
        elif ptype == "code":
            ent = MessageEntityCode(offset=offset, length=len(ptext))
        elif ptype == "quote":
            ent = None
            final_text += "> " + ptext + "\n"
            offset += len(ptext) + 3
            continue
        else:
            ent = None
        if ent:
            entities.append(ent)
        final_text += ptext
        offset += len(ptext)
    return final_text, entities

HEART_FRAMES = [
    "🖤🤍🤍🤍🖤\n🤍🖤🖤🖤🤍\n🤍🖤🖤🖤🤍\n🤍🖤🖤🖤🤍\n🖤🤍🤍🤍🖤\n🤍🖤🖤🖤🤍\n🤍🤍🖤🤍🤍",
    "❤️🤍🤍🤍❤️\n🤍❤️❤️❤️🤍\n🤍❤️❤️❤️🤍\n🤍❤️❤️❤️🤍\n❤️🤍🤍🤍❤️\n🤍❤️❤️❤️🤍\n🤍🤍❤️🤍🤍",
    "💖🤍🤍🤍💖\n🤍💖💖💖🤍\n🤍💖💖💖🤍\n🤍💖💖💖🤍\n💖🤍🤍🤍💖\n🤍💖💖💖🤍\n🤍🤍💖🤍🤍",
    "💗🤍🤍🤍💗\n🤍💗💗💗🤍\n🤍💗💗💗🤍\n🤍💗💗💗🤍\n💗🤍🤍🤍💗\n🤍💗💗💗🤍\n🤍🤍💗🤍🤍",
    "💕🤍🤍🤍💕\n🤍💕💕💕🤍\n🤍💕💕💕🤍\n🤍💕💕💕🤍\n💕🤍🤍🤍💕\n🤍💕💕💕🤍\n🤍🤍💕🤍🤍"
]

WAVE_FRAMES = ["~", "~~", "~~~", "~~~~", "~~~~~", "~~~~", "~~~", "~~", "~"]
BEAT_FRAMES = ["💓", "💗", "💖", "💝", "💖", "💗", "💓"]

LOVE_FRAMES = [
    "💝  L  💝",
    "💝  Lo  💝",
    "💝  Lov  💝",
    "💝  Love  💝",
    "💝  Love 💝",
    "💝  Love  💝",
    "💝  Lov  💝",
    "💝  Lo  💝",
    "💝  L  💝"
]

MOON_FRAMES = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
MOON2_FRAMES = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
CLOCK2_FRAMES = ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"]
THUNDER_FRAMES = ["☁️", "⛅", "🌩️", "⚡", "🌩️", "⛅", "☁️"]
COLOR_HEART_FRAMES = ["❤️", "🧡", "💛", "💚", "💙", "💜", "💙", "💚", "💛", "🧡"]
EARTH_FRAMES = ["🌍", "🌎", "🌏"]

TYPING_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
PROGRESS_FRAMES = ["▰▱▱▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱▱▱", "▰▰▰▰▱▱▱▱▱▱",
                   "▰▰▰▰▰▱▱▱▱▱", "▰▰▰▰▰▰▱▱▱▱", "▰▰▰▰▰▰▰▱▱▱", "▰▰▰▰▰▰▰▰▱▱",
                   "▰▰▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰▰▰"]

async def animate_heart(event):
    for _ in range(2):
        for frame in HEART_FRAMES:
            await event.edit(f"**❤️ Animation Heart ❤️**\n\n{frame}")
            await asyncio.sleep(0.3)

async def animate_wave(event):
    for _ in range(3):
        for frame in WAVE_FRAMES:
            await event.edit(f"**🌊 Wave Animation**\n\n{frame}")
            await asyncio.sleep(0.2)

async def animate_beat(event):
    for _ in range(3):
        for frame in BEAT_FRAMES:
            await event.edit(f"**💓 Heartbeat**\n\n{frame}")
            await asyncio.sleep(0.4)

async def animate_love(event):
    for _ in range(2):
        for frame in LOVE_FRAMES:
            await event.edit(f"**💝 Love Animation**\n\n{frame}")
            await asyncio.sleep(0.3)

async def animate_moon(event):
    for _ in range(2):
        for frame in MOON_FRAMES:
            await event.edit(f"**🌙 Moon Phase**\n\n{frame}")
            await asyncio.sleep(0.3)

async def animate_moon2(event):
    for _ in range(2):
        for frame in MOON2_FRAMES:
            await event.edit(f"**🌕 Moon 2**\n\n{frame}")
            await asyncio.sleep(0.3)

async def animate_clock2(event):
    for _ in range(2):
        for frame in CLOCK2_FRAMES:
            await event.edit(f"**🕐 Clock**\n\n{frame}")
            await asyncio.sleep(0.2)

async def animate_thunder(event):
    for _ in range(3):
        for frame in THUNDER_FRAMES:
            await event.edit(f"**⚡ Thunder**\n\n{frame}")
            await asyncio.sleep(0.3)

async def animate_color_heart(event):
    for _ in range(2):
        for frame in COLOR_HEART_FRAMES:
            await event.edit(f"**🌈 Colored Heart**\n\n{frame}  {frame}  {frame}")
            await asyncio.sleep(0.3)

async def animate_earth(event):
    for _ in range(3):
        for frame in EARTH_FRAMES:
            await event.edit(f"**🌍 Earth Spin**\n\n{frame}")
            await asyncio.sleep(0.5)

async def animate_typing(event):
    for _ in range(3):
        for frame in TYPING_FRAMES:
            await event.edit(f"**⌨️ Typing...**\n\n{frame}")
            await asyncio.sleep(0.15)

async def animate_progress(event):
    for frame in PROGRESS_FRAMES:
        await event.edit(f"**📊 Progress**\n\n{frame}")
        await asyncio.sleep(0.3)
