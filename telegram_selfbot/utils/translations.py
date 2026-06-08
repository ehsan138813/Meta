import hashlib
import time

try:
    from googletrans import Translator
    _translator = Translator()
    _available = True
except:
    _available = False

TRANSLATION_TARGETS = {
    "english": "en",
    "arabic": "ar",
    "chinese": "zh-cn",
    "russian": "ru"
}

def translate_text(text, target_lang="en"):
    if not _available:
        return f"[Translation unavailable - install googletrans==4.0.0rc1]"
    try:
        result = _translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        return f"[Error: {str(e)}]"

def get_iran_time():
    import datetime
    utc_now = datetime.datetime.utcnow()
    iran_tz = datetime.timedelta(hours=3, minutes=30)
    iran_time = utc_now + iran_tz
    return iran_time

def format_time(style=1):
    t = get_iran_time()
    styles = {
        1: t.strftime("%H:%M"),
        2: t.strftime("%I:%M %p"),
        3: t.strftime("%H:%M:%S"),
        4: t.strftime("%I:%M:%S %p"),
        5: t.strftime("%H:%M - %Y/%m/%d"),
    }
    return styles.get(style, styles[1])

def generate_license_key():
    raw = f"{time.time()}{hashlib.md5(str(time.time_ns()).encode()).hexdigest()}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:24].upper()
    return "-".join([h[i:i+4] for i in range(0, 24, 4)])
