# core/combat_system.py
import pygame
import math
from typing import List, Optional, Tuple
from game_objects.bullet import Bullet
from units.unit import Unit
from maps.test_map import TestMap
from core.constants import TILE_SIZE

class CombatSystem:
    def __init__(self):
        self.bullets: List[Bullet] = []
    
    def create_bullet(self, attacker: Unit, target: Unit, weapon) -> Optional[Bullet]:
        """Create a bullet for an attack."""
        # Проверяем, может ли атакующий стрелять
        if not self._can_shoot(attacker, weapon):
            return None
        
        # Вычитаем патроны и энергию
        weapon.ammo -= 1
        attacker.energy -= 1
        
        print(f"{attacker.unit_type} стреляет! Патроны: {weapon.ammo}/{weapon.max_ammo}, Энергия: {attacker.energy}/{attacker.max_energy}")
        
        # Создаем пулю
        bullet = self._create_bullet_object(attacker, target, weapon)
        self.bullets.append(bullet)
        
        return bullet
    
    def _can_shoot(self, attacker: Unit, weapon) -> bool:
        """Check if attacker can shoot."""
        if weapon.ammo <= 0:
            print("Нет патронов!")
            return False
        
        if attacker.energy <= 0:
            print("Недостаточно энергии для атаки!")
            return False
        
        return True
    
    def _create_bullet_object(self, attacker: Unit, target: Unit, weapon) -> Bullet:
        """Create bullet object."""
        # Координаты в центре тайлов
        start_x = attacker.x + 0.5
        start_y = attacker.y + 0.5
        target_x = target.x + 0.5
        target_y = target.y + 0.5
        
        # Параметры пули
        bullet_speed = 0.5  # Тайлов в тик
        bullet_damage = weapon.damage
        bullet_accuracy = (attacker.accuracy + weapon.accuracy) / 2  # Средняя точность
        
        return Bullet(
            start_x=start_x,
            start_y=start_y,
            target_x=target_x,
            target_y=target_y,
            speed=bullet_speed,
            damage=bullet_damage,
            attacker_unit=attacker,
            accuracy=bullet_accuracy
        )
    
    def update_bullets(self, game_map: TestMap) -> None:
        """Update all bullets and handle collisions."""
        bullets_to_remove = []
        
        for bullet in self.bullets[:]:  # Используем копию для безопасного удаления
            collision_result = bullet.update(game_map, game_map.units)
            
            if collision_result[0] == 'hit_unit':
                hit_unit = collision_result[1]
                self._handle_unit_hit(bullet, hit_unit, game_map)
                bullets_to_remove.append(bullet)
            elif collision_result[0] == 'hit_wall':
                hit_position = collision_result[1]
                print(f"Пуля попала в стену в {hit_position}")
                bullets_to_remove.append(bullet)
            elif collision_result[0] == 'miss' and collision_result[1] is not None:
                # Пуля пролетела максимальную дистанцию
                miss_position = collision_result[1]
                print(f"Пуля пролетела мимо, упала в {miss_position}")
                bullets_to_remove.append(bullet)
            # Если результат 'miss' с None, пуля продолжает лететь
        
        # Удаляем обработанные пули
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
    
    def _handle_unit_hit(self, bullet: Bullet, hit_unit: Unit, game_map: TestMap) -> None:
        """Handle bullet hitting a unit."""
        # Убеждаемся, что это не стреляющий юнит (двойная проверка)
        if hit_unit == bullet.attacker:
            print(f"ОШИБКА: Пуля попала в стреляющего юнита!")
            return
        
        # Наносим урон
        damage_dealt = max(0, bullet.damage - hit_unit.armor)
        actual_damage = hit_unit.take_damage(damage_dealt)
        
        # Определяем, был ли это союзник или враг
        relation = "врага" if hit_unit.faction != bullet.attacker.faction else "союзника"
        print(f"Пуля попала в {relation} {hit_unit.unit_type} и нанесла {actual_damage} урона. HP: {hit_unit.hp}/{hit_unit.max_hp}")
        
        # Проверяем смерть юнита
        if hit_unit.hp <= 0:
            self._handle_unit_death(hit_unit, game_map)
    
    def _handle_unit_death(self, unit: Unit, game_map: TestMap) -> None:
        """Handle unit death."""
        print(f"{unit.unit_type} повержен!")
        
        # Создаем труп
        game_map.create_corpse(unit)
        
        # Удаляем юнита из списка
        game_map.units.remove(unit)
    
    def draw_bullets(self, screen, camera, sprite_loader) -> None:
        """Draw all bullets."""
        for bullet in self.bullets:
            bullet.draw(screen, camera, sprite_loader, TILE_SIZE)
    
    def clear_bullets(self) -> None:
        """Clear all bullets (e.g., when returning to menu)."""
        self.bullets.clear()
    
    def has_active_bullets(self) -> bool:
        """Check if there are any active bullets."""
        return len(self.bullets) > 0