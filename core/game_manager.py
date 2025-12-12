# core/game_manager.py
from typing import Optional, Tuple
from systems.game_state import GameState
from systems.camera import Camera
from maps.test_map import TestMap
from units.unit import Unit
from core.combat_system import CombatSystem
from core.line_of_sight import LineOfSight
from core.constants import TILE_SIZE, COMBAT_STATE_IDLE
from core.exceptions import *  # Добавляем импорт

class GameManager:
    def __init__(self):
        self.game_state = GameState()
        self.camera = Camera()
        self.current_map: Optional[TestMap] = None
        self.combat_system = CombatSystem()
        self.selected_unit: Optional[Unit] = None
        self.hovered_unit: Optional[Unit] = None
        self.los_system = LineOfSight()
        self.visible_enemies = set()  # Множество координат видимых врагов для текущей фракции
    
    def start_game(self, map_name: str = "test") -> None:
        """Initialize game with selected map."""
        if map_name == "test":
            self.current_map = TestMap()
            self.game_state.current_map = self.current_map
            self.game_state.turn_faction = "player"
            
            print(f"DEBUG: Игра начата с картой {map_name}")
            print(f"DEBUG: На карте {len(self.current_map.units)} юнитов")
            
            if self.current_map:
                # Рассчитываем начальную видимость врагов
                self.update_line_of_sight()
    
    def update_line_of_sight(self):
        """Обновить видимость врагов для текущей фракции."""
        if not self.current_map:
            return
        
        current_faction = self.game_state.turn_faction
        print(f"\nDEBUG: Обновление прямой видимости для фракции {current_faction}")
        
        # Собираем всех врагов (живых) - те, у кого фракция НЕ равна текущей
        all_enemies = [
            u for u in self.current_map.units 
            if u.faction != current_faction and u.hp > 0
        ]
        
        # Собираем всех своих юнитов (живых)
        friendly_units = [
            u for u in self.current_map.units 
            if u.faction == current_faction and u.hp > 0
        ]
        
        visible_enemies = set()
        
        # Каждый свой юнит проверяет видимость врагов
        for friendly in friendly_units:
            visible = self.los_system.get_visible_enemies(
                friendly.x, friendly.y,
                self.current_map,
                all_enemies,  # Только врагов проверяем
                current_faction  # Передаем фракцию зрителя
            )
            for enemy in visible:
                visible_enemies.add((enemy.x, enemy.y))
                print(f"  {friendly.unit_type} ({current_faction}) на ({friendly.x},{friendly.y}) видит врага {enemy.unit_type} ({enemy.faction}) на ({enemy.x},{enemy.y})")
        
        self.visible_enemies = visible_enemies
        print(f"DEBUG: Фракция {current_faction} видит {len(visible_enemies)} врагов")
    
    def is_enemy_visible(self, enemy_x: int, enemy_y: int, faction: str = None) -> bool:
        """Проверяет, виден ли враг на указанных координатах для указанной фракции."""
        if faction is None:
            faction = self.game_state.turn_faction
        
        # Если координаты в visible_enemies - значит виден
        return (enemy_x, enemy_y) in self.visible_enemies
    
    def select_unit(self, unit: Unit) -> bool:
        """Select a unit if it belongs to current faction."""
        if unit.faction == self.game_state.turn_faction:
            self.selected_unit = unit
            self.game_state.selected_unit = unit
            print(f"DEBUG: Выбран юнит {unit.unit_type} на ({unit.x},{unit.y})")
            return True
        print(f"DEBUG: Не могу выбрать {unit.unit_type} - не та фракция ({unit.faction} vs {self.game_state.turn_faction})")
        return False
    
    def move_unit(self, dx: int, dy: int) -> bool:
        """Move selected unit with proper error handling."""
        if not self.selected_unit:
            raise UnitNotFoundException("No unit selected")
        
        if self.selected_unit.faction != self.game_state.turn_faction:
            raise NotYourTurnException(
                self.selected_unit.faction,
                self.game_state.turn_faction
            )
        
        try:
            success = self.selected_unit.move(dx, dy, self.current_map)
            if success:
                print(f"DEBUG: Юнит перемещен на ({self.selected_unit.x},{self.selected_unit.y})")
                self.update_line_of_sight()
            return success
        except GameException as e:
            # Логируем ошибку
            print(f"ERROR: {e}")
            # Показываем сообщение пользователю (будет реализовано в UI)
            self.last_error = str(e)
            return False
    
    def end_turn(self) -> None:
        """End current player turn."""
        if not self.current_map:
            return
        
        print(f"\nDEBUG: Завершение хода для {self.game_state.turn_faction}")
        
        # Восстанавливаем энергию всех юнитов текущей фракции
        for unit in self.current_map.units:
            if unit.faction == self.game_state.turn_faction:
                unit.end_turn()
                print(f"  Юнит {unit.unit_type} восстановил энергию до {unit.energy}")
        
        # Переключаем фракцию
        if self.game_state.turn_faction == "player":
            self.game_state.turn_faction = "enemy"
            print("DEBUG: Ход врага начинается.")
        else:
            self.game_state.turn_faction = "player"
            print("DEBUG: Ход игрока начинается.")
        
        # Сбрасываем состояние боя
        self.game_state.combat_state = COMBAT_STATE_IDLE
        self.game_state.targeting_unit = None
        self.game_state.targeting_weapon = None
        
        # Снимаем выделение
        self.selected_unit = None
        self.game_state.selected_unit = None
        
        # Очищаем пули
        self.combat_system.clear_bullets()
        
        # Обновляем видимость для новой фракции
        self.update_line_of_sight()
    
    def update(self) -> None:
        """Update game state."""
        self.camera.update()
        if self.current_map:
            self.combat_system.update_bullets(self.current_map)
    
    def get_world_coords_from_screen(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        world_x = screen_x / self.camera.zoom + self.camera.x
        world_y = screen_y / self.camera.zoom + self.camera.y
        return world_x, world_y
    
    def get_grid_coords_from_screen(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """Convert screen coordinates to grid coordinates."""
        world_x, world_y = self.get_world_coords_from_screen(screen_x, screen_y)
        grid_x = int(world_x / TILE_SIZE)
        grid_y = int(world_y / TILE_SIZE)
        return grid_x, grid_y
    
    def get_visible_enemies_for_unit(self, unit: Unit):
        """Get enemies visible to a specific unit."""
        if not self.current_map:
            return []
        
        # Собираем всех врагов
        all_enemies = [u for u in self.current_map.units if u.faction != unit.faction and u.hp > 0]
        
        # Получаем видимых врагов для этого юнита
        visible = self.los_system.get_visible_enemies(
            unit.x, unit.y,
            self.current_map,
            all_enemies,
            unit.faction
        )
        
        print(f"DEBUG: Юнит {unit.unit_type} видит {len(visible)} врагов")
        return visible
    
    def can_attack_target(self, attacker: Unit, target: Unit) -> bool:
        """Check if attacker can attack target (visible and in range)."""
        if not attacker.equipped_weapon:
            raise ValueError(f"{attacker.unit_type} не имеет оружия")
        
        # Проверяем видимость для фракции атакующего
        if not self.is_enemy_visible(target.x, target.y, attacker.faction):
            raise TargetNotVisibleException(target.x, target.y)
        
        # Проверяем дистанцию
        distance = abs(attacker.x - target.x) + abs(target.y - attacker.y)
        if distance > attacker.equipped_weapon.max_range:
            raise ValueError(f"Враг вне досягаемости ({distance} > {attacker.equipped_weapon.max_range})")
        
        # Проверяем патроны
        if attacker.equipped_weapon.ammo <= 0:
            raise NoAmmoException(attacker.equipped_weapon.name)
        
        # Проверяем энергию
        if attacker.energy <= 0:
            raise NotEnoughEnergyException(1, attacker.energy)
        
        return True