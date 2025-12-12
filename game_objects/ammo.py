# game_objects/ammo.py

class Ammo:
    def __init__(self, name, ammo_type, ammo_count, weight):
        self.name = name
        self.ammo_type = ammo_type  # Тип патронов (например, "9mm", "5.56mm", "12g", "7.62mm")
        self.ammo_count = ammo_count # Количество патронов в магазине/обойме
        self.weight = weight

    # --- НОВАЯ ФУНКЦИЯ: Клонирование магазина ---
    def clone(self):
        """Create a copy of this ammo magazine with the same properties but independent state."""
        # Создаём новый объект с теми же параметрами
        new_ammo = Ammo(
            name=self.name,
            ammo_type=self.ammo_type,
            ammo_count=self.ammo_count, # Копируем текущее количество патронов
            weight=self.weight
        )
        return new_ammo
    # --- КОНЕЦ НОВОЙ ФУНКЦИИ ---

    def get_info(self):
        """Get ammo info as dictionary."""
        return {
            'name': self.name,
            'ammo_type': self.ammo_type,
            'ammo_count': self.ammo_count,
            'weight': self.weight
        }
