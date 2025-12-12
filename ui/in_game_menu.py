import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT

class InGameMenu:
    def __init__(self):
        """
        Класс меню паузы в игре.
        """
        # Загрузка шрифтов
        try:
            self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 32)  # Уменьшили с 36
            self.small_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 20)  # Уменьшили с 24
            self.large_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 42)  # Уменьшили с 48
        except:
            print("Could not load freesansbold in InGameMenu, using default.")
            self.font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 20)
            self.large_font = pygame.font.Font(None, 42)
        
        # Уменьшили количество опций или сделаем их компактнее
        self.options = ["Продолжить", "Сохранить игру", "Загрузить игру", "Выход в меню", "Выход"]
        self.selected = 0
        self.active = True
        
        # Уменьшили отступы между опциями
        self.option_spacing = 50  # Было 60
        
        # Для анимации
        self.animation_offset = 0
        self.animation_speed = 2
        
        # Полупрозрачный фон
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
    
    def handle_event(self, event):
        """Handle pause menu events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_RETURN:
                selected_option = self.options[self.selected]
                self._play_confirmation_sound()
                return selected_option
            elif event.key == pygame.K_ESCAPE:
                self._play_cancel_sound()
                return "Продолжить"
        
        # Поддержка мыши
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            result = self._handle_mouse_click(event.pos)
            if result:
                return result
        
        return None
    
    def _handle_mouse_motion(self, mouse_pos):
        """Обрабатывает движение мыши для подсветки опций."""
        menu_x, menu_y, menu_width, menu_height = self._get_menu_dimensions()
        
        for i in range(len(self.options)):
            option_rect = self._get_option_rect(i, menu_x, menu_y)
            if option_rect.collidepoint(mouse_pos) and self.selected != i:
                self.selected = i
                self._play_hover_sound()
                break
    
    def _handle_mouse_click(self, mouse_pos):
        """Обрабатывает клик мыши по опциям."""
        menu_x, menu_y, menu_width, menu_height = self._get_menu_dimensions()
        
        for i, option in enumerate(self.options):
            option_rect = self._get_option_rect(i, menu_x, menu_y)
            if option_rect.collidepoint(mouse_pos):
                self.selected = i
                self._play_confirmation_sound()
                return option
        
        return None
    
    def _get_menu_dimensions(self):
        """Возвращает размеры и позицию меню."""
        menu_width = 450  # Уменьшили с 500
        menu_height = 450  # Уменьшили с 450
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        return menu_x, menu_y, menu_width, menu_height
    
    def _get_option_rect(self, index, menu_x, menu_y):
        """Возвращает прямоугольник для опции меню."""
        y_pos = menu_y + 150 + index * self.option_spacing  # Уменьшили начальную позицию
        return pygame.Rect(menu_x + 50, y_pos - 20, 350, 40)  # Уменьшили высоту
    
    def _play_selection_sound(self):
        """Воспроизводит звук выбора."""
        pass
    
    def _play_confirmation_sound(self):
        """Воспроизводит звук подтверждения."""
        pass
    
    def _play_cancel_sound(self):
        """Воспроизводит звук отмены."""
        pass
    
    def _play_hover_sound(self):
        """Воспроизводит звук наведения."""
        pass
    
    def update(self, dt):
        """Обновляет анимации."""
        self.animation_offset += self.animation_speed * dt
        if self.animation_offset > 100:
            self.animation_offset = 0
    
    def draw(self, screen):
        """Draw the pause menu overlay"""
        # Полупрозрачный оверлей поверх игры
        screen.blit(self.overlay, (0, 0))
        
        menu_x, menu_y, menu_width, menu_height = self._get_menu_dimensions()
        
        # Фон меню с эффектом свечения
        for i in range(3, 0, -1):
            glow_rect = pygame.Rect(
                menu_x - i, menu_y - i,
                menu_width + i*2, menu_height + i*2
            )
            glow_color = (50, 70, 100, 50 - i*10)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height), 
                           border_radius=12 + i*2)  # Уменьшили радиус
            screen.blit(glow_surface, glow_rect)
        
        # Основной фон меню
        menu_bg = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, (40, 45, 60), menu_bg, border_radius=12)
        pygame.draw.rect(screen, (80, 90, 120), menu_bg, 3, border_radius=12)
        
        # Внутренняя подсветка
        inner_bg = pygame.Rect(menu_x + 5, menu_y + 5, menu_width - 10, menu_height - 10)
        pygame.draw.rect(screen, (50, 55, 70, 100), inner_bg, border_radius=10)
        
        # Заголовок
        title = self.large_font.render("Пауза", True, (255, 220, 100))
        title_shadow = self.large_font.render("Пауза", True, (150, 130, 60, 150))
        
        # Эффект тени
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 2, menu_y + 53))
        screen.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 50))
        screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle = self.small_font.render("Игра приостановлена", True, (180, 190, 220))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 95))
        screen.blit(subtitle, subtitle_rect)
        
        # Разделительная линия
        line_y = menu_y + 115
        pygame.draw.line(screen, (80, 90, 120), (menu_x + 50, line_y), (menu_x + menu_width - 50, line_y), 2)
        pygame.draw.line(screen, (120, 140, 180), (menu_x + 50, line_y + 1), (menu_x + menu_width - 50, line_y + 1), 1)
        
        # Опции меню
        for i, option in enumerate(self.options):
            is_selected = i == self.selected
            y_pos = menu_y + 150 + i * self.option_spacing
            option_rect = self._get_option_rect(i, menu_x, menu_y)
            
            # Фон для выбранной опции
            if is_selected:
                # Анимированный фон
                pulse = (pygame.time.get_ticks() // 10) % 100
                alpha = 100 + int(50 * (pulse / 100))
                
                pulse_surface = pygame.Surface((option_rect.width, option_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(pulse_surface, (70, 80, 110, alpha), 
                               (0, 0, option_rect.width, option_rect.height), border_radius=6)
                screen.blit(pulse_surface, option_rect)
                
                pygame.draw.rect(screen, (150, 170, 220), option_rect, 2, border_radius=6)
            
            # Определяем цвет для опции
            if option == "Продолжить":
                color = (180, 220, 180) if is_selected else (140, 200, 140)
            elif option == "Сохранить игру":
                color = (180, 200, 220) if is_selected else (140, 180, 220)
            elif option == "Загрузить игру":
                color = (220, 200, 180) if is_selected else (220, 180, 140)
            elif option == "Выход в меню":
                color = (220, 180, 180) if is_selected else (220, 140, 140)
            elif option == "Выход":
                color = (220, 150, 150) if is_selected else (220, 100, 100)
            else:
                color = WHITE if is_selected else LIGHT_GRAY
            
            # Текст опции
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=option_rect.center)
            screen.blit(text, text_rect)
            
            # Индикатор выбора
            if is_selected:
                selector_left = self.small_font.render("»", True, (255, 200, 50))
                selector_right = self.small_font.render("«", True, (255, 200, 50))
                screen.blit(selector_left, (text_rect.left - 30, text_rect.centery - 8))
                screen.blit(selector_right, (text_rect.right + 15, text_rect.centery - 8))
        
        # Подсказки внизу
        hints_y = menu_y + menu_height - 60
        hints = [
            "ESC - Продолжить игру",
            "F5 - Быстрое сохранение",
            "F9 - Быстрая загрузка"
        ]
        
        for i, hint in enumerate(hints):
            hint_surface = self.small_font.render(hint, True, (150, 160, 180))
            hint_rect = hint_surface.get_rect(center=(SCREEN_WIDTH // 2, hints_y + i * 18))
            screen.blit(hint_surface, hint_rect)