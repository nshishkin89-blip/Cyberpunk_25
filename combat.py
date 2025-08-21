#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Боевая система для Cyberpunk RPG
Автобои между игроками с расчетом урона и наград
"""

import random
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from player import Player

class NPC:
    """Неигровой персонаж для боев"""
    def __init__(self, name: str, level: int, health: int, attack: int, defense: int, speed: int):
        self.name = name
        self.level = level
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.critical_damage = 15

class CombatSystem:
    def __init__(self):
        self.npc_database = self._create_npc_database()
        self.combat_history = []
    
    def _create_npc_database(self) -> List[NPC]:
        """Создает базу данных NPC для боев"""
        npcs = []
        
        # Базовые NPC
        npcs.extend([
            NPC("Кибер-гангстер", 1, 80, 12, 6, 7),
            NPC("Нейрон-хакер", 2, 90, 15, 8, 9),
            NPC("Плазменный наемник", 3, 100, 18, 10, 8),
            NPC("Квантовый страж", 4, 120, 22, 15, 10),
            NPC("Хроно-охотник", 5, 140, 25, 18, 12),
            NPC("Нанобот-убийца", 6, 160, 28, 20, 14),
            NPC("Гравитационный воин", 7, 180, 32, 25, 16),
            NPC("Нейронный титан", 8, 200, 35, 28, 18),
            NPC("Квантовый демон", 9, 220, 38, 30, 20),
            NPC("Хроно-властелин", 10, 250, 42, 35, 22)
        ])
        
        # Элитные NPC
        npcs.extend([
            NPC("Кибер-легенда", 15, 300, 50, 40, 25),
            NPC("Нейронный бог", 20, 400, 60, 50, 30),
            NPC("Плазменный тиран", 25, 500, 70, 60, 35),
            NPC("Квантовый император", 30, 600, 80, 70, 40),
            NPC("Хроно-создатель", 35, 700, 90, 80, 45)
        ])
        
        return npcs
    
    def find_opponent(self, player: Player) -> Optional[NPC]:
        """Находит подходящего противника для игрока"""
        # Фильтруем NPC по уровню (не более чем на 3 уровня выше/ниже)
        suitable_npcs = []
        for npc in self.npc_database:
            level_diff = abs(npc.level - player.level)
            if level_diff <= 3:
                suitable_npcs.append(npc)
        
        if not suitable_npcs:
            return None
        
        # Выбираем случайного противника
        return random.choice(suitable_npcs)
    
    def execute_battle(self, player: Player, opponent: NPC) -> Dict:
        """Проводит бой между игроком и противником"""
        # Отмечаем начало боя
        player.start_combat()
        
        # Получаем характеристики игрока с учетом предметов
        player_stats = player.get_total_stats()
        
        # Инициализируем бой
        player_health = player.health
        opponent_health = opponent.health
        
        battle_rounds = []
        round_num = 1
        
        # Основной цикл боя
        while player_health > 0 and opponent_health > 0 and round_num <= 20:
            round_result = self._execute_round(
                player, opponent, player_stats, 
                player_health, opponent_health, round_num
            )
            
            player_health = round_result['player_health']
            opponent_health = round_result['opponent_health']
            
            battle_rounds.append(round_result)
            round_num += 1
        
        # Определяем победителя
        if player_health > 0 and opponent_health <= 0:
            # Игрок победил
            result = "victory"
            message = "Победа! Ты одолел противника!"
            experience_gained = self._calculate_experience_reward(player, opponent, True)
            credits_gained = self._calculate_credits_reward(player, opponent, True)
            
            # Обновляем статистику игрока
            player.combat_wins += 1
            player.add_experience(experience_gained)
            player.add_credits(credits_gained)
            
        elif opponent_health > 0 and player_health <= 0:
            # Противник победил
            result = "defeat"
            message = "Поражение! Противник оказался сильнее..."
            experience_gained = self._calculate_experience_reward(player, opponent, False)
            credits_gained = self._calculate_credits_reward(player, opponent, False)
            
            # Обновляем статистику игрока
            player.combat_losses += 1
            player.add_experience(experience_gained)
            player.add_credits(credits_gained)
            
        else:
            # Ничья (превышен лимит раундов)
            result = "draw"
            message = "Ничья! Бой затянулся слишком долго..."
            experience_gained = self._calculate_experience_reward(player, opponent, False)
            credits_gained = self._calculate_credits_reward(player, opponent, False)
            
            player.add_experience(experience_gained)
            player.add_credits(credits_gained)
        
        # Обновляем здоровье игрока
        player.health = max(1, player_health)  # Минимум 1 HP
        
        # Создаем описание боя
        battle_description = self._create_battle_description(battle_rounds, result)
        
        # Сохраняем историю боя
        battle_record = {
            'timestamp': datetime.now(),
            'player_id': player.user_id,
            'opponent_name': opponent.name,
            'result': result,
            'rounds': len(battle_rounds),
            'experience_gained': experience_gained,
            'credits_gained': credits_gained
        }
        self.combat_history.append(battle_record)
        
        return {
            'result': result,
            'description': battle_description,
            'player_damage': player.max_health - player_health,
            'opponent_damage': opponent.max_health - opponent_health,
            'experience_gained': experience_gained,
            'credits_gained': credits_gained,
            'message': message,
            'rounds': len(battle_rounds)
        }
    
    def _execute_round(self, player: Player, opponent: NPC, player_stats: Dict, 
                       player_health: int, opponent_health: int, round_num: int) -> Dict:
        """Выполняет один раунд боя"""
        round_result = {
            'round': round_num,
            'player_health': player_health,
            'opponent_health': opponent_health,
            'player_damage': 0,
            'opponent_damage': 0,
            'events': []
        }
        
        # Определяем порядок атак (скорость + случайность)
        player_initiative = player_stats['speed'] + random.randint(-2, 2)
        opponent_initiative = opponent.speed + random.randint(-2, 2)
        
        # Игрок атакует первым
        if player_initiative >= opponent_initiative:
            # Атака игрока
            player_damage = self._calculate_damage(player_stats['attack'], opponent.defense, player_stats['critical_damage'])
            opponent_health = max(0, opponent_health - player_damage)
            round_result['opponent_damage'] = player_damage
            round_result['events'].append(f"Ты наносишь {player_damage} урона!")
            
            # Проверяем, не побежден ли противник
            if opponent_health <= 0:
                round_result['opponent_health'] = 0
                return round_result
            
            # Атака противника
            opponent_damage = self._calculate_damage(opponent.attack, player_stats['defense'], opponent.critical_damage)
            player_health = max(0, player_health - opponent_damage)
            round_result['player_damage'] = opponent_damage
            round_result['events'].append(f"Противник наносит {opponent_damage} урона!")
            
        else:
            # Противник атакует первым
            opponent_damage = self._calculate_damage(opponent.attack, player_stats['defense'], opponent.critical_damage)
            player_health = max(0, player_health - opponent_damage)
            round_result['player_damage'] = opponent_damage
            round_result['events'].append(f"Противник наносит {opponent_damage} урона!")
            
            # Проверяем, не побежден ли игрок
            if player_health <= 0:
                round_result['player_health'] = 0
                return round_result
            
            # Атака игрока
            player_damage = self._calculate_damage(player_stats['attack'], opponent.defense, player_stats['critical_damage'])
            opponent_health = max(0, opponent_health - player_damage)
            round_result['opponent_damage'] = player_damage
            round_result['events'].append(f"Ты наносишь {player_damage} урона!")
        
        round_result['player_health'] = player_health
        round_result['opponent_health'] = opponent_health
        
        return round_result
    
    def _calculate_damage(self, attack: int, defense: int, critical_chance: int) -> int:
        """Рассчитывает урон с учетом атаки, защиты и критических ударов"""
        # Базовый урон
        base_damage = max(1, attack - defense // 2)
        
        # Проверка критического удара
        if random.randint(1, 100) <= critical_chance:
            base_damage = int(base_damage * 1.5)
        
        # Добавляем случайность
        final_damage = base_damage + random.randint(-2, 2)
        
        return max(1, final_damage)
    
    def _calculate_experience_reward(self, player: Player, opponent: NPC, victory: bool) -> int:
        """Рассчитывает награду опыта за бой"""
        base_exp = opponent.level * 10
        
        if victory:
            # Бонус за победу
            base_exp = int(base_exp * 1.5)
            
            # Бонус за победу над более сильным противником
            if opponent.level > player.level:
                level_diff = opponent.level - player.level
                base_exp += level_diff * 5
        else:
            # Меньше опыта за поражение
            base_exp = int(base_exp * 0.3)
        
        return max(1, base_exp)
    
    def _calculate_credits_reward(self, player: Player, opponent: NPC, victory: bool) -> int:
        """Рассчитывает награду кредитов за бой"""
        base_credits = opponent.level * 5
        
        if victory:
            # Бонус за победу
            base_credits = int(base_credits * 1.5)
            
            # Бонус за победу над более сильным противником
            if opponent.level > player.level:
                level_diff = opponent.level - player.level
                base_credits += level_diff * 3
        else:
            # Меньше кредитов за поражение
            base_credits = int(base_credits * 0.2)
        
        return max(0, base_credits)
    
    def _create_battle_description(self, battle_rounds: List[Dict], result: str) -> str:
        """Создает описание боя"""
        if not battle_rounds:
            return "Бой не состоялся."
        
        description = f"Бой длился {len(battle_rounds)} раундов.\n\n"
        
        # Показываем ключевые моменты
        for i, round_data in enumerate(battle_rounds[-3:], 1):  # Последние 3 раунда
            description += f"Раунд {round_data['round']}:\n"
            for event in round_data['events']:
                description += f"• {event}\n"
            description += f"Здоровье: Ты {round_data['player_health']}, Противник {round_data['opponent_health']}\n\n"
        
        if result == "victory":
            description += "🏆 Ты одержал победу в этом бою!"
        elif result == "defeat":
            description += "💀 Противник оказался сильнее..."
        else:
            description += "🤝 Бой завершился вничью."
        
        return description
    
    def get_combat_stats(self, player: Player) -> Dict:
        """Возвращает статистику боев игрока"""
        player_battles = [battle for battle in self.combat_history if battle['player_id'] == player.user_id]
        
        if not player_battles:
            return {
                'total_battles': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'average_rounds': 0
            }
        
        total_battles = len(player_battles)
        wins = len([b for b in player_battles if b['result'] == 'victory'])
        losses = len([b for b in player_battles if b['result'] == 'defeat'])
        win_rate = (wins / total_battles) * 100 if total_battles > 0 else 0
        average_rounds = sum(b['rounds'] for b in player_battles) / total_battles
        
        return {
            'total_battles': total_battles,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 1),
            'average_rounds': round(average_rounds, 1)
        }
    
    def get_recent_battles(self, player: Player, limit: int = 5) -> List[Dict]:
        """Возвращает последние бои игрока"""
        player_battles = [battle for battle in self.combat_history if battle['player_id'] == player.user_id]
        return sorted(player_battles, key=lambda x: x['timestamp'], reverse=True)[:limit]
