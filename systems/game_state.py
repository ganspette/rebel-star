# systems/game_state.py
from core.constants import COMBAT_STATE_IDLE

class GameState:
    def __init__(self):
        self.state = 'menu'  # menu, game, pause
        self.selected_unit = None
        self.hovered_unit = None
        self.show_unit_info = False
        self.unit_info_x = 0
        self.unit_info_y = 0
        self.current_map = None
        # self.turn = 'player'  # player, enemy, etc. # <-- УБРАНО: заменено на turn_faction
        # --- НОВОЕ: Состояние боя ---
        self.combat_state = COMBAT_STATE_IDLE
        self.targeting_unit = None # Юнит, который атакует
        self.targeting_weapon = None # Оружие, которым атакуют
        # --- КОНЕЦ НОВОГО ---
        
        # --- НОВОЕ: Фракция, чей ход ---
        self.turn_faction = "player" # Может быть "player", "enemy", "neutral", etc.
        # --- КОНЕЦ НОВОГО ---