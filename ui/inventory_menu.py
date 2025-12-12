# ui/inventory_menu.py
import pygame
from core.constants import WHITE, BLACK, LIGHT_GRAY, DARK_GRAY, SCREEN_WIDTH, SCREEN_HEIGHT
from game_objects.weapon import Weapon
from game_objects.ammo import Ammo

class InventoryMenu:
    def __init__(self, unit, game_map):
        # --- Загрузка шрифтов ---
        try:
            self.font = pygame.font.Font(pygame.font.match_font('freesansbold'), 36)
            self.small_font = pygame.font.Font(pygame.font.match_font('freesansbold'), 24)
        except:
            print("Could not load freesansbold in InventoryMenu, using default.")
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            
        self.unit = unit
        self.game_map = game_map
        self.active = True
        self.selected_item_index = -1
        self.scroll_offset = 0
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
        
        # Собираем все предметы для отображения
        all_items = []
        
        # Инвентарь
        for i, item in enumerate(self.unit.inventory):
            all_items.append({
                'item': item,
                'type': 'inventory',
                'index': i
            })
        
        # Экипированное оружие
        if self.unit.equipped_weapon:
            all_items.append({
                'item': self.unit.equipped_weapon,
                'type': 'equipped',
                'index': -1
            })
        
        # Создаем кнопки
        y_offset = self.content_rect.y + 10 - self.scroll_offset
        
        for item_info in all_items:
            item = item_info['item']
            item_type = item_info['type']
            index = item_info['index']
            
            # Проверяем, виден ли предмет в текущей области прокрутки
            if y_offset + self.item_spacing < self.content_rect.top or y_offset > self.content_rect.bottom:
                y_offset += self.item_spacing
                continue
            
            # Определяем тип предмета и создаем текст
            if isinstance(item, Weapon):
                text = self.small_font.render(
                    f"{item.name} (Урон: {item.damage}, Точность: {item.accuracy}%, Патроны: {item.ammo}/{item.max_ammo})", 
                    True, WHITE
                )
                
                if item_type == 'inventory':
                    # Оружие в инвентаре
                    equip_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, self.button_width, self.button_height)
                    drop_rect = pygame.Rect(self.content_rect.x + 10 + self.button_width + self.button_spacing, y_offset + 25, self.button_width, self.button_height)
                    
                    self.buttons.append({
                        'item': item,
                        'item_type': 'inventory_weapon',
                        'equip_rect': equip_rect,
                        'drop_rect': drop_rect,
                        'reload_rect': None,
                        'text_surface': text,
                        'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                        'index': index
                    })
                else:  # equipped
                    # Экипированное оружие
                    unequip_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, self.button_width, self.button_height)
                    drop_rect = pygame.Rect(self.content_rect.x + 10 + self.button_width + self.button_spacing, y_offset + 25, self.button_width, self.button_height)
                    reload_rect = pygame.Rect(self.content_rect.x + 10 + 2 * (self.button_width + self.button_spacing), y_offset + 25, self.button_width, self.button_height)
                    
                    self.buttons.append({
                        'item': item,
                        'item_type': 'equipped',
                        'unequip_rect': unequip_rect,
                        'drop_rect': drop_rect,
                        'reload_rect': reload_rect,
                        'text_surface': text,
                        'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                        'index': index
                    })
                    
            elif isinstance(item, Ammo):
                text = self.small_font.render(
                    f"{item.name} (Тип: {item.ammo_type}, Патроны: {item.ammo_count})", 
                    True, WHITE
                )
                
                # Магазин в инвентаре
                drop_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, self.button_width, self.button_height)
                reload_rect = pygame.Rect(self.content_rect.x + 10 + self.button_width + self.button_spacing, y_offset + 25, self.button_width, self.button_height)
                
                self.buttons.append({
                    'item': item,
                    'item_type': 'inventory_ammo',
                    'drop_rect': drop_rect,
                    'reload_rect': reload_rect,
                    'text_surface': text,
                    'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                    'index': index
                })
            else:
                text = self.small_font.render(f"Неизвестный предмет", True, WHITE)
                drop_rect = pygame.Rect(self.content_rect.x + 10, y_offset + 25, self.button_width, self.button_height)
                
                self.buttons.append({
                    'item': item,
                    'item_type': 'inventory_other',
                    'drop_rect': drop_rect,
                    'reload_rect': None,
                    'text_surface': text,
                    'text_rect': pygame.Rect(self.content_rect.x + 10, y_offset, text.get_width(), text.get_height()),
                    'index': index
                })
            
            y_offset += self.item_spacing

    def _update_scrollbar(self):
        """Обновить параметры скроллбара."""
        total_items = len(self.unit.inventory) + (1 if self.unit.equipped_weapon else 0)
        total_height = total_items * self.item_spacing
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
        """Handle inventory menu events."""
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
                    if button_info['item_type'] == 'inventory_weapon':
                        if button_info['equip_rect'].collidepoint(mouse_pos):
                            self.unit.equip_weapon(button_info['item'])
                            return "refresh"
                        elif button_info['drop_rect'].collidepoint(mouse_pos):
                            dropped_item = self.unit.drop_item(button_info['item'])
                            if dropped_item:
                                self.game_map.items.append({
                                    'type': 'weapon',
                                    'object': dropped_item,
                                    'x': self.unit.x,
                                    'y': self.unit.y
                                })
                            return "drop_on_map"
                            
                    elif button_info['item_type'] == 'inventory_ammo':
                        if button_info['drop_rect'].collidepoint(mouse_pos):
                            dropped_item = self.unit.drop_item(button_info['item'])
                            if dropped_item:
                                self.game_map.items.append({
                                    'type': 'ammo',
                                    'object': dropped_item,
                                    'x': self.unit.x,
                                    'y': self.unit.y
                                })
                            return "drop_on_map"
                        elif button_info['reload_rect'].collidepoint(mouse_pos):
                            if self.unit.equipped_weapon and self.unit.equipped_weapon.ammo_type == button_info['item'].ammo_type:
                                success = self.unit.reload_weapon()
                                if success:
                                    return "refresh"
                                    
                    elif button_info['item_type'] == 'equipped':
                        if button_info['unequip_rect'].collidepoint(mouse_pos):
                            self.unit.unequip_weapon()
                            return "refresh"
                        elif button_info['drop_rect'].collidepoint(mouse_pos):
                            equipped_item = self.unit.equipped_weapon
                            if equipped_item:
                                self.unit.equipped_weapon = None
                                self.game_map.items.append({
                                    'type': 'weapon',
                                    'object': equipped_item,
                                    'x': self.unit.x,
                                    'y': self.unit.y
                                })
                            return "drop_on_map"
                        elif button_info['reload_rect'].collidepoint(mouse_pos):
                            success = self.unit.reload_weapon()
                            if success:
                                return "refresh"
                                
                    elif button_info['item_type'] == 'inventory_other':
                        if button_info['drop_rect'].collidepoint(mouse_pos):
                            dropped_item = self.unit.drop_item(button_info['item'])
                            if dropped_item:
                                self.game_map.items.append({
                                    'type': 'other',
                                    'object': dropped_item,
                                    'x': self.unit.x,
                                    'y': self.unit.y
                                })
                            return "drop_on_map"

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
        """Draw the inventory menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # Menu box
        pygame.draw.rect(screen, DARK_GRAY, self.menu_rect)
        pygame.draw.rect(screen, WHITE, self.menu_rect, 2)

        # Title
        total_items = len(self.unit.inventory) + (1 if self.unit.equipped_weapon else 0)
        title = self.font.render(f"Инвентарь ({total_items} предметов)", True, WHITE)
        title_rect = title.get_rect(center=(self.menu_rect.centerx, self.menu_rect.y + 20))
        screen.blit(title, title_rect)

        # Рисуем область контента с маской
        clip_rect = screen.get_clip()
        screen.set_clip(self.content_rect)
        
        # Draw items and buttons
        for button_info in self.buttons:
            screen.blit(button_info['text_surface'], button_info['text_rect'])
            
            if button_info['item_type'] == 'inventory_weapon':
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['equip_rect'])
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['drop_rect'])
                
                equip_text = self.small_font.render("Экипировать", True, BLACK)
                drop_text = self.small_font.render("Выкинуть", True, BLACK)
                screen.blit(equip_text, (button_info['equip_rect'].x + 5, button_info['equip_rect'].y + 5))
                screen.blit(drop_text, (button_info['drop_rect'].x + 5, button_info['drop_rect'].y + 5))
                
            elif button_info['item_type'] == 'inventory_ammo':
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['drop_rect'])
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['reload_rect'])
                
                drop_text = self.small_font.render("Выкинуть", True, BLACK)
                reload_text = self.small_font.render("Перезарядка", True, BLACK)
                screen.blit(drop_text, (button_info['drop_rect'].x + 5, button_info['drop_rect'].y + 5))
                screen.blit(reload_text, (button_info['reload_rect'].x + 5, button_info['reload_rect'].y + 5))
                
            elif button_info['item_type'] == 'equipped':
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['unequip_rect'])
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['drop_rect'])
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['reload_rect'])
                
                unequip_text = self.small_font.render("Снять", True, BLACK)
                drop_text = self.small_font.render("Выкинуть", True, BLACK)
                reload_text = self.small_font.render("Перезарядка", True, BLACK)
                screen.blit(unequip_text, (button_info['unequip_rect'].x + 5, button_info['unequip_rect'].y + 5))
                screen.blit(drop_text, (button_info['drop_rect'].x + 5, button_info['drop_rect'].y + 5))
                screen.blit(reload_text, (button_info['reload_rect'].x + 5, button_info['reload_rect'].y + 5))
                
            elif button_info['item_type'] == 'inventory_other':
                pygame.draw.rect(screen, LIGHT_GRAY, button_info['drop_rect'])
                drop_text = self.small_font.render("Выкинуть", True, BLACK)
                screen.blit(drop_text, (button_info['drop_rect'].x + 5, button_info['drop_rect'].y + 5))
        
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