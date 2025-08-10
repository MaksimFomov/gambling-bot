"""
Модуль для работы с базой данных.

Содержит все функции для работы с SQLite базой данных:
- Инициализация базы данных
- Операции с пользователями
- Управление сигналами
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from contextlib import contextmanager

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """Контекстный менеджер для работы с базой данных."""
    conn = None
    try:
        conn = sqlite3.connect(DatabaseConfig.DATABASE_PATH, timeout=30.0)
        # Включаем внешние ключи
        conn.execute("PRAGMA foreign_keys = ON")
        # Включаем WAL режим для лучшей производительности
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка операций с БД: {e}")
        raise
    except sqlite3.DatabaseError as e:
        logger.error(f"Ошибка базы данных: {e}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка БД: {e}")
        raise
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения с БД: {e}")


class DatabaseManager:
    """Менеджер для работы с базой данных."""
    
    @staticmethod
    def init_database() -> bool:
        """
        Инициализирует базу данных и создает необходимые таблицы.
        
        Returns:
            bool: True если инициализация прошла успешно, False в противном случае
        """
        try:
            # Проверяем, существует ли директория для БД
            import os
            db_dir = os.path.dirname(DatabaseConfig.DATABASE_PATH)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)
                logger.info(f"Создана директория для БД: {db_dir}")
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Создаем таблицу пользователей
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        registered INTEGER DEFAULT 0,
                        auto_signal INTEGER DEFAULT 0,
                        joined_at TEXT,
                        last_signal_text TEXT,
                        last_signal_time TEXT,
                        next_signal_update TEXT,
                        current_menu INTEGER DEFAULT 1
                    )
                """)
                
                # Создаем индексы для улучшения производительности
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_registered ON users(registered)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_auto_signal ON users(auto_signal)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_joined_at ON users(joined_at)")
                
                conn.commit()
            
            logger.info("База данных инициализирована успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")
            return False
    
    @staticmethod
    def add_user(user_id: int, username: Optional[str] = None) -> bool:
        """
        Добавляет нового пользователя в базу данных.
        
        Args:
            user_id: ID пользователя в Telegram
            username: Имя пользователя (опционально)
            
        Returns:
            bool: True если пользователь добавлен успешно
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, joined_at) VALUES (?, ?, ?)",
                    (user_id, username, datetime.utcnow().isoformat())
                )
                conn.commit()
            
            logger.info(f"Пользователь {user_id} добавлен в БД")
            return True
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user(user_id: int) -> Optional[Tuple]:
        """
        Получает информацию о пользователе из базы данных.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Tuple с данными пользователя или None если пользователь не найден
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user(user_id: int, field: str, value: Any) -> bool:
        """
        Обновляет поле пользователя в базе данных.
        
        Args:
            user_id: ID пользователя в Telegram
            field: Название поля для обновления
            value: Новое значение
            
        Returns:
            bool: True если обновление прошло успешно
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
                conn.commit()
            
            logger.debug(f"Обновлено поле {field} для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления пользователя {user_id}: {e}")
            return False
    
    @staticmethod
    def get_user_signal_info(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о последнем сигнале пользователя.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            Dict с информацией о сигнале или None если сигнал не найден
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT last_signal_text, last_signal_time, next_signal_update FROM users WHERE user_id = ?", 
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if result and result[0]:
                    return {
                        "text": result[0],
                        "time": datetime.fromisoformat(result[1]) if result[1] else None,
                        "next_update": datetime.fromisoformat(result[2]) if result[2] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Ошибка получения сигнала пользователя {user_id}: {e}")
            return None
    
    @staticmethod
    def update_user_signal(user_id: int, signal_text: str, signal_time: datetime, next_update: datetime) -> bool:
        """
        Обновляет информацию о сигнале пользователя.
        
        Args:
            user_id: ID пользователя в Telegram
            signal_text: Текст сигнала
            signal_time: Время генерации сигнала
            next_update: Время следующего обновления
            
        Returns:
            bool: True если обновление прошло успешно
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users 
                    SET last_signal_text = ?, last_signal_time = ?, next_signal_update = ? 
                    WHERE user_id = ?
                """, (signal_text, signal_time.isoformat(), next_update.isoformat(), user_id))
                conn.commit()
            
            logger.debug(f"Обновлен сигнал для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка обновления сигнала пользователя {user_id}: {e}")
            return False
    
    @staticmethod
    def get_users_with_auto_signals() -> List[int]:
        """
        Получает список пользователей с включенными авто-сигналами.
        
        Returns:
            List[int]: Список ID пользователей
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE auto_signal = 1")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка получения пользователей с авто-сигналами: {e}")
            return []
    
    @staticmethod
    def get_statistics() -> Dict[str, int]:
        """
        Получает статистику пользователей.
        
        Returns:
            Dict[str, int]: Статистика с ключами 'total', 'registered', 'auto_on'
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM users")
                total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE registered = 1")
                registered = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM users WHERE auto_signal = 1")
                auto_on = cursor.fetchone()[0]
                
                return {
                    'total': total,
                    'registered': registered,
                    'auto_on': auto_on
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {'total': 0, 'registered': 0, 'auto_on': 0}


# Функции для обратной совместимости
def init_db() -> bool:
    """Инициализация базы данных (для обратной совместимости)."""
    return DatabaseManager.init_database()


def add_user(user_id: int, username: Optional[str] = None) -> bool:
    """Добавление пользователя (для обратной совместимости)."""
    return DatabaseManager.add_user(user_id, username)


def get_user(user_id: int) -> Optional[Tuple]:
    """Получение пользователя (для обратной совместимости)."""
    return DatabaseManager.get_user(user_id)


def update_user(user_id: int, field: str, value: Any) -> bool:
    """Обновление пользователя (для обратной совместимости)."""
    return DatabaseManager.update_user(user_id, field, value)


def get_user_signal_info(user_id: int) -> Optional[Dict[str, Any]]:
    """Получение информации о сигнале (для обратной совместимости)."""
    return DatabaseManager.get_user_signal_info(user_id)


def update_user_signal(user_id: int, signal_text: str, signal_time: datetime, next_update: datetime) -> bool:
    """Обновление сигнала (для обратной совместимости)."""
    return DatabaseManager.update_user_signal(user_id, signal_text, signal_time, next_update) 