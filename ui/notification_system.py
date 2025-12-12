# ui/notification_system.py
"""
Система уведомлений для отображения ошибок и сообщений
"""
import pygame
from typing import List, Dict, Any
from core.constants import WHITE, BLACK, RED, GREEN, SCREEN_WIDTH, SCREEN_HEIGHT

class Notification:
    def __init__(self, message: str, type: str = "info", duration: float = 3.0):
        """
        Создает уведомление.
        
        Args:
            message: Текст сообщения
            type: Тип сообщения ("info", "error", "success", "warning")
            duration: Длительность показа в секундах
        """
        self.message = message
        self.type = type
        self.duration = duration
        self.timer = 0.0
        self.active = True
        
        # Цвета в зависимости от типа
        self.colors = {
            "info": (70, 130, 180),     # SteelBlue
            "error": (220, 50, 50),     # Красный
            "success": (50, 180, 50),   # Зеленый
            "warning": (220, 180, 50)   # Желтый
        }

class NotificationSystem:
    def add_info(self, message: str):
        """Добавляет информационное уведомление."""
        self.add_notification(f"ℹ {message}", "info")

    def __init__(self):
        self.notifications: List[Notification] = []
        self.font = pygame.font.Font(None, 24)
        self.max_notifications = 5
        
    def add_notification(self, message: str, type: str = "info"):
        """Добавляет новое уведомление."""
        notification = Notification(message, type)
        self.notifications.append(notification)
        
        # Ограничиваем количество уведомлений
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
    
    def add_error(self, message: str):
        """Добавляет уведомление об ошибке."""
        self.add_notification(f"ОШИБКА: {message}", "error")
    
    def add_success(self, message: str):
        """Добавляет уведомление об успехе."""
        self.add_notification(f"✓ {message}", "success")
    
    def add_warning(self, message: str):
        """Добавляет предупреждение."""
        self.add_notification(f"⚠ {message}", "warning")
    
    def update(self, dt: float):
        """Обновляет таймеры уведомлений."""
        for notification in self.notifications[:]:
            notification.timer += dt
            if notification.timer >= notification.duration:
                self.notifications.remove(notification)
    
    def draw(self, screen):
        """Рисует уведомления на экране."""
        if not self.notifications:
            return
        
        # Позиция первого уведомления
        start_y = 10
        padding = 10
        
        for i, notification in enumerate(self.notifications):
            # Вычисляем прозрачность (fade out)
            alpha = 255
            if notification.timer > notification.duration - 1.0:
                # Плавное исчезновение в последнюю секунду
                alpha = int(255 * (notification.duration - notification.timer))
            
            # Создаем поверхность для уведомления
            text_surface = self.font.render(notification.message, True, WHITE)
            
            # Размеры фона
            bg_width = text_surface.get_width() + padding * 2
            bg_height = text_surface.get_height() + padding * 2
            
            # Позиция
            x = SCREEN_WIDTH - bg_width - 10
            y = start_y + i * (bg_height + 5)
            
            # Цвет фона
            bg_color = notification.colors.get(notification.type, (70, 130, 180))
            
            # Создаем фон с прозрачностью
            bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surface, (*bg_color, alpha), (0, 0, bg_width, bg_height), border_radius=5)
            pygame.draw.rect(bg_surface, (255, 255, 255, alpha), (0, 0, bg_width, bg_height), 2, border_radius=5)
            
            # Рисуем фон и текст
            screen.blit(bg_surface, (x, y))
            text_rect = text_surface.get_rect(center=(x + bg_width // 2, y + bg_height // 2))
            screen.blit(text_surface, text_rect)