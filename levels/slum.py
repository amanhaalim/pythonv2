# levels/slum.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class SlumLevel(BaseLevel):
    name = "slum"
    level_index = 0
    width = 2560  # Compact width — no unreachable edges

    def setup(self, player, companion):
        player.x, player.y = 100, C.GROUND_Y - 64
        companion.x, companion.y = 160, C.GROUND_Y - 64

        # Ground + invisible boundary walls
        self._make_ground()
        self._make_walls()

        # Platforms — tightly spaced so player can always reach next one
        # Max horizontal gap: ~180px (well within jump range)
        # Heights vary by ±80-160px
        layout = [
            # x,    y,                  w
            (280,  C.GROUND_Y - 80,   180),  # 0
            (500,  C.GROUND_Y - 140,  160),  # 1
            (700,  C.GROUND_Y - 100,  200),  # 2  <-- puzzle 1 near here
            (940,  C.GROUND_Y - 170,  160),  # 3
            (1140, C.GROUND_Y - 100,  200),  # 4
            (1380, C.GROUND_Y - 150,  180),  # 5
            (1600, C.GROUND_Y - 90,   220),  # 6
            (1860, C.GROUND_Y - 160,  160),  # 7  <-- puzzle 2 near here
            (2060, C.GROUND_Y - 100,  200),  # 8
            (2300, C.GROUND_Y - 130,  180),  # 9  <-- exit near here
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(360,  C.GROUND_Y - 32, 280,  520,  "drone"),
            Enemy(780,  C.GROUND_Y - 32, 620,  960,  "guard"),
            Enemy(1200, C.GROUND_Y - 32, 1060, 1420, "drone"),
            Enemy(1650, C.GROUND_Y - 32, 1500, 1880, "guard"),
            Enemy(2100, C.GROUND_Y - 32, 1960, 2320, "drone"),
        ]

        # Collectibles
        for px, py in [(460, C.GROUND_Y - 40), (860, C.GROUND_Y - 180),
                       (1250, C.GROUND_Y - 40), (1700, C.GROUND_Y - 110),
                       (2150, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — math cipher
        p1 = Interactable(720, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Cipher Lock")
        p1.puzzle_type = "math"
        self.interactables.append(p1)
        self.puzzles_queue.append("math")

        # Puzzle 2 — tic tac toe
        p2 = Interactable(1880, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Play Robot")
        p2.puzzle_type = "ttt"
        self.interactables.append(p2)
        self.puzzles_queue.append("ttt")

        # Exit — near end of level
        ex = Interactable(2380, C.GROUND_Y - 80, 60, 80, "exit", "[E] Exit Slums")
        self.interactables.append(ex)

        self.puzzles_needed = 2
        companion.say("Welcome to the Rusted Slums, Kai. Solve the puzzles to unlock the exit.")
