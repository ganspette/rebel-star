# units/unit.py
import pygame
from core.constants import UNIT_TYPES
from core.exceptions import *  # Добавляем импорт

class Unit:
    def __init__(self, unit_type, x, y, faction="neutral"):
        self.unit_type = unit_type
        self.x = x
        self.y = y
        # --- НОВОЕ: Фракция ---
        self.faction = faction
        # --- КОНЕЦ НОВОГО ---
        
        # Load sprite
        self.sprite_loader = None  # Will be set by game
        # Используем sprite из UNIT_TYPES
        self.sprite_name = UNIT_TYPES[unit_type]['sprite']
        
        # Stats based on unit type
        stats = self._get_base_stats(unit_type)
        self.max_hp = stats['hp']
        self.hp = self.max_hp
        self.strength = stats['strength']
        self.agility = stats['agility']
        self.max_energy = stats['energy']
        self.energy = self.max_energy
        self.accuracy = stats['accuracy']
        self.armor = stats['armor']
        
        # Inventory
        self.inventory = []
        self.equipped_weapon = None
        self.carrying_capacity = self.strength * 10  # Example calculation
        # current_load теперь будет вычисляться по требованию
        # self.current_load = 0 # Удаляем эту переменную
            
    def _get_base_stats(self, unit_type):
        """Get base stats for different unit types"""
        stats = {
            'easy': {
                'hp': 50,
                'strength': 5,
                'agility': 10,
                'energy': 10,
                'accuracy': 70,
                'armor': 2
            },
            'average': {
                'hp': 80,
                'strength': 8,
                'agility': 7,
                'energy': 8,
                'accuracy': 75,
                'armor': 4
            },
            'heavy': {
                'hp': 120,
                'strength': 12,
                'agility': 4,
                'energy': 6,
                'accuracy': 65,
                'armor': 8
            }
        }
        return stats.get(unit_type, stats['easy'])
    
    # --- НОВАЯ ФУНКЦИЯ: Проверка дружественности ---
    def is_friendly(self, other_unit):
        """Check if another unit is friendly."""
        return self.faction == other_unit.faction
    
    def is_enemy(self, other_unit):
        """Check if another unit is an enemy."""
        return self.faction != other_unit.faction
    # --- КОНЕЦ НОВОЙ ФУНКЦИИ ---

    def move(self, dx, dy, game_map):
        """Move unit if possible"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Проверяем энергию
        if self.energy <= 0:
            raise NotEnoughEnergyException(1, self.energy)
        
        # Проверяем доступность пути
        if not game_map.is_walkable(new_x, new_y):
            raise PathBlockedException(new_x, new_y)
        
        # Проверяем, нет ли другого юнита на клетке
        if any(unit.x == new_x and unit.y == new_y for unit in game_map.units):
            raise PathBlockedException(new_x, new_y)
        
        # Выполняем движение
        self.x = new_x
        self.y = new_y
        self.energy -= 1
        return True
    
    def can_move(self):
        """Check if unit can move"""
        return self.energy > 0
    
    def end_turn(self):
        """End turn and restore energy"""
        self.energy = self.max_energy
    
    def take_damage(self, damage):
        """Take damage and reduce HP"""
        actual_damage = max(0, damage - self.armor)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount):
        """Heal unit"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def add_item(self, item):
        """Add item to inventory if not already present and within capacity."""
        # Проверяем, что предмет не в инвентаре и не экипирован
        if item not in self.inventory and item != self.equipped_weapon:
            # Вычисляем нагрузку
            current_load = sum(i.weight for i in self.inventory)
            if self.equipped_weapon:
                current_load += self.equipped_weapon.weight
            
            potential_load = current_load + item.weight
            if potential_load > self.carrying_capacity:
                raise InventoryFullException(
                    item.name if hasattr(item, 'name') else "предмет", 
                    self.carrying_capacity
                )
            
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item):
        """Remove item from inventory."""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def reload_weapon(self, energy_cost=1):
        """Reload equipped weapon using ammo from inventory."""
        if not self.equipped_weapon:
            raise ValueError(f"{self.unit_type} не имеет экипированного оружия для перезарядки.")
    
        if self.energy < energy_cost:
            raise NotEnoughEnergyException(energy_cost, self.energy)
    
        # Найдём подходящий магазин в инвентаре
        ammo_to_use = None
        for item in self.inventory:
            # Проверяем, является ли предмет магазином и подходит ли он
            if (hasattr(item, 'ammo_type') and 
                hasattr(item, 'ammo_count') and 
                item.ammo_type == self.equipped_weapon.ammo_type and 
                item.ammo_count > 0):
                ammo_to_use = item
                break
    
        if not ammo_to_use:
            # Проверяем, может оружие уже полностью заряжено
            if self.equipped_weapon.ammo >= self.equipped_weapon.max_ammo:
                raise ValueError(f"{self.equipped_weapon.name} уже полностью заряжен.")
            else:
                raise NoAmmoException(self.equipped_weapon.name)
    
        # Перезаряжаем
        ammo_left_in_item = self.equipped_weapon.reload(ammo_to_use)
        self.energy -= energy_cost
    
        # Если магазин опустел, удаляем его из инвентаря
        if ammo_left_in_item <= 0:
            self.remove_item(ammo_to_use)
    
        return True

    def equip_weapon(self, weapon):
        """Equip a weapon, unequipping current one if necessary."""
        # Проверяем, есть ли оружие в инвентаре
        if weapon in self.inventory:
            # --- ОБНОВЛЕНО: Обрабатываем вес экипированного оружия ---
            # Если уже есть экипированное оружие, возвращаем его в инвентарь
            if self.equipped_weapon:
                # Добавляем старое оружие в инвентарь (если его там нет)
                if self.equipped_weapon not in self.inventory:
                    self.inventory.append(self.equipped_weapon)

            # Убираем новое оружие ИЗ инвентаря
            self.inventory.remove(weapon)
            # --- КОНЕЦ ОБНОВЛЕНИЯ ---
            # Экипируем новое оружие
            self.equipped_weapon = weapon
            return True
        return False
    
    def unequip_weapon(self):
        """Unequip current weapon and add it to inventory."""
        if self.equipped_weapon:
            # Проверяем, влезет ли вес экипированного оружия в инвентарь
            current_inv_weight = sum(i.weight for i in self.inventory)
            potential_inv_weight = current_inv_weight + self.equipped_weapon.weight
            if potential_inv_weight <= self.carrying_capacity:
                # --- ОБНОВЛЕНО: Обрабатываем вес при снятии ---
                # Добавляем оружие в инвентарь (если его там нет)
                if self.equipped_weapon not in self.inventory:
                    self.inventory.append(self.equipped_weapon)
                # Снимаем оружие
                self.equipped_weapon = None
                # --- КОНЕЦ ОБНОВЛЕНИЯ ---
                return True
            else:
                # Не влезает, не снимаем
                print(f"Cannot unequip {self.equipped_weapon.name}, inventory full!")
                return False
        return False
    
    def drop_item(self, item):
        """Drop an item from inventory or equipped slot. Returns the dropped item object or None."""
        # Попробуем сначала удалить из инвентаря
        if self.remove_item(item):
            return item
        # Если не в инвентаре, проверим экипировку
        if self.equipped_weapon == item:
            # Если это экипированное оружие, сначала снимаем его ВРУЧНУЮ
            # Обнуляем слот экипировки
            self.equipped_weapon = None
            # НЕ добавляем оружие обратно в инвентарь
            return item # Возвращаем сам объект
        return None # Предмет не найден ни в инвентаре, ни экипирован

    def get_sprite(self, size):
        """Get unit sprite"""
        # ИСПРАВЛЕНО: Проверяем, что sprite_loader существует
        if self.sprite_loader:
            return self.sprite_loader.get_scaled_sprite(self.sprite_name, size)
        return None # Возвращаем None, если sprite_loader не установлен
    
    def get_stats(self):
        """Get unit stats as dictionary with Russian keys"""
        # --- ОБНОВЛЕНО: Вычисляем current_load динамически ---
        current_load = sum(i.weight for i in self.inventory)
        if self.equipped_weapon:
            current_load += self.equipped_weapon.weight
        # --- КОНЕЦ ОБНОВЛЕНИЯ ---
        
        # --- НОВОЕ: Получаем информацию об экипированном оружии ---
        equipped_name = "Нет"
        equipped_ammo_info = ""
        if self.equipped_weapon:
            equipped_name = self.equipped_weapon.name
            # Проверяем, есть ли атрибуты ammo и max_ammo у оружия
            if hasattr(self.equipped_weapon, 'ammo') and hasattr(self.equipped_weapon, 'max_ammo'):
                 equipped_ammo_info = f" ({self.equipped_weapon.ammo}/{self.equipped_weapon.max_ammo})"

        # --- КОНЕЦ НОВОГО ---
        return {
            'Тип': UNIT_TYPES[self.unit_type]['name'],
            'Фракция': self.faction, # --- НОВОЕ ---
            'HP': self.hp,
            'Макс. HP': self.max_hp,
            'Сила': self.strength,
            'Ловкость': self.agility,
            'Энергия': self.energy,
            'Макс. энергия': self.max_energy,
            'Точность': self.accuracy,
            'Броня': self.armor,
            'Грузоподъёмность': self.carrying_capacity,
            'Текущая нагрузка': current_load, # Теперь это динамически вычисленное значение
            'Экипировано': equipped_name + equipped_ammo_info # Объединяем имя и патроны
        }
