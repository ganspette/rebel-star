# ui/corpse_pickup_menu.py
import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo

class CorpsePickupMenu:
    def __init__(self, items_on_corpse, unit, corpse, all_corpses_list, main_font, small_font):
        self.font = main_font
        self.small_font = small_font
        self.items_on_corpse = items_on_corpse
        self.unit = unit
        self.corpse = corpse
        self.all_corpses_list = all_corpses_list
        self.active = True
        self.selected_item_index = -1
        self.scroll_offset = 0  # Смещение для прокрутки
        self.max_scroll = 0

        # --- Параметры меню ---
        button_width = 100
        button_height = 25
        self.item_spacing = 60
        button_spacing = 5
        self.items_per_page = 5  # Максимальное количество предметов на странице

        menu_width = 700
        menu_height = 400  # Фиксированная высота
        self.menu_rect = pygame.Rect((SCREEN_WIDTH - menu_width) // 2, (SCREEN_HEIGHT - menu_height) // 2, menu_width, menu_height)
        
        # Область для прокрутки (внутренняя область)
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
        
        for i, item_obj in enumerate(self.items_on_corpse):
            # Проверяем, виден ли предмет в текущей области прокрутки
            if y_offset + self.item_spacing < self.content_rect.top or y_offset > self.content_rect.bottom:
                y_offset += self.item_spacing
                continue
            
            # Определяем тип предмета и создаем соответствующий текст
            if isinstance(item_obj, Weapon):
                # Оружие
                text = self.small_font.render(
                    f"{item_obj.name} (Урон: {item_obj.damage}, Точность: {item_obj.accuracy}%, Патроны: {item_obj.ammo}/{item_obj.max_ammo})", 
                    True, WHITE
                )
                # Для оружия есть кнопки "Подобрать" и "Экипировать"
                pickup_button_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, 100, 25)
                equip_button_rect = pygame.Rect(self.content_rect.x + 120, y_offset + 25, 100, 25)
                
                self.buttons.append({
                    'item_object': item_obj,
                    'item_type': 'weapon',
                    'pickup_rect': pickup_button_rect,
                    'equip_rect': equip_button_rect,
                    'text_surface': text,
                    'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                    'index': i,
                    'visible': True
                })
                
            elif isinstance(item_obj, Ammo):
                # Магазин/патроны
                text = self.small_font.render(
                    f"{item_obj.name} (Тип: {item_obj.ammo_type}, Патроны: {item_obj.ammo_count})", 
                    True, WHITE
                )
                # Для магазина только кнопка "Подобрать"
                pickup_button_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, 100, 25)
                
                self.buttons.append({
                    'item_object': item_obj,
                    'item_type': 'ammo',
                    'pickup_rect': pickup_button_rect,
                    'equip_rect': None,
                    'text_surface': text,
                    'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                    'index': i,
                    'visible': True
                })
            else:
                # Неизвестный тип предмета
                text = self.small_font.render(f"Неизвестный предмет", True, WHITE)
                pickup_button_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, 100, 25)
                
                self.buttons.append({
                    'item_object': item_obj,
                    'item_type': 'unknown',
                    'pickup_rect': pickup_button_rect,
                    'equip_rect': None,
                    'text_surface': text,
                    'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                    'index': i,
                    'visible': True
                })
            
            y_offset += self.item_spacing

    def _update_scrollbar(self):
        """Обновить параметры скроллбара."""
        total_height = len(self.items_on_corpse) * self.item_spacing
        visible_height = self.content_rect.height
        
        if total_height > visible_height:
            self.max_scroll = total_height - visible_height + 20
            # Высота ползунка пропорциональна видимой области
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
        """Handle corpse pickup menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем клик по скроллбару
            if event.button == 1 and self.scrollbar_rect.collidepoint(mouse_pos):
                if self.thumb_rect and self.thumb_rect.collidepoint(mouse_pos):
                    self.dragging_scroll = True
                    self.drag_start_y = mouse_pos[1]
                    self.drag_start_scroll = self.scroll_offset
                else:
                    # Клик по области скроллбара (но не по ползунку)
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
                # Проверяем клики по кнопкам предметов
                for button_info in self.buttons:
                    # Обработка кнопки "Подобрать"
                    if button_info['pickup_rect'].collidepoint(mouse_pos):
                        item_obj = button_info['item_object']
                        if self.unit.add_item(item_obj):
                            if item_obj in self.corpse['inventory']:
                                self.corpse['inventory'].remove(item_obj)
                                print(f"Item {item_obj.name} picked up from corpse.")
                                
                                # Обновляем список предметов
                                self.items_on_corpse = [item for item in self.items_on_corpse if item != item_obj]
                                
                                # Если труп опустел, удаляем его
                                if not self.corpse['inventory']:
                                    self.all_corpses_list.remove(self.corpse)
                                    print("Corpse removed (no items left).")
                                    return "close"
                                
                                # Пересоздаем кнопки
                                self._create_buttons()
                                self._update_scrollbar()
                                return "refresh"
                        else:
                            return "inventory_full"
                    
                    # Обработка кнопки "Экипировать" (только для оружия)
                    elif (button_info['item_type'] == 'weapon' and 
                          button_info['equip_rect'] and 
                          button_info['equip_rect'].collidepoint(mouse_pos)):
                        item_obj = button_info['item_object']
                        if self.unit.add_item(item_obj):
                            if item_obj in self.corpse['inventory']:
                                self.corpse['inventory'].remove(item_obj)
                                print(f"Item {item_obj.name} equipped from corpse.")
                                self.unit.equip_weapon(item_obj)
                                
                                # Обновляем список предметов
                                self.items_on_corpse = [item for item in self.items_on_corpse if item != item_obj]
                                
                                # Если труп опустел, удаляем его
                                if not self.corpse['inventory']:
                                    self.all_corpses_list.remove(self.corpse)
                                    print("Corpse removed (no items left).")
                                    return "close"
                                
                                # Пересоздаем кнопки
                                self._create_buttons()
                                self._update_scrollbar()
                                return "refresh"
                        else:
                            return "inventory_full"

                if self.close_button_rect.collidepoint(mouse_pos):
                    return "close"

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
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
        """Draw the corpse pickup menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Menu box
        pygame.draw.rect(screen, DARK_GRAY, self.menu_rect)
        pygame.draw.rect(screen, WHITE, self.menu_rect, 2)

        # Title
        title = self.font.render(f"Подобрать с трупа ({len(self.items_on_corpse)} предметов)", True, WHITE)
        title_rect = title.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + 20))
        screen.blit(title, title_rect)

        # Рисуем область контента с маской
        clip_rect = screen.get_clip()
        screen.set_clip(self.content_rect)
        
        # Draw items and buttons (только видимые)
        for button_info in self.buttons:
            # Текст предмета
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
        
        # Рисуем рамку области контента
        pygame.draw.rect(screen, (100, 100, 100), self.content_rect, 1)
        
        # Рисуем скроллбар если нужно
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