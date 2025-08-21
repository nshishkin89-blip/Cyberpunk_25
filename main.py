#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cyberpunk RPG Telegram Bot
Киберпанк RPG игра с автобоями и поиском предметов по геолокации
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Location
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

from game_engine import GameEngine
from player import Player
from combat import CombatSystem
from items import ItemManager
from locations import LocationManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CyberpunkRPGBot:
    def __init__(self):
        self.config = self.load_config()
        self.game_engine = GameEngine()
        self.combat_system = CombatSystem()
        self.item_manager = ItemManager()
        self.location_manager = LocationManager()
        self.players: Dict[int, Player] = {}
        
    def load_config(self) -> dict:
        """Загрузка конфигурации игры"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Файл config.json не найден!")
            return {}
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start - начало игры"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Неизвестный"
        
        if user_id not in self.players:
            # Создаем нового игрока
            player = Player(user_id, username)
            self.players[user_id] = player
            welcome_msg = f"""
🎮 *Добро пожаловать в Cyberpunk RPG!* 🎮

🌃 *Мир будущего ждет тебя, киберпанк!*

👤 **Твой персонаж:**
• Имя: {username}
• Уровень: {player.level}
• Здоровье: {player.health}/{player.max_health}
• Кредиты: {player.credits}
• Опыт: {player.experience}/{player.experience_to_next_level}

🎯 **Доступные команды:**
• /profile - Профиль персонажа
• /combat - Автобои
• /search - Поиск предметов
• /inventory - Инвентарь
• /shop - Магазин
• /help - Помощь

*Готов к приключениям в неоновом городе?* 🌆
            """
        else:
            player = self.players[user_id]
            welcome_msg = f"""
🎮 *С возвращением в Cyberpunk RPG!* 🎮

👤 **Твой персонаж:**
• Имя: {username}
• Уровень: {player.level}
• Здоровье: {player.health}/{player.max_health}
• Кредиты: {player.credits}
• Опыт: {player.experience}/{player.experience_to_next_level}

