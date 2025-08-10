"""
Конфигурация бота для Gates of Olympus AI Bot.

Этот модуль содержит все настройки бота, включая токены, ссылки,
настройки базы данных и планировщика.
"""

import os
from typing import Optional

# Загружаем переменные окружения из .env файла (если файл существует)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не установлен, используем значения по умолчанию


class BotConfig:
    """Конфигурация Telegram бота."""
    
    # Telegram Bot Token (строка)
    TOKEN: str = os.getenv("BOT_TOKEN", "7790674836:AAH88tJkBUBTj5SsCduxZHVfrno-Gudpt30")
    
    # Admin User ID (целое число)
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "578529330"))


class LinksConfig:
    """Конфигурация ссылок."""
    
    # Casino Bonus Link (ссылка на бонус казино)
    BONUS_LINK: str = os.getenv("BONUS_LINK", "https://your-casino-link.com?ref=promo")
    
    # Telegram Group Link (ссылка на группу Telegram)
    GROUP_LINK: str = os.getenv("GROUP_LINK", "https://t.me/+MmF7VX1_WsU4ZTEy")


class ImagesConfig:
    """Конфигурация изображений."""
    
    # Базовая папка для изображений
    IMAGES_DIR: str = os.getenv("IMAGES_DIR", "assets/images")
    
    # Пути к изображениям для различных меню
    WELCOME_IMAGE: str = os.path.join(IMAGES_DIR, os.getenv("WELCOME_IMAGE", "welcome.png"))
    REGISTRATION_IMAGE: str = os.path.join(IMAGES_DIR, os.getenv("REGISTRATION_IMAGE", "registration.png"))
    MAIN_MENU_IMAGE: str = os.path.join(IMAGES_DIR, os.getenv("MAIN_MENU_IMAGE", "main_menu.png"))


class DatabaseConfig:
    """Конфигурация базы данных."""
    
    # Database Path (путь к файлу базы данных)
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "users.db")


class SchedulerConfig:
    """Конфигурация планировщика."""
    
    # Signal Interval Settings (интервалы генерации сигналов в минутах)
    MIN_SIGNAL_INTERVAL: int = int(os.getenv("MIN_SIGNAL_INTERVAL", "40"))
    MAX_SIGNAL_INTERVAL: int = int(os.getenv("MAX_SIGNAL_INTERVAL", "80"))
    
    @classmethod
    def validate_intervals(cls) -> bool:
        """Проверяет корректность интервалов генерации сигналов."""
        if cls.MIN_SIGNAL_INTERVAL <= 0 or cls.MAX_SIGNAL_INTERVAL <= 0:
            return False
        if cls.MIN_SIGNAL_INTERVAL > cls.MAX_SIGNAL_INTERVAL:
            return False
        return True


class NotificationConfig:
    """Конфигурация уведомлений и сообщений."""
    
    # Win Notification Settings (настройки уведомлений о выигрышах в часах)
    WIN_NOTIFICATION_INTERVAL_MIN: int = int(os.getenv("WIN_NOTIFICATION_INTERVAL_MIN", "4"))
    WIN_NOTIFICATION_INTERVAL_MAX: int = int(os.getenv("WIN_NOTIFICATION_INTERVAL_MAX", "8"))
    
    # Motivational Message Settings (настройки мотивационных сообщений в часах)
    MOTIVATIONAL_INTERVAL_MIN: int = int(os.getenv("MOTIVATIONAL_INTERVAL_MIN", "8"))
    MOTIVATIONAL_INTERVAL_MAX: int = int(os.getenv("MOTIVATIONAL_INTERVAL_MAX", "12"))
    
    # Win Notification User Selection (процент от общего числа пользователей)
    WIN_NOTIFICATION_USER_PERCENTAGE_MIN: int = int(os.getenv("WIN_NOTIFICATION_USER_PERCENTAGE_MIN", "100"))
    WIN_NOTIFICATION_USER_PERCENTAGE_MAX: int = int(os.getenv("WIN_NOTIFICATION_USER_PERCENTAGE_MAX", "100"))
    WIN_NOTIFICATION_MAX_USERS: int = int(os.getenv("WIN_NOTIFICATION_MAX_USERS", "100"))
    
    # Motivational Message User Selection (процент от пользователей с авто-сигналами)
    MOTIVATIONAL_USER_PERCENTAGE_MIN: int = int(os.getenv("MOTIVATIONAL_USER_PERCENTAGE_MIN", "100"))
    MOTIVATIONAL_USER_PERCENTAGE_MAX: int = int(os.getenv("MOTIVATIONAL_USER_PERCENTAGE_MAX", "100"))
    MOTIVATIONAL_MAX_USERS: int = int(os.getenv("MOTIVATIONAL_MAX_USERS", "100"))
    
    # Message Delay Settings (задержки между отправками сообщений в секундах)
    WIN_NOTIFICATION_DELAY_MIN: float = float(os.getenv("WIN_NOTIFICATION_DELAY_MIN", "1.0"))
    WIN_NOTIFICATION_DELAY_MAX: float = float(os.getenv("WIN_NOTIFICATION_DELAY_MAX", "3.0"))
    MOTIVATIONAL_DELAY_MIN: float = float(os.getenv("MOTIVATIONAL_DELAY_MIN", "2.0"))
    MOTIVATIONAL_DELAY_MAX: float = float(os.getenv("MOTIVATIONAL_DELAY_MAX", "5.0"))
    
    @classmethod
    def validate_notification_settings(cls) -> bool:
        """Проверяет корректность настроек уведомлений."""
        if (cls.WIN_NOTIFICATION_INTERVAL_MIN <= 0 or cls.WIN_NOTIFICATION_INTERVAL_MAX <= 0 or
            cls.MOTIVATIONAL_INTERVAL_MIN <= 0 or cls.MOTIVATIONAL_INTERVAL_MAX <= 0):
            return False
        if (cls.WIN_NOTIFICATION_INTERVAL_MIN > cls.WIN_NOTIFICATION_INTERVAL_MAX or
            cls.MOTIVATIONAL_INTERVAL_MIN > cls.MOTIVATIONAL_INTERVAL_MAX):
            return False
        if (cls.WIN_NOTIFICATION_USER_PERCENTAGE_MIN <= 0 or 
            cls.WIN_NOTIFICATION_USER_PERCENTAGE_MAX <= 0 or
            cls.MOTIVATIONAL_USER_PERCENTAGE_MIN <= 0 or 
            cls.MOTIVATIONAL_USER_PERCENTAGE_MAX <= 0):
            return False
        return True


