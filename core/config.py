# core/config.py
"""
Конфигурационный файл игры
"""
import json
import os
from typing import Dict, Any

class GameConfig:
    def __init__(self, config_file="config/game_config.json"):
        self.config_file = config_file
        self.default_config = {
            "game": {
                "fps": 60,
                "autosave": True,
                "autosave_interval": 300,  # секунд
                "quick_save_slots": 10,
                "max_save_files": 50
            },
            "graphics": {
                "resolution": [1200, 800],
                "fullscreen": False,
                "vsync": True,
                "particle_effects": True,
                "show_damage_numbers": True
            },
            "audio": {
                "volume_master": 0.7,
                "volume_music": 0.5,
                "volume_sfx": 0.8,
                "mute": False
            },
            "controls": {
                "keyboard": {
                    "move_up": "w",
                    "move_down": "s",
                    "move_left": "a",
                    "move_right": "d",
                    "end_turn": "return",
                    "quick_save": "f5",
                    "quick_load": "f9",
                    "inventory": "i",
                    "pickup": "p",
                    "reload": "r"
                },
                "mouse": {
                    "sensitivity": 1.0,
                    "invert_y": False
                }
            },
            "gameplay": {
                "difficulty": "normal",
                "fog_of_war": True,
                "line_of_sight": True,
                "permadeath": False,
                "auto_end_turn": False
            }
        }
        self.config = self.default_config.copy()
        self.load()
    
    def load(self):
        """Загружает конфигурацию из файла."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Рекурсивное обновление конфигурации
                    self._update_dict(self.config, loaded_config)
                print(f"Конфигурация загружена из {self.config_file}")
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}. Используются настройки по умолчанию.")
        else:
            print("Конфигурационный файл не найден. Используются настройки по умолчанию.")
            self.save()  # Создаем файл с настройками по умолчанию
    
    def save(self):
        """Сохраняет конфигурацию в файл."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Конфигурация сохранена в {self.config_file}")
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
    
    def get(self, key_path: str, default=None):
        """Получает значение по пути ключей (например, 'game.fps')."""
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value):
        """Устанавливает значение по пути ключей."""
        keys = key_path.split('.')
        config_ref = self.config
        
        for key in keys[:-1]:
            if key not in config_ref:
                config_ref[key] = {}
            config_ref = config_ref[key]
        
        config_ref[keys[-1]] = value
        self.save()
    
    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию."""
        self.config = self.default_config.copy()
        self.save()
    
    def _update_dict(self, target: Dict, source: Dict):
        """Рекурсивно обновляет словарь."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_dict(target[key], value)
            else:
                target[key] = value

# Глобальный экземпляр конфигурации
config = GameConfig()