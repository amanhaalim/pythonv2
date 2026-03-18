# constants.py — Global game constants

SCREEN_W = 1280
SCREEN_H = 720
FPS = 60
TITLE = "RUST & RUIN: The Last Child"

# Ground Y position (pixels from top)
GROUND_Y = 560

# Colors
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
BLUE       = (50,  100, 220)
YELLOW     = (255, 220, 50)
ORANGE     = (255, 140, 0)
CYAN       = (50,  220, 220)
PURPLE     = (140, 50,  200)
GREY       = (120, 120, 120)
DARK_GREY  = (40,  40,  40)
LIGHT_GREY = (180, 180, 180)

# Palette per level
LEVEL_PALETTES = [
    {"sky": (25, 20, 35),   "ground": (60, 50, 40),  "accent": (180, 80, 40)},   # Slum
    {"sky": (200, 150, 80), "ground": (210, 170, 90), "accent": (255, 200, 60)},  # Desert
    {"sky": (30,  80, 160), "ground": (50,  120, 80), "accent": (80,  200, 220)}, # Beach
    {"sky": (10,  10, 20),  "ground": (40,  30, 20),  "accent": (220, 60,  40)},  # Battlefield
]

# Physics
GRAVITY     = 1200   # px/s²
JUMP_SPEED  = -520   # px/s
PLAYER_SPEED = 220   # px/s

# Tile size
TILE = 32

# UI
UI_FONT = "monospace"
DIALOG_BG = (10, 10, 25, 200)

# Story flags
FLAG_SLUM_DONE     = "slum_done"
FLAG_DESERT_DONE   = "desert_done"
FLAG_BEACH_DONE    = "beach_done"
FLAG_BOSS_DONE     = "boss_done"
