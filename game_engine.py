#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Игровой движок для Cyberpunk RPG
Управление основной игровой логикой и механиками
"""

import json
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from player import Player
from items import ItemManager
from combat import CombatSystem
from locations import LocationManager

class GameEngine:
    def __init__(self):
        self.item_manager = ItemManager()
        self.combat_system = CombatSystem()
        self.location_manager = LocationManager()
        self.players: Dict[int, Player] = {}
        self.game_events = []
        self.daily_resets = {}
        
        # Загружаем сохраненных игроков
        self.load_players()
    
    def create_player(self, user_id: int, username: str) -> Player:
        """Создает нового игрока"""
        player = Player(user_id, username)
        self.players[user_id] = player
        self.save_players()
        return player
    
    def get_player(self, user_id: int) -> Optional[Player]:
        """Получает игрока по ID"""
        return self.players.get(user_id)
    
    def save_players(self):
        """Сохраняет всех игроков"""
        try:
            players_data = {}
            for user_id, player in self.players.items():
                players_data[user_id] = player.to_dict()
            
            with open('players_data.json', 'w', encoding='utf-8') as f:
                json.dump(players_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения игроков: {e}")
    
    def load_players(self):
        """Загружает сохраненных игроков"""
        try:
            with open('players_data.json', 'r', encoding='utf-8') as f:
                players_data = json.load(f)
            
            for user_id, player_data in players_data.items():
                player = Player.from_dict(player_data)
                self.players[int(user_id)] = player
        except FileNotFoundError:
            # Файл не существует, начинаем с пустого списка
            pass
        except Exception as e:
            print(f"Ошибка загрузки игроков: {e}")
    
    def process_daily_reset(self):
        """Обрабатывает ежедневный сброс"""
        now = datetime.now()
        today = now.date()
        
        for user_id, player in self.players.items():
            if user_id not in self.daily_resets:
                self.daily_resets[user_id] = None
            
            last_reset = self.daily_resets[user_id]
            if last_reset is None or last_reset.date() < today:
                # Выполняем ежедневный сброс
                self._daily_player_reset(player)
                self.daily_resets[user_id] = now
        
        # Сохраняем изменения
        self.save_players()
    
    def _daily_player_reset(self, player: Player):
        """Выполняет ежедневный сброс для игрока"""
        # Восстанавливаем здоровье
        player.health = player.max_health
        
        # Ежедневные бонусы
        daily_bonus = 50 + (player.level * 5)
        player.add_credits(daily_bonus)
        
        # Сбрасываем кулдауны
        player.last_combat = None
        player.last_search = None
        
        # Добавляем событие
        self.add_game_event(f"Игрок {player.username} получил ежедневный бонус: {daily_bonus} кредитов")
    
    def add_game_event(self, event_description: str):
        """Добавляет игровое событие"""
        event = {
            'timestamp': datetime.now(),
            'description': event_description
        }
        self.game_events.append(event)
        
        # Ограничиваем количество событий
        if len(self.game_events) > 100:
            self.game_events = self.game_events[-100:]
    
    def get_game_events(self, limit: int = 10) -> List[Dict]:
        """Возвращает последние игровые события"""
        return self.game_events[-limit:]
    
    def get_leaderboard(self, category: str = "level", limit: int = 10) -> List[Dict]:
        """Возвращает таблицу лидеров"""
        if not self.players:
            return []
        
        # Сортируем игроков по выбранной категории
        if category == "level":
            sorted_players = sorted(self.players.values(), key=lambda p: p.level, reverse=True)
        elif category == "experience":
            sorted_players = sorted(self.players.values(), key=lambda p: p.experience, reverse=True)
        elif category == "credits":
            sorted_players = sorted(self.players.values(), key=lambda p: p.credits, reverse=True)
        elif category == "combat_wins":
            sorted_players = sorted(self.players.values(), key=lambda p: p.combat_wins, reverse=True)
        elif category == "items_found":
            sorted_players = sorted(self.players.values(), key=lambda p: p.items_found, reverse=True)
        else:
            sorted_players = sorted(self.players.values(), key=lambda p: p.level, reverse=True)
        
        # Формируем таблицу лидеров
        leaderboard = []
        for i, player in enumerate(sorted_players[:limit], 1):
            leaderboard.append({
                'rank': i,
                'username': player.username,
                'level': player.level,
                'value': getattr(player, category, player.level)
            })
        
        return leaderboard
    
    def get_game_stats(self) -> Dict:
        """Возвращает общую статистику игры"""
        if not self.players:
            return {
                'total_players': 0,
                'average_level': 0,
                'total_experience': 0,
                'total_credits': 0,
                'total_combats': 0,
                'total_items_found': 0
            }
        
        total_players = len(self.players)
        total_level = sum(p.level for p in self.players.values())
        total_experience = sum(p.experience for p in self.players.values())
        total_credits = sum(p.credits for p in self.players.values())
        total_combats = sum(p.combat_wins + p.combat_losses for p in self.players.values())
        total_items_found = sum(p.items_found for p in self.players.values())
        
        return {
            'total_players': total_players,
            'average_level': round(total_level / total_players, 1),
            'total_experience': total_experience,
            'total_credits': total_credits,
            'total_combats': total_combats,
            'total_items_found': total_items_found
        }
    
    def process_player_action(self, player: Player, action: str, **kwargs) -> Dict:
        """Обрабатывает действие игрока"""
        result = {
            'success': False,
            'message': '',
            'rewards': {},
            'penalties': {}
        }
        
        if action == "combat":
            # Проверяем возможность боя
            if not player.can_combat():
                result['message'] = f"Подожди {player.get_combat_cooldown()} секунд перед следующим боем!"
                return result
            
            # Находим противника
            opponent = self.combat_system.find_opponent(player)
            if not opponent:
                result['message'] = "Не удалось найти противника. Попробуй позже!"
                return result
            
            # Проводим бой
            battle_result = self.combat_system.execute_battle(player, opponent)
            
            result['success'] = True
            result['message'] = battle_result['message']
            result['rewards'] = {
                'experience': battle_result['experience_gained'],
                'credits': battle_result['credits_gained']
            }
            
            # Добавляем событие
            self.add_game_event(f"Игрок {player.username} сражался с {opponent.name}")
            
        elif action == "search":
            # Проверяем возможность поиска
            if not player.can_search():
                result['message'] = f"Подожди {player.get_search_cooldown()} секунд перед следующим поиском!"
                return result
            
            # Проверяем наличие геолокации
            if 'location' not in kwargs:
                result['message'] = "Нужна геолокация для поиска!"
                return result
            
            # Ищем предметы
            found_items = self.location_manager.search_items(kwargs['location'], player)
            
            if not found_items:
                result['message'] = "Предметы не найдены. Попробуй в другом месте!"
            else:
                result['success'] = True
                result['message'] = f"Найдено {len(found_items)} предметов!"
                result['rewards'] = {
                    'items': [item.name for item in found_items],
                    'experience': len(found_items) * 5  # Опыт за каждый найденный предмет
                }
                
                # Добавляем опыт за поиск
                player.add_experience(len(found_items) * 5)
                
                # Добавляем событие
                self.add_game_event(f"Игрок {player.username} нашел {len(found_items)} предметов")
        
        # Сохраняем изменения
        self.save_players()
        
        return result
    
    def get_player_progress(self, player: Player) -> Dict:
        """Возвращает прогресс игрока"""
        # Вычисляем прогресс до следующего уровня
        progress_percent = (player.experience / player.experience_to_next_level) * 100
        
        # Определяем ранг игрока
        if player.level >= 30:
            rank = "Легенда"
        elif player.level >= 20:
            rank = "Мастер"
        elif player.level >= 15:
            rank = "Эксперт"
        elif player.level >= 10:
            rank = "Ветеран"
        elif player.level >= 5:
            rank = "Опытный"
        else:
            rank = "Новичок"
        
        # Статистика боев
        combat_stats = self.combat_system.get_combat_stats(player)
        
        # Статистика поисков
        location_stats = self.location_manager.get_location_stats(player.user_id)
        
        return {
            'level': player.level,
            'experience': player.experience,
            'experience_to_next_level': player.experience_to_next_level,
            'progress_percent': round(progress_percent, 1),
            'rank': rank,
            'combat_stats': combat_stats,
            'location_stats': location_stats,
            'total_playtime': player.get_playtime()
        }
    
    def get_recommendations(self, player: Player) -> List[str]:
        """Возвращает рекомендации для игрока"""
        recommendations = []
        
        # Проверяем здоровье
        if player.health < player.max_health * 0.5:
            recommendations.append("Твое здоровье низкое! Используй меди-гель или отдохни.")
        
        # Проверяем уровень
        if player.level < 5:
            recommendations.append("Сражайся с противниками, чтобы получить опыт и повысить уровень!")
        
        # Проверяем инвентарь
        if len(player.inventory) < 3:
            recommendations.append("Исследуй локации, чтобы найти полезные предметы!")
        
        # Проверяем кредиты
        if player.credits < 100:
            recommendations.append("Участвуй в боях, чтобы заработать кредиты!")
        
        # Проверяем кулдауны
        if not player.can_combat():
            cooldown = player.get_combat_cooldown()
            recommendations.append(f"Подожди {cooldown} секунд перед следующим боем.")
        
        if not player.can_search():
            cooldown = player.get_search_cooldown()
            recommendations.append(f"Подожди {cooldown} секунд перед следующим поиском.")
        
        if not recommendations:
            recommendations.append("Ты на правильном пути! Продолжай развивать персонажа.")
        
        return recommendations
    
    def cleanup_inactive_players(self, days_inactive: int = 30):
        """Удаляет неактивных игроков"""
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        players_to_remove = []
        
        for user_id, player in self.players.items():
            if player.last_combat and player.last_combat < cutoff_date:
                if player.last_search and player.last_search < cutoff_date:
                    players_to_remove.append(user_id)
        
        for user_id in players_to_remove:
            del self.players[user_id]
            if user_id in self.daily_resets:
                del self.daily_resets[user_id]
        
        if players_to_remove:
            self.save_players()
            self.add_game_event(f"Удалено {len(players_to_remove)} неактивных игроков")
    
    def backup_game_data(self):
        """Создает резервную копию игровых данных"""
        try:
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'players': {str(uid): player.to_dict() for uid, player in self.players.items()},
                'game_events': self.game_events,
                'daily_resets': {str(uid): reset.isoformat() if reset else None 
                                for uid, reset in self.daily_resets.items()}
            }
            
            backup_filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_filename, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            return backup_filename
        except Exception as e:
            print(f"Ошибка создания резервной копии: {e}")
            return None
