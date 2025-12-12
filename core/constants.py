# core/constants.py
# Screen settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TILE_SIZE = 40

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BROWN = (139, 69, 19)

# Game states
MENU = 'menu'
GAME = 'game'
PAUSE = 'pause'

# Unit types - обновлено
UNIT_TYPES = {
    # Игрок/союзники
    'easy': {'sprite': 'easy.png', 'name': 'Лёгкий'},
    'average': {'sprite': 'average.png', 'name': 'Средний'},
    'heavy': {'sprite': 'heavy.png', 'name': 'Тяжёлый'},
    # Враги - новые типы
    'enemy_easy': {'sprite': 'enemy_easy.png', 'name': 'Лёгкий Враг'},
    'enemy_average': {'sprite': 'enemy_average.png', 'name': 'Средний Враг'},
    'enemy_heavy': {'sprite': 'enemy_heavy.png', 'name': 'Тяжёлый Враг'}
}

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

# Camera
ZOOM_FACTOR = 1.1
MIN_ZOOM = 0.5
MAX_ZOOM = 2.0

# Combat
COMBAT_STATE_IDLE = 'idle'
COMBAT_STATE_TARGETING = 'targeting'
COMBAT_STATE_ATTACKING = 'attacking'

# Vision system
MAX_VISION_RANGE = 10  # Максимальная дальность обзора
VISIBLE_COLOR = (255, 255, 255, 180)  # Цвет видимых тайлов
FOG_OF_WAR_COLOR = (50, 50, 50, 200)  # Цвет тумана войны