*Что будем делать сегодня?* 🚀
            """
        
        keyboard = [
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            [InlineKeyboardButton("⚔️ Автобои", callback_data="combat")],
            [InlineKeyboardButton("🔍 Поиск предметов", callback_data="search")],
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
            [InlineKeyboardButton("🏪 Магазин", callback_data="shop")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /profile - профиль персонажа"""
        user_id = update.effective_user.id
        if user_id not in self.players:
            await update.message.reply_text("❌ Сначала начни игру командой /start")
            return
        
        player = self.players[user_id]
        profile_msg = f"""
👤 *ПРОФИЛЬ ПЕРСОНАЖА* 👤

🌃 **Основная информация:**
• Имя: {player.username}
• Уровень: {player.level}
• Здоровье: {player.health}/{player.max_health}
• Кредиты: {player.credits}
• Опыт: {player.experience}/{player.experience_to_next_level}

⚔️ **Боевые характеристики:**
• Атака: {player.attack}
• Защита: {player.defense}
• Скорость: {player.speed}
• Критический урон: {player.critical_damage}%

🏆 **Достижения:**
• Победы в боях: {player.combat_wins}
• Найденные предметы: {player.items_found}
• Время в игре: {player.get_playtime()}

*Ты становишься сильнее с каждым днем!* 💪
        """
        
        keyboard = [
            [InlineKeyboardButton("⚔️ Автобои", callback_data="combat")],
            [InlineKeyboardButton("🔍 Поиск предметов", callback_data="search")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def combat_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /combat - автобои"""
        user_id = update.effective_user.id
        if user_id not in self.players:
            await update.message.reply_text("❌ Сначала начни игру командой /start")
            return
        
        player = self.players[user_id]
        
        if not player.can_combat():
            cooldown = player.get_combat_cooldown()
            await update.message.reply_text(f"⏰ Подожди {cooldown} секунд перед следующим боем!")
            return
        
        # Находим противника
        opponent = self.combat_system.find_opponent(player)
        if not opponent:
            await update.message.reply_text("❌ Не удалось найти противника. Попробуй позже!")
            return
        
        # Проводим бой
        battle_result = self.combat_system.execute_battle(player, opponent)
        
        battle_msg = f"""
⚔️ *АВТОБОЙ ЗАВЕРШЕН!* ⚔️

👤 **Ты:** {player.username} (Уровень {player.level})
👹 **Противник:** {opponent.name} (Уровень {opponent.level})

🎯 **Результат боя:**
{battle_result['description']}

💥 **Урон:**
• Ты нанес: {battle_result['player_damage']}
• Противник нанес: {battle_result['opponent_damage']}

🏆 **Награды:**
• Опыт: +{battle_result['experience_gained']}
• Кредиты: +{battle_result['credits_gained']}
• Здоровье: {player.health}/{player.max_health}

*{battle_result['message']}*
        """
        
        keyboard = [
            [InlineKeyboardButton("⚔️ Еще бой", callback_data="combat")],
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            battle_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /search - поиск предметов по геолокации"""
        user_id = update.effective_user.id
        if user_id not in self.players:
            await update.message.reply_text("❌ Сначала начни игру командой /start")
            return
        
        player = self.players[user_id]
        
        if not player.can_search():
            cooldown = player.get_search_cooldown()
            await update.message.reply_text(f"⏰ Подожди {cooldown} секунд перед следующим поиском!")
            return
        
        # Проверяем, есть ли геолокация
        if not context.user_data.get('last_location'):
            await update.message.reply_text(
                "📍 Для поиска предметов нужно поделиться своей геолокацией!\n\n"
                "Отправь свою локацию, а затем используй /search снова."
            )
            return
        
        location = context.user_data['last_location']
        found_items = self.location_manager.search_items(location, player)
        
        if not found_items:
            search_msg = """
🔍 *ПОИСК ПРЕДМЕТОВ* 🔍

📍 **Локация:** Твоя текущая позиция
❌ **Результат:** Предметы не найдены

*Попробуй поискать в другом месте или подожди обновления локации!*
            """
        else:
            items_text = "\n".join([f"• {item.name} ({item.rarity})" for item in found_items])
            search_msg = f"""
🔍 *ПОИСК ПРЕДМЕТОВ* 🔍

📍 **Локация:** Твоя текущая позиция
✅ **Найдено предметов:** {len(found_items)}

🎁 **Найденные предметы:**
{items_text}

*Все предметы добавлены в твой инвентарь!*
            """
            
            # Добавляем предметы игроку
            for item in found_items:
                player.add_item(item)
                player.items_found += 1
        
        keyboard = [
            [InlineKeyboardButton("🔍 Еще поиск", callback_data="search")],
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            search_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_location(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка геолокации от пользователя"""
        user_id = update.effective_user.id
        location = update.message.location
        
        # Сохраняем локацию пользователя
        context.user_data['last_location'] = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timestamp': datetime.now()
        }
        
        await update.message.reply_text(
            "📍 Геолокация получена! Теперь ты можешь искать предметы командой /search"
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "profile":
            await self.profile_command(update, context)
        elif query.data == "combat":
            await self.combat_command(update, context)
        elif query.data == "search":
            await self.search_command(update, context)
        elif query.data == "inventory":
            await self.inventory_command(update, context)
        elif query.data == "shop":
            await self.shop_command(update, context)
        elif query.data == "main_menu":
            await self.start_command(update, context)
    
    async def inventory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /inventory - инвентарь"""
        user_id = update.effective_user.id
        if user_id not in self.players:
            await update.message.reply_text("❌ Сначала начни игру командой /start")
            return
        
        player = self.players[user_id]
        
        if not player.inventory:
            inventory_msg = """
🎒 *ИНВЕНТАРЬ* 🎒

❌ **Твой инвентарь пуст!**

*Отправляйся на поиски предметов командой /search или покупай в магазине!*
            """
        else:
            items_text = "\n".join([f"• {item.name} ({item.rarity}) - {item.description}" for item in player.inventory])
            inventory_msg = f"""
🎒 *ИНВЕНТАРЬ* 🎒

📦 **Предметов:** {len(player.inventory)}

🎁 **Твои предметы:**
{items_text}

*Используй предметы для усиления персонажа!*
            """
        
        keyboard = [
            [InlineKeyboardButton("🔍 Поиск предметов", callback_data="search")],
            [InlineKeyboardButton("🏪 Магазин", callback_data="shop")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            inventory_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def shop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /shop - магазин"""
        user_id = update.effective_user.id
        if user_id not in self.players:
            await update.message.reply_text("❌ Сначала начни игру командой /start")
            return
        
        player = self.players[user_id]
        
        shop_items = self.item_manager.get_shop_items()
        shop_msg = f"""
🏪 *МАГАЗИН КИБЕРПАНК* 🏪

💰 **Твои кредиты:** {player.credits}

🛒 **Доступные товары:**
        """
        
        for item in shop_items:
            shop_msg += f"\n• {item.name} ({item.rarity}) - {item.cost} кредитов"
            shop_msg += f"\n  {item.description}"
        
        shop_msg += "\n\n*Используй /buy <название> для покупки!*"
        
        keyboard = [
            [InlineKeyboardButton("🔍 Поиск предметов", callback_data="search")],
            [InlineKeyboardButton("🎒 Инвентарь", callback_data="inventory")],
            [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            shop_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help - помощь"""
        help_msg = """
🎮 *CYBERPUNK RPG - ПОМОЩЬ* 🎮

🌃 **Описание игры:**
Киберпанк RPG игра в мире будущего с автобоями и поиском предметов по геолокации.

🎯 **Основные команды:**
• /start - Начать игру
• /profile - Профиль персонажа
• /combat - Автобои с другими игроками
• /search - Поиск предметов по геолокации
• /inventory - Инвентарь
• /shop - Магазин предметов
• /help - Эта справка

📍 **Геолокация:**
Для поиска предметов поделись своей локацией, затем используй /search

⚔️ **Автобои:**
Сражайся с другими игроками, получай опыт и кредиты

🎁 **Предметы:**
Находи и покупай предметы для усиления персонажа

*Удачи в неоновом городе!* 🌆
        """
        
        keyboard = [
            [InlineKeyboardButton("🎮 Начать игру", callback_data="main_menu")],
            [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(self.config['telegram_bot_token']).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("profile", self.profile_command))
        application.add_handler(CommandHandler("combat", self.combat_command))
        application.add_handler(CommandHandler("search", self.search_command))
        application.add_handler(CommandHandler("inventory", self.inventory_command))
        application.add_handler(CommandHandler("shop", self.shop_command))
        application.add_handler(CommandHandler("help", self.help_command))
        
        # Обработчики сообщений
        application.add_handler(MessageHandler(filters.LOCATION, self.handle_location))
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Запускаем бота
        logger.info("Cyberpunk RPG Bot запущен!")
        application.run_polling()

if __name__ == "__main__":
    bot = CyberpunkRPGBot()
    bot.run()
