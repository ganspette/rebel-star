# tests/test_exceptions.py
"""
Тесты для пользовательских исключений
"""
import pytest
from core.exceptions import *

def test_path_blocked_exception():
    """Тест исключения заблокированного пути."""
    exception = PathBlockedException(5, 10)
    assert str(exception) == "Путь заблокирован в позиции (5, 10)"
    assert exception.x == 5
    assert exception.y == 10

def test_no_ammo_exception():
    """Тест исключения отсутствия патронов."""
    exception = NoAmmoException("Пистолет")
    assert str(exception) == "Нет патронов в Пистолет"

def test_inventory_full_exception():
    """Тест исключения полного инвентаря."""
    exception = InventoryFullException("Магазин", 100)
    assert str(exception) == "Нельзя добавить Магазин: инвентарь полон (вместимость: 100)"

def test_not_your_turn_exception():
    """Тест исключения не своего хода."""
    exception = NotYourTurnException("player", "enemy")
    assert str(exception) == "Фракция player не может действовать сейчас. Требуется: enemy"