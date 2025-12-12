# ui/pickup_menu.py
import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo

class PickupMenu:
    def __init__(self, items, unit, all_map_items):
        # --- Загрузка шрифтов ---
        try:
            self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
            self.small_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 24)
        except:
            print("Could not load freesansbold in PickupMenu, using default.")
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        
        self.items = items  # Список предметов на клетке
        self.unit = unit    # Ссылка на юнита
        self.all_map_items = all_map_items # Ссылка на исходный список предметов карты
        self.active = True
        self.selected_item_index = -1
        self.scroll_offset = 0  # Смещение для прокрутки
        self.max_scroll = 0

        # --- Параметры меню ---
        self.button_width = 100
        self.button_height = 25
        self.item_spacing = 60
        self.button_spacing = 5

        # Размеры меню
        menu_width = 700
        menu_height = 400  # Фиксированная высота
        self.menu_rect = pygame.Rect((SCREEN_WIDTH - menu_width) // 2, (SCREEN_HEIGHT - menu_height) // 2, menu_width, menu_height)
        
        # Область для прокрутки
        self.content_rect = pygame.Rect(
            self.menu_rect.x + 10,
            self.menu_rect.y + 50,
            self.menu_rect.width - 40,  # Оставляем место для скроллбара
            self.menu_rect.height - 100
        )

        # --- Создание кнопок ---
        self.buttons = []
        self._create_buttons()

        # Кнопка "Закрыть"
        close_button_width = 80
        close_button_height = 30
        self.close_button_rect = pygame.Rect(
            self.menu_rect.x + self.menu_rect.width - close_button_width - 10,
            self.menu_rect.y + self.menu_rect.height - close_button_height - 5,
            close_button_width, close_button_height
        )

        # Скроллбар
        self.scrollbar_width = 15
        self.scrollbar_rect = pygame.Rect(
            self.menu_rect.right - self.scrollbar_width - 5,
            self.content_rect.top,
            self.scrollbar_width,
            self.content_rect.height
        )
        self._update_scrollbar()

    def _create_buttons(self):
        """Создать кнопки для всех предметов."""
        self.buttons = []
        y_offset = self.content_rect.y + 10 - self.scroll_offset
        
        for i, item_dict in enumerate(self.items):
            # Проверяем, виден ли предмет в текущей области прокрутки
            if y_offset + self.item_spacing < self.content_rect.top or y_offset > self.content_rect.bottom:
                y_offset += self.item_spacing
                continue
            
            item_obj = item_dict['object']
            item_type = item_dict['type']

            # Текст предмета
            if item_type == 'weapon':
                if isinstance(item_obj, Weapon):
                    text = self.small_font.render(
                        f"{item_obj.name} (Урон: {item_obj.damage}, Точность: {item_obj.accuracy}%, Патроны: {item_obj.ammo}/{item_obj.max_ammo})", 
                        True, WHITE
                    )
                else:
                    text = self.small_font.render(f"{item_obj.name}", True, WHITE)
                    
            elif item_type == 'ammo':
                if isinstance(item_obj, Ammo):
                    text = self.small_font.render(
                        f"{item_obj.name} (Тип: {item_obj.ammo_type}, Патроны: {item_obj.ammo_count})", 
                        True, WHITE
                    )
                else:
                    text = self.small_font.render(f"{item_obj.name}", True, WHITE)
            else:
                text = self.small_font.render(f"Неизвестный предмет", True, WHITE)

            # Позиционирование
            text_rect = pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height())
            
            # Кнопки
            pickup_button_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, self.button_width, self.button_height)
            equip_button_rect = None
            
            if item_type == 'weapon':
                equip_button_rect = pygame.Rect(
                    self.content_rect.x + 10 + self.button_width + self.button_spacing, 
                    y_offset + 25, 
                    self.button_width, 
                    self.button_height
                )

            self.buttons.append({
                'item_dict': item_dict,
                'item_type': item_type,
                'pickup_rect': pickup_button_rect,
                'equip_rect': equip_button_rect,
                'text_surface': text,
                'text_rect': text_rect,
                'index': i,
                'visible': True
            })
            
            y_offset += self.item_spacing

    def _update_scrollbar(self):
        """Обновить параметры скроллбара."""
        total_height = len(self.items) * self.item_spacing
        visible_height = self.content_rect.height
        
        if total_height > visible_height:
            self.max_scroll = total_height - visible_height + 20
            self.thumb_height = max(30, (visible_height / total_height) * self.scrollbar_rect.height)
            self.thumb_rect = pygame.Rect(
                self.scrollbar_rect.x,
                self.scrollbar_rect.y + (self.scroll_offset / self.max_scroll) * (self.scrollbar_rect.height - self.thumb_height),
                self.scrollbar_rect.width,
                self.thumb_height
            )
        else:
            self.max_scroll = 0
            self.thumb_rect = None

    def handle_event(self, event):
        """Handle pickup menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клик по скроллбару
            if event.button == 1 and self.scrollbar_rect.collidepoint(mouse_pos):
                if self.thumb_rect and self.thumb_rect.collidepoint(mouse_pos):
                    self.dragging_scroll = True
                    self.drag_start_y = mouse_pos[1]
                    self.drag_start_scroll = self.scroll_offset
                else:
                    relative_y = mouse_pos[1] - self.scrollbar_rect.y
                    self.scroll_offset = (relative_y / self.scrollbar_rect.height) * self.max_scroll
                    self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
                    self._create_buttons()
                    self._update_scrollbar()
                return None
            
            elif event.button == 4:  # Колесо мыши вверх
                self.scroll_offset = max(0, self.scroll_offset - 30)
                self._create_buttons()
                self._update_scrollbar()
                return None
                
            elif event.button == 5:  # Колесо мыши вниз
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                self._create_buttons()
                self._update_scrollbar()
                return None
            
            elif event.button == 1:  # Левый клик
                for button_info in self.buttons:
                    if button_info['pickup_rect'].collidepoint(mouse_pos):
                        item_dict = button_info['item_dict']
                        item_to_add = item_dict['object']
                        
                        if self.unit.add_item(item_to_add):
                            original_items_on_tile = [
                                orig_item for orig_item in self.all_map_items 
                                if orig_item['x'] == item_dict['x'] and orig_item['y'] == item_dict['y']
                            ]
                            
                            for orig_item in original_items_on_tile:
                                if (orig_item['type'] == item_dict['type'] and 
                                    hasattr(orig_item['object'], 'name') and 
                                    hasattr(item_dict['object'], 'name') and
                                    orig_item['object'].name == item_dict['object'].name):
                                    
                                    self.all_map_items.remove(orig_item)
                                    self.items = [it for it in self.items if it != item_dict]
                                    
                                    if not self.items:
                                        return "close"
                                    
                                    self._create_buttons()
                                    self._update_scrollbar()
                                    return "refresh"
                            
                    elif (button_info['item_type'] == 'weapon' and 
                          button_info['equip_rect'] and 
                          button_info['equip_rect'].collidepoint(mouse_pos)):
                        
                        item_dict = button_info['item_dict']
                        item_to_equip = item_dict['object']
                        
                        if self.unit.add_item(item_to_equip):
                            original_items_on_tile = [
                                orig_item for orig_item in self.all_map_items 
                                if orig_item['x'] == item_dict['x'] and orig_item['y'] == item_dict['y']
                            ]
                            
                            for orig_item in original_items_on_tile:
                                if (orig_item['type'] == item_dict['type'] and 
                                    hasattr(orig_item['object'], 'name') and 
                                    hasattr(item_dict['object'], 'name') and
                                    orig_item['object'].name == item_dict['object'].name):
                                    
                                    self.all_map_items.remove(orig_item)
                                    self.items = [it for it in self.items if it != item_dict]
                                    self.unit.equip_weapon(item_to_equip)
                                    
                                    if not self.items:
                                        return "close"
                                    
                                    self._create_buttons()
                                    self._update_scrollbar()
                                    return "refresh"

                if self.close_button_rect.collidepoint(mouse_pos):
                    return "close"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if hasattr(self, 'dragging_scroll'):
                    self.dragging_scroll = False
                
        elif event.type == pygame.MOUSEMOTION:
            if hasattr(self, 'dragging_scroll') and self.dragging_scroll:
                delta_y = event.pos[1] - self.drag_start_y
                self.scroll_offset = self.drag_start_scroll + (delta_y / self.scrollbar_rect.height) * self.max_scroll
                self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
                self._create_buttons()
                self._update_scrollbar()
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "close"
            elif event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 30)
                self._create_buttons()
                self._update_scrollbar()
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(self.max_scroll, self.scroll_offset + 30)
                self._create_buttons()
                self._update_scrollbar()

        return None

    def draw(self, screen):
        """Draw the pickup menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Menu box
        pygame.draw.rect(screen, DARK_GRAY, self.menu_rect)
        pygame.draw.rect(screen, WHITE, self.menu_rect, 2)

        # Title
        title = self.font.render(f"Подобрать предмет ({len(self.items)} предметов)", True, WHITE)
        title_rect = title.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + 20))
        screen.blit(title, title_rect)

        # Рисуем область контента с маской
        clip_rect = screen.get_clip()
        screen.set_clip(self.content_rect)
        
        # Draw items and buttons
        for button_info in self.buttons:
            screen.blit(button_info['text_surface'], button_info['text_rect'])
            
            # Кнопка "Подобрать"
            pygame.draw.rect(screen, LIGHT_GRAY, button_info['pickup_rect'])
            pickup_text = self.small_font.render("Подобрать", True, BLACK)
            screen.blit(pickup_text, (button_info['pickup_rect'].x + 5, button_info['pickup_rect'].y + 5))
            
            # Кнопка "Экипировать" (только для оружия)
            if button_info['item_type'] == 'weapon' and button_info['equip_rect']:
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['equip_rect'])
                equip_text = self.small_font.render("Экипировать", True, BLACK)
                screen.blit(equip_text, (button_info['equip_rect'].x + 5, button_info['equip_rect'].y + 5))
        
        screen.set_clip(clip_rect)
        
        # Рамка области контента
        pygame.draw.rect(screen, (100, 100, 100), self.content_rect, 1)
        
        # Скроллбар
        if self.max_scroll > 0:
            pygame.draw.rect(screen, (80, 80, 80), self.scrollbar_rect)
            if self.thumb_rect:
                pygame.draw.rect(screen, (120, 120, 120), self.thumb_rect)
                pygame.draw.rect(screen, (150, 150, 150), self.thumb_rect, 1)
        
        # Подсказка для прокрутки
        if self.max_scroll > 0:
            hint_text = self.small_font.render("Используйте колесо мыши или стрелки ↑↓ для прокрутки", True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + self.menu_rect.height - 55))
            screen.blit(hint_text, hint_rect)

        # Кнопка "Закрыть"
        pygame.draw.rect(screen, LIGHT_GRAY, self.close_button_rect)
        close_text = self.small_font.render("Закрыть", True, BLACK)
        screen.blit(close_text, (self.close_button_rect.x + 5, self.close_button_rect.y + 5))