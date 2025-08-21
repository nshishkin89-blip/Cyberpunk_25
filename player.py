#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль игрока для Cyberpunk RPG
Управление характеристиками, опытом и прогрессом
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from items import Item

class Player:
    def __init__(self, user_id: int, username: str):
        self.user_id = user_id
        self.username = username
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
        self.credits = 1000
        self.health = 100
        self.max_health = 100
        
        # Боевые характеристики
        self.attack = 10
        self.defense = 5
        self.speed = 8
        self.critical_damage = 15
        
        # Статистика
        self.combat_wins = 0
        self.combat_losses = 0
        self.items_found = 0
        self.playtime_start = datetime.now()
        self.last_combat = None
        self.last_search = None
        
        # Инвентарь
        self.inventory: List[Item] = []
        self.equipped_items: Dict[str, Item] = {}
        
        # Настройки кулдаунов
        self.combat_cooldown = 300  # 5 минут
        self.search_cooldown = 600   # 10 минут
    
    def add_experience(self, amount: int) -> bool:
        """Добавляет опыт и проверяет повышение уровня"""
        self.experience += amount
        
        if self.experience >= self.experience_to_next_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Повышение уровня персонажа"""
        self.level += 1
        self.experience -= self.experience_to_next_level
        
        # Увеличиваем требования к следующему уровню
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        
        # Улучшаем характеристики
        self.max_health += 20
        self.health = self.max_health  # Восстанавливаем здоровье
        self.attack += 3
        self.defense += 2
        self.speed += 1
        self.critical_damage += 1
        
        # Бонусные кредиты за уровень
        self.credits += 100
    
    def add_credits(self, amount: int):
        """Добавляет кредиты"""
        self.credits += amount
    
    def spend_credits(self, amount: int) -> bool:
        """Тратит кредиты, возвращает True если успешно"""
        if self.credits >= amount:
            self.credits -= amount
            return True
        return False
    
    def take_damage(self, damage: int):
        """Получает урон"""
        actual_damage = max(1, damage - self.defense)
        self.health = max(0, self.health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int):
        """Восстанавливает здоровье"""
        self.health = min(self.max_health, self.health + amount)
    
    def add_item(self, item: Item):
        """Добавляет предмет в инвентарь"""
        self.inventory.append(item)
        self.apply_item_effects(item)
    
    def remove_item(self, item: Item):
        """Убирает предмет из инвентаря"""
        if item in self.inventory:
            self.inventory.remove(item)
            self.remove_item_effects(item)
    
    def apply_item_effects(self, item: Item):
        """Применяет эффекты предмета к персонажу"""
        if item.type == "weapon":
            self.attack += item.attack_bonus
        elif item.type == "armor":
            self.defense += item.defense_bonus
        elif item.type == "implant":
            self.speed += item.speed_bonus
            self.critical_damage += item.critical_bonus
    
    def remove_item_effects(self, item: Item):
        """Убирает эффекты предмета с персонажа"""
        if item.type == "weapon":
            self.attack -= item.attack_bonus
        elif item.type == "armor":
            self.defense -= item.defense_bonus
        elif item.type == "implant":
            self.speed -= item.speed_bonus
            self.critical_damage -= item.critical_bonus
    
    def can_combat(self) -> bool:
        """Проверяет, может ли игрок участвовать в бою"""
        if self.last_combat is None:
            return True
        
        time_since_combat = datetime.now() - self.last_combat
        return time_since_combat.total_seconds() >= self.combat_cooldown
    
    def can_search(self) -> bool:
        """Проверяет, может ли игрок искать предметы"""
        if self.last_search is None:
            return True
        
        time_since_search = datetime.now() - self.last_search
        return time_since_search.total_seconds() >= self.search_cooldown
    
    def get_combat_cooldown(self) -> int:
        """Возвращает оставшееся время до следующего боя в секундах"""
        if self.last_combat is None:
            return 0
        
        time_since_combat = datetime.now() - self.last_combat
        remaining = self.combat_cooldown - time_since_combat.total_seconds()
        return max(0, int(remaining))
    
    def get_search_cooldown(self) -> int:
        """Возвращает оставшееся время до следующего поиска в секундах"""
        if self.last_search is None:
            return 0
        
        time_since_search = datetime.now() - self.last_search
        remaining = self.search_cooldown - time_since_search.total_seconds()
        return max(0, int(remaining))
    
    def start_combat(self):
        """Отмечает начало боя"""
        self.last_combat = datetime.now()
    
    def start_search(self):
        """Отмечает начало поиска"""
        self.last_search = datetime.now()
    
    def get_playtime(self) -> str:
        """Возвращает время игры в читаемом формате"""
        playtime = datetime.now() - self.playtime_start
        days = playtime.days
        hours = playtime.seconds // 3600
        minutes = (playtime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}д {hours}ч {minutes}м"
        elif hours > 0:
            return f"{hours}ч {minutes}м"
        else:
            return f"{minutes}м"
    
    def get_total_stats(self) -> Dict[str, int]:
        """Возвращает общие характеристики с учетом предметов"""
        total_attack = self.attack
        total_defense = self.defense
        total_speed = self.speed
        total_critical = self.critical_damage
        
        for item in self.inventory:
            if item.type == "weapon":
                total_attack += item.attack_bonus
            elif item.type == "armor":
                total_defense += item.defense_bonus
            elif item.type == "implant":
                total_speed += item.speed_bonus
                total_critical += item.critical_bonus
        
        return {
            "attack": total_attack,
            "defense": total_defense,
            "speed": total_speed,
            "critical_damage": total_critical
        }
    
    def to_dict(self) -> Dict:
        """Конвертирует игрока в словарь для сохранения"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "level": self.level,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "credits": self.credits,
            "health": self.health,
            "max_health": self.max_health,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "critical_damage": self.critical_damage,
            "combat_wins": self.combat_wins,
            "combat_losses": self.combat_losses,
            "items_found": self.items_found,
            "playtime_start": self.playtime_start.isoformat(),
            "last_combat": self.last_combat.isoformat() if self.last_combat else None,
            "last_search": self.last_search.isoformat() if self.last_search else None,
            "inventory": [item.to_dict() for item in self.inventory]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        """Создает игрока из словаря"""
        player = cls(data["user_id"], data["username"])
        player.level = data["level"]
        player.experience = data["experience"]
        player.experience_to_next_level = data["experience_to_next_level"]
        player.credits = data["credits"]
        player.health = data["health"]
        player.max_health = data["max_health"]
        player.attack = data["attack"]
        player.defense = data["defense"]
        player.speed = data["speed"]
        player.critical_damage = data["critical_damage"]
        player.combat_wins = data["combat_wins"]
        player.combat_losses = data["combat_losses"]
        player.items_found = data["items_found"]
        player.playtime_start = datetime.fromisoformat(data["playtime_start"])
        
        if data["last_combat"]:
            player.last_combat = datetime.fromisoformat(data["last_combat"])
        if data["last_search"]:
            player.last_search = datetime.fromisoformat(data["last_search"])
        
        # Восстанавливаем инвентарь
        for item_data in data["inventory"]:
            item = Item.from_dict(item_data)
            player.inventory.append(item)
            player.apply_item_effects(item)
        
        return player
