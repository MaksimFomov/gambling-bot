"""
Основной файл для запуска Gates of Olympus AI Bot.

Этот файл запускает бота с использованием новой модульной структуры.
"""

import logging
from src.bot import GamblingBot
from src.database import DatabaseManager
from src.scheduler import AutoSignalScheduler
from src.config import LoggingConfig, BotConfig

# Настройка логирования
import logging.handlers

# Создаем форматтер
formatter = logging.Formatter(LoggingConfig.LOG_FORMAT)

# Настраиваем корневой логгер
root_logger = logging.getLogger()
root_logger.setLevel(getattr(logging, LoggingConfig.LOG_LEVEL))

# Очищаем существующие обработчики
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Добавляем обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Добавляем обработчик для файла с ротацией
file_handler = logging.handlers.RotatingFileHandler(
    LoggingConfig.LOG_FILE,
    maxBytes=LoggingConfig.LOG_MAX_SIZE,
    backupCount=LoggingConfig.LOG_BACKUP_COUNT,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)


def main():
    """Основная функция для запуска бота."""
    try:
        # Проверка конфигурации
        logger.info("Проверка конфигурации...")
        if not BotConfig.TOKEN or len(BotConfig.TOKEN) < 10:
            logger.error("Неверный токен бота. Проверьте переменную окружения BOT_TOKEN")
            return
        
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        if not DatabaseManager.init_database():
            logger.error("Ошибка инициализации базы данных")
            return
        
        # Создание и запуск бота
        logger.info("Запуск бота...")
        bot = GamblingBot()
        
        # Запуск планировщика авто-сигналов
        scheduler = AutoSignalScheduler(bot.app)
        scheduler.start()
        
        # Запуск бота
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Завершение работы бота")


if __name__ == "__main__":
    main() 