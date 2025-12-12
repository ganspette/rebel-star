# game_objects/weapon_definitions.py
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo # Импортируем новый класс

def create_test_weapons():
    """Create test weapons for the game."""
    # Возвращаем *новые* экземпляры каждый раз
    return [
        Weapon("Пистолет", 15, 80, 100, 2, 15, 0), # ammo_capacity=15, initial_ammo=0
        Weapon("Автомат", 25, 75, 100, 4, 30, 0), # ammo_capacity=30, initial_ammo=0
        Weapon("Снайперская винтовка", 50, 95, 100, 6, 10, 0), # ammo_capacity=10, initial_ammo=0
        Weapon("Тяжелый пулемет", 40, 70, 100, 8, 100, 0), # ammo_capacity=100, initial_ammo=0
        Weapon("Дробовик", 35, 60, 100, 5, 8, 0) # ammo_capacity=8, initial_ammo=0
    ]

def create_test_ammo():
    """Create test ammo/magazines for the game."""
    return [
        Ammo("Магазин Пистолета", "9mm", 15, 0.5),
        Ammo("Магазин Автомата", "5.56mm", 30, 0.5),
        Ammo("Обойма Снайперки", "7.62mm", 10, 0.3),
        Ammo("Лента Пулемета", "7.62mm", 100, 5.0),
        Ammo("Коробка Патронов", "12g", 20, 1.0) # Пример "контейнера" с патронами, а не магазина
    ]