class SignalGenerationConfig:
    """Конфигурация генерации сигналов."""
    
    # Manual Signal Generation Cooldown (кулдаун ручной генерации сигналов в минутах)
    MANUAL_SIGNAL_COOLDOWN: int = int(os.getenv("MANUAL_SIGNAL_COOLDOWN", "10"))
    
    # Auto Signal Generation Settings (включение авто-генерации сигналов)
    AUTO_SIGNAL_ENABLED: bool = os.getenv("AUTO_SIGNAL_ENABLED", "true").lower() == "true"
    
    # Signal Quality Settings (настройки качества сигналов в процентах)
    MIN_SIGNAL_ACCURACY: int = int(os.getenv("MIN_SIGNAL_ACCURACY", "75"))
    MAX_SIGNAL_ACCURACY: int = int(os.getenv("MAX_SIGNAL_ACCURACY", "98"))
    
    # Signal Multiplier Range (диапазон множителей сигналов)
    MIN_SIGNAL_MULTIPLIER: int = int(os.getenv("MIN_SIGNAL_MULTIPLIER", "50"))
    MAX_SIGNAL_MULTIPLIER: int = int(os.getenv("MAX_SIGNAL_MULTIPLIER", "1000"))
    
    @classmethod
    def validate_signal_settings(cls) -> bool:
        """Проверяет корректность настроек генерации сигналов."""
        if (cls.MANUAL_SIGNAL_COOLDOWN <= 0 or
            cls.MIN_SIGNAL_ACCURACY <= 0 or cls.MAX_SIGNAL_ACCURACY <= 0 or
            cls.MIN_SIGNAL_MULTIPLIER <= 0 or cls.MAX_SIGNAL_MULTIPLIER <= 0):
            return False
        if (cls.MIN_SIGNAL_ACCURACY > cls.MAX_SIGNAL_ACCURACY or
            cls.MIN_SIGNAL_MULTIPLIER > cls.MAX_SIGNAL_MULTIPLIER):
            return False
        return True


class LoggingConfig:
    """Конфигурация логирования."""
    
    # Logging Level (уровень логирования)
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Log File Settings (настройки файла логов)
    LOG_FILE: str = os.getenv("LOG_FILE", "bot.log")
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB в байтах
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))


# Экспортируем все конфигурации для обратной совместимости
TOKEN = BotConfig.TOKEN
BONUS_LINK = LinksConfig.BONUS_LINK
GROUP_LINK = LinksConfig.GROUP_LINK
ADMIN_ID = BotConfig.ADMIN_ID
DATABASE_PATH = DatabaseConfig.DATABASE_PATH
MIN_SIGNAL_INTERVAL = SchedulerConfig.MIN_SIGNAL_INTERVAL
MAX_SIGNAL_INTERVAL = SchedulerConfig.MAX_SIGNAL_INTERVAL
LOG_LEVEL = LoggingConfig.LOG_LEVEL
LOG_FORMAT = LoggingConfig.LOG_FORMAT

# Новые экспорты для уведомлений и сигналов
WIN_NOTIFICATION_INTERVAL_MIN = NotificationConfig.WIN_NOTIFICATION_INTERVAL_MIN
WIN_NOTIFICATION_INTERVAL_MAX = NotificationConfig.WIN_NOTIFICATION_INTERVAL_MAX
MOTIVATIONAL_INTERVAL_MIN = NotificationConfig.MOTIVATIONAL_INTERVAL_MIN
MOTIVATIONAL_INTERVAL_MAX = NotificationConfig.MOTIVATIONAL_INTERVAL_MAX
MANUAL_SIGNAL_COOLDOWN = SignalGenerationConfig.MANUAL_SIGNAL_COOLDOWN
AUTO_SIGNAL_ENABLED = SignalGenerationConfig.AUTO_SIGNAL_ENABLED

# Экспорты для изображений
IMAGES_DIR = ImagesConfig.IMAGES_DIR
WELCOME_IMAGE = ImagesConfig.WELCOME_IMAGE
REGISTRATION_IMAGE = ImagesConfig.REGISTRATION_IMAGE
MAIN_MENU_IMAGE = ImagesConfig.MAIN_MENU_IMAGE 