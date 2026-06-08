import sqlite3
import os
import json
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "selfbot.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        phone TEXT,
        first_name TEXT DEFAULT '',
        last_name TEXT DEFAULT '',
        license_key TEXT,
        license_expiry TEXT,
        is_active INTEGER DEFAULT 0,
        joined_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        permissions TEXT DEFAULT '{}',
        added_by INTEGER,
        added_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS licenses (
        key TEXT PRIMARY KEY,
        duration_days INTEGER,
        created_by INTEGER,
        used_by INTEGER,
        used_at TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS settings (
        user_id INTEGER,
        setting TEXT,
        value TEXT,
        PRIMARY KEY (user_id, setting)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS silence_list (
        user_id INTEGER,
        silenced_by INTEGER,
        until TEXT,
        reason TEXT,
        PRIMARY KEY (user_id, silenced_by)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS friends (
        user_id INTEGER,
        friend_id INTEGER,
        custom_msg TEXT DEFAULT '',
        added_at TEXT,
        PRIMARY KEY (user_id, friend_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS enemies (
        user_id INTEGER,
        enemy_id INTEGER,
        custom_msg TEXT DEFAULT '',
        added_at TEXT,
        PRIMARY KEY (user_id, enemy_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS crushes (
        user_id INTEGER,
        crush_id INTEGER,
        custom_msg TEXT DEFAULT '',
        added_at TEXT,
        PRIMARY KEY (user_id, crush_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS secretary_msgs (
        user_id INTEGER,
        step INTEGER,
        message TEXT,
        PRIMARY KEY (user_id, step)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        card_number TEXT,
        amount TEXT,
        receipt_photo TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS force_join (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        chat_title TEXT,
        added_by INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS timed_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message_text TEXT,
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS custom_status (
        user_id INTEGER PRIMARY KEY,
        status_type TEXT DEFAULT 'none',
        status_text TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS login_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        phone TEXT,
        code TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS user_accounts (
        user_id INTEGER PRIMARY KEY,
        phone TEXT,
        session_file TEXT,
        is_loggedin INTEGER DEFAULT 0,
        added_by INTEGER,
        stars INTEGER DEFAULT 0,
        gifts INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def get_setting(user_id, setting, default=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE user_id=? AND setting=?", (user_id, setting))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default

def set_setting(user_id, setting, value):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO settings (user_id, setting, value) VALUES (?,?,?)", (user_id, setting, str(value)))
    conn.commit()
    conn.close()

def is_silenced(user_id, silenced_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT until FROM silence_list WHERE user_id=? AND silenced_by=?", (user_id, silenced_by))
    row = c.fetchone()
    conn.close()
    if row:
        until = row[0]
        if until == "forever":
            return True
        if until:
            try:
                until_dt = datetime.fromisoformat(until)
                if datetime.now() < until_dt:
                    return True
                else:
                    remove_silence(user_id, silenced_by)
                    return False
            except:
                return True
    return False

def add_silence(user_id, silenced_by, duration_minutes=None):
    conn = get_conn()
    c = conn.cursor()
    if duration_minutes:
        until = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
    else:
        until = "forever"
    c.execute("REPLACE INTO silence_list (user_id, silenced_by, until) VALUES (?,?,?)", (user_id, silenced_by, until))
    conn.commit()
    conn.close()

def remove_silence(user_id, silenced_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM silence_list WHERE user_id=? AND silenced_by=?", (user_id, silenced_by))
    conn.commit()
    conn.close()

def get_silence_list(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, until FROM silence_list WHERE silenced_by=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_friend(user_id, friend_id, custom_msg=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO friends (user_id, friend_id, custom_msg, added_at) VALUES (?,?,?,?)",
              (user_id, friend_id, custom_msg, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def remove_friend(user_id, friend_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM friends WHERE user_id=? AND friend_id=?", (user_id, friend_id))
    conn.commit()
    conn.close()

def add_enemy(user_id, enemy_id, custom_msg=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO enemies (user_id, enemy_id, custom_msg, added_at) VALUES (?,?,?,?)",
              (user_id, enemy_id, custom_msg, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def remove_enemy(user_id, enemy_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM enemies WHERE user_id=? AND enemy_id=?", (user_id, enemy_id))
    conn.commit()
    conn.close()

def add_crush(user_id, crush_id, custom_msg=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO crushes (user_id, crush_id, custom_msg, added_at) VALUES (?,?,?,?)",
              (user_id, crush_id, custom_msg, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def remove_crush(user_id, crush_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM crushes WHERE user_id=? AND crush_id=?", (user_id, crush_id))
    conn.commit()
    conn.close()

def get_list(user_id, list_type):
    conn = get_conn()
    c = conn.cursor()
    table = {"friend": "friends", "enemy": "enemies", "crush": "crushes"}.get(list_type)
    if not table:
        conn.close()
        return []
    c.execute(f"SELECT * FROM {table} WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_license(key, duration_days, created_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO licenses (key, duration_days, created_by, created_at) VALUES (?,?,?,?)",
              (key, duration_days, created_by, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def use_license(key, user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE key=? AND used_by IS NULL", (key,))
    row = c.fetchone()
    if row:
        c.execute("UPDATE licenses SET used_by=?, used_at=? WHERE key=?",
                  (user_id, datetime.now().isoformat(), key))
        c.execute("UPDATE users SET license_key=?, license_expiry=?, is_active=1 WHERE user_id=?",
                  (key, (datetime.now() + timedelta(days=row[1])).isoformat(), user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def check_license(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT license_expiry, is_active FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if not row or not row[1]:
        return False
    if row[0]:
        try:
            exp = datetime.fromisoformat(row[0])
            if datetime.now() > exp:
                return False
        except:
            return False
    return True

def is_admin(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM admins WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def get_admin_permissions(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT permissions FROM admins WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}

def set_admin_permissions(user_id, permissions, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO admins (user_id, permissions, added_by, added_at) VALUES (?,?,?,?)",
              (user_id, json.dumps(permissions), added_by, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def get_all_admins():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM admins")
    rows = c.fetchall()
    conn.close()
    return rows

def set_secretary_msgs(user_id, messages):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM secretary_msgs WHERE user_id=?", (user_id,))
    for i, msg in enumerate(messages[:3], 1):
        c.execute("INSERT INTO secretary_msgs (user_id, step, message) VALUES (?,?,?)", (user_id, i, msg))
    conn.commit()
    conn.close()

def get_secretary_msgs(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT step, message FROM secretary_msgs WHERE user_id=? ORDER BY step", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_payment(user_id, card_number, amount, receipt_photo):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO payments (user_id, card_number, amount, receipt_photo, created_at) VALUES (?,?,?,?,?)",
              (user_id, card_number, amount, receipt_photo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_pending_payments():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE status='pending' ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def approve_payment(payment_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE payments SET status='approved' WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()

def reject_payment(payment_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE payments SET status='rejected' WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()

def add_force_join(chat_id, chat_title, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO force_join (chat_id, chat_title, added_by) VALUES (?,?,?)",
              (chat_id, chat_title, added_by))
    conn.commit()
    conn.close()

def remove_force_join(chat_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM force_join WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def get_force_joins():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM force_join")
    rows = c.fetchall()
    conn.close()
    return rows

def save_timed_message(user_id, text):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO timed_messages (user_id, message_text, created_at) VALUES (?,?,?)",
              (user_id, text, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_timed_messages(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM timed_messages WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_login_attempt(user_id, phone, code=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO login_attempts (user_id, phone, code, status, created_at) VALUES (?,?,?,?,?)",
              (user_id, phone, code, "pending" if not code else "code_received", datetime.now().isoformat()))
    conn.commit()
    conn.close()

def update_login_attempt(user_id, code):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE login_attempts SET code=?, status='code_received' WHERE user_id=? AND status='pending'",
              (code, user_id))
    conn.commit()
    conn.close()

def get_login_attempts(limit=20):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM login_attempts ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_user_account(user_id, phone, session_file, added_by):
    conn = get_conn()
    c = conn.cursor()
    c.execute("REPLACE INTO user_accounts (user_id, phone, session_file, is_loggedin, added_by) VALUES (?,?,?,1,?)",
              (user_id, phone, session_file, added_by))
    conn.commit()
    conn.close()

def set_login_state(user_id, step, data):
    set_setting(user_id, "login_step", step)
    set_setting(user_id, "login_data", json.dumps(data) if data else "")

def get_login_state(user_id):
    step = get_setting(user_id, "login_step", None)
    if step is None:
        return None, None
    raw = get_setting(user_id, "login_data", "{}")
    try:
        data = json.loads(raw)
    except:
        data = {}
    return step, data

def clear_login_state(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM settings WHERE user_id=? AND (setting='login_step' OR setting='login_data')", (user_id,))
    conn.commit()
    conn.close()

def is_user_loggedin(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT is_loggedin FROM user_accounts WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] == 1

def get_all_accounts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM user_accounts")
    rows = c.fetchall()
    conn.close()
    return rows

def remove_account(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM user_accounts WHERE user_id=?", (user_id,))
    c.execute("UPDATE users SET is_active=0 WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM settings WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM secretary_msgs WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM timed_messages WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM friends WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM enemies WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM crushes WHERE user_id=?", (user_id,))
    c.execute("DELETE FROM silence_list WHERE user_id=? OR silenced_by=?", (user_id, user_id))
    c.execute("DELETE FROM payments WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    import os
    session_path = os.path.join(os.path.dirname(__file__), "sessions", f"user_{user_id}.session")
    if os.path.exists(session_path):
        os.remove(session_path)
    temp_path = os.path.join(os.path.dirname(__file__), "sessions", f"temp_{user_id}.session")
    if os.path.exists(temp_path):
        os.remove(temp_path)

init_db()
