# levels/slum.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class SlumLevel(BaseLevel):
    name = "slum"
    level_index = 0
    width = 3200

    def setup(self, player, companion):
        player.x, player.y = 100, C.GROUND_Y - 64
        companion.x, companion.y = 160, C.GROUND_Y - 64

        # Ground
        self._make_ground()

        # Platforms — ruined building ledges
        layout = [
            (320, C.GROUND_Y - 90, 160),
            (560, C.GROUND_Y - 160, 140),
            (760, C.GROUND_Y - 110, 180),
            (980, C.GROUND_Y - 200, 120),
            (1140, C.GROUND_Y - 90, 200),
            (1400, C.GROUND_Y - 150, 160),
            (1640, C.GROUND_Y - 100, 240),
            (1940, C.GROUND_Y - 180, 140),
            (2180, C.GROUND_Y - 120, 200),
            (2440, C.GROUND_Y - 160, 180),
            (2700, C.GROUND_Y - 90, 260),
            (2980, C.GROUND_Y - 140, 180),
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(400, C.GROUND_Y - 32, 300, 600, "drone"),
            Enemy(850, C.GROUND_Y - 32, 700, 1000, "guard"),
            Enemy(1300, C.GROUND_Y - 32, 1100, 1500, "drone"),
            Enemy(1700, C.GROUND_Y - 32, 1500, 1900, "guard"),
            Enemy(2200, C.GROUND_Y - 32, 2000, 2400, "drone"),
            Enemy(2600, C.GROUND_Y - 32, 2400, 2800, "guard"),
        ]

        # Collectibles (scrap)
        for px, py in [(500, C.GROUND_Y - 40), (900, C.GROUND_Y - 180),
                       (1300, C.GROUND_Y - 40), (1700, C.GROUND_Y - 120),
                       (2200, C.GROUND_Y - 40), (2700, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — math (sealed door terminal)
        p1 = Interactable(700, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Cipher Lock")
        p1.puzzle_type = "math"
        self.interactables.append(p1)
        self.puzzles_queue.append("math")

        # Puzzle 2 — tic tac toe (robot guard game)
        p2 = Interactable(1900, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Play Robot")
        p2.puzzle_type = "ttt"
        self.interactables.append(p2)
        self.puzzles_queue.append("ttt")

        # Exit
        ex = Interactable(3050, C.GROUND_Y - 80, 60, 80, "exit", "[E] Exit Slums")
        self.interactables.append(ex)

        self.puzzles_needed = 2

        # Companion greeting
        companion.say("Welcome to the Rusted Slums, Kai. Solve the puzzles to unlock the exit.")
