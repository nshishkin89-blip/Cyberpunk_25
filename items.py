#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль предметов для Cyberpunk RPG
Управление оружием, броней, имплантами и другими предметами
"""

import random
from typing import Dict, List, Optional

class Item:
    def __init__(self, name: str, item_type: str, rarity: str, description: str, 
                 cost: int, attack_bonus: int = 0, defense_bonus: int = 0, 
                 speed_bonus: int = 0, critical_bonus: int = 0):
        self.name = name
        self.type = item_type
        self.rarity = rarity
        self.description = description
        self.cost = cost
        self.attack_bonus = attack_bonus
        self.defense_bonus = defense_bonus
        self.speed_bonus = speed_bonus
        self.critical_bonus = critical_bonus
    
    def to_dict(self) -> Dict:
        """Конвертирует предмет в словарь"""
        return {
            "name": self.name,
            "type": self.type,
            "rarity": self.rarity,
            "description": self.description,
            "cost": self.cost,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "speed_bonus": self.speed_bonus,
            "critical_bonus": self.critical_bonus
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """Создает предмет из словаря"""
        return cls(
            name=data["name"],
            item_type=data["type"],
            rarity=data["rarity"],
            description=data["description"],
            cost=data["cost"],
            attack_bonus=data.get("attack_bonus", 0),
            defense_bonus=data.get("defense_bonus", 0),
            speed_bonus=data.get("speed_bonus", 0),
            critical_bonus=data.get("critical_bonus", 0)
        )

class ItemManager:
    def __init__(self):
        self.items_database = self._create_items_database()
        self.rarity_weights = {
            "common": 60,
            "rare": 30,
            "epic": 8,
            "legendary": 2
        }
    
    def _create_items_database(self) -> List[Item]:
        """Создает базу данных предметов"""
        items = []
        
        # Оружие
        items.extend([
            Item("Кибер-меч", "weapon", "common", "Базовый кибер-меч с энергетическим лезвием", 100, attack_bonus=5),
            Item("Плазменный пистолет", "weapon", "rare", "Мощный плазменный пистолет", 300, attack_bonus=12),
            Item("Квантовый лазер", "weapon", "epic", "Продвинутый квантовый лазер", 800, attack_bonus=20),
            Item("Нейронный деструктор", "weapon", "legendary", "Легендарное оружие будущего", 2000, attack_bonus=35),
            Item("Нанобот-кастет", "weapon", "common", "Кастет с наноботами", 80, attack_bonus=4),
            Item("Гравитационная пушка", "weapon", "epic", "Оружие, использующее гравитацию", 1200, attack_bonus=25),
            Item("Хроно-бластер", "weapon", "legendary", "Оружие, замедляющее время", 2500, attack_bonus=40)
        ])
        
        # Броня
        items.extend([
            Item("Кибер-жилет", "armor", "common", "Легкая кибер-броня", 120, defense_bonus=8),
            Item("Нейронный костюм", "armor", "rare", "Броня с нейронной защитой", 400, defense_bonus=15),
            Item("Квантовая броня", "armor", "epic", "Продвинутая квантовая защита", 1000, defense_bonus=25),
            Item("Хроно-щит", "armor", "legendary", "Легендарная броня времени", 2500, defense_bonus=40),
            Item("Нанобот-панцирь", "armor", "rare", "Броня из наноботов", 350, defense_bonus=12),
            Item("Плазменный щит", "armor", "epic", "Энергетический щит", 900, defense_bonus=22)
        ])
        
        # Импланты
        items.extend([
            Item("Нейронный ускоритель", "implant", "common", "Базовый имплант для ускорения", 150, speed_bonus=3),
            Item("Кибер-глаз", "implant", "rare", "Имплант с улучшенным зрением", 500, critical_bonus=8),
            Item("Квантовый процессор", "implant", "epic", "Продвинутый мозговой имплант", 1200, speed_bonus=8, critical_bonus=12),
            Item("Хроно-имплант", "implant", "legendary", "Легендарный имплант времени", 3000, speed_bonus=15, critical_bonus=20),
            Item("Нанобот-стимулятор", "implant", "rare", "Имплант для стимуляции", 400, speed_bonus=5),
            Item("Плазменный активатор", "implant", "epic", "Имплант плазменной энергии", 1000, critical_bonus=15)
        ])
        
        # Утилиты
        items.extend([
            Item("Меди-гель", "utility", "common", "Восстанавливает здоровье", 50),
            Item("Энергетический стимулятор", "utility", "rare", "Временно увеличивает характеристики", 200),
            Item("Квантовый регенератор", "utility", "epic", "Быстрое восстановление", 600),
            Item("Хроно-ревертер", "utility", "legendary", "Полное восстановление", 1500),
            Item("Нанобот-ремонтник", "utility", "rare", "Автоматический ремонт", 300),
            Item("Плазменный аккумулятор", "utility", "epic", "Увеличивает максимальное здоровье", 800)
        ])
        
        return items
    
    def get_random_item(self, rarity: Optional[str] = None) -> Item:
        """Возвращает случайный предмет заданной редкости"""
        if rarity:
            available_items = [item for item in self.items_database if item.rarity == rarity]
        else:
            available_items = self.items_database
        
        if not available_items:
            return self.get_random_item("common")
        
        return random.choice(available_items)
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """Возвращает предметы определенного типа"""
        return [item for item in self.items_database if item.type == item_type]
    
    def get_items_by_rarity(self, rarity: str) -> List[Item]:
        """Возвращает предметы определенной редкости"""
        return [item for item in self.items_database if item.rarity == rarity]
    
    def get_shop_items(self) -> List[Item]:
        """Возвращает предметы для магазина"""
        # Возвращаем случайную выборку предметов для магазина
        shop_items = []
        for rarity in ["common", "rare", "epic", "legendary"]:
            items = self.get_items_by_rarity(rarity)
            if items:
                shop_items.append(random.choice(items))
        
        return shop_items
    
    def generate_location_items(self, location_type: str, player_level: int) -> List[Item]:
        """Генерирует предметы для определенной локации"""
        items = []
        num_items = random.randint(1, 3)
        
        for _ in range(num_items):
            # Определяем редкость на основе уровня игрока и типа локации
            rarity = self._determine_rarity(player_level, location_type)
            item = self.get_random_item(rarity)
            items.append(item)
        
        return items
    
    def _determine_rarity(self, player_level: int, location_type: str) -> str:
        """Определяет редкость предмета на основе уровня игрока и типа локации"""
        # Базовые шансы
        base_chances = {
            "common": 60,
            "rare": 30,
            "epic": 8,
            "legendary": 2
        }
        
        # Модификаторы по уровню
        level_modifier = min(player_level // 5, 3)  # Максимум +3 к шансам
        
        # Модификаторы по типу локации
        location_modifiers = {
            "city_center": {"rare": 5, "epic": 3, "legendary": 1},
            "industrial_zone": {"common": 10, "rare": 5},
            "underground": {"rare": 8, "epic": 5, "legendary": 2},
            "cyber_market": {"rare": 10, "epic": 8, "legendary": 3},
            "wasteland": {"common": 15, "rare": 10, "epic": 5}
        }
        
        # Применяем модификаторы
        final_chances = base_chances.copy()
        
        # Модификатор уровня
        for rarity in ["rare", "epic", "legendary"]:
            final_chances[rarity] += level_modifier
        
        # Модификатор локации
        if location_type in location_modifiers:
            for rarity, modifier in location_modifiers[location_type].items():
                final_chances[rarity] += modifier
                final_chances["common"] -= modifier
        
        # Нормализуем шансы
        total = sum(final_chances.values())
        final_chances = {k: v / total * 100 for k, v in final_chances.items()}
        
        # Выбираем редкость
        rand = random.random() * 100
        cumulative = 0
        
        for rarity, chance in final_chances.items():
            cumulative += chance
            if rand <= cumulative:
                return rarity
        
        return "common"
    
    def get_item_by_name(self, name: str) -> Optional[Item]:
        """Находит предмет по названию"""
        for item in self.items_database:
            if item.name.lower() == name.lower():
                return item
        return None
    
    def get_rarity_color(self, rarity: str) -> str:
        """Возвращает цвет для редкости предмета"""
        colors = {
            "common": "⚪",
            "rare": "🔵",
            "epic": "🟣",
            "legendary": "🟡"
        }
        return colors.get(rarity, "⚪")
    
    def get_rarity_description(self, rarity: str) -> str:
        """Возвращает описание редкости"""
        descriptions = {
            "common": "Обычный",
            "rare": "Редкий",
            "epic": "Эпический",
            "legendary": "Легендарный"
        }
        return descriptions.get(rarity, "Неизвестно")
