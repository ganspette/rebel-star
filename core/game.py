# core/game.py
import pygame
import sys
import os
from core.constants import *
from core.sprite_loader import SpriteLoader

# Импорт систем
from systems.camera import Camera
from systems.game_state import GameState
from core.combat_system import CombatSystem
from core.game_manager import GameManager
from core.input_handler import InputHandler

# Импорт UI меню
from ui.main_menu import MainMenu
from ui.in_game_menu import InGameMenu
from ui.pickup_menu import PickupMenu
from ui.inventory_menu import InventoryMenu
from ui.map_selection_menu import MapSelectionMenu
from ui.corpse_pickup_menu import CorpsePickupMenu

# Импорт новых систем
from core.save_system import SaveSystem
from core.load_system import LoadSystem
from ui.notification_system import NotificationSystem

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rebel Star")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.sprite_loader = SpriteLoader()
        
        # --- Инициализируем GameManager ---
        self.game_manager = GameManager()
        self.game_manager.game_state = GameState()
        self.game_manager.camera = Camera()
        self.game_manager.combat_system = CombatSystem()
        
        # Новые системы
        self.save_system = SaveSystem()
        self.load_system = LoadSystem()
        self.notification_system = NotificationSystem()
        
        # UI меню
        self.main_menu = MainMenu()
        self.pause_menu = InGameMenu()
        self.map_selection_menu = MapSelectionMenu()
        self.pickup_menu = None
        self.inventory_menu = None
        
        # Состояния меню сохранения/загрузки
        self.save_menu_active = False
        self.load_menu_active = False
        self.save_slots = []
        
        # --- Инициализируем InputHandler ---
        self.input_handler = InputHandler(self)
        # --- КОНЕЦ ИНИЦИАЛИЗАЦИИ ---
        
        self.running = True
        
        # UI шрифты
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # Таймер для уведомлений
        self.last_time = pygame.time.get_ticks()
    
    def is_menu_active(self):
        """Check if any menu is active."""
        state = self.game_manager.game_state.state
        in_load_menu = (state == 'menu' and self.main_menu.in_load_menu)
        
        return (state in ['menu', 'pause', 'map_selection', 'pickup', 'inventory'] or
                self.pickup_menu is not None or 
                self.inventory_menu is not None or
                in_load_menu)
    
    def start_game(self, map_name="test"):
        """Initialize game with selected map"""
        self.game_manager.start_game(map_name)
        if self.game_manager.current_map:
            self.game_manager.current_map.sprite_loader = self.sprite_loader
            
            # Set player unit sprite loader
            for unit in self.game_manager.current_map.units:
                unit.sprite_loader = self.sprite_loader
    
    def handle_events(self):
        """Handle all pygame events"""
        # Используем InputHandler для обработки всех событий
        self.running = self.input_handler.handle_events()
    
    def update(self):
        """Update game state"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_time) / 1000.0  # в секундах
        self.last_time = current_time
        
        # Обновляем уведомления
        self.notification_system.update(dt)
        
        # Обновляем анимации меню
        if self.game_manager.game_state.state == 'menu':
            self.main_menu.update(dt)
        elif self.game_manager.game_state.state == 'map_selection':
            self.map_selection_menu.update(dt)
        elif self.game_manager.game_state.state == 'pause':
            self.pause_menu.update(dt)
        
        # Обновляем игровое состояние
        self.game_manager.update()
    
    def draw(self):
        """Draw everything"""
        self.screen.fill(BLACK)
        
        state = self.game_manager.game_state.state
        
        if state == 'menu':
            self.main_menu.draw(self.screen)
        elif state == 'map_selection':
            self.map_selection_menu.draw(self.screen)
        elif state == 'pickup':
            if self.pickup_menu:
                self.draw_game()
                self.pickup_menu.draw(self.screen)
        elif state == 'inventory':
            if self.inventory_menu:
                self.draw_game()
                self.inventory_menu.draw(self.screen)
        elif state == 'game':
            self.draw_game()
        elif state == 'pause':
            self.draw_game()  # Сначала рисуем игру
            self.pause_menu.draw(self.screen)  # Затем меню паузы поверх
        
        # Всегда рисуем уведомления поверх всего
        self.notification_system.draw(self.screen)
        
        pygame.display.flip()
    
    def draw_game(self):
        """Draw the game world - карта всегда видна, враги только в LOS."""
        if not self.game_manager.current_map:
            return
        
        current_faction = self.game_manager.game_state.turn_faction
        
        # 1. Рисуем ВСЮ карту (всегда видна)
        for y in range(self.game_manager.current_map.height):
            for x in range(self.game_manager.current_map.width):
                screen_x = (x * TILE_SIZE - self.game_manager.camera.x) * self.game_manager.camera.zoom
                screen_y = (y * TILE_SIZE - self.game_manager.camera.y) * self.game_manager.camera.zoom
                
                if (-TILE_SIZE * self.game_manager.camera.zoom <= screen_x <= SCREEN_WIDTH and 
                    -TILE_SIZE * self.game_manager.camera.zoom <= screen_y <= SCREEN_HEIGHT):
                    
                    sprite = self.game_manager.current_map.get_sprite(x, y)
                    if sprite:
                        scaled_sprite = pygame.transform.scale(
                            sprite, 
                            (int(TILE_SIZE * self.game_manager.camera.zoom), 
                             int(TILE_SIZE * self.game_manager.camera.zoom))
                        )
                        self.screen.blit(scaled_sprite, (screen_x, screen_y))
        
        # 2. Рисуем предметы (всегда видны)
        for item in self.game_manager.current_map.items:
            if item['type'] in ['weapon', 'ammo']:
                screen_x = (item['x'] * TILE_SIZE - self.game_manager.camera.x) * self.game_manager.camera.zoom
                screen_y = (item['y'] * TILE_SIZE - self.game_manager.camera.y) * self.game_manager.camera.zoom
                pygame.draw.circle(self.screen, (255, 255, 0), 
                                 (int(screen_x + TILE_SIZE * self.game_manager.camera.zoom // 2), 
                                  int(screen_y + TILE_SIZE * self.game_manager.camera.zoom // 2)), 
                                 int(8 * self.game_manager.camera.zoom))
        
        # 3. Рисуем трупы (всегда видны)
        for corpse in self.game_manager.current_map.corpses:
            screen_x = (corpse['x'] * TILE_SIZE - self.game_manager.camera.x) * self.game_manager.camera.zoom
            screen_y = (corpse['y'] * TILE_SIZE - self.game_manager.camera.y) * self.game_manager.camera.zoom
            
            sprite = self.sprite_loader.get_scaled_sprite(corpse['sprite'], 
                (int(TILE_SIZE * self.game_manager.camera.zoom), int(TILE_SIZE * self.game_manager.camera.zoom)))
            if sprite:
                self.screen.blit(sprite, (screen_x, screen_y))
        
        # 4. Рисуем пули
        self.game_manager.combat_system.draw_bullets(self.screen, self.game_manager.camera, self.sprite_loader)
        
        # 5. Рисуем юнитов
        for unit in self.game_manager.current_map.units:
            # Проверяем, нужно ли рисовать врага
            if unit.faction != current_faction:
                # Враг - проверяем видимость для ТЕКУЩЕЙ фракции
                if not self.game_manager.is_enemy_visible(unit.x, unit.y, current_faction):
                    continue  # Пропускаем невидимого врага
            
            screen_x = (unit.x * TILE_SIZE - self.game_manager.camera.x) * self.game_manager.camera.zoom
            screen_y = (unit.y * TILE_SIZE - self.game_manager.camera.y) * self.game_manager.camera.zoom
            
            sprite = unit.get_sprite((int(TILE_SIZE * self.game_manager.camera.zoom), 
                                     int(TILE_SIZE * self.game_manager.camera.zoom)))
            if sprite:
                self.screen.blit(sprite, (screen_x, screen_y))
            
            # Выделение выбранного юнита (только свои)
            if (self.game_manager.game_state.selected_unit == unit and 
                unit.faction == current_faction):
                pygame.draw.rect(self.screen, (255, 255, 0), 
                               (screen_x, screen_y, 
                                int(TILE_SIZE * self.game_manager.camera.zoom), 
                                int(TILE_SIZE * self.game_manager.camera.zoom)), 2)
        
        # 6. UI элементы
        if self.game_manager.game_state.hovered_unit:
            unit = self.game_manager.game_state.hovered_unit
            # Показываем информацию только если юнит виден для текущей фракции
            if (unit.faction == current_faction or
                self.game_manager.is_enemy_visible(unit.x, unit.y, current_faction)):
                info_text = f"{UNIT_TYPES[unit.unit_type]['name']} (Фракция: {unit.faction}) (HP: {unit.hp}/{unit.max_hp})"
                text_surface = self.small_font.render(info_text, True, WHITE)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.screen.blit(text_surface, (mouse_x + 10, mouse_y - 20))
            else:
                # Для невидимых врагов показываем "???"
                info_text = "??? (Враг скрыт)"
                text_surface = self.small_font.render(info_text, True, WHITE)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.screen.blit(text_surface, (mouse_x + 10, mouse_y - 20))
        
        # 7. Панель информации о выбранном юните
        if self.game_manager.game_state.selected_unit:
            self.draw_unit_info_panel()
        
        # 8. HUD
        self.draw_hud()
        
        # 9. Отладочная информация (опционально)
        # debug_text = f"Ход: {current_faction} | Видимых врагов: {len(self.game_manager.visible_enemies)}"
        # debug_surface = self.small_font.render(debug_text, True, (255, 255, 0))
        # self.screen.blit(debug_surface, (10, SCREEN_HEIGHT - 40))
    
    def draw_unit_info_panel(self):
        """Draw unit information panel"""
        unit = self.game_manager.game_state.selected_unit
        if not unit:
            return
        
        panel_width = 250
        panel_height = 300
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = 50
        
        # Draw panel background
        panel_surface = pygame.Surface((panel_width, panel_height))
        panel_surface.set_alpha(200)
        panel_surface.fill((50, 50, 50))
        self.screen.blit(panel_surface, (panel_x, panel_y))
        
        # Draw border
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw unit info
        y_offset = panel_y + 10
        stats = unit.get_stats()
        
        title = self.font.render(f"{stats['Тип']}", True, WHITE)
        self.screen.blit(title, (panel_x + 10, y_offset))
        y_offset += 30
        
        for key, value in stats.items():
            if key != 'Тип':
                text = self.small_font.render(f"{key}: {value}", True, WHITE)
                self.screen.blit(text, (panel_x + 10, y_offset))
                y_offset += 20
                if y_offset > panel_y + panel_height - 20:
                    break
    
    def draw_hud(self):
        """Draw HUD elements"""
        # Draw turn indicator
        turn_text = self.font.render(f"Ход: {self.game_manager.game_state.turn_faction.capitalize()}", True, WHITE)
        self.screen.blit(turn_text, (10, 10))
        
        # Draw combat state indicator
        if self.game_manager.game_state.combat_state != COMBAT_STATE_IDLE:
            combat_text = self.font.render(
                f"Атака: {self.game_manager.game_state.targeting_unit.unit_type if self.game_manager.game_state.targeting_unit else 'N/A'}", 
                True, RED
            )
            self.screen.blit(combat_text, (10, 35))
        
        # Draw controls info
        controls = [
            "WASD - движение | +/- - зум | Enter - конец хода",
            "ESC - меню | ЛКМ - выбрать юнита | ПКМ - атака",
            "P - подобрать | I - инвентарь | R - перезарядка",
            "F5 - быстрое сохранение | F9 - быстрая загрузка"
        ]
        
        # Рисуем с отступом от нижнего края
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, LIGHT_GRAY)
            # Располагаем ближе к низу, но с отступом
            y_pos = SCREEN_HEIGHT - 20 - (len(controls) - i) * 20
            self.screen.blit(text, (10, y_pos))
    
    def try_pickup_item(self):
        """Try to open pickup menu if selected unit is on a tile with items"""
        if (not self.game_manager.game_state.selected_unit or 
            not self.game_manager.current_map or 
            self.game_manager.game_state.selected_unit.faction != self.game_manager.game_state.turn_faction):
            return

        x, y = self.game_manager.game_state.selected_unit.x, self.game_manager.game_state.selected_unit.y
        items = self.game_manager.current_map.get_items_at(x, y)
        corpses = self.game_manager.current_map.get_corpses_at(x, y)
        
        if items:
            items_for_menu = []
            for item_dict in items:
                if item_dict['type'] == 'weapon':
                    cloned_weapon = item_dict['object'].clone()
                    items_for_menu.append({
                        'type': 'weapon',
                        'object': cloned_weapon,
                        'x': item_dict['x'],
                        'y': item_dict['y']
                    })
                elif item_dict['type'] == 'ammo':
                    cloned_ammo = item_dict['object'].clone()
                    items_for_menu.append({
                        'type': 'ammo',
                        'object': cloned_ammo,
                        'x': item_dict['x'],
                        'y': item_dict['y']
                    })
            
            if items_for_menu:
                self.pickup_menu = PickupMenu(items_for_menu, self.game_manager.game_state.selected_unit, self.game_manager.current_map.items)
                self.game_manager.game_state.state = 'pickup'
        elif corpses:
            corpse = corpses[0]
            corpse_items_for_menu = []
            for item in corpse['inventory']:
                if hasattr(item, 'ammo'):
                    cloned_item = item.clone()
                    corpse_items_for_menu.append(cloned_item)
                elif hasattr(item, 'ammo_count'):
                    cloned_item = item.clone()
                    corpse_items_for_menu.append(cloned_item)
                else:
                    corpse_items_for_menu.append(item)
            
            if corpse_items_for_menu:
                self._try_pickup_corpse_items(corpse, corpse_items_for_menu)
        else:
            print("No items or corpses to pick up here.")
    
    def _try_pickup_corpse_items(self, corpse, corpse_items_list):
        """Open pickup menu for items on a corpse."""
        if corpse_items_list:
            self.pickup_menu = CorpsePickupMenu(
                corpse_items_list, 
                self.game_manager.game_state.selected_unit, 
                corpse, 
                self.game_manager.current_map.corpses, 
                self.font,
                self.small_font
            )
            self.game_manager.game_state.state = 'pickup'
    
    def open_inventory(self):
        """Open inventory menu for selected unit"""
        if (not self.game_manager.game_state.selected_unit or 
            self.game_manager.game_state.selected_unit.faction != self.game_manager.game_state.turn_faction):
            return

        self.inventory_menu = InventoryMenu(self.game_manager.game_state.selected_unit, self.game_manager.current_map)
        self.game_manager.game_state.state = 'inventory'
    
    def try_reload_weapon(self):
        """Attempt to reload the selected unit's equipped weapon."""
        if (self.game_manager.game_state.selected_unit and 
            self.game_manager.game_state.selected_unit.faction == self.game_manager.game_state.turn_faction):
            
            unit = self.game_manager.game_state.selected_unit
            
            if unit.equipped_weapon:
                try:
                    if unit.energy > 0:
                        success = unit.reload_weapon()
                        if success:
                            self.notification_system.add_success(
                                f"{unit.unit_type} перезарядил {unit.equipped_weapon.name}."
                            )
                        else:
                            self.notification_system.add_error(
                                f"Не удалось перезарядить {unit.unit_type}."
                            )
                    else:
                        self.notification_system.add_error(
                            f"{unit.unit_type} нет энергии для перезарядки."
                        )
                except Exception as e:
                    # Обрабатываем исключения из unit.reload_weapon()
                    self.notification_system.add_error(str(e))
            else:
                self.notification_system.add_error(
                    f"{unit.unit_type} не имеет экипированного оружия для перезарядки."
                )
        else:
            self.notification_system.add_error("Не выбран юнит или не ваш ход для перезарядки.")
    
    def quick_save(self):
        """Быстрое сохранение игры (F5)."""
        try:
            save_path = self.save_system.save_game(self.game_manager)
            self.notification_system.add_success(f"Игра сохранена: {save_path}")
            return True
        except Exception as e:
            self.notification_system.add_error(f"Ошибка сохранения: {str(e)}")
            return False
    
    def quick_load(self):
        """Быстрая загрузка последнего сохранения (F9)."""
        saves = self.save_system.list_saves()
        if not saves:
            self.notification_system.add_warning("Нет доступных сохранений")
            return False
        
        try:
            latest_save = saves[0]  # Самое свежее сохранение
            save_data = self.save_system.load_game(latest_save['filepath'])
            self.load_system.restore_game(save_data, self.game_manager)
            self.notification_system.add_success(f"Игра загружена: {latest_save['name']}")
            return True
        except Exception as e:
            self.notification_system.add_error(f"Ошибка загрузки: {str(e)}")
            return False
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()