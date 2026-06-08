import sqlite3
import json
from config import DB_PATH

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone TEXT,
                license_key TEXT,
                license_expire REAL,
                is_active INTEGER DEFAULT 1,
                joined_at REAL
            );
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER,
                key TEXT,
                value TEXT,
                PRIMARY KEY (user_id, key)
            );
            CREATE TABLE IF NOT EXISTS silences (
                owner_id INTEGER,
                target_id INTEGER,
                until REAL,
                PRIMARY KEY (owner_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS enemies (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS crushes (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS force_joins (
                user_id INTEGER,
                chat_id INTEGER,
                chat_title TEXT,
                PRIMARY KEY (user_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS secretary (
                user_id INTEGER,
                msg_order INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, msg_order)
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                card_number TEXT,
                amount REAL,
                receipt_photo TEXT,
                status TEXT DEFAULT 'pending',
                created_at REAL
            );
            CREATE TABLE IF NOT EXISTS licenses (
                code TEXT PRIMARY KEY,
                duration_days INTEGER,
                created_by INTEGER,
                used_by INTEGER,
                created_at REAL,
                activated_at REAL
            );
            CREATE TABLE IF NOT EXISTS enemy_texts (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS friend_texts (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS crush_texts (
                user_id INTEGER,
                target_id INTEGER,
                text TEXT,
                PRIMARY KEY (user_id, target_id)
            );
            CREATE TABLE IF NOT EXISTS broadcast_groups (
                user_id INTEGER,
                group_id INTEGER,
                group_title TEXT,
                PRIMARY KEY (user_id, group_id)
            );
            CREATE TABLE IF NOT EXISTS panel_states (
                user_id INTEGER,
                module TEXT,
                state INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, module)
            );
        """)
        self.conn.commit()

    def get_setting(self, user_id, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE user_id=? AND key=?", (user_id, key))
        row = self.cursor.fetchone()
        return row[0] if row else default

    def set_setting(self, user_id, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (user_id, key, value) VALUES (?,?,?)", (user_id, key, value))
        self.conn.commit()

    def get_panel_state(self, user_id, module):
        self.cursor.execute("SELECT state FROM panel_states WHERE user_id=? AND module=?", (user_id, module))
        row = self.cursor.fetchone()
        return row[0] if row else 0

    def set_panel_state(self, user_id, module, state):
        self.cursor.execute("INSERT OR REPLACE INTO panel_states (user_id, module, state) VALUES (?,?,?)", (user_id, module, state))
        self.conn.commit()

    def toggle_panel_state(self, user_id, module):
        current = self.get_panel_state(user_id, module)
        new_state = 0 if current else 1
        self.set_panel_state(user_id, module, new_state)
        return new_state

    def is_silenced(self, owner_id, target_id):
        import time
        self.cursor.execute("SELECT until FROM silences WHERE owner_id=? AND target_id=?", (owner_id, target_id))
        row = self.cursor.fetchone()
        if row:
            if row[0] == 0 or row[0] > time.time():
                return True
            self.cursor.execute("DELETE FROM silences WHERE owner_id=? AND target_id=?", (owner_id, target_id))
            self.conn.commit()
        return False

    def add_silence(self, owner_id, target_id, until=0):
        self.cursor.execute("INSERT OR REPLACE INTO silences (owner_id, target_id, until) VALUES (?,?,?)", (owner_id, target_id, until))
        self.conn.commit()

    def remove_silence(self, owner_id, target_id):
        self.cursor.execute("DELETE FROM silences WHERE owner_id=? AND target_id=?", (owner_id, target_id))
        self.conn.commit()

    def get_silence_list(self, owner_id):
        self.cursor.execute("SELECT target_id, until FROM silences WHERE owner_id=?", (owner_id,))
        return self.cursor.fetchall()

    def add_license(self, code, duration_days, created_by):
        import time
        self.cursor.execute("INSERT INTO licenses (code, duration_days, created_by, created_at) VALUES (?,?,?,?)",
                          (code, duration_days, created_by, time.time()))
        self.conn.commit()

    def activate_license(self, code, user_id):
        import time
        self.cursor.execute("UPDATE licenses SET used_by=?, activated_at=? WHERE code=? AND used_by IS NULL",
                          (user_id, time.time(), code))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def check_license(self, user_id):
        self.cursor.execute("SELECT license_expire FROM users WHERE user_id=?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return False
        import time
        return row[0] > time.time()

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return self.cursor.fetchone()

    def add_user(self, user_id, phone, license_expire):
        import time
        self.cursor.execute("INSERT OR REPLACE INTO users (user_id, phone, license_expire, is_active, joined_at) VALUES (?,?,?,1,?)",
                          (user_id, phone, license_expire, time.time()))
        self.conn.commit()

    def deactivate_user(self, user_id):
        self.cursor.execute("UPDATE users SET is_active=0 WHERE user_id=?", (user_id,))
        self.conn.commit()

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        for table in ["settings", "silences", "enemies", "friends", "crushes", "force_joins", "secretary", "payments", "panel_states"]:
            self.cursor.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
        self.conn.commit()

    def add_enemy(self, user_id, target_id, text=""):
        self.cursor.execute("INSERT OR REPLACE INTO enemies (user_id, target_id, text) VALUES (?,?,?)", (user_id, target_id, text))
        self.conn.commit()

    def add_friend(self, user_id, target_id, text=""):
        self.cursor.execute("INSERT OR REPLACE INTO friends (user_id, target_id, text) VALUES (?,?,?)", (user_id, target_id, text))
        self.conn.commit()

    def add_crush(self, user_id, target_id, text=""):
        self.cursor.execute("INSERT OR REPLACE INTO crushes (user_id, target_id, text) VALUES (?,?,?)", (user_id, target_id, text))
        self.conn.commit()

    def remove_enemy(self, user_id, target_id):
        self.cursor.execute("DELETE FROM enemies WHERE user_id=? AND target_id=?", (user_id, target_id))
        self.conn.commit()

    def remove_friend(self, user_id, target_id):
        self.cursor.execute("DELETE FROM friends WHERE user_id=? AND target_id=?", (user_id, target_id))
        self.conn.commit()

    def remove_crush(self, user_id, target_id):
        self.cursor.execute("DELETE FROM crushes WHERE user_id=? AND target_id=?", (user_id, target_id))
        self.conn.commit()

    def get_list(self, user_id, list_type):
        self.cursor.execute(f"SELECT target_id, text FROM {list_type}s WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()

    def set_secretary(self, user_id, msg_order, text):
        self.cursor.execute("INSERT OR REPLACE INTO secretary (user_id, msg_order, text) VALUES (?,?,?)", (user_id, msg_order, text))
        self.conn.commit()

    def get_secretary(self, user_id):
        self.cursor.execute("SELECT msg_order, text FROM secretary WHERE user_id=? ORDER BY msg_order", (user_id,))
        return self.cursor.fetchall()

    def add_force_join(self, user_id, chat_id, chat_title):
        self.cursor.execute("INSERT OR REPLACE INTO force_joins (user_id, chat_id, chat_title) VALUES (?,?,?)", (user_id, chat_id, chat_title))
        self.conn.commit()

    def remove_force_join(self, user_id, chat_id):
        self.cursor.execute("DELETE FROM force_joins WHERE user_id=? AND chat_id=?", (user_id, chat_id))
        self.conn.commit()

    def get_force_joins(self, user_id):
        self.cursor.execute("SELECT chat_id, chat_title FROM force_joins WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()

    def get_all_users(self):
        self.cursor.execute("SELECT user_id, phone, is_active FROM users")
        return self.cursor.fetchall()

    def add_payment(self, user_id, card_number, amount, receipt_photo):
        import time
        self.cursor.execute("INSERT INTO payments (user_id, card_number, amount, receipt_photo, status, created_at) VALUES (?,?,?,?,'pending',?)",
                          (user_id, card_number, amount, receipt_photo, time.time()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_payments(self, user_id):
        self.cursor.execute("SELECT * FROM payments WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()

    def update_payment_status(self, payment_id, status):
        self.cursor.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
        self.conn.commit()

    def add_broadcast_group(self, user_id, group_id, group_title):
        self.cursor.execute("INSERT OR REPLACE INTO broadcast_groups (user_id, group_id, group_title) VALUES (?,?,?)", (user_id, group_id, group_title))
        self.conn.commit()

    def remove_broadcast_group(self, user_id, group_id):
        self.cursor.execute("DELETE FROM broadcast_groups WHERE user_id=? AND group_id=?", (user_id, group_id))
        self.conn.commit()

    def get_broadcast_groups(self, user_id):
        self.cursor.execute("SELECT group_id, group_title FROM broadcast_groups WHERE user_id=?", (user_id,))
        return self.cursor.fetchall()
