#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример запуска Cyberpunk RPG Bot
Дополнительные настройки и конфигурация
"""

import asyncio
import logging
import sys
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cyberpunk_rpg.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска"""
    try:
        # Проверяем наличие конфигурации
        config_path = Path('config.json')
        if not config_path.exists():
            logger.error("Файл config.json не найден!")
            logger.info("Создайте config.json с токеном вашего бота")
            return
        
        # Импортируем и запускаем бота
        from main import CyberpunkRPGBot
        
        logger.info("🚀 Запуск Cyberpunk RPG Bot...")
        logger.info("🌃 Киберпанк мир ждет тебя!")
        
        # Создаем экземпляр бота
        bot = CyberpunkRPGBot()
        
        # Запускаем бота
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        logger.exception("Детали ошибки:")

if __name__ == "__main__":
    # Запускаем асинхронную функцию
    asyncio.run(main())
