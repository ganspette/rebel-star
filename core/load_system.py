# core/load_system.py
"""
Система загрузки игрового состояния
"""
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo
from units.unit import Unit
from maps.test_map import TestMap
from systems.camera import Camera
from systems.game_state import GameState
from core.game_manager import GameManager

class LoadSystem:
    def __init__(self):
        pass
    
    def restore_game(self, save_data, game_manager):
        """
        Восстанавливает игровое состояние из сохраненных данных.
        """
        # Восстанавливаем карту
        map_data = save_data['map_state']
        game_map = TestMap(map_data['width'], map_data['height'])
        game_map.grid = map_data['grid']
        
        # Восстанавливаем юнитов
        game_map.units = self._restore_units(save_data['units'])
        
        # Восстанавливаем предметы
        game_map.items = self._restore_items(save_data['items'])
        
        # Восстанавливаем трупы
        game_map.corpses = self._restore_corpses(save_data['corpses'])
        
        # Настраиваем GameManager
        game_manager.current_map = game_map
        game_manager.game_state.current_map = game_map
        
        # Восстанавливаем состояние игры
        game_state_data = save_data['game_state']
        game_manager.game_state.turn_faction = game_state_data['turn_faction']
        game_manager.game_state.combat_state = game_state_data['combat_state']
        
        # Восстанавливаем выбранного юнита
        selected_index = game_state_data['selected_unit_index']
        if 0 <= selected_index < len(game_map.units):
            game_manager.select_unit(game_map.units[selected_index])
        
        # Восстанавливаем видимых врагов
        game_manager.visible_enemies = set(
            tuple(pos) for pos in game_state_data['visible_enemies']
        )
        
        # Восстанавливаем камеру
        camera_data = save_data['camera']
        game_manager.camera.x = camera_data['x']
        game_manager.camera.y = camera_data['y']
        game_manager.camera.zoom = camera_data['zoom']
        
        # Устанавливаем спрайт-лоадер для юнитов
        for unit in game_map.units:
            unit.sprite_loader = game_manager.current_map.sprite_loader
        
        print("Игровое состояние успешно восстановлено")
        return game_manager
    
    def _restore_units(self, units_data):
        """Восстанавливает юнитов."""
        units = []
        for unit_data in units_data:
            unit = Unit(
                unit_data['unit_type'],
                unit_data['x'],
                unit_data['y'],
                unit_data['faction']
            )
            unit.hp = unit_data['hp']
            unit.max_hp = unit_data['max_hp']
            unit.energy = unit_data['energy']
            unit.max_energy = unit_data['max_energy']
            
            # Восстанавливаем инвентарь
            unit.inventory = self._restore_inventory(unit_data['inventory'])
            
            # Восстанавливаем экипированное оружие
            weapon_data = unit_data['equipped_weapon']
            if weapon_data:
                weapon = self._restore_weapon(weapon_data)
                unit.equip_weapon(weapon)
            
            units.append(unit)
        return units
    
    def _restore_inventory(self, inventory_data):
        """Восстанавливает инвентарь."""
        inventory = []
        for item_data in inventory_data:
            if item_data['type'] == 'weapon':
                weapon = self._restore_weapon(item_data['data'])
                inventory.append(weapon)
            elif item_data['type'] == 'ammo':
                ammo = self._restore_ammo(item_data['data'])
                inventory.append(ammo)
        return inventory
    
    def _restore_weapon(self, weapon_data):
        """Восстанавливает оружие."""
        return Weapon(
            name=weapon_data['name'],
            damage=weapon_data['damage'],
            accuracy=weapon_data['accuracy'],
            max_range=weapon_data['max_range'],
            weight=weapon_data['weight'],
            ammo_capacity=weapon_data['max_ammo'],
            initial_ammo=weapon_data['ammo']
        )
    
    def _restore_ammo(self, ammo_data):
        """Восстанавливает патроны."""
        return Ammo(
            name=ammo_data['name'],
            ammo_type=ammo_data['ammo_type'],
            ammo_count=ammo_data['ammo_count'],
            weight=ammo_data['weight']
        )
    
    def _restore_items(self, items_data):
        """Восстанавливает предметы на карте."""
        items = []
        for item_data in items_data:
            if item_data['type'] == 'weapon':
                obj = self._restore_weapon(item_data['object'])
            elif item_data['type'] == 'ammo':
                obj = self._restore_ammo(item_data['object'])
            else:
                continue
            
            items.append({
                'type': item_data['type'],
                'object': obj,
                'x': item_data['x'],
                'y': item_data['y']
            })
        return items
    
    def _restore_corpses(self, corpses_data):
        """Восстанавливает трупы."""
        corpses = []
        for corpse_data in corpses_data:
            inventory = self._restore_inventory(corpse_data['inventory'])
            corpses.append({
                'x': corpse_data['x'],
                'y': corpse_data['y'],
                'sprite': corpse_data['sprite'],
                'inventory': inventory
            })
        return corpses