# game_objects/bullet.py
import pygame
import math
import random

class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, speed, damage, attacker_unit, accuracy):
        self.x = start_x
        self.y = start_y
        self.speed = speed
        self.damage = damage
        self.attacker = attacker_unit # Ссылка на юнита, который выстрелил
        self.start_x = start_x
        self.start_y = start_y

        # --- Расчёт направления с учётом точности ---
        dx = target_x - start_x
        dy = target_y - start_y
        distance_to_target = math.sqrt(dx**2 + dy**2)

        # Базовое направление (нормализованный вектор)
        if distance_to_target != 0:
            dir_x = dx / distance_to_target
            dir_y = dy / distance_to_target
        else:
            # Если цель на той же позиции (маловероятно, но на всякий случай)
            dir_x, dir_y = 0, 0

        # --- Учёт точности ---
        base_error = (100 - accuracy) / 10
        distance_factor = max(1.0, distance_to_target / 5.0)
        max_error_angle_deg = base_error * distance_factor

        error_angle_rad = math.radians(random.uniform(-max_error_angle_deg, max_error_angle_deg))

        # Поворот базового направления на случайный угол
        cos_angle = math.cos(error_angle_rad)
        sin_angle = math.sin(error_angle_rad)

        self.vx = dir_x * cos_angle - dir_y * sin_angle
        self.vy = dir_x * sin_angle + dir_y * cos_angle
        # --- КОНЕЦ УЧЁТА ТОЧНОСТИ ---

        self.traveled_distance = 0
        self.hit_target = False
        self.hit_wall = False
        # Убираем target_x/y из проверок - будем проверять все юниты на пути
        self.collision_radius = 0.3  # Уменьшим радиус для более точной проверки
        self.max_range = 50  # Максимальная дальность полёта пули

    def update(self, game_map, all_units):
        """
        Update bullet position and check for collisions.
        Returns tuple: (result_type, hit_unit_or_position)
        - 'hit_unit': если пуля попала в юнита (возвращает юнита)
        - 'hit_wall': если пуля попала в стену (возвращает позицию)
        - 'miss': если пуля пролетела максимальную дистанцию (возвращает позицию)
        """
        if self.hit_target or self.hit_wall:
            return ('miss', None)  # Пуля уже достигла цели или врезалась в стену

        # Перемещаем пулю
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed

        # Увеличиваем пройденное расстояние
        self.traveled_distance += self.speed

        # Проверяем, не превышена ли максимальная дальность
        if self.traveled_distance > self.max_range:
            return ('miss', (int(self.x), int(self.y)))

        # Проверяем столкновение со стенами (или другими препятствиями)
        tile_x = int(self.x)
        tile_y = int(self.y)
        if not game_map.is_walkable(tile_x, tile_y):
            # Пуля попала в стену
            self.hit_wall = True
            return ('hit_wall', (tile_x, tile_y))

        # Проверяем столкновение с юнитами на пути
        # Ищем всех юнитов вблизи текущей позиции пули
        for unit in all_units:
            # Пропускаем стреляющего юнита
            if unit == self.attacker:
                continue
                
            # Проверяем расстояние от пули до центра юнита
            dx = self.x - (unit.x + 0.5)
            dy = self.y - (unit.y + 0.5)
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Если пуля достаточно близко к юниту
            if distance <= self.collision_radius:
                self.hit_target = True
                return ('hit_unit', unit)

        return ('miss', None)  # Пуля не достигла цели и не врезалась

    def draw(self, screen, camera, sprite_loader, tile_size):
        """Draw the bullet."""
        screen_x = (self.x * tile_size - camera.x) * camera.zoom
        screen_y = (self.y * tile_size - camera.y) * camera.zoom

        # Рисуем пулю как маленький кружок
        color = (255, 255, 0)  # Жёлтый цвет для примера
        radius = int(3 * camera.zoom)  # Немного увеличим радиус
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)
        
        # Для отладки можно рисовать линию траектории
        # start_screen_x = (self.start_x * tile_size - camera.x) * camera.zoom
        # start_screen_y = (self.start_y * tile_size - camera.y) * camera.zoom
        # pygame.draw.line(screen, (255, 200, 0, 128), 
        #                 (int(start_screen_x), int(start_screen_y)),
        #                 (int(screen_x), int(screen_y)), 1)