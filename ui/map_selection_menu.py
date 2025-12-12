import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT

class MapSelectionMenu:
    def __init__(self):
        """
        Класс меню выбора карты.
        """
        # Загрузка шрифтов
        try:
            self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
            self.small_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 24)
            self.large_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 48)
        except:
            print("Could not load freesansbold in MapSelectionMenu, using default.")
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 48)
        
        # Список доступных карт
        self.maps = [
            {
                'name': 'test',
                'display_name': 'Тестовая карта',
                'description': 'Маленькая тренировочная карта с препятствиями',
                'size': '15x15',
                'difficulty': 'Легкая'
            },
            {
                'name': 'urban',
                'display_name': 'Городские руины',
                'description': 'Заброшенный город с разрушенными зданиями',
                'size': '20x20',
                'difficulty': 'Средняя'
            },
            {
                'name': 'forest',
                'display_name': 'Забытый лес',
                'description': 'Густой лес с ограниченной видимостью',
                'size': '25x25',
                'difficulty': 'Сложная'
            },
            {
                'name': 'military',
                'display_name': 'Военная база',
                'description': 'Заброшенная военная база с укреплениями',
                'size': '30x30',
                'difficulty': 'Очень сложная'
            }
        ]
        
        self.options = [map_info['display_name'] for map_info in self.maps] + ["Назад"]
        self.selected = 0
        self.active = True
        
        # Для анимации
        self.animation_offset = 0
        self.animation_speed = 1.5
        
        # Фоновое изображение
        self.background = None
        self._init_background()
    
    def _init_background(self):
        """Инициализирует фоновое изображение."""
        try:
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            # Градиент от темного к более темному
            for y in range(SCREEN_HEIGHT):
                color_value = int(40 + (y / SCREEN_HEIGHT) * 15)
                pygame.draw.line(self.background, (color_value, color_value, color_value + 10), 
                               (0, y), (SCREEN_WIDTH, y))
        except Exception as e:
            print(f"Не удалось создать фон: {e}")
            self.background = None
    
    def handle_event(self, event):
        """Handle map selection events"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_RETURN:
                selected_option = self.options[self.selected]
                if selected_option == "Назад":
                    self._play_cancel_sound()
                    return "Назад"
                else:
                    self._play_confirmation_sound()
                    return "Выбрать"
            elif event.key == pygame.K_ESCAPE:
                self._play_cancel_sound()
                return "Назад"
        
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
        # Проверяем все опции в основном списке
        for i in range(len(self.options)):
            text_rect = self._get_option_rect(i)
            if text_rect.collidepoint(mouse_pos) and self.selected != i:
                self.selected = i
                self._play_hover_sound()
                return
        
        # Также проверяем кнопку "Назад" внизу
        back_button_rect = self._get_back_button_rect()
        if back_button_rect.collidepoint(mouse_pos) and self.selected != len(self.options) - 1:
            self.selected = len(self.options) - 1
            self._play_hover_sound()
    
    def _handle_mouse_click(self, mouse_pos):
        """Обрабатывает клик мыши по опциям."""
        # Сначала проверяем клик по опциям в основном списке
        for i, option in enumerate(self.options):
            text_rect = self._get_option_rect(i)
            if text_rect.collidepoint(mouse_pos):
                self.selected = i
                
                if option == "Назад":
                    self._play_cancel_sound()
                    return "Назад"
                else:
                    self._play_confirmation_sound()
                    return "Выбрать"
        
        # Проверяем клик по кнопке "Назад" внизу
        back_button_rect = self._get_back_button_rect()
        if back_button_rect.collidepoint(mouse_pos):
            self.selected = len(self.options) - 1
            self._play_cancel_sound()
            return "Назад"
        
        return None
    
    def _get_option_rect(self, index):
        """Возвращает прямоугольник для опции меню."""
        # Используем те же координаты, что и при отрисовке
        y_pos = 340 + index * 60
        return pygame.Rect(SCREEN_WIDTH // 2 - 200, y_pos - 25, 400, 50)
    
    def _get_back_button_rect(self):
        """Возвращает прямоугольник для кнопки 'Назад'."""
        return pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
    
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
    
    def get_selected_map(self):
        """Get the name of the selected map"""
        if self.selected < len(self.maps):
            return self.maps[self.selected]['name']
        return None
    
    def get_selected_map_info(self):
        """Получает информацию о выбранной карте."""
        if self.selected < len(self.maps):
            return self.maps[self.selected]
        return None
    
    def draw(self, screen):
        """Draw the map selection menu"""
        # Фон
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)
        
        # Заголовок
        title = self.large_font.render("Выбор карты", True, WHITE)
        title_shadow = self.large_font.render("Выбор карты", True, (100, 100, 100))
        
        # Эффект тени
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 2, 102))
        screen.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle = self.small_font.render("Выберите локацию для сражения", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        screen.blit(subtitle, subtitle_rect)
        
        # Информация о выбранной карте
        map_info = self.get_selected_map_info()
        if map_info:
            # Фон для информации о карте
            info_bg = pygame.Rect(SCREEN_WIDTH // 2 - 250, 180, 500, 80)
            pygame.draw.rect(screen, (50, 50, 70, 180), info_bg, border_radius=10)
            pygame.draw.rect(screen, (100, 100, 120), info_bg, 2, border_radius=10)
            
            # Название карты
            map_name = self.font.render(map_info['display_name'], True, (255, 200, 100))
            name_rect = map_name.get_rect(center=(SCREEN_WIDTH // 2, 200))
            screen.blit(map_name, name_rect)
            
            # Информация о карте
            info_text = f"{map_info['size']} | Сложность: {map_info['difficulty']}"
            info_surface = self.small_font.render(info_text, True, LIGHT_GRAY)
            info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, 230))
            screen.blit(info_surface, info_rect)
        
        # Опции меню (карты + "Назад")
        for i, option in enumerate(self.options):
            is_selected = i == self.selected
            is_map_option = i < len(self.maps)
            
            # Позиция
            y_pos = 340 + i * 60
            option_rect = self._get_option_rect(i)
            
            # Фон для выбранной опции
            if is_selected:
                pygame.draw.rect(screen, (70, 70, 90, 200), option_rect, border_radius=8)
                pygame.draw.rect(screen, (150, 150, 170), option_rect, 2, border_radius=8)
            
            # Цвет текста
            if is_selected:
                color = WHITE
            elif is_map_option:
                color = (200, 220, 255)  # Голубоватый для карт
            else:
                color = LIGHT_GRAY
            
            # Текст опции
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=option_rect.center)
            screen.blit(text, text_rect)
            
            # Индикатор выбора (только для карт)
            if is_selected and is_map_option:
                # Иконка выбора
                selector_left = self.small_font.render("▶", True, (255, 200, 50))
                selector_right = self.small_font.render("◀", True, (255, 200, 50))
                screen.blit(selector_left, (text_rect.left - 40, text_rect.centery - 10))
                screen.blit(selector_right, (text_rect.right + 20, text_rect.centery - 10))
        
        # Кнопка "Назад" внизу
        back_button_rect = self._get_back_button_rect()
        
        # Проверяем, наведена ли мышь на кнопку
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = back_button_rect.collidepoint(mouse_pos)
        is_selected = self.selected == len(self.options) - 1
        
        # Рисуем кнопку
        if is_hovered or is_selected:
            pygame.draw.rect(screen, (90, 90, 110), back_button_rect, border_radius=5)
            pygame.draw.rect(screen, (170, 170, 190), back_button_rect, 2, border_radius=5)
        else:
            pygame.draw.rect(screen, (80, 80, 100), back_button_rect, border_radius=5)
            pygame.draw.rect(screen, (120, 120, 140), back_button_rect, 2, border_radius=5)
        
        back_text = self.small_font.render("Назад (ESC)", True, WHITE if (is_hovered or is_selected) else LIGHT_GRAY)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Инструкции
        instructions = [
            "Используйте стрелки ↑↓ или мышь для выбора карты",
            "Нажмите Enter или ЛКМ для подтверждения",
            "ESC или кнопка 'Назад' для возврата"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 + i * 20))
            screen.blit(text, text_rect)