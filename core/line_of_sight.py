# core/line_of_sight.py
import pygame
import math
from typing import Set, Tuple, List

class LineOfSight:
    def __init__(self):
        self.visible_units = set()  # Видимые вражеские юниты
    
    def has_line_of_sight(self, x1: int, y1: int, x2: int, y2: int, game_map) -> bool:
        """
        Check line of sight using Bresenham's line algorithm.
        Возвращает True если есть прямая видимость между точками.
        """
        # Если точки совпадают
        if x1 == x2 and y1 == y2:
            return True
        
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        x, y = x1, y1
        n = 1 + dx + dy
        x_inc = 1 if x2 > x1 else -1
        y_inc = 1 if y2 > y1 else -1
        error = dx - dy
        dx *= 2
        dy *= 2
        
        # Пропускаем начальную точку
        for i in range(1, n):
            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx
            
            # Проверяем границы
            if not (0 <= x < game_map.width and 0 <= y < game_map.height):
                return False
            
            # Если это стена, прерываем луч
            if game_map.grid[y][x] == 1:
                # Если это конечная точка, все равно не видно
                return False
            
            # Если достигли конечной точки
            if x == x2 and y == y2:
                return True
        
        return False
    
    def calculate_los(self, viewer_x: int, viewer_y: int, game_map, all_units, viewer_faction: str) -> Set[Tuple[int, int]]:
        """
        Рассчитать, каких врагов видно с позиции (viewer_x, viewer_y).
        viewer_faction - фракция зрителя.
        """
        visible_enemies = set()
        
        for unit in all_units:
            # Пропускаем своих и мертвых
            if unit.faction == viewer_faction or unit.hp <= 0:
                continue
            
            # Проверяем линию видимости
            if self.has_line_of_sight(viewer_x, viewer_y, unit.x, unit.y, game_map):
                visible_enemies.add((unit.x, unit.y))
                print(f"DEBUG: {viewer_faction} видит врага {unit.unit_type} на ({unit.x},{unit.y})")
        
        self.visible_units = visible_enemies
        return visible_enemies
    
    def get_visible_enemies(self, viewer_x: int, viewer_y: int, game_map, all_units, viewer_faction: str) -> List:
        """Возвращает список видимых вражеских юнитов для конкретной фракции."""
        visible = []
        for unit in all_units:
            # Враги - те, у кого фракция НЕ равна viewer_faction
            if unit.faction != viewer_faction and unit.hp > 0:
                if self.has_line_of_sight(viewer_x, viewer_y, unit.x, unit.y, game_map):
                    visible.append(unit)
        return visible
    
    def reset(self):
        """Сбросить видимые юниты."""
        self.visible_units.clear()