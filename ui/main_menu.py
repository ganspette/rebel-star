import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu:
    def __init__(self):
        """
        Класс главного меню игры.
        """
        # Загрузка шрифтов
        try:
            self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
            self.small_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 24)
        except:
            print("Could not load freesansbold in MainMenu, using default.")
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        # Опции главного меню
        self.options = ["Новая игра", "Загрузить", "Настройки", "Выход"]
        self.selected = 0
        self.active = True
        
        # Для меню загрузки
        self.save_slots = []
        self.in_load_menu = False
        self.selected_save_slot = 0
        
        # Для анимации (опционально)
        self.animation_offset = 0
        self.animation_speed = 2
        
        # Фоновое изображение (если есть)
        self.background = None
        
        # Инициализируем фон, если доступны изображения
        self._init_background()
    
    def _init_background(self):
        """Инициализирует фоновое изображение, если доступно."""
        try:
            # Можно добавить фоновое изображение для меню
            # Для примера создаем простой градиентный фон
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            # Создаем градиент от темно-серого к черному
            for y in range(SCREEN_HEIGHT):
                color_value = int(30 + (y / SCREEN_HEIGHT) * 20)
                pygame.draw.line(self.background, (color_value, color_value, color_value), 
                               (0, y), (SCREEN_WIDTH, y))
        except Exception as e:
            print(f"Не удалось создать фон меню: {e}")
            self.background = None
    
    def handle_event(self, event):
        """
        Обрабатывает события в главном меню.
        
        Returns:
            str или None: Результат обработки события
        """
        if self.in_load_menu:
            return self._handle_load_menu_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
                self._play_selection_sound()
            elif event.key == pygame.K_RETURN:
                selected_option = self.options[self.selected]
                if selected_option == "Новая игра":
                    self._play_confirmation_sound()
                    return "Новая игра"
                elif selected_option == "Загрузить":
                    self._play_confirmation_sound()
                    self.in_load_menu = True
                    self.selected_save_slot = 0
                    return "load_menu"
                elif selected_option == "Настройки":
                    self._play_confirmation_sound()
                    return "Настройки"
                elif selected_option == "Выход":
                    self._play_confirmation_sound()
                    return "Выход"
            elif event.key == pygame.K_ESCAPE:
                self._play_cancel_sound()
                return "Выход"
        
        # Поддержка мыши для выбора опций
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            result = self._handle_mouse_click(event.pos)
            if result:
                return result
        
        return None
    
    def _handle_load_menu_event(self, event):
        """Обрабатывает события в меню загрузки."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._play_cancel_sound()
                self.in_load_menu = False
                return "back_to_main"
            elif event.key == pygame.K_UP:
                self.selected_save_slot = max(0, self.selected_save_slot - 1)
                self._play_selection_sound()
            elif event.key == pygame.K_DOWN:
                self.selected_save_slot = min(len(self.save_slots) - 1, self.selected_save_slot + 1)
                self._play_selection_sound()
            elif event.key == pygame.K_RETURN:
                if self.save_slots:
                    self._play_confirmation_sound()
                    selected_slot = self.save_slots[self.selected_save_slot]
                    return f"load:{selected_slot['filename']}"
                else:
                    self._play_error_sound()
        
        # Поддержка мыши в меню загрузки
        elif event.type == pygame.MOUSEMOTION:
            self._handle_load_menu_mouse_motion(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # ЛКМ
            result = self._handle_load_menu_mouse_click(event.pos)
            if result:
                return result
        
        return None
    
    def _handle_mouse_motion(self, mouse_pos):
        """Обрабатывает движение мыши для подсветки опций."""
        if not self.in_load_menu:
            # Проверяем наведение на опции главного меню
            for i, option in enumerate(self.options):
                text_rect = self._get_option_rect(i)
                if text_rect.collidepoint(mouse_pos) and self.selected != i:
                    self.selected = i
                    self._play_hover_sound()
                    break
    
    def _handle_mouse_click(self, mouse_pos):
        """Обрабатывает клик мыши по опциям меню."""
        for i, option in enumerate(self.options):
            text_rect = self._get_option_rect(i)
            if text_rect.collidepoint(mouse_pos):
                self.selected = i
                self._play_confirmation_sound()
                
                if option == "Новая игра":
                    return "Новая игра"
                elif option == "Загрузить":
                    self.in_load_menu = True
                    self.selected_save_slot = 0
                    return "load_menu"
                elif option == "Настройки":
                    return "Настройки"
                elif option == "Выход":
                    return "Выход"
        
        return None
    
    def _handle_load_menu_mouse_motion(self, mouse_pos):
        """Обрабатывает движение мыши в меню загрузки."""
        if self.in_load_menu:
            # Проверяем наведение на слоты сохранения
            for i in range(len(self.save_slots)):
                slot_rect = self._get_save_slot_rect(i)
                if slot_rect.collidepoint(mouse_pos) and self.selected_save_slot != i:
                    self.selected_save_slot = i
                    self._play_hover_sound()
                    break
    
    def _handle_load_menu_mouse_click(self, mouse_pos):
        """Обрабатывает клик мыши в меню загрузки."""
        # Проверяем клик по кнопке "Назад"
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        if back_rect.collidepoint(mouse_pos):
            self._play_cancel_sound()
            self.in_load_menu = False
            return "back_to_main"
        
        # Проверяем клик по слотам сохранения
        for i in range(len(self.save_slots)):
            slot_rect = self._get_save_slot_rect(i)
            if slot_rect.collidepoint(mouse_pos):
                self.selected_save_slot = i
                self._play_confirmation_sound()
                selected_slot = self.save_slots[i]
                return f"load:{selected_slot['filename']}"
        
        return None
    
    def _get_option_rect(self, index):
        """Возвращает прямоугольник для опции меню по индексу."""
        text = self.font.render(self.options[index], True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + index * 50))
        # Расширяем область клика для удобства
        return text_rect.inflate(20, 10)
    
    def _get_save_slot_rect(self, index):
        """Возвращает прямоугольник для слота сохранения."""
        start_y = 150
        slot_height = 40
        return pygame.Rect(SCREEN_WIDTH // 2 - 200, start_y + index * slot_height, 400, slot_height)
    
    def _play_selection_sound(self):
        """Воспроизводит звук выбора (заглушка)."""
        # Здесь можно добавить воспроизведение звука
        pass
    
    def _play_confirmation_sound(self):
        """Воспроизводит звук подтверждения (заглушка)."""
        pass
    
    def _play_cancel_sound(self):
        """Воспроизводит звук отмены (заглушка)."""
        pass
    
    def _play_hover_sound(self):
        """Воспроизводит звук наведения (заглушка)."""
        pass
    
    def _play_error_sound(self):
        """Воспроизводит звук ошибки (заглушка)."""
        pass
    
    def set_save_slots(self, slots):
        """
        Устанавливает список слотов сохранения для меню загрузки.
        
        Args:
            slots: Список словарей с информацией о сохранениях
        """
        self.save_slots = slots
    
    def update(self, dt):
        """
        Обновляет состояние меню (анимации и т.д.).
        
        Args:
            dt: Время с последнего обновления в секундах
        """
        # Простая анимация для фона или элементов
        self.animation_offset += self.animation_speed * dt
        if self.animation_offset > 100:
            self.animation_offset = 0
    
    # ui/main_menu.py - метод draw() уже должен быть правильным
    def draw(self, screen):
        """
        Отрисовывает главное меню или меню загрузки.
        
        Args:
            screen: Поверхность pygame для отрисовки
        """
        if self.in_load_menu:
            self._draw_load_menu(screen)
        else:
            self._draw_main_menu(screen)
    
    def _draw_main_menu(self, screen):
        """Отрисовывает главное меню."""
        # Фон
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(DARK_GRAY)
        
        # Заголовок игры
        title = self.font.render("Rebel Star", True, WHITE)
        title_shadow = self.font.render("Rebel Star", True, (100, 100, 100))
        
        # Эффект тени для заголовка
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + 2, 152))
        screen.blit(title_shadow, title_rect)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle = self.small_font.render("Тактическая ролевая игра", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(subtitle, subtitle_rect)
        
        # Опции меню
        for i, option in enumerate(self.options):
            color = WHITE if i == self.selected else LIGHT_GRAY
            
            # Эффект выделения для выбранной опции
            if i == self.selected:
                # Подсветка фона для выбранной опции
                option_bg = pygame.Rect(0, 0, 300, 40)
                option_bg.center = (SCREEN_WIDTH // 2, 250 + i * 50)
                pygame.draw.rect(screen, (50, 50, 70, 128), option_bg, border_radius=5)
                pygame.draw.rect(screen, (100, 100, 120), option_bg, 2, border_radius=5)
            
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250 + i * 50))
            screen.blit(text, text_rect)
            
            # Индикатор выбора (стрелка)
            if i == self.selected:
                arrow_left = self.small_font.render(">", True, (255, 200, 50))
                arrow_right = self.small_font.render("<", True, (255, 200, 50))
                screen.blit(arrow_left, (text_rect.left - 30, text_rect.centery - 10))
                screen.blit(arrow_right, (text_rect.right + 10, text_rect.centery - 10))
        
        # Версия игры
        version = self.small_font.render("Версия 1.0", True, (150, 150, 150))
        version_rect = version.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 10))
        screen.blit(version, version_rect)
        
        # Инструкции
        instructions = [
            "Используйте стрелки ↑↓ или мышь для выбора",
            "Нажмите Enter или ЛКМ для подтверждения",
            "ESC для выхода из игры"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 20))
            screen.blit(text, text_rect)
    
    def _draw_load_menu(self, screen):
        """Отрисовывает меню загрузки игры."""
        # Полупрозрачный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        # Контейнер меню
        menu_width = 600
        menu_height = 500
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        # Фон меню
        pygame.draw.rect(screen, DARK_GRAY, (menu_x, menu_y, menu_width, menu_height), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 120), (menu_x, menu_y, menu_width, menu_height), 3, border_radius=10)
        
        # Заголовок
        title = self.font.render("Загрузка игры", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 40))
        screen.blit(title, title_rect)
        
        # Список сохранений
        if not self.save_slots:
            # Нет сохранений
            no_saves_text = self.small_font.render("Нет доступных сохранений", True, LIGHT_GRAY)
            no_saves_rect = no_saves_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 150))
            screen.blit(no_saves_text, no_saves_rect)
            
            hint_text = self.small_font.render("Начните новую игру, чтобы создать сохранение", True, (200, 200, 100))
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + 180))
            screen.blit(hint_text, hint_rect)
        else:
            # Рисуем список сохранений
            start_y = menu_y + 80
            slot_height = 40
            
            for i, slot in enumerate(self.save_slots):
                slot_rect = pygame.Rect(menu_x + 50, start_y + i * slot_height, menu_width - 100, slot_height - 5)
                
                # Подсветка выбранного слота
                if i == self.selected_save_slot:
                    pygame.draw.rect(screen, (70, 70, 90), slot_rect, border_radius=5)
                    pygame.draw.rect(screen, (150, 150, 170), slot_rect, 2, border_radius=5)
                else:
                    pygame.draw.rect(screen, (60, 60, 70), slot_rect, border_radius=5)
                    pygame.draw.rect(screen, (80, 80, 100), slot_rect, 1, border_radius=5)
                
                # Форматирование информации о сохранении
                if 'created' in slot and slot['created']:
                    date_str = slot['created'][:19].replace('T', ' ')
                else:
                    date_str = "Дата неизвестна"
                
                # Имя сохранения
                name_text = self.small_font.render(slot.get('name', 'Безымянное сохранение'), True, WHITE)
                screen.blit(name_text, (slot_rect.x + 10, slot_rect.y + 5))
                
                # Дата и информация
                info_text = self.small_font.render(f"{date_str} | Карта: {slot.get('map_name', 'test')}", 
                                                  True, LIGHT_GRAY)
                screen.blit(info_text, (slot_rect.x + 10, slot_rect.y + 23))
                
                # Индикатор выбора
                if i == self.selected_save_slot:
                    selector = self.small_font.render("►", True, (255, 200, 50))
                    screen.blit(selector, (slot_rect.x - 20, slot_rect.centery - 8))
            
            # Подсказка о количестве сохранений
            count_text = self.small_font.render(f"Найдено сохранений: {len(self.save_slots)}", 
                                               True, (150, 150, 150))
            count_rect = count_text.get_rect(center=(SCREEN_WIDTH // 2, menu_y + menu_height - 80))
            screen.blit(count_text, count_rect)
        
        # Кнопка "Назад"
        back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 40)
        pygame.draw.rect(screen, (80, 80, 100), back_button_rect, border_radius=5)
        pygame.draw.rect(screen, (120, 120, 140), back_button_rect, 2, border_radius=5)
        
        back_text = self.small_font.render("Назад (ESC)", True, WHITE)
        back_text_rect = back_text.get_rect(center=back_button_rect.center)
        screen.blit(back_text, back_text_rect)
        
        # Инструкции
        instructions = [
            "Используйте стрелки ↑↓ или мышь для выбора сохранения",
            "Нажмите Enter или ЛКМ для загрузки",
            "ESC или кнопка 'Назад' для возврата"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 + i * 20))
            screen.blit(text, text_rect)