# maps/test_map.py
from units.unit import Unit
from game_objects.weapon_definitions import create_test_weapons, create_test_ammo
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo
import random

class TestMap:
    def __init__(self, width=15, height=15):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]  # 0 = floor, 1 = wall
        self.units = []
        self.items = []  # Will store weapons and other items (остаётся для совместимости, но не используется)
        # --- НОВОЕ: Хранилище трупов ---
        self.corpses = [] # Список словарей {'x': x, 'y': y, 'inventory': [items], 'sprite': 'dead.png'}
        # --- КОНЕЦ НОВОГО ---
        self.sprite_loader = None
        
        self._create_walls()
        self._create_center_wall()
        self._create_units_and_equip()
        # _create_items_and_ammo больше нет, так как предметы не спавнятся на карте
    
    def _create_walls(self):
        """Create walls around the perimeter"""
        for x in range(self.width):
            self.grid[0][x] = 1  # Top wall
            self.grid[self.height-1][x] = 1  # Bottom wall
        
        for y in range(self.height):
            self.grid[y][0] = 1  # Left wall
            self.grid[y][self.width-1] = 1  # Right wall
    
    def _create_center_wall(self):
        """Create a vertical wall in the center of the map."""
        center_x = self.width // 2
        # Стена высотой 5 клеток, примерно по центру по высоте
        wall_height = 5
        start_y = (self.height - wall_height) // 2
        
        for y in range(start_y, start_y + wall_height):
            self.grid[y][center_x] = 1

    def _create_units_and_equip(self):
        """Create units and equip them with weapons and ammo."""
        weapons = create_test_weapons()
        ammo_types = create_test_ammo() # Теперь это список шаблонов
        
        # Player units (left side) - фракция "player"
        # Heavy unit at center-left
        player_unit = Unit('heavy', 2, self.height // 2, faction="player")
        # Give a weapon and ammo
        if weapons:
            weapon_template = weapons[0] # Берём шаблон
            weapon_copy = weapon_template.clone() # Создаём копию
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            player_unit.add_item(weapon_copy) # Добавляем копию
            player_unit.equip_weapon(weapon_copy) # Экипируем копию
        
        # Give some ammo magazines (copies)
        if ammo_types:
            for _ in range(2): # Два магазина
                ammo_template = random.choice(ammo_types) # Выбираем шаблон
                ammo_copy = ammo_template.clone() # Создаём копию
                player_unit.add_item(ammo_copy) # Добавляем копию
        
        self.units.append(player_unit)
        
        # Additional friendly units on the left
        # Easy unit near top-left
        friendly1 = Unit('easy', 3, 3, faction="player")
        if weapons:
            weapon_template = random.choice(weapons)
            weapon_copy = weapon_template.clone()
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            friendly1.add_item(weapon_copy)
            friendly1.equip_weapon(weapon_copy)
        
        if ammo_types:
            for _ in range(2):
                ammo_template = random.choice(ammo_types)
                ammo_copy = ammo_template.clone()
                friendly1.add_item(ammo_copy)
        
        self.units.append(friendly1)
        
        # Average unit near bottom-left
        friendly2 = Unit('average', 4, self.height - 4, faction="player")
        if weapons:
            weapon_template = random.choice(weapons)
            weapon_copy = weapon_template.clone()
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            friendly2.add_item(weapon_copy)
            friendly2.equip_weapon(weapon_copy)
        
        if ammo_types:
            for _ in range(2):
                ammo_template = random.choice(ammo_types)
                ammo_copy = ammo_template.clone()
                friendly2.add_item(ammo_copy)
        
        self.units.append(friendly2)
        
        # Enemy units (right side) - фракция "enemy"
        # Heavy enemy unit
        enemy_heavy = Unit('enemy_heavy', self.width - 3, self.height // 2, faction="enemy")
        if weapons:
            weapon_template = random.choice(weapons)
            weapon_copy = weapon_template.clone()
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            enemy_heavy.add_item(weapon_copy)
            enemy_heavy.equip_weapon(weapon_copy)
        
        if ammo_types:
            for _ in range(2):
                ammo_template = random.choice(ammo_types)
                ammo_copy = ammo_template.clone()
                enemy_heavy.add_item(ammo_copy)
        
        self.units.append(enemy_heavy)
        
        # Easy enemy near top-right
        enemy_easy = Unit('enemy_easy', self.width - 4, 3, faction="enemy")
        if weapons:
            weapon_template = random.choice(weapons)
            weapon_copy = weapon_template.clone()
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            enemy_easy.add_item(weapon_copy)
            enemy_easy.equip_weapon(weapon_copy)
        
        if ammo_types:
            for _ in range(2):
                ammo_template = random.choice(ammo_types)
                ammo_copy = ammo_template.clone()
                enemy_easy.add_item(ammo_copy)
        
        self.units.append(enemy_easy)
        
        # Average enemy near bottom-right
        enemy_average = Unit('enemy_average', self.width - 5, self.height - 4, faction="enemy")
        if weapons:
            weapon_template = random.choice(weapons)
            weapon_copy = weapon_template.clone()
            
            # ДОБАВЛЯЕМ ПАТРОНЫ В ОРУЖИЕ
            weapon_copy.ammo = weapon_copy.max_ammo  # Полный магазин
            
            enemy_average.add_item(weapon_copy)
            enemy_average.equip_weapon(weapon_copy)
        
        if ammo_types:
            for _ in range(2):
                ammo_template = random.choice(ammo_types)
                ammo_copy = ammo_template.clone()
                enemy_average.add_item(ammo_copy)
        
        self.units.append(enemy_average)


    
    def _create_units(self):
        """Create initial units"""
        # Create player unit at center-left
        player_unit = Unit('heavy', 2, self.height // 2)  # Heavy unit at left center
        self.units.append(player_unit)
        
        # Create some enemy units
        enemy1 = Unit('easy', 10, 5)
        enemy2 = Unit('average', 8, 10)
        self.units.extend([enemy1, enemy2])
    
    # --- ИЗМЕНЕНО: Создание оружия и магазинов ---
    def _create_items_and_ammo(self):
        """Create test items (weapons) and ammo magazines scattered around the map"""
        weapons = create_test_weapons()
        ammo_types = create_test_ammo()
        
        # Place weapons randomly on the map (not on walls or units)
        placed_weapons = 0
        while placed_weapons < 3: # Уменьшим количество оружия
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            # Check if position is walkable and no unit is there
            if self.is_walkable(x, y) and not any(unit.x == x and unit.y == y for unit in self.units):
                weapon = random.choice(weapons)
                # Добавляем оружие
                self.items.append({
                    'type': 'weapon',
                    'object': weapon,
                    'x': x,
                    'y': y
                })
                # print(f"Spawned weapon {weapon.name} at ({x}, {y})") # Отладка

                # --- СПАВН МАГАЗИНОВ ---
                # Найдём подходящий магазин для этого оружия
                matching_ammo = [a for a in ammo_types if a.ammo_type == weapon.ammo_type]
                if matching_ammo:
                    # Спавним два магазина этого типа рядом с оружием
                    for i in range(2):
                        # Попробуем найти соседнюю пустую клетку
                        found_spot = False
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.width and 0 <= ny < self.height and
                                self.is_walkable(nx, ny) and
                                not any(unit.x == nx and unit.y == ny for unit in self.units) and
                                not any(item['x'] == nx and item['y'] == ny for item in self.items)):
                                # Нашли подходящую клетку
                                ammo_item = random.choice(matching_ammo)
                                self.items.append({
                                    'type': 'ammo',
                                    'object': ammo_item,
                                    'x': nx,
                                    'y': ny
                                })
                                # print(f"Spawned ammo {ammo_item.name} at ({nx}, {ny}) for weapon {weapon.name}") # Отладка
                                found_spot = True
                                break # Выходим из цикла поиска клетки после первого успеха
                        # Если не нашли соседнюю клетку, спавним на случайную позицию
                        if not found_spot:
                            placed_ammo = 0
                            while placed_ammo < 1: # Попробуем найти место ещё раз
                                ax = random.randint(1, self.width - 2)
                                ay = random.randint(1, self.height - 2)
                                if (self.is_walkable(ax, ay) and
                                    not any(unit.x == ax and unit.y == ay for unit in self.units) and
                                    not any(item['x'] == ax and item['y'] == ay for item in self.items)):
                                    ammo_item = random.choice(matching_ammo)
                                    self.items.append({
                                        'type': 'ammo',
                                        'object': ammo_item,
                                        'x': ax,
                                        'y': ay
                                    })
                                    # print(f"Spawned ammo {ammo_item.name} at random ({ax}, {ay}) for weapon {weapon.name}") # Отладка
                                    placed_ammo += 1
                # --- КОНЕЦ СПАВНА МАГАЗИНОВ ---
                
                placed_weapons += 1

        # Также добавим немного "свободных" магазинов, не связанных с оружием
        placed_ammo_alone = 0
        while placed_ammo_alone < 2:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)

            # Check if position is walkable and no unit/item is there
            if (self.is_walkable(x, y) and
                not any(unit.x == x and unit.y == y for unit in self.units) and
                not any(item['x'] == x and item['y'] == y for item in self.items)):
                ammo = random.choice(ammo_types)
                self.items.append({
                    'type': 'ammo',
                    'object': ammo,
                    'x': x,
                    'y': y
                })
                placed_ammo_alone += 1
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---

    def is_walkable(self, x, y):
        """Check if position is walkable"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 0
        return False
    
    def get_units_at(self, x, y):
        """Get units at specific position"""
        return [unit for unit in self.units if unit.x == x and unit.y == y]
    
    def get_items_at(self, x, y):
        """Get items at specific position (empty list now, as items are on units)"""
        return []

    def get_corpses_at(self, x, y):
        """Get corpses at specific position"""
        return [corpse for corpse in self.corpses if corpse['x'] == x and corpse['y'] == y]

    # --- НОВАЯ ФУНКЦИЯ: Создание трупа ---
    def create_corpse(self, unit):
        """Create a corpse at unit's location with its inventory."""
        corpse_sprite = 'dead.png'
        if unit.faction == "enemy":
            corpse_sprite = 'enemy_dead.png'
        
        # Проверяем, есть ли уже труп на этой клетке
        existing_corpse = None
        for corpse in self.corpses:
            if corpse['x'] == unit.x and corpse['y'] == unit.y:
                existing_corpse = corpse
                break
        
        if existing_corpse:
            # Объединяем инвентари
            print(f"Объединяем инвентарь с существующим трупом на ({unit.x}, {unit.y})")
            existing_corpse['inventory'].extend(unit.inventory.copy())
            if unit.equipped_weapon:
                existing_corpse['inventory'].append(unit.equipped_weapon)
            print(f"Теперь в трупе {len(existing_corpse['inventory'])} предметов")
        else:
            # Создаем новый труп
            corpse = {
                'x': unit.x,
                'y': unit.y,
                'inventory': unit.inventory.copy(),
                'equipped_weapon': unit.equipped_weapon,
                'sprite': corpse_sprite
            }
            if corpse['equipped_weapon']:
                corpse['inventory'].append(corpse['equipped_weapon'])
            self.corpses.append(corpse)
            print(f"Создан труп на ({corpse['x']}, {corpse['y']}) с {len(corpse['inventory'])} предметами.")
    
    def get_sprite(self, x, y):
        """Get sprite for map tile"""
        if self.grid[y][x] == 1:  # Wall
            return self.sprite_loader.get_scaled_sprite('wall.png', (40, 40))
        else:  # Floor
            return self.sprite_loader.get_scaled_sprite('floor.png', (40, 40))
