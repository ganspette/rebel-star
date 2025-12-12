# core/exceptions.py
"""
Пользовательские исключения для игры Rebel Star
"""

class GameException(Exception):
    """Базовое исключение для игры"""
    pass

class PathBlockedException(GameException):
    """Путь заблокирован"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        super().__init__(f"Путь заблокирован в позиции ({x}, {y})")

class NoAmmoException(GameException):
    """Нет патронов"""
    def __init__(self, weapon_name):
        super().__init__(f"Нет патронов в {weapon_name}")

class NotEnoughEnergyException(GameException):
    """Недостаточно энергии"""
    def __init__(self, required, available):
        super().__init__(f"Недостаточно энергии. Нужно: {required}, есть: {available}")

class InventoryFullException(GameException):
    """Инвентарь полон"""
    def __init__(self, item_name, capacity):
        super().__init__(f"Нельзя добавить {item_name}: инвентарь полон (вместимость: {capacity})")

class UnitNotFoundException(GameException):
    """Юнит не найден"""
    pass

class NotYourTurnException(GameException):
    """Не ваш ход"""
    def __init__(self, faction, required_faction):
        super().__init__(f"Фракция {faction} не может действовать сейчас. Требуется: {required_faction}")

class TargetNotVisibleException(GameException):
    """Цель не видна"""
    def __init__(self, target_x, target_y):
        super().__init__(f"Цель на позиции ({target_x}, {target_y}) не видна")