# core/save_system.py
"""
Система сохранения и загрузки игрового состояния
"""
import pickle
import json
import zlib
import base64
from datetime import datetime
from typing import Dict, Any, Optional
import os

class SaveSystem:
    def __init__(self, save_dir="saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
    def save_game(self, game_manager, filename: Optional[str] = None) -> str:
        """
        Сохраняет игровое состояние.
        Возвращает путь к файлу сохранения.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.rsg"
        
        filepath = os.path.join(self.save_dir, filename)
        
        # Собираем состояние игры
        save_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'game_state': self._serialize_game_state(game_manager),
            'map_state': self._serialize_map(game_manager.current_map),
            'units': self._serialize_units(game_manager.current_map.units),
            'items': self._serialize_items(game_manager.current_map.items),
            'corpses': self._serialize_corpses(game_manager.current_map.corpses),
            'camera': {
                'x': game_manager.camera.x,
                'y': game_manager.camera.y,
                'zoom': game_manager.camera.zoom
            }
        }
        
        try:
            # Сериализуем и сжимаем данные
            serialized = pickle.dumps(save_data)
            compressed = zlib.compress(serialized, level=9)
            
            # Кодируем в base64 для надежности
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            # Сохраняем с метаданными
            save_file = {
                'metadata': {
                    'version': '1.0',
                    'name': filename,
                    'created': datetime.now().isoformat(),
                    'map_name': 'test'
                },
                'data': encoded
            }
            
            with open(filepath, 'w') as f:
                json.dump(save_file, f, indent=2)
            
            print(f"Игра сохранена: {filepath}")
            return filepath
            
        except Exception as e:
            raise RuntimeError(f"Ошибка сохранения игры: {e}")
    
    def load_game(self, filepath: str) -> Dict[str, Any]:
        """
        Загружает игровое состояние из файла.
        Возвращает словарь с данными для восстановления.
        """
        try:
            with open(filepath, 'r') as f:
                save_file = json.load(f)
            
            # Декодируем данные
            encoded = save_file['data']
            compressed = base64.b64decode(encoded.encode('utf-8'))
            serialized = zlib.decompress(compressed)
            save_data = pickle.loads(serialized)
            
            print(f"Игра загружена: {filepath}")
            return save_data
            
        except Exception as e:
            raise RuntimeError(f"Ошибка загрузки игры: {e}")
    
    def list_saves(self) -> list:
        """Возвращает список доступных сохранений."""
        saves = []
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.rsg'):
                filepath = os.path.join(self.save_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        metadata = json.load(f)['metadata']
                    saves.append({
                        'filename': filename,
                        'filepath': filepath,
                        'name': metadata['name'],
                        'created': metadata['created'],
                        'map_name': metadata.get('map_name', 'unknown')
                    })
                except:
                    continue
        # Сортируем по дате создания (новые сверху)
        saves.sort(key=lambda x: x['created'], reverse=True)
        return saves
    
    def _serialize_game_state(self, game_manager):
        """Сериализует состояние игры."""
        return {
            'turn_faction': game_manager.game_state.turn_faction,
            'combat_state': game_manager.game_state.combat_state,
            'selected_unit_index': self._find_unit_index(
                game_manager.game_state.selected_unit,
                game_manager.current_map.units
            ),
            'visible_enemies': list(game_manager.visible_enemies)
        }
    
    def _serialize_map(self, game_map):
        """Сериализует карту."""
        return {
            'width': game_map.width,
            'height': game_map.height,
            'grid': game_map.grid,
            'items': self._serialize_items(game_map.items)
        }
    
    def _serialize_units(self, units):
        """Сериализует юнитов."""
        serialized = []
        for unit in units:
            unit_data = {
                'unit_type': unit.unit_type,
                'x': unit.x,
                'y': unit.y,
                'faction': unit.faction,
                'hp': unit.hp,
                'max_hp': unit.max_hp,
                'energy': unit.energy,
                'max_energy': unit.max_energy,
                'inventory': self._serialize_inventory(unit.inventory),
                'equipped_weapon': self._serialize_weapon(unit.equipped_weapon)
            }
            serialized.append(unit_data)
        return serialized
    
    def _serialize_inventory(self, inventory):
        """Сериализует инвентарь."""
        inv_data = []
        for item in inventory:
            if hasattr(item, 'ammo'):
                inv_data.append({
                    'type': 'weapon',
                    'data': self._serialize_weapon(item)
                })
            elif hasattr(item, 'ammo_count'):
                inv_data.append({
                    'type': 'ammo',
                    'data': self._serialize_ammo(item)
                })
        return inv_data
    
    def _serialize_weapon(self, weapon):
        """Сериализует оружие."""
        if not weapon:
            return None
        return {
            'name': weapon.name,
            'damage': weapon.damage,
            'accuracy': weapon.accuracy,
            'max_range': weapon.max_range,
            'weight': weapon.weight,
            'ammo': weapon.ammo,
            'max_ammo': weapon.max_ammo,
            'ammo_type': weapon.ammo_type
        }
    
    def _serialize_ammo(self, ammo):
        """Сериализует патроны."""
        return {
            'name': ammo.name,
            'ammo_type': ammo.ammo_type,
            'ammo_count': ammo.ammo_count,
            'weight': ammo.weight
        }
    
    def _serialize_items(self, items):
        """Сериализует предметы на карте."""
        serialized = []
        for item in items:
            item_data = {
                'type': item['type'],
                'x': item['x'],
                'y': item['y']
            }
            if item['type'] == 'weapon':
                item_data['object'] = self._serialize_weapon(item['object'])
            elif item['type'] == 'ammo':
                item_data['object'] = self._serialize_ammo(item['object'])
            serialized.append(item_data)
        return serialized
    
    def _serialize_corpses(self, corpses):
        """Сериализует трупы."""
        serialized = []
        for corpse in corpses:
            corpse_data = {
                'x': corpse['x'],
                'y': corpse['y'],
                'sprite': corpse['sprite'],
                'inventory': self._serialize_inventory(corrode['inventory'])
            }
            serialized.append(corpse_data)
        return serialized
    
    def _find_unit_index(self, unit, units_list):
        """Находит индекс юнита в списке."""
        if not unit:
            return -1
        for i, u in enumerate(units_list):
            if u is unit:
                return i
        return -1