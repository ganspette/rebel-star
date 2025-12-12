# core/input_handler.py
import pygame
from typing import Optional, Callable, Dict, Any, Tuple
from core.constants import COMBAT_STATE_TARGETING, COMBAT_STATE_IDLE, TILE_SIZE

class InputHandler:
    def __init__(self, game):
        """
        Обработчик ввода для игры Rebel Star.
        
        Args:
            game: Ссылка на основной класс Game
        """
        self.game = game
        self.key_handlers: Dict[int, Callable] = {}
        self.mouse_handlers: Dict[int, Callable] = {}
        
        # Убираем save_load_menu_active - используем main_menu.in_load_menu
        
        # Регистрируем обработчики по умолчанию
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default input handlers."""
        # Обработчики клавиш (кроме ESC - обрабатываем отдельно)
        self.register_key_handler(pygame.K_RETURN, self._handle_enter)
        self.register_key_handler(pygame.K_PLUS, self._handle_zoom_in)
        self.register_key_handler(pygame.K_EQUALS, self._handle_zoom_in)
        self.register_key_handler(pygame.K_MINUS, self._handle_zoom_out)
        self.register_key_handler(pygame.K_p, self._handle_pickup)
        self.register_key_handler(pygame.K_i, self._handle_inventory)
        self.register_key_handler(pygame.K_r, self._handle_reload)
        
        # Обработчики WASD для движения
        self.register_key_handler(pygame.K_w, lambda: self._handle_movement(0, -1))
        self.register_key_handler(pygame.K_s, lambda: self._handle_movement(0, 1))
        self.register_key_handler(pygame.K_a, lambda: self._handle_movement(-1, 0))
        self.register_key_handler(pygame.K_d, lambda: self._handle_movement(1, 0))
        
        # Добавляем новые горячие клавиши для сохранения/загрузки
        self.register_key_handler(pygame.K_F5, self._handle_quick_save)
        self.register_key_handler(pygame.K_F9, self._handle_quick_load)
    
    def register_key_handler(self, key: int, handler: Callable):
        """Register a handler for a specific key."""
        self.key_handlers[key] = handler
    
    def register_mouse_handler(self, button: int, handler: Callable):
        """Register a handler for a specific mouse button."""
        self.mouse_handlers[button] = handler
    
    def handle_events(self) -> bool:
        """
        Handle all pygame events. 
        Returns False if game should quit.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Если есть активное меню, передаем событие ему
            if self.game.is_menu_active():
                menu_result = self._handle_menu_event(event)
                if menu_result is False:  # Если меню вернуло False - выходим
                    return False
                elif menu_result == "back_to_main":
                    # Обработка возврата из меню загрузки
                    continue
            else:
                # Иначе обрабатываем как игровое событие
                self._handle_game_event(event)
        
        return True
    
    def _handle_menu_event(self, event):
        """Handle events when menu is active."""
        state = self.game.game_manager.game_state.state
        
        # Проверяем, находимся ли мы в главном меню или в меню загрузки
        in_main_menu = state == 'menu'
        in_load_menu = in_main_menu and self.game.main_menu.in_load_menu
        
        # Обработка ESC для выхода из игры
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if in_load_menu:
                # В меню загрузки ESC должен возвращать в главное меню
                self.game.main_menu.in_load_menu = False
                return "back_to_main"
            elif in_main_menu and not in_load_menu:
                # В главном меню (не в меню загрузки) ESC выходит из игры
                return False
        
        # Если активно меню загрузки в главном меню
        if in_load_menu:
            return self._handle_load_menu_in_main(event)
        
        # Обработка других меню
        if state == 'menu':
            result = self.game.main_menu.handle_event(event)
            if result:
                if result == "Новая игра":
                    self.game.game_manager.game_state.state = 'map_selection'
                    self.game.map_selection_menu.selected = 0
                elif result == "Загрузить":
                    # Показываем меню загрузки
                    self.game.save_slots = self.game.save_system.list_saves()
                    self.game.main_menu.set_save_slots(self.game.save_slots)
                    self.game.main_menu.in_load_menu = True
                elif result == "Настройки":
                    # TODO: Реализовать настройки
                    print("Настройки пока не реализованы")
                elif result == "Выход":
                    return False  # Выход из игры
                elif result.startswith("load:"):
                    # Загрузка конкретного сохранения
                    filename = result.split(":")[1]
                    self._load_save(filename)
        
        elif state == 'map_selection':
            result = self.game.map_selection_menu.handle_event(event)
            if result:
                if result == "Назад":
                    self.game.game_manager.game_state.state = 'menu'
                elif result == "Выбрать":
                    selected_map = self.game.map_selection_menu.get_selected_map()
                    if selected_map:
                        self.game.start_game(selected_map)
                        self.game.game_manager.game_state.state = 'game'
        
        elif state == 'pickup' and self.game.pickup_menu:
            result = self.game.pickup_menu.handle_event(event)
            if result:
                if result == "close":
                    self.game.game_manager.game_state.state = 'game'
                    self.game.pickup_menu = None
                elif result == "success":
                    self.game.game_manager.game_state.state = 'game'
                    self.game.pickup_menu = None
                elif result == "inventory_full":
                    self.game.game_manager.game_state.state = 'game'
                    self.game.pickup_menu = None
        
        elif state == 'inventory' and self.game.inventory_menu:
            result = self.game.inventory_menu.handle_event(event)
            if result:
                if result == "close":
                    self.game.game_manager.game_state.state = 'game'
                    self.game.inventory_menu = None
                elif result == "refresh":
                    from ui.inventory_menu import InventoryMenu
                    self.game.inventory_menu = InventoryMenu(
                        self.game.game_manager.game_state.selected_unit, 
                        self.game.game_manager.current_map
                    )
                elif result == "drop_on_map":
                    from ui.inventory_menu import InventoryMenu
                    self.game.inventory_menu = InventoryMenu(
                        self.game.game_manager.game_state.selected_unit, 
                        self.game.game_manager.current_map
                    )
        
        elif state == 'pause':
            # Прямая передача события в меню паузы
            result = self.game.pause_menu.handle_event(event)
            if result:
                if result == "Продолжить":
                    self.game.game_manager.game_state.state = 'game'
                elif result == "Сохранить игру":
                    # Быстрое сохранение
                    self.game.quick_save()
                elif result == "Загрузить игру":
                    # Быстрая загрузка
                    self.game.quick_load()
                elif result == "Настройки":
                    # TODO: Реализовать настройки
                    self.game.notification_system.add_info("Настройки пока не реализованы")
                elif result == "Выход в меню":
                    self.game.game_manager.game_state.state = 'menu'
                    self.game.game_manager.current_map = None
                    self.game.game_manager.game_state.current_map = None
                    self.game.main_menu.selected = 0
                    self.game.main_menu.in_load_menu = False
                    self.game.pickup_menu = None
                    self.game.inventory_menu = None
                    self.game.game_manager.game_state.combat_state = COMBAT_STATE_IDLE
                    self.game.game_manager.game_state.targeting_unit = None
                    self.game.game_manager.game_state.targeting_weapon = None
                    self.game.game_manager.combat_system.clear_bullets()
                    self.game.game_manager.game_state.turn_faction = "player"
                elif result == "Выход":
                    return False  # Выход из игры
            
            return None
    
    def _handle_load_menu_in_main(self, event):
        """Handle events in load menu from main menu."""
        result = self.game.main_menu.handle_event(event)
        
        if result == "back_to_main":
            # Возврат в главное меню
            self.game.main_menu.in_load_menu = False
            return "back_to_main"
        elif result and result.startswith("load:"):
            # Загрузка сохранения
            filename = result.split(":")[1]
            self._load_save(filename)
        
        return None
    
    def _handle_game_event(self, event):
        """Handle events when in game state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Переключение паузы
                self._handle_escape()
            elif event.key in self.key_handlers:
                self.key_handlers[event.key]()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                self._handle_left_click(event.pos)
            elif event.button == 3:  # Right click
                self._handle_right_click(event.pos)
            elif event.button == 4:  # Mouse wheel up
                self.game.game_manager.camera.zoom_in()
            elif event.button == 5:  # Mouse wheel down
                self.game.game_manager.camera.zoom_out()
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mousemotion(event.pos)
    
    def _handle_mousemotion(self, mouse_pos: Tuple[int, int]):
        """Handle mouse motion for hover effects."""
        if self.game.game_manager.current_map:
            grid_x, grid_y = self.game.game_manager.get_grid_coords_from_screen(mouse_pos[0], mouse_pos[1])
            units = self.game.game_manager.current_map.get_units_at(grid_x, grid_y)
            if units:
                self.game.game_manager.hovered_unit = units[0]
                self.game.game_manager.game_state.hovered_unit = units[0]
            else:
                self.game.game_manager.hovered_unit = None
                self.game.game_manager.game_state.hovered_unit = None
    
    # ===== DEFAULT HANDLERS =====
    
    def _handle_escape(self):
        """Handle ESC key - toggle pause."""
        if self.game.game_manager.game_state.state == 'game':
            self.game.game_manager.game_state.state = 'pause'
            self.game.pause_menu.selected = 0
        elif self.game.game_manager.game_state.state == 'pause':
            self.game.game_manager.game_state.state = 'game'
    
    def _handle_enter(self):
        """Handle Enter key - end turn."""
        if self.game.game_manager.game_state.state == 'game':
            self.game.game_manager.end_turn()
    
    def _handle_zoom_in(self):
        """Handle zoom in."""
        self.game.game_manager.camera.zoom_in()
    
    def _handle_zoom_out(self):
        """Handle zoom out."""
        self.game.game_manager.camera.zoom_out()
    
    def _handle_pickup(self):
        """Handle pickup key."""
        if (self.game.game_manager.game_state.state == 'game' and 
            self.game.game_manager.game_state.selected_unit and 
            self.game.game_manager.game_state.selected_unit.faction == self.game.game_manager.game_state.turn_faction):
            self.game.try_pickup_item()
    
    def _handle_inventory(self):
        """Handle inventory key."""
        if (self.game.game_manager.game_state.state == 'game' and 
            self.game.game_manager.game_state.selected_unit and 
            self.game.game_manager.game_state.selected_unit.faction == self.game.game_manager.game_state.turn_faction):
            self.game.open_inventory()
    
    def _handle_reload(self):
        """Handle reload key."""
        if (self.game.game_manager.game_state.state == 'game' and 
            self.game.game_manager.game_state.selected_unit and 
            self.game.game_manager.game_state.selected_unit.faction == self.game.game_manager.game_state.turn_faction):
            self.game.try_reload_weapon()
    
    def _handle_movement(self, dx: int, dy: int):
        """Handle movement."""
        if self.game.game_manager.game_state.state == 'game':
            try:
                success = self.game.game_manager.move_unit(dx, dy)
                if success:
                    self.game.notification_system.add_success(
                        f"Юнит перемещен на ({self.game.game_manager.selected_unit.x}, {self.game.game_manager.selected_unit.y})"
                    )
            except Exception as e:
                # Показываем ошибку через систему уведомлений
                self.game.notification_system.add_error(str(e))
    
    def _handle_quick_save(self):
        """Handle quick save (F5)."""
        if self.game.game_manager.game_state.state == 'game':
            try:
                save_path = self.game.save_system.save_game(self.game.game_manager)
                self.game.notification_system.add_success(f"Игра сохранена: {save_path}")
            except Exception as e:
                self.game.notification_system.add_error(f"Ошибка сохранения: {str(e)}")
    
    def _handle_quick_load(self):
        """Handle quick load (F9)."""
        if self.game.game_manager.game_state.state == 'game':
            self.game.quick_load()
    
    def _handle_left_click(self, mouse_pos: Tuple[int, int]):
        """Handle left mouse click - select unit."""
        if self.game.game_manager.game_state.state == 'game':
            if self.game.game_manager.game_state.combat_state == COMBAT_STATE_TARGETING:
                # Отменяем таргетинг при клике на пустое место
                self.game.game_manager.game_state.combat_state = COMBAT_STATE_IDLE
                self.game.game_manager.game_state.targeting_unit = None
                self.game.game_manager.game_state.targeting_weapon = None
                self.game.notification_system.add_warning("Таргетинг отменен")
            else:
                # Выбор юнита
                grid_x, grid_y = self.game.game_manager.get_grid_coords_from_screen(mouse_pos[0], mouse_pos[1])
                units = self.game.game_manager.current_map.get_units_at(grid_x, grid_y)
                
                if units:
                    unit = units[0]
                    try:
                        if self.game.game_manager.select_unit(unit):
                            # Проверяем, есть ли у юнита оружие и патроны
                            weapon_info = ""
                            if unit.equipped_weapon:
                                weapon_info = f" | Оружие: {unit.equipped_weapon.name} ({unit.equipped_weapon.ammo}/{unit.equipped_weapon.max_ammo})"
                            
                            self.game.notification_system.add_info(
                                f"Выбран {unit.unit_type}{weapon_info}"
                            )
                    except Exception as e:
                        # Обрабатываем исключения при выборе юнита
                        self.game.notification_system.add_error(str(e))
                else:
                    # Клик по пустой клетке - снимаем выделение
                    self.game.game_manager.selected_unit = None
                    self.game.game_manager.game_state.selected_unit = None
                    # Не показываем уведомление при снятии выделения, чтобы не засорять экран
    
    def _handle_right_click(self, mouse_pos: Tuple[int, int]):
        """Handle right mouse click for attacking."""
        if (self.game.game_manager.game_state.state == 'game' and 
            self.game.game_manager.game_state.selected_unit and 
            self.game.game_manager.game_state.selected_unit.equipped_weapon and
            self.game.game_manager.game_state.selected_unit.faction == self.game.game_manager.game_state.turn_faction):
            
            grid_x, grid_y = self.game.game_manager.get_grid_coords_from_screen(mouse_pos[0], mouse_pos[1])
            units = self.game.game_manager.current_map.get_units_at(grid_x, grid_y)
            
            if units:
                target_unit = units[0]
                if target_unit.is_enemy(self.game.game_manager.game_state.selected_unit):
                    try:
                        # Проверяем через GameManager
                        if self.game.game_manager.can_attack_target(
                            self.game.game_manager.game_state.selected_unit,
                            target_unit
                        ):
                            # Используем систему боя
                            bullet = self.game.game_manager.combat_system.create_bullet(
                                self.game.game_manager.game_state.selected_unit,
                                target_unit,
                                self.game.game_manager.game_state.selected_unit.equipped_weapon
                            )
                            if bullet:
                                self.game.notification_system.add_success(
                                    f"Атакую врага {target_unit.unit_type}"
                                )
                                # После атаки обновляем видимость
                                self.game.game_manager.update_line_of_sight()
                    except Exception as e:
                        self.game.notification_system.add_error(str(e))
                else:
                    self.game.notification_system.add_warning("Нельзя атаковать союзника!")
            else:
                # Отменяем таргетинг при клике на пустое место
                if self.game.game_manager.game_state.combat_state == COMBAT_STATE_TARGETING:
                    self.game.game_manager.game_state.combat_state = COMBAT_STATE_IDLE
                    self.game.game_manager.game_state.targeting_unit = None
                    self.game.game_manager.game_state.targeting_weapon = None
                    self.game.notification_system.add_warning("Таргетинг отменен")
    
    # ===== SAVE/LOAD HELPERS =====
    
    def _load_save(self, filename: str):
        """Загружает игру из указанного файла."""
        try:
            save_data = self.game.save_system.load_game(f"saves/{filename}")
            self.game.load_system.restore_game(save_data, self.game.game_manager)
            
            self.game.main_menu.in_load_menu = False
            self.game.game_manager.game_state.state = 'game'
            
            self.game.notification_system.add_success(f"Игра загружена: {filename}")
        except Exception as e:
            self.game.notification_system.add_error(f"Ошибка загрузки: {str(e)}")
    
    def _save_game(self, filename: Optional[str] = None):
        """Сохраняет игру в указанный файл."""
        try:
            save_path = self.game.save_system.save_game(self.game.game_manager, filename)
            
            self.game.main_menu.in_load_menu = False
            self.game.game_manager.game_state.state = 'pause'  # Возвращаемся в паузу
            
            self.game.notification_system.add_success(f"Игра сохранена: {save_path}")
        except Exception as e:
            self.game.notification_system.add_error(f"Ошибка сохранения: {str(e)}")