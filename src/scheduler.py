"""
Модуль для планировщика авто-сигналов и уведомлений о выигрышах.

Содержит логику для автоматической отправки сигналов
пользователям с включенными авто-сигналами и уведомлений о выигрышах.
"""

import asyncio
import random
import logging
from datetime import datetime, timedelta
from typing import Optional, List

from apscheduler.schedulers.background import BackgroundScheduler

from .config import SchedulerConfig, NotificationConfig, SignalGenerationConfig
from .database import DatabaseManager, get_db_connection
from .signal_generator import SignalGenerator
from .win_messages import WinMessageTemplates

logger = logging.getLogger(__name__)


class AutoSignalScheduler:
    """Планировщик авто-сигналов."""
    
    def __init__(self, app):
        """
        Инициализация планировщика.
        
        Args:
            app: Экземпляр Application из python-telegram-bot
        """
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.loop: asyncio.AbstractEventLoop | None = None
        self._setup_job()
    
    def _setup_job(self):
        """Настройка задач планировщика."""
        # Проверяем корректность интервалов генерации сигналов
        if not SchedulerConfig.validate_intervals():
            logger.error("Некорректные интервалы планировщика. Используем значения по умолчанию.")
            interval = random.randint(40, 80)  # Значения по умолчанию в минутах
        else:
            interval = random.randint(SchedulerConfig.MIN_SIGNAL_INTERVAL, SchedulerConfig.MAX_SIGNAL_INTERVAL)
        
        # Задача для авто-сигналов (каждые 40-80 минут)
        self.scheduler.add_job(
            func=self._schedule_auto_signal_task,
            trigger='interval',
            minutes=interval,
            id='auto_signal_job'
        )
        
        # Задача для уведомлений о выигрышах (каждые 4-8 часов)
        self.scheduler.add_job(
            func=self._schedule_win_notification_task,
            trigger='interval',
            hours=random.randint(NotificationConfig.WIN_NOTIFICATION_INTERVAL_MIN, NotificationConfig.WIN_NOTIFICATION_INTERVAL_MAX),
            id='win_notification_job'
        )
        
        # Задача для мотивационных сообщений (каждые 8-12 часов)
        self.scheduler.add_job(
            func=self._schedule_motivational_task,
            trigger='interval',
            hours=random.randint(NotificationConfig.MOTIVATIONAL_INTERVAL_MIN, NotificationConfig.MOTIVATIONAL_INTERVAL_MAX),
            id='motivational_job'
        )
        
        logger.info(f"Планировщик настроен с интервалом {interval} минут для авто-сигналов")
        logger.info("Добавлены задачи для уведомлений о выигрышах и мотивационных сообщений")
    
    def start(self, loop: asyncio.AbstractEventLoop | None = None):
        """Запуск планировщика.
        Args:
            loop: Запущенный event loop приложения, в который будут отправляться корутины
        """
        if loop is not None:
            self.loop = loop
        self.scheduler.start()
        logger.info("Планировщик авто-сигналов запущен")
    
    def stop(self):
        """Остановка планировщика."""
        self.scheduler.shutdown()
        logger.info("Планировщик авто-сигналов остановлен")
    
    def _schedule_auto_signal_task(self):
        """
        Функция-обертка для планировщика авто-сигналов.
        Безопасно выполняет авто-сигналы в основном event loop.
        """
        try:
            running_loop = self.loop
            if running_loop and running_loop.is_running():
                asyncio.run_coroutine_threadsafe(self._auto_signal(), running_loop)
            else:
                logger.warning("Основной event loop приложения еще не запущен. Задача авто-сигнала пропущена.")
        except Exception as e:
            logger.error(f"Ошибка в schedule_auto_signal_task: {e}")
    
    async def _auto_signal(self):
        """
        Основная логика авто-сигналов.
        Отправляет сигналы всем пользователям с включенными авто-сигналами.
        """
        try:
            # Получаем пользователей с включенными авто-сигналами
            auto_users = DatabaseManager.get_users_with_auto_signals()
            
            if not auto_users:
                logger.info("Нет пользователей с включенными авто-сигналами")
                return
            
            logger.info(f"Отправляем авто-сигналы {len(auto_users)} пользователям")
            
            for user_id in auto_users:
                try:
                    # Генерируем сигнал для пользователя
                    signal_text = SignalGenerator.generate_signal_for_user(user_id)
                    
                    if signal_text:
                        # Отправляем сигнал пользователю
                        await self.app.bot.send_message(
                            chat_id=user_id,
                            text=signal_text,
                            parse_mode="Markdown"
                        )
                        logger.info(f"Авто-сигнал отправлен пользователю {user_id}")
                    else:
                        logger.info(f"Сигнал не сгенерирован для пользователя {user_id}")
                    
                    # Увеличиваем задержку между отправками для предотвращения конфликтов (0.5 секунды)
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Ошибка обработки автосигнала для пользователя {user_id}: {e}")
                    # Продолжаем с следующим пользователем
                    continue
        except Exception as e:
            logger.error(f"Критическая ошибка в auto_signal: {e}")
    
    def _schedule_win_notification_task(self):
        """
        Функция-обертка для планировщика уведомлений о выигрышах.
        Безопасно выполняет отправку уведомлений в основном event loop.
        """
        try:
            running_loop = self.loop
            if running_loop and running_loop.is_running():
                asyncio.run_coroutine_threadsafe(self._send_win_notifications(), running_loop)
            else:
                logger.warning("Основной event loop приложения еще не запущен. Задача уведомлений о выигрышах пропущена.")
        except Exception as e:
            logger.error(f"Ошибка в schedule_win_notification_task: {e}")
    
    def _schedule_motivational_task(self):
        """
        Функция-обертка для планировщика мотивационных сообщений.
        Безопасно выполняет отправку мотивационных сообщений в основном event loop.
        """
        try:
            running_loop = self.loop
            if running_loop and running_loop.is_running():
                asyncio.run_coroutine_threadsafe(self._send_motivational_messages(), running_loop)
            else:
                logger.warning("Основной event loop приложения еще не запущен. Задача мотивационных сообщений пропущена.")
        except Exception as e:
            logger.error(f"Ошибка в schedule_motivational_task: {e}")
    
    async def _send_win_notifications(self):
        """
        Отправка уведомлений о выигрышах случайным пользователям.
        """
        try:
            # Получаем всех зарегистрированных пользователей
            all_users = self._get_all_registered_users()
            
            if not all_users:
                logger.info("Нет зарегистрированных пользователей для отправки уведомлений о выигрышах")
                return
            
            # Выбираем случайных пользователей (процент в пределах конфигурации, максимум по лимиту)
            percentage = random.randint(
                max(1, NotificationConfig.WIN_NOTIFICATION_USER_PERCENTAGE_MIN),
                max(NotificationConfig.WIN_NOTIFICATION_USER_PERCENTAGE_MIN, NotificationConfig.WIN_NOTIFICATION_USER_PERCENTAGE_MAX)
            )
            num_users = max(1, min(
                len(all_users) * percentage // 100,
                NotificationConfig.WIN_NOTIFICATION_MAX_USERS
            ))
            selected_users = random.sample(all_users, min(num_users, len(all_users)))
            
            logger.info(f"Отправляем уведомления о выигрышах {len(selected_users)} пользователям")
            
            # Выбираем тип сообщения (случайный, по времени, со статистикой)
            message_type = random.choice(['random', 'time_based', 'with_stats'])
            
            for user_id in selected_users:
                try:
                    if message_type == 'random':
                        message = WinMessageTemplates.get_random_win_message()
                    elif message_type == 'time_based':
                        message = WinMessageTemplates.get_time_based_message()
                    else:  # with_stats
                        stats = self._generate_fake_stats()
                        message = WinMessageTemplates.get_win_message_with_stats(stats)
                    
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                    logger.info(f"Уведомление о выигрыше отправлено пользователю {user_id}")
                    
                    # Небольшая задержка между отправками (1-3 секунды)
                    await asyncio.sleep(random.uniform(
                        NotificationConfig.WIN_NOTIFICATION_DELAY_MIN,
                        NotificationConfig.WIN_NOTIFICATION_DELAY_MAX
                    ))
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки уведомления о выигрыше пользователю {user_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Критическая ошибка в send_win_notifications: {e}")
    
    async def _send_motivational_messages(self):
        """
        Отправка мотивационных сообщений пользователям.
        """
        try:
            # Получаем пользователей с авто-сигналами (они более активны)
            auto_users = DatabaseManager.get_users_with_auto_signals()
            
            if not auto_users:
                logger.info("Нет пользователей с авто-сигналами для мотивационных сообщений")
                return
            
            # Выбираем случайных пользователей (процент в пределах конфигурации, максимум по лимиту)
            percentage = random.randint(
                max(1, NotificationConfig.MOTIVATIONAL_USER_PERCENTAGE_MIN),
                max(NotificationConfig.MOTIVATIONAL_USER_PERCENTAGE_MIN, NotificationConfig.MOTIVATIONAL_USER_PERCENTAGE_MAX)
            )
            num_users = max(1, min(
                len(auto_users) * percentage // 100,
                NotificationConfig.MOTIVATIONAL_MAX_USERS
            ))
            selected_users = random.sample(auto_users, min(num_users, len(auto_users)))
            
            logger.info(f"Отправляем мотивационные сообщения {len(selected_users)} пользователям")
            
            for user_id in selected_users:
                try:
                    message = WinMessageTemplates.get_motivational_message()
                    
                    await self.app.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode="Markdown"
                    )
                    logger.info(f"Мотивационное сообщение отправлено пользователю {user_id}")
                    
                    # Задержка между отправками (2-5 секунд)
                    await asyncio.sleep(random.uniform(
                        NotificationConfig.MOTIVATIONAL_DELAY_MIN,
                        NotificationConfig.MOTIVATIONAL_DELAY_MAX
                    ))
                    
                except Exception as e:
                    logger.error(f"Ошибка отправки мотивационного сообщения пользователю {user_id}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Критическая ошибка в send_motivational_messages: {e}")
    
    def _get_all_registered_users(self) -> List[int]:
        """
        Получает список всех зарегистрированных пользователей.
        
        Returns:
            List[int]: Список ID зарегистрированных пользователей
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE registered = 1")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка получения зарегистрированных пользователей: {e}")
            return []
    
    def _generate_fake_stats(self) -> dict:
        """
        Генерирует фейковую статистику для сообщений о выигрышах.
        
        Returns:
            dict: Словарь со статистикой
        """
        return {
            'successful': random.randint(15, 35),  # Количество успешных сигналов
            'total_win': random.randint(500000, 2000000),  # Общий выигрыш в рублях
            'active': random.randint(80, 150)  # Количество активных пользователей
        }


# Функции для обратной совместимости
def schedule_auto_signal_task(app):
    """Функция-обертка для планировщика (для обратной совместимости)."""
    scheduler = AutoSignalScheduler(app)
    scheduler._schedule_auto_signal_task()


async def auto_signal(app):
    """Функция авто-сигналов (для обратной совместимости)."""
    scheduler = AutoSignalScheduler(app)
    await scheduler._auto_signal() 