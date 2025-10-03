import sqlite3
import logging
import random
from datetime import datetime, timedelta

DATABASE_PATH = 'users.db'
DEFAULT_CONFIG_TEXT = "Default VPN configuration"

def init_db():
    """Инициализация базы данных: создание таблиц users и config."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        # Таблица пользователей
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                    (user_id INTEGER PRIMARY KEY, 
                     username TEXT, 
                     internal_id TEXT UNIQUE, 
                     registration_date DATETIME)''')
        # Таблица для хранения конфига
        c.execute('''CREATE TABLE IF NOT EXISTS config 
                    (id INTEGER PRIMARY KEY, 
                     config_text TEXT)''')
        # Проверяем, есть ли конфиг в базе
        c.execute("SELECT config_text FROM config WHERE id = 1")
        if not c.fetchone():
            c.execute("INSERT INTO config (id, config_text) VALUES (?, ?)", (1, DEFAULT_CONFIG_TEXT))
        # Обратная совместимость: добавляем registration_date, если отсутствует
        c.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in c.fetchall()]
        if 'registration_date' not in columns:
            c.execute("ALTER TABLE users ADD COLUMN registration_date DATETIME")
            c.execute("UPDATE users SET registration_date = ?", (datetime.now(),))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка инициализации базы данных: {e}")
    finally:
        conn.close()

def get_current_config():
    """Получение текущего конфига из базы данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT config_text FROM config WHERE id = 1")
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        logging.error(f"Ошибка получения конфига из базы: {e}")
        return None

def generate_config():
    """Генерация уникального internal_id и получение текущего конфига."""
    internal_id = f"VPN-{random.randint(100, 999)}"
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        while True:
            c.execute("SELECT internal_id FROM users WHERE internal_id = ?", (internal_id,))
            if not c.fetchone():
                break
            internal_id = f"VPN-{random.randint(100, 999)}"
        conn.close()
        config_text = get_current_config()
        if config_text is None:
            return None, None
        return internal_id, config_text
    except sqlite3.Error as e:
        logging.error(f"Ошибка генерации internal_id: {e}")
        return None, None

def register_user(user_id, username):
    """Регистрация нового пользователя в базе данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        internal_id, config = generate_config()
        if internal_id is None or config is None:
            return None, None
        c.execute("INSERT INTO users (user_id, username, internal_id, registration_date) VALUES (?, ?, ?, ?)",
                 (user_id, username, internal_id, datetime.now()))
        conn.commit()
        conn.close()
        return internal_id, config
    except sqlite3.Error as e:
        logging.error(f"Ошибка регистрации пользователя: {e}")
        return None, None

def get_user_internal_id(user_id):
    """Получение internal_id пользователя по user_id."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT internal_id FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except sqlite3.Error as e:
        logging.error(f"Ошибка получения internal_id: {e}")
        return None

def update_config(new_config):
    """Обновление конфига в базе данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM config WHERE id = 1")
        c.execute("INSERT INTO config (id, config_text) VALUES (?, ?)", (1, new_config))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logging.error(f"Ошибка обновления конфига в базе: {e}")
        return False

def get_user_stats():
    """Получение статистики пользователей."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE registration_date >= ?",
                 (datetime.now() - timedelta(hours=24),))
        users_24h = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE registration_date >= ?",
                 (datetime.now() - timedelta(days=3),))
        users_3d = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE registration_date >= ?",
                 (datetime.now() - timedelta(days=7),))
        users_7d = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE registration_date >= ?",
                 (datetime.now() - timedelta(days=30),))
        users_30d = c.fetchone()[0]
        conn.close()
        return {
            "total": total_users,
            "24h": users_24h,
            "3d": users_3d,
            "7d": users_7d,
            "30d": users_30d
        }
    except sqlite3.Error as e:
        logging.error(f"Ошибка получения статистики пользователей: {e}")
        return None

def get_all_user_ids():
    """Получение всех user_id из базы данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id FROM users")
        users = [row[0] for row in c.fetchall()]
        conn.close()
        return users
    except sqlite3.Error as e:
        logging.error(f"Ошибка получения списка пользователей: {e}")

        return []

def get_all_users():
    """Получение всех данных пользователей из базы данных."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, internal_id, username, registration_date FROM users")
        users = [
            {
                "tg_id": row[0],
                "vpn_id": row[1],
                "username": row[2],
                "registered_at": row[3]
            } for row in c.fetchall()
        ]
        conn.close()
        return users
    except sqlite3.Error as e:
        logging.error(f"Ошибка получения данных пользователей: {e}")
        return None
