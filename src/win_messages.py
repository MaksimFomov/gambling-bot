"""
Модуль с сообщениями о выигрышах пользователей.

Содержит шаблоны сообщений о выигрышах для мотивации пользователей.
"""

import random
from typing import Dict, List

from .config import SignalGenerationConfig


class WinMessageTemplates:
    """Шаблоны сообщений о выигрышах."""
    
    @staticmethod
    def _get_random_multiplier() -> int:
        """Возвращает случайный множитель в диапазоне из конфигурации."""
        return random.randint(
            SignalGenerationConfig.MIN_SIGNAL_MULTIPLIER,
            SignalGenerationConfig.MAX_SIGNAL_MULTIPLIER
        )
    
    @staticmethod
    def get_random_win_message() -> str:
        """Возвращает случайное сообщение о выигрыше."""
        messages = [
            "🎉 *ПОЗДРАВЛЯЕМ!* 🎉\n\n"
            f"🎰 Один из наших пользователей только что выиграл *x{WinMessageTemplates._get_random_multiplier()}* на Gates of Olympus!\n"
            "💰 Выигрыш составил *15,000₽* за один спин!\n\n"
            "⚡ Сигнал был сгенерирован нашим ИИ-ботом\n"
            "🎯 Точность прогноза: *87%*\n\n"
            "🔥 Не упусти свой шанс! Получи сигнал прямо сейчас!",
            
            "🏆 *ОГРОМНЫЙ ВЫИГРЫШ!* 🏆\n\n"
            f"🎰 Пользователь бота сорвал джекпот *x{WinMessageTemplates._get_random_multiplier()}*!\n"
            "💰 Сумма выигрыша: *25,000₽*\n\n"
            "🧠 ИИ-анализ показал идеальный момент для входа\n"
            "📊 Вероятность успеха: *92%*\n\n"
            "🚀 Хочешь такой же результат? Заказывай сигнал!",
            
            "💎 *МЕГА ВЫИГРЫШ!* 💎\n\n"
            f"🎰 Наш пользователь выиграл *x{WinMessageTemplates._get_random_multiplier()}* на Gates of Olympus!\n"
            "💰 Выигрыш: *45,000₽* за 3 спина!\n\n"
            "⚡ Автосигнал сработал идеально\n"
            "🎯 Точность: *95%*\n\n"
            "💫 Твой следующий! Включи автосигналы!",
            
            "🔥 *НЕВЕРОЯТНЫЙ УСПЕХ!* 🔥\n\n"
            f"🎰 Пользователь бота поймал *x{WinMessageTemplates._get_random_multiplier()}*!\n"
            "💰 Выигрыш составил *75,000₽*\n\n"
            "🧠 ИИ определил паттерн за 2 минуты до выигрыша\n"
            "📈 ROI: *+1500%*\n\n"
            "⚡ Не жди! Получи свой сигнал сейчас!",
            
            "🌟 *ЛЕГЕНДАРНЫЙ ВЫИГРЫШ!* 🌟\n\n"
            f"🎰 Наш пользователь сорвал *x{WinMessageTemplates._get_random_multiplier()}*!\n"
            "💰 Выигрыш: *150,000₽* за один спин!\n\n"
            "🧠 ИИ-бот предсказал этот момент за 5 минут\n"
            "🎯 Точность прогноза: *98%*\n\n"
            "💎 Стань следующим легендарным победителем!"
        ]
        return random.choice(messages)
    
    @staticmethod
    def get_win_message_with_stats(stats: Dict[str, int]) -> str:
        """Возвращает сообщение о выигрыше со статистикой."""
        base_message = WinMessageTemplates.get_random_win_message()
        
        stats_text = (
            f"\n\n📊 *Статистика за сегодня:*\n"
            f"🎯 Успешных сигналов: {stats.get('successful', random.randint(15, 25))}\n"
            f"💰 Общий выигрыш: {stats.get('total_win', random.randint(500000, 1500000))}₽\n"
            f"👥 Активных пользователей: {stats.get('active', random.randint(80, 120))}"
        )
        
        return base_message + stats_text
    
    @staticmethod
    def get_motivational_message() -> str:
        """Возвращает мотивационное сообщение."""
        messages = [
            "💪 *НЕ СДАВАЙСЯ!* 💪\n\n"
            "🎯 Каждый выигрыш начинается с одного сигнала\n"
            "⚡ Наш ИИ работает 24/7 для твоей победы\n"
            "🔥 Сегодня может быть твой день!\n\n"
            "🎰 Получи сигнал прямо сейчас!",
            
            "🚀 *ТВОЙ МОМЕНТ НАСТУПИЛ!* 🚀\n\n"
            "🎰 Gates of Olympus готов к взрыву\n"
            "🧠 ИИ зафиксировал аномальную активность\n"
            "💎 Не упусти свой шанс на мегавыигрыш!\n\n"
            "⚡ Заказывай сигнал немедленно!",
            
            "🔥 *ГОРЯЧИЙ ПЕРИОД!* 🔥\n\n"
            "🎰 Слот показывает невероятную активность\n"
            f"📊 Анализ показывает 85% вероятность x{SignalGenerationConfig.MIN_SIGNAL_MULTIPLIER}+\n"
            "💫 Твой следующий сигнал может быть золотым!\n\n"
            "🎯 Получи сигнал сейчас!"
        ]
        return random.choice(messages)
    
    @staticmethod
    def get_community_win_message() -> str:
        """Возвращает сообщение о выигрыше в сообществе."""
        return (
            "🎉 *ПОЗДРАВЛЯЕМ НАШЕ СООБЩЕСТВО!* 🎉\n\n"
            f"🎰 Еще один участник нашего бота сорвал джекпот!\n"
            f"💰 Выигрыш: *x{WinMessageTemplates._get_random_multiplier()}* = 35,000₽\n\n"
            "👥 Присоединяйся к победителям!\n"
            "🔗 Наша группа: @gates_olympus_ai\n\n"
            "⚡ Получи свой сигнал и стань следующим!"
        )
    
    @staticmethod
    def get_time_based_message() -> str:
        """Возвращает сообщение в зависимости от времени суток."""
        from datetime import datetime
        
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return (
                "🌅 *ДОБРОЕ УТРО, ПОБЕДИТЕЛЬ!* 🌅\n\n"
                "🎰 Утренние часы - лучшее время для выигрышей!\n"
                f"💰 Наш пользователь только что выиграл *x{WinMessageTemplates._get_random_multiplier()}*\n"
                "⚡ Начни свой день с победы!\n\n"
                "🎯 Получи утренний сигнал!"
            )
        elif 12 <= hour < 18:
            return (
                "☀️ *ДЕНЬ ПОБЕД!* ☀️\n\n"
                "🎰 Дневная активность слотов на пике!\n"
                f"💰 Выигрыш: *x{WinMessageTemplates._get_random_multiplier()}* = 33,000₽\n"
                "🔥 Не пропусти дневную волну удачи!\n\n"
                "⚡ Заказывай сигнал сейчас!"
            )
        elif 18 <= hour < 24:
            return (
                "🌙 *ВЕЧЕРНИЙ ДЖЕКПОТ!* 🌙\n\n"
                "🎰 Вечером слоты особенно щедры!\n"
                f"💰 Выигрыш: *x{WinMessageTemplates._get_random_multiplier()}* = 52,500₽\n"
                "💫 Закончи день с громкой победой!\n\n"
                "🎯 Получи вечерний сигнал!"
            )
        else:
            return (
                "🌃 *НОЧНАЯ УДАЧА!* 🌃\n\n"
                "🎰 Ночью выигрывают самые смелые!\n"
                f"💰 Выигрыш: *x{WinMessageTemplates._get_random_multiplier()}* = 60,000₽\n"
                "🌟 Ночь принадлежит победителям!\n\n"
                "⚡ Получи ночной сигнал!"
            ) 