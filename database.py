from typing import Optional
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    db_path = Path('data/users.db')
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            phone TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def save_user(telegram_id: int, phone: str) -> bool:
    """Сохранение пользователя в БД"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (telegram_id, phone)
            VALUES (?, ?)
        ''', (telegram_id, phone))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving user: {e}")
        return False
    finally:
        conn.close()

def get_user_phone(telegram_id: int) -> Optional[str]:
    """Получение номера телефона пользователя"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT phone FROM users WHERE telegram_id = ?', (telegram_id,))
        result = cursor.fetchone()
        
        return result[0] if result else None
    except Exception as e:
        logger.error(f"Error getting user phone: {e}")
        return None
    finally:
        conn.close() 