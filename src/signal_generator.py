"""
Модуль для генерации сигналов.

Содержит логику генерации сигналов для пользователей,
включая проверку времени и создание уникальных сигналов.
"""

import random
import logging
import threading
from datetime import datetime, timedelta
from typing import Optional

from .database import DatabaseManager
from .config import SignalGenerationConfig

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Генератор сигналов для Gates of Olympus."""
    
    # Возможные множители
    MULTIPLIERS = ["x25+", "x50+", "x100+"]
    
    # Возможные количества спинов
    SPIN_COUNTS = [30, 50, 70, 100]
    
    # Диапазон уверенности
    MIN_CONFIDENCE = SignalGenerationConfig.MIN_SIGNAL_ACCURACY
    MAX_CONFIDENCE = SignalGenerationConfig.MAX_SIGNAL_ACCURACY
    
    # Диапазон времени до следующего сигнала (минуты)
    MIN_NEXT_UPDATE = 10
    MAX_NEXT_UPDATE = 25
    
    # Блокировки для каждого пользователя
    _user_locks = {}
    _locks_lock = threading.Lock()
    
    @classmethod
    def _get_user_lock(cls, user_id: int) -> threading.Lock:
        """Получает блокировку для конкретного пользователя."""
        with cls._locks_lock:
            if user_id not in cls._user_locks:
                cls._user_locks[user_id] = threading.Lock()
            return cls._user_locks[user_id]
    
    @classmethod
    def generate_signal_for_user(cls, user_id: int) -> Optional[str]:
        """
        Генерирует сигнал для конкретного пользователя.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            str: Текст сигнала или None если сигнал не может быть сгенерирован
        """
        # Получаем блокировку для пользователя
        user_lock = cls._get_user_lock(user_id)
        
        # Пытаемся получить блокировку
        if not user_lock.acquire(blocking=False):
            logger.warning(f"Попытка генерации сигнала для пользователя {user_id} заблокирована (уже выполняется)")
            return None
        
        try:
            now = datetime.utcnow()
            
            # Получаем информацию о последнем сигнале пользователя
            user_signal_info = DatabaseManager.get_user_signal_info(user_id)
            
            # Проверяем, можно ли генерировать новый сигнал
            if user_signal_info and user_signal_info["next_update"] and now < user_signal_info["next_update"]:
                logger.info(f"Сигнал не генерируется для пользователя {user_id}. Следующее обновление: {user_signal_info['next_update']}")
                return None

            # Генерируем новый сигнал
            signal_text = cls._create_signal_text(now)
            
            # Сохраняем информацию о сигнале для пользователя
            next_update = now + timedelta(minutes=random.randint(cls.MIN_NEXT_UPDATE, cls.MAX_NEXT_UPDATE))
            
            try:
                if DatabaseManager.update_user_signal(user_id, signal_text, now, next_update):
                    logger.info(f"Сгенерирован новый сигнал для пользователя {user_id}. Следующее обновление: {next_update}")
                    return signal_text
                else:
                    logger.error(f"Ошибка сохранения сигнала для пользователя {user_id}")
                    return None
            except Exception as db_error:
                logger.error(f"Ошибка базы данных при генерации сигнала для пользователя {user_id}: {db_error}")
                return None
                
        except Exception as e:
            logger.error(f"Ошибка при генерации сигнала для пользователя {user_id}: {e}")
            return None
        finally:
            # Освобождаем блокировку
            try:
                user_lock.release()
            except Exception as release_error:
                logger.error(f"Ошибка при освобождении блокировки для пользователя {user_id}: {release_error}")
    
    @classmethod
    def generate_signal(cls) -> str:
        """
        Генерирует базовый сигнал (для обратной совместимости).
        
        Returns:
            str: Текст сигнала
        """
        now = datetime.utcnow()
        return cls._create_signal_text(now)
    
    @classmethod
    def _create_signal_text(cls, timestamp: datetime) -> str:
        """
        Создает текст сигнала.
        
        Args:
            timestamp: Время генерации сигнала
            
        Returns:
            str: Текст сигнала
        """
        multiplier = random.choice(cls.MULTIPLIERS)
        spins = random.choice(cls.SPIN_COUNTS)
        confidence = random.randint(cls.MIN_CONFIDENCE, cls.MAX_CONFIDENCE)
        
        return (
            f"📡 *Сигнал от ИИ-бота:*\n\n"
            f"🎰 *Gates of Olympus*\n"
            f"💥 Вероятность выигрыша {multiplier} — *{confidence}%*\n"
            f"🎯 Рекомендуется: *{spins} спинов*\n"
            f"🕒 Время: {timestamp.strftime('%H:%M UTC')}"
        )


# Функции для обратной совместимости
def generate_signal_for_user(user_id: int) -> Optional[str]:
    """Генерация сигнала для пользователя (для обратной совместимости)."""
    return SignalGenerator.generate_signal_for_user(user_id)


def generate_signal() -> str:
    """Генерация базового сигнала (для обратной совместимости)."""
    return SignalGenerator.generate_signal() 