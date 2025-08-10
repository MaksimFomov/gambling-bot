"""
Основной модуль Telegram бота для Gates of Olympus.

Содержит все обработчики команд и основную логику бота.
"""

import asyncio
import random
import logging
from typing import Optional
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from .config import BotConfig, LinksConfig, LoggingConfig, SchedulerConfig, ImagesConfig
from .database import DatabaseManager
from .signal_generator import SignalGenerator
from .keyboards import KeyboardFactory
from .messages import MessageTemplates

# Настройка логирования
logging.basicConfig(
    format=LoggingConfig.LOG_FORMAT,
    level=getattr(logging, LoggingConfig.LOG_LEVEL)
)
logger = logging.getLogger(__name__)


class GamblingBot:
    """Основной класс бота."""
    
    def __init__(self):
        """Инициализация бота."""
        # Проверяем валидность токена
        if not self._validate_token():
            raise ValueError("Неверный токен бота")
        
        self.app = Application.builder().token(BotConfig.TOKEN).build()
        self._setup_handlers()
        self._setup_error_handlers()
        self._check_resources()
    
    def _validate_token(self) -> bool:
        """Проверяет валидность токена бота."""
        if not BotConfig.TOKEN or len(BotConfig.TOKEN) < 10:
            logger.error("Токен бота недействителен или слишком короткий")
            return False
        
        # Проверяем формат токена (должен содержать двоеточие)
        if ':' not in BotConfig.TOKEN:
            logger.error("Неверный формат токена бота")
            return False
        
        return True
    
    def _check_resources(self) -> bool:
        """Проверяет наличие необходимых ресурсов."""
        import os
        
        # Проверяем наличие файлов изображений
        image_files = ['bonus.png', 'welcome.png']
        for image_file in image_files:
            if not os.path.exists(image_file):
                logger.warning(f"Файл изображения не найден: {image_file}")
        
        return True
    
    def _setup_handlers(self):
        """Настройка обработчиков команд."""
        # Основные команды
        self.app.add_handler(CommandHandler("start", self._start_command))
        self.app.add_handler(CommandHandler("menu", self._menu_command))
        self.app.add_handler(CommandHandler("signal", self._signal_command))
        self.app.add_handler(CommandHandler("auto", self._auto_command))
        self.app.add_handler(CommandHandler("help", self._help_command))
        self.app.add_handler(CommandHandler("community", self._community_command))
        self.app.add_handler(CommandHandler("status", self._status_command))
        self.app.add_handler(CommandHandler("stats", self._stats_command))
        
        # Обработчик текстовых сообщений (кнопок меню)
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
        
        # Обработчик inline кнопок
        self.app.add_handler(CallbackQueryHandler(self._handle_callback))
    
    def _setup_error_handlers(self):
        """Настройка обработчиков ошибок."""
        # Добавляем обработчик для конфликтов (несколько экземпляров бота)
        self.app.add_error_handler(self._error_handler)
    
    async def _error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик ошибок."""
        try:
            # Логируем ошибку
            logger.error(f"Exception while handling an update: {context.error}")
            
            # Обрабатываем специфические ошибки
            if "Conflict" in str(context.error) and "getUpdates" in str(context.error):
                logger.warning("Обнаружен конфликт с другим экземпляром бота. Перезапуск...")
                # Можно добавить логику перезапуска здесь
                return
            
            # Для других ошибок можно отправить сообщение пользователю
            if update and hasattr(update, 'effective_chat'):
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text="❌ Произошла ошибка при обработке запроса. Попробуйте позже."
                    )
                except Exception as send_error:
                    logger.error(f"Не удалось отправить сообщение об ошибке: {send_error}")
                    
        except Exception as e:
            logger.error(f"Ошибка в обработчике ошибок: {e}")
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start."""
        user = update.effective_user
        logger.info(f"Команда /start от пользователя {user.id}")
        
        # Добавляем пользователя в базу данных
        DatabaseManager.add_user(user.id, user.username)
        
        # Получаем данные пользователя
        db_user = DatabaseManager.get_user(user.id)
        
        if not db_user or not db_user[2]:  # Не зарегистрирован
            # Отправляем картинку с сообщением о регистрации
            try:
                with open(ImagesConfig.REGISTRATION_IMAGE, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=MessageTemplates.welcome_message(user.first_name),
                        reply_markup=KeyboardFactory.registration_inline_keyboard(LinksConfig.BONUS_LINK),
                        parse_mode="Markdown"
                    )
            except FileNotFoundError:
                # Если картинка не найдена, отправляем только текст
                await update.message.reply_text(
                    MessageTemplates.welcome_message(user.first_name),
                    reply_markup=KeyboardFactory.registration_inline_keyboard(LinksConfig.BONUS_LINK),
                    parse_mode="Markdown"
                )
        else:
            await self._show_main_menu(update, context, db_user[3])
    
    async def _menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /menu."""
        user = update.effective_user
        user_id = user.id
        logger.info(f"Команда /menu от пользователя {user_id}")
        
        # Добавляем пользователя в базу данных (если его нет)
        DatabaseManager.add_user(user_id, user.username)
        
        # Получаем данные пользователя
        db_user = DatabaseManager.get_user(user_id)
        
        if not db_user or not db_user[2]:  # Не зарегистрирован
            # Отправляем картинку с сообщением о необходимости регистрации
            try:
                with open(ImagesConfig.REGISTRATION_IMAGE, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption="❌ Для доступа к меню необходимо сначала зарегистрироваться в казино.\n"
                                "Используйте команду /start для регистрации.",
                        reply_markup=KeyboardFactory.registration_inline_keyboard(LinksConfig.BONUS_LINK)
                    )
            except FileNotFoundError:
                # Если картинка не найдена, отправляем только текст
                await update.message.reply_text(
                    "❌ Для доступа к меню необходимо сначала зарегистрироваться в казино.\n"
                    "Используйте команду /start для регистрации.",
                    reply_markup=KeyboardFactory.registration_inline_keyboard(LinksConfig.BONUS_LINK)
                )
        else:
            await self._show_main_menu(update, context, db_user[3])
    
    async def _signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /signal."""
        user = update.effective_user
        user_id = user.id
        logger.info(f"Команда /signal от пользователя {user_id}")
        
        # Проверяем регистрацию
        db_user = DatabaseManager.get_user(user_id)
        if not db_user or not db_user[2]:
            await update.message.reply_text(MessageTemplates.error_messages()['not_registered'])
            return
        
        await self._generate_signal_for_user(update, context, user_id)
    
    async def _auto_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /auto."""
        user = update.effective_user
        user_id = user.id
        logger.info(f"Команда /auto от пользователя {user_id}")
        
        # Проверяем регистрацию
        db_user = DatabaseManager.get_user(user_id)
        if not db_user or not db_user[2]:
            await update.message.reply_text(MessageTemplates.error_messages()['not_registered'])
            return
        
        # Переключаем статус авто-сигналов
        new_status = 0 if db_user[3] else 1
        if DatabaseManager.update_user(user_id, "auto_signal", new_status):
            status_text = MessageTemplates.info_messages()['auto_enabled'] if new_status else MessageTemplates.info_messages()['auto_disabled']
            await update.message.reply_text(status_text)
        else:
            await update.message.reply_text(MessageTemplates.error_messages()['settings_error'])
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help."""
        try:
            user_id = update.effective_user.id
            logger.info(f"Команда /help от пользователя {user_id}")
            
            # Получаем данные пользователя для показа главного меню
            db_user = DatabaseManager.get_user(user_id)
            if db_user and db_user[2]:  # Если пользователь зарегистрирован
                await update.message.reply_text(
                    MessageTemplates.help_detailed(), 
                    parse_mode="Markdown",
                    reply_markup=KeyboardFactory.main_menu(db_user[3])
                )
            else:
                # Если пользователь не зарегистрирован, показываем справку без меню
                await update.message.reply_text(MessageTemplates.help_detailed(), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды /help: {e}")
            await update.message.reply_text(MessageTemplates.error_messages()['help_error'])
    
    async def _community_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /community."""
        logger.info(f"Команда /community от пользователя {update.effective_user.id}")
        await update.message.reply_text(
            MessageTemplates.community_info(LinksConfig.GROUP_LINK),
            parse_mode="Markdown",
            reply_markup=KeyboardFactory.community_keyboard(LinksConfig.GROUP_LINK)
        )
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status."""
        user = update.effective_user
        user_id = user.id
        logger.info(f"Команда /status от пользователя {user_id}")
        
        # Получаем данные пользователя
        db_user = DatabaseManager.get_user(user_id)
        if not db_user:
            await update.message.reply_text(MessageTemplates.error_messages()['user_not_found'])
            return
        
        if not db_user[2]:
            await update.message.reply_text(MessageTemplates.error_messages()['not_registered'])
            return
        
        # Получаем информацию о сигнале
        signal_info = DatabaseManager.get_user_signal_info(user_id)
        
        # Формируем данные пользователя для шаблона
        user_data = {
            'auto_signal': db_user[3]
        }
        
        await update.message.reply_text(
            MessageTemplates.status_message(user_data, signal_info),
            parse_mode="Markdown"
        )
    
    async def _stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats (только для админа)."""
        try:
            user_id = update.effective_user.id
            logger.info(f"Команда /stats от пользователя {user_id}")
            
            if user_id != BotConfig.ADMIN_ID:
                await update.message.reply_text(MessageTemplates.error_messages()['no_access'])
                return
            
            stats = DatabaseManager.get_statistics()
            await update.message.reply_text(MessageTemplates.statistics(stats), parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Ошибка при выполнении команды /stats: {e}")
            await update.message.reply_text(MessageTemplates.error_messages()['stats_error'])
    
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений от кнопок меню."""
        text = update.message.text
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"Текстовое сообщение от пользователя {user_id}: '{text}'")
        
        # Простой тест
        if text == "тест":
            await update.message.reply_text(MessageTemplates.info_messages()['test_success'])
            return
        
        # Получаем данные пользователя
        db_user = DatabaseManager.get_user(user_id)
        if not db_user:
            await update.message.reply_text(MessageTemplates.error_messages()['user_not_found'])
            return
        
        # Проверяем регистрацию для всех функций
        if not db_user[2]:
            await update.message.reply_text(
                MessageTemplates.error_messages()['not_registered'],
                reply_markup=KeyboardFactory.registration_inline_keyboard(LinksConfig.BONUS_LINK)
            )
            return
        
        # Обработка кнопки перехода в главное меню
        if text == "📋 Перейти в главное меню":
            await self._show_main_menu(update, context, db_user[3])
            return
        
        # Обработка основных кнопок меню
        if text == "⚡ Получить сигнал":
            await self._generate_signal_for_user(update, context, user_id)
        
        elif text == "🔔 Авто-сигналы":
            new_status = 0 if db_user[3] else 1
            if DatabaseManager.update_user(user_id, "auto_signal", new_status):
                status_text = MessageTemplates.info_messages()['auto_enabled'] if new_status else MessageTemplates.info_messages()['auto_disabled']
                await update.message.reply_text(status_text, reply_markup=KeyboardFactory.main_menu(new_status))
            else:
                await update.message.reply_text(MessageTemplates.error_messages()['settings_error'], reply_markup=KeyboardFactory.main_menu(db_user[3]))
        
        elif text == "🛟 Помощь":
            try:
                await update.message.reply_text(MessageTemplates.help_detailed(), parse_mode="Markdown", reply_markup=KeyboardFactory.main_menu(db_user[3]))
            except Exception as e:
                logger.error(f"Ошибка при показе помощи через кнопку: {e}")
                await update.message.reply_text(MessageTemplates.error_messages()['help_error'], reply_markup=KeyboardFactory.main_menu(db_user[3]))
        
        elif text == "👥 Сообщество":
            await update.message.reply_text(
                MessageTemplates.community_info(LinksConfig.GROUP_LINK),
                parse_mode="Markdown",
                reply_markup=KeyboardFactory.community_keyboard(LinksConfig.GROUP_LINK)
            )
        
        else:
            # Неизвестная команда
            logger.info(f"Неизвестная команда от пользователя {user_id}: '{text}'")
            await update.message.reply_text(
                f"❓ Неизвестная команда: '{text}'. Используйте кнопки меню или команду /start для начала работы.",
                reply_markup=KeyboardFactory.main_menu(db_user[3])
            )
    
    async def _handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback запросов от inline кнопок."""
        query = update.callback_query
        user_id = query.from_user.id
        
        try:
            await query.answer()
        except Exception as e:
            logger.error(f"Ошибка при ответе на callback query: {e}")
        
        logger.info(f"Callback query от пользователя {user_id}: {query.data}")
        
        # Обработка различных callback данных
        if query.data == "casino_done":
            await self._handle_casino_done(query, context)
            return
        
        # Для остальных callback проверяем регистрацию
        db_user = DatabaseManager.get_user(user_id)
        if not db_user:
            try:
                await query.edit_message_text(MessageTemplates.error_messages()['user_not_found'])
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")
            return
        
        # Обработка остальных callback данных
        if query.data == "go_to_bot":
            await self._handle_go_to_bot(query, context, db_user)
        elif query.data == "gen_signal":
            await self._generate_signal_for_user_callback(query, context, user_id)
        elif query.data == "toggle_auto_signal":
            await self._handle_toggle_auto_signal(query, context, db_user)
        elif query.data == "help":
            await self._handle_help_callback(query, context)
        elif query.data == "community":
            await self._handle_community_callback(query, context)
    
    async def _handle_casino_done(self, query, context):
        """Обработка завершения регистрации в казино."""
        user_id = query.from_user.id
        
        if DatabaseManager.update_user(user_id, "registered", 1):
            try:
                await query.message.delete()
                # Отправляем картинку с приглашением в группу
                try:
                    with open(ImagesConfig.WELCOME_IMAGE, 'rb') as photo:
                        await context.bot.send_photo(
                            chat_id=query.message.chat_id,
                            photo=photo,
                            caption=MessageTemplates.registration_success_detailed(LinksConfig.GROUP_LINK),
                            reply_markup=KeyboardFactory.registration_success_keyboard(LinksConfig.GROUP_LINK),
                            parse_mode="Markdown"
                        )
                except FileNotFoundError:
                    # Если картинка не найдена, отправляем только текст
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=MessageTemplates.registration_success_detailed(LinksConfig.GROUP_LINK),
                        reply_markup=KeyboardFactory.registration_success_keyboard(LinksConfig.GROUP_LINK)
                    )
            except Exception as e:
                logger.error(f"Ошибка при обработке завершения регистрации: {e}")
        else:
            await query.edit_message_text(MessageTemplates.error_messages()['registration_error'])
    
    async def _handle_go_to_bot(self, query, context, db_user):
        """Обработка перехода к боту."""
        try:
            await query.message.delete()
            # Получаем обновленные данные пользователя после регистрации
            updated_user = DatabaseManager.get_user(query.from_user.id)
            if updated_user:
                fake_update = type('Update', (), {'effective_chat': type('Chat', (), {'id': query.message.chat_id})()})()
                await self._show_main_menu(fake_update, context, updated_user[3])
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="❌ Произошла ошибка при получении данных пользователя. Попробуйте позже."
                )
        except Exception as e:
            logger.error(f"Ошибка при переходе к боту: {e}")
            await query.edit_message_text("❌ Произошла ошибка при переходе к боту. Попробуйте позже.")
    
    async def _generate_signal_for_user_callback(self, query, context, user_id):
        """Генерация сигнала через callback."""
        try:
            # Проверяем, не занята ли система (обычная проверка времени)
            user_signal_info = DatabaseManager.get_user_signal_info(user_id)
            if user_signal_info and user_signal_info["next_update"] and datetime.utcnow() < user_signal_info["next_update"]:
                # Показываем прошлый сигнал с сообщением об ожидании
                await self._send_last_signal_or_wait_message(context, query.message.chat_id, user_id)
                return
            
            # Список для хранения ID промежуточных сообщений
            intermediate_messages = []
            
            # Эмуляция обработки рулетки
            msg1 = await context.bot.send_message(chat_id=query.message.chat_id, text="🎰 Анализирую рулетку...", parse_mode="Markdown")
            intermediate_messages.append(msg1.message_id)
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg2 = await context.bot.send_message(chat_id=query.message.chat_id, text="📊 Сканирую паттерны...", parse_mode="Markdown")
            intermediate_messages.append(msg2.message_id)
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg3 = await context.bot.send_message(chat_id=query.message.chat_id, text="🧠 ИИ обрабатывает данные...", parse_mode="Markdown")
            intermediate_messages.append(msg3.message_id)
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg4 = await context.bot.send_message(chat_id=query.message.chat_id, text=MessageTemplates.info_messages()['scanning'], parse_mode="Markdown")
            intermediate_messages.append(msg4.message_id)
            await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
            await asyncio.sleep(random.randint(3, 6))
            
            signal = SignalGenerator.generate_signal_for_user(user_id)
            if signal:
                # Отправляем финальный сигнал
                await context.bot.send_message(chat_id=query.message.chat_id, text=signal, parse_mode="Markdown")
                
                # Удаляем все промежуточные сообщения
                for msg_id in intermediate_messages:
                    try:
                        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение {msg_id}: {e}")
            # Убираем else блок - не вызываем _send_last_signal_or_wait_message второй раз
        except Exception as e:
            logger.error(f"Ошибка при генерации сигнала через callback для пользователя {user_id}: {e}")
            # При ошибке показываем только сообщение об анализе
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="🕒 Анализ ещё не завершён.\nИИ всё ещё обрабатывает данные рулетки.\n\nПопробуйте позже."
            )
    
    async def _handle_toggle_auto_signal(self, query, context, db_user):
        """Переключение авто-сигналов."""
        user_id = query.from_user.id
        new_status = 0 if db_user[3] else 1
        
        if DatabaseManager.update_user(user_id, "auto_signal", new_status):
            try:
                await query.message.delete()
                status_text = MessageTemplates.info_messages()['auto_enabled'] if new_status else MessageTemplates.info_messages()['auto_disabled']
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=status_text,
                    reply_markup=KeyboardFactory.main_menu(new_status)
                )
            except Exception as e:
                logger.error(f"Ошибка при переключении автосигналов: {e}")
        else:
            await query.answer(MessageTemplates.error_messages()['settings_error'])
    
    async def _handle_help_callback(self, query, context):
        """Обработка помощи через callback."""
        try:
            await query.answer()
            # Получаем данные пользователя для показа главного меню
            user_id = query.from_user.id
            db_user = DatabaseManager.get_user(user_id)
            if db_user and db_user[2]:  # Если пользователь зарегистрирован
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=MessageTemplates.help_detailed(),
                    parse_mode="Markdown",
                    reply_markup=KeyboardFactory.main_menu(db_user[3])
                )
            else:
                # Если пользователь не зарегистрирован, показываем справку без меню
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=MessageTemplates.help_detailed(),
                    parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Ошибка при показе помощи: {e}")
            await query.answer(MessageTemplates.error_messages()['help_error'])
    
    async def _handle_community_callback(self, query, context):
        """Обработка сообщества через callback."""
        try:
            await query.answer()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=MessageTemplates.community_info(LinksConfig.GROUP_LINK),
                parse_mode="Markdown",
                reply_markup=KeyboardFactory.community_keyboard(LinksConfig.GROUP_LINK)
            )
        except Exception as e:
            logger.error(f"Ошибка при показе сообщества: {e}")
            await query.answer(MessageTemplates.error_messages()['community_error'])
    
    async def _generate_signal_for_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
        """Генерация сигнала для пользователя."""
        try:
            # Проверяем, не занята ли система (обычная проверка времени)
            user_signal_info = DatabaseManager.get_user_signal_info(user_id)
            if user_signal_info and user_signal_info["next_update"] and datetime.utcnow() < user_signal_info["next_update"]:
                # Показываем прошлый сигнал с сообщением об ожидании
                await self._send_last_signal_or_wait_message(context, update.message.chat_id, user_id)
                return
            
            # Список для хранения ID промежуточных сообщений
            intermediate_messages = []
            
            # Эмуляция обработки рулетки
            msg1 = await update.message.reply_text("🎰 Анализирую рулетку...", parse_mode="Markdown")
            intermediate_messages.append(msg1.message_id)
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg2 = await update.message.reply_text("📊 Сканирую паттерны...", parse_mode="Markdown")
            intermediate_messages.append(msg2.message_id)
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg3 = await update.message.reply_text("🧠 ИИ обрабатывает данные...", parse_mode="Markdown")
            intermediate_messages.append(msg3.message_id)
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
            await asyncio.sleep(2)
            
            msg4 = await update.message.reply_text(MessageTemplates.info_messages()['scanning'], parse_mode="Markdown")
            intermediate_messages.append(msg4.message_id)
            await context.bot.send_chat_action(chat_id=update.message.chat_id, action="typing")
            await asyncio.sleep(random.randint(3, 6))
            
            signal = SignalGenerator.generate_signal_for_user(user_id)
            if signal:
                # Отправляем финальный сигнал
                await update.message.reply_text(signal, parse_mode="Markdown", reply_markup=KeyboardFactory.main_menu(True))
                
                # Удаляем все промежуточные сообщения
                for msg_id in intermediate_messages:
                    try:
                        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg_id)
                    except Exception as e:
                        logger.warning(f"Не удалось удалить сообщение {msg_id}: {e}")
            # Убираем else блок - не вызываем _send_last_signal_or_wait_message второй раз
        except Exception as e:
            logger.error(f"Ошибка при генерации сигнала для пользователя {user_id}: {e}")
            # При ошибке показываем только сообщение об анализе
            await update.message.reply_text(
                "🕒 Анализ ещё не завершён.\nИИ всё ещё обрабатывает данные рулетки.\n\nПопробуйте позже."
            )
    
    async def _send_last_signal_or_wait_message(self, context, chat_id: int, user_id: int):
        """Отправка последнего сигнала или сообщения об ожидании."""
        user_signal_info = DatabaseManager.get_user_signal_info(user_id)
        if user_signal_info and user_signal_info["text"]:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"🕒 Анализ ещё не завершён.\nИИ всё ещё обрабатывает данные рулетки.\n\nВот *последний актуальный сигнал*:\n\n{user_signal_info['text']}",
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=MessageTemplates.info_messages()['analysis_in_progress']
            )
    
    async def _show_main_menu(self, update, context, auto_signal_enabled: bool):
        """Показ главного меню."""
        chat_id = update.effective_chat.id if hasattr(update, 'effective_chat') else update.message.chat_id
        
        # Отправляем картинку с главным меню
        try:
            with open(ImagesConfig.MAIN_MENU_IMAGE, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=photo,
                    caption=MessageTemplates.main_menu_welcome(),
                    reply_markup=KeyboardFactory.main_menu(auto_signal_enabled),
                    parse_mode="Markdown"
                )
        except FileNotFoundError:
            # Если картинка не найдена, отправляем только текст
            await context.bot.send_message(
                chat_id=chat_id,
                text=MessageTemplates.main_menu_welcome(),
                reply_markup=KeyboardFactory.main_menu(auto_signal_enabled),
                parse_mode="Markdown"
            )
    
    def run(self):
        """Запуск бота."""
        logger.info("✅ Бот запущен.")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Функция для обратной совместимости
def main():
    """Основная функция для запуска бота."""
    DatabaseManager.init_database()
    bot = GamblingBot()
    bot.run()


if __name__ == "__main__":
    main() 