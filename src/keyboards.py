"""
Модуль для создания клавиатур и меню.

Содержит все функции для создания различных типов клавиатур:
- Главное меню
- Меню регистрации
- Inline кнопки
"""

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from typing import List


class KeyboardFactory:
    """Фабрика для создания клавиатур."""
    
    @staticmethod
    def main_menu(auto_enabled: bool) -> ReplyKeyboardMarkup:
        """
        Создает главное меню с кнопками.
        
        Args:
            auto_enabled: Включены ли авто-сигналы
            
        Returns:
            ReplyKeyboardMarkup: Главное меню
        """
        keyboard = [
            [KeyboardButton("⚡ Получить сигнал"), KeyboardButton("🔔 Авто-сигналы")],
            [KeyboardButton("👥 Сообщество"), KeyboardButton("🛟 Помощь")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def registration_menu() -> ReplyKeyboardMarkup:
        """
        Создает меню для регистрации.
        
        Returns:
            ReplyKeyboardMarkup: Меню регистрации
        """
        keyboard = [
            [KeyboardButton("🎰 Зарегистрироваться в казино")],
            [KeyboardButton("✅ Я зарегистрировался")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def registration_inline_keyboard(bonus_link: str) -> InlineKeyboardMarkup:
        """
        Создает inline клавиатуру для регистрации.
        
        Args:
            bonus_link: Ссылка на бонус казино
            
        Returns:
            InlineKeyboardMarkup: Inline клавиатура регистрации
        """
        keyboard = [
            [InlineKeyboardButton("🎰 Зарегистрироваться в казино", url=bonus_link)],
            [InlineKeyboardButton("✅ Я зарегистрировался", callback_data="casino_done")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def community_keyboard(group_link: str) -> InlineKeyboardMarkup:
        """
        Создает inline клавиатуру для сообщества.
        
        Args:
            group_link: Ссылка на группу
            
        Returns:
            InlineKeyboardMarkup: Клавиатура сообщества
        """
        keyboard = [[InlineKeyboardButton("📢 Присоединиться к группе", url=group_link)]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def registration_success_keyboard(group_link: str) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру после успешной регистрации.
        
        Args:
            group_link: Ссылка на группу
            
        Returns:
            InlineKeyboardMarkup: Клавиатура после регистрации
        """
        keyboard = [
            [InlineKeyboardButton("📢 Подписаться на группу", url=group_link)],
            [InlineKeyboardButton("🚀 Перейти к боту", callback_data="go_to_bot")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def go_to_main_menu_keyboard() -> ReplyKeyboardMarkup:
        """
        Создает клавиатуру с кнопкой "Перейти в главное меню".
        
        Returns:
            ReplyKeyboardMarkup: Клавиатура с кнопкой перехода в главное меню
        """
        keyboard = [
            [KeyboardButton("📋 Перейти в главное меню")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def first_menu_keyboard() -> ReplyKeyboardMarkup:
        """
        Создает первое меню (приветственное).
        
        Returns:
            ReplyKeyboardMarkup: Первое меню
        """
        keyboard = [
            [KeyboardButton("🎯 Начать знакомство")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def second_menu_keyboard() -> ReplyKeyboardMarkup:
        """
        Создает второе меню (информационное).
        
        Returns:
            ReplyKeyboardMarkup: Второе меню
        """
        keyboard = [
            [KeyboardButton("📚 Узнать больше")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    
    @staticmethod
    def third_menu_keyboard() -> ReplyKeyboardMarkup:
        """
        Создает третье меню (регистрация).
        
        Returns:
            ReplyKeyboardMarkup: Третье меню
        """
        keyboard = [
            [KeyboardButton("🎰 Зарегистрироваться в казино")],
            [KeyboardButton("✅ Я зарегистрировался")]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


# Функции для обратной совместимости
def main_menu(auto_enabled: bool) -> ReplyKeyboardMarkup:
    """Создание главного меню (для обратной совместимости)."""
    return KeyboardFactory.main_menu(auto_enabled)


def registration_menu() -> ReplyKeyboardMarkup:
    """Создание меню регистрации (для обратной совместимости)."""
    return KeyboardFactory.registration_menu() 