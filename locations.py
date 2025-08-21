#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль локаций для Cyberpunk RPG
Управление поиском предметов по геолокации
"""

import random
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from player import Player
from items import ItemManager

class Location:
    """Представляет локацию в игре"""
    def __init__(self, name: str, location_type: str, latitude: float, longitude: float, 
                 description: str, item_spawn_rate: float = 0.7):
        self.name = name
        self.type = location_type
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.item_spawn_rate = item_spawn_rate
        self.last_refresh = datetime.now()
        self.current_items = []
        self.refresh_interval = timedelta(hours=1)  # Обновление каждый час
    
    def needs_refresh(self) -> bool:
        """Проверяет, нужно ли обновить локацию"""
        return datetime.now() - self.last_refresh > self.refresh_interval
    
    def refresh_items(self, item_manager: ItemManager, player_level: int):
        """Обновляет предметы в локации"""
        self.current_items = []
        self.last_refresh = datetime.now()
        
        # Генерируем новые предметы
        if random.random() < self.item_spawn_rate:
            num_items = random.randint(1, 3)
            for _ in range(num_items):
                item = item_manager.get_random_item()
                self.current_items.append(item)
    
    def get_distance(self, lat: float, lon: float) -> float:
        """Вычисляет расстояние до локации в метрах"""
        # Простая формула гаверсинуса для вычисления расстояния
        R = 6371000  # Радиус Земли в метрах
        
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(lat), math.radians(lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c

class LocationManager:
    def __init__(self):
        self.item_manager = ItemManager()
        self.locations = self._create_locations()
        self.player_locations = {}  # Кэш локаций игроков
        self.search_history = {}    # История поисков
    
    def _create_locations(self) -> List[Location]:
        """Создает базу данных локаций"""
        locations = []
        
        # Центр города
        locations.extend([
            Location("Неоновый проспект", "city_center", 55.7558, 37.6176, 
                    "Главная улица города с яркими неоновыми вывесками", 0.8),
            Location("Кибер-плаза", "city_center", 55.7560, 37.6178, 
                    "Центральная площадь с торговыми центрами", 0.9),
            Location("Нейрон-башня", "city_center", 55.7562, 37.6180, 
                    "Высокотехнологичный небоскреб", 0.7),
            Location("Плазменный рынок", "cyber_market", 55.7564, 37.6182, 
                    "Рынок с редкими технологиями", 0.95),
            Location("Квантовый банк", "city_center", 55.7566, 37.6184, 
                    "Банк с квантовой защитой", 0.6)
        ])
        
        # Промышленная зона
        locations.extend([
            Location("Нанобот-завод", "industrial_zone", 55.7570, 37.6186, 
                    "Завод по производству наноботов", 0.7),
            Location("Плазменная фабрика", "industrial_zone", 55.7572, 37.6188, 
                    "Фабрика плазменного оружия", 0.8),
            Location("Квантовая лаборатория", "industrial_zone", 55.7574, 37.6190, 
                    "Секретная лаборатория", 0.6),
            Location("Кибер-верфь", "industrial_zone", 55.7576, 37.6192, 
                    "Верфь для кибер-кораблей", 0.5)
        ])
        
        # Подземелье
        locations.extend([
            Location("Нейронные катакомбы", "underground", 55.7580, 37.6194, 
                    "Подземные туннели с нейронными сетями", 0.8),
            Location("Плазменные пещеры", "underground", 55.7582, 37.6196, 
                    "Пещеры с плазменными кристаллами", 0.9),
            Location("Квантовый бункер", "underground", 55.7584, 37.6198, 
                    "Секретный бункер", 0.7),
            Location("Хроно-шахта", "underground", 55.7586, 37.6200, 
                    "Шахта с временными аномалиями", 0.6)
        ])
        
        # Пустошь
        locations.extend([
            Location("Нейронная пустошь", "wasteland", 55.7590, 37.6202, 
                    "Пустошь с нейронными остатками", 0.5),
            Location("Плазменная пустыня", "wasteland", 55.7592, 37.6204, 
                    "Пустыня с плазменными бурями", 0.6),
            Location("Квантовые руины", "wasteland", 55.7594, 37.6206, 
                    "Руины древней цивилизации", 0.8),
            Location("Хроно-кратер", "wasteland", 55.7596, 37.6208, 
                    "Кратер с временными искажениями", 0.7)
        ])
        
        return locations
    
    def search_items(self, player_location: Dict, player: Player) -> List:
        """Ищет предметы в локации игрока"""
        player_lat = player_location['latitude']
        player_lon = player_location['longitude']
        
        # Отмечаем начало поиска
        player.start_search()
        
        # Находим ближайшие локации
        nearby_locations = self._find_nearby_locations(player_lat, player_lon)
        
        if not nearby_locations:
            return []
        
        found_items = []
        
        for location in nearby_locations:
            # Проверяем, нужно ли обновить локацию
            if location.needs_refresh():
                location.refresh_items(self.item_manager, player.level)
            
            # Проверяем, есть ли предметы в локации
            if location.current_items:
                # Игрок может найти предметы с определенной вероятностью
                if random.random() < 0.7:  # 70% шанс найти предметы
                    # Выбираем случайные предметы
                    num_found = random.randint(1, min(2, len(location.current_items)))
                    selected_items = random.sample(location.current_items, num_found)
                    
                    for item in selected_items:
                        found_items.append(item)
                        # Убираем найденный предмет из локации
                        location.current_items.remove(item)
        
        # Записываем в историю поиска
        self._record_search(player.user_id, player_location, found_items)
        
        return found_items
    
    def _find_nearby_locations(self, lat: float, lon: float, max_distance: float = 1000) -> List[Location]:
        """Находит локации в радиусе поиска"""
        nearby = []
        
        for location in self.locations:
            distance = location.get_distance(lat, lon)
            if distance <= max_distance:
                nearby.append(location)
        
        # Сортируем по расстоянию
        nearby.sort(key=lambda loc: loc.get_distance(lat, lon))
        
        return nearby
    
    def _record_search(self, player_id: int, location: Dict, items_found: List):
        """Записывает поиск в историю"""
        if player_id not in self.search_history:
            self.search_history[player_id] = []
        
        search_record = {
            'timestamp': datetime.now(),
            'location': location,
            'items_found': [item.name for item in items_found],
            'num_items': len(items_found)
        }
        
        self.search_history[player_id].append(search_record)
        
        # Ограничиваем историю последними 10 поисками
        if len(self.search_history[player_id]) > 10:
            self.search_history[player_id] = self.search_history[player_id][-10:]
    
    def get_search_history(self, player_id: int) -> List[Dict]:
        """Возвращает историю поисков игрока"""
        return self.search_history.get(player_id, [])
    
    def get_location_info(self, lat: float, lon: float) -> Dict:
        """Возвращает информацию о локации игрока"""
        nearby_locations = self._find_nearby_locations(lat, lon, 500)  # В радиусе 500м
        
        if not nearby_locations:
            return {
                'type': 'unknown',
                'name': 'Неизвестная территория',
                'description': 'Ты находишься в неизвестной местности.',
                'nearby_locations': [],
                'search_radius': 100
            }
        
        # Определяем тип текущей локации
        closest_location = nearby_locations[0]
        current_type = closest_location.type
        
        # Описание типа локации
        type_descriptions = {
            'city_center': 'Центр киберпанк-города с неоновыми огнями и высокими зданиями.',
            'industrial_zone': 'Промышленная зона с заводами и фабриками будущего.',
            'underground': 'Подземные туннели и катакомбы с секретными технологиями.',
            'cyber_market': 'Рынок с редкими кибер-товарами и имплантами.',
            'wasteland': 'Пустошь на окраине города с опасными аномалиями.'
        }
        
        # Ближайшие локации для поиска
        nearby_info = []
        for loc in nearby_locations[:3]:  # Показываем 3 ближайшие
            distance = int(loc.get_distance(lat, lon))
            nearby_info.append({
                'name': loc.name,
                'distance': distance,
                'type': loc.type,
                'description': loc.description
            })
        
        return {
            'type': current_type,
            'name': closest_location.name,
            'description': type_descriptions.get(current_type, 'Неизвестная территория.'),
            'nearby_locations': nearby_info,
            'search_radius': 100
        }
    
    def create_random_event(self, player_location: Dict, player: Player) -> Optional[Dict]:
        """Создает случайное событие в локации"""
        lat = player_location['latitude']
        lon = player_location['longitude']
        
        # 10% шанс случайного события
        if random.random() > 0.1:
            return None
        
        # Типы случайных событий
        event_types = [
            {
                'type': 'cyber_gang',
                'name': 'Кибер-банда',
                'description': 'Ты столкнулся с кибер-бандой!',
                'reward': {'credits': 50, 'experience': 20},
                'risk': {'health_loss': 10}
            },
            {
                'type': 'tech_scrap',
                'name': 'Технологический мусор',
                'description': 'Нашел кучу технологического мусора!',
                'reward': {'credits': 30, 'experience': 15},
                'risk': {'health_loss': 0}
            },
            {
                'type': 'neural_anomaly',
                'name': 'Нейронная аномалия',
                'description': 'Странная нейронная аномалия!',
                'reward': {'credits': 100, 'experience': 50},
                'risk': {'health_loss': 25}
            },
            {
                'type': 'quantum_storm',
                'name': 'Квантовая буря',
                'description': 'Начинается квантовая буря!',
                'reward': {'credits': 80, 'experience': 40},
                'risk': {'health_loss': 20}
            }
        ]
        
        event = random.choice(event_types)
        
        # Игрок может принять или отказаться от события
        # Пока просто применяем награды и риски
        if 'credits' in event['reward']:
            player.add_credits(event['reward']['credits'])
        if 'experience' in event['reward']:
            player.add_experience(event['reward']['experience'])
        if 'health_loss' in event['risk']:
            player.take_damage(event['risk']['health_loss'])
        
        return event
    
    def get_location_stats(self, player_id: int) -> Dict:
        """Возвращает статистику поисков игрока"""
        history = self.get_search_history(player_id)
        
        if not history:
            return {
                'total_searches': 0,
                'total_items_found': 0,
                'favorite_locations': [],
                'last_search': None
            }
        
        total_searches = len(history)
        total_items_found = sum(record['num_items'] for record in history)
        
        # Любимые локации (где найдено больше всего предметов)
        location_stats = {}
        for record in history:
            loc_key = f"{record['location']['latitude']:.4f},{record['location']['longitude']:.4f}"
            if loc_key not in location_stats:
                location_stats[loc_key] = 0
            location_stats[loc_key] += record['num_items']
        
        favorite_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_searches': total_searches,
            'total_items_found': total_items_found,
            'favorite_locations': [f"Локация {i+1}" for i in range(len(favorite_locations))],
            'last_search': history[-1]['timestamp'] if history else None
        }
