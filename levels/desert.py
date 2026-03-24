# levels/desert.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class DesertLevel(BaseLevel):
    name = "desert"
    level_index = 1
    width = 2560

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()
        self._make_walls()

        # Sand dune platforms — compact gaps
        layout = [
            (260,  C.GROUND_Y - 80,   200),
            (500,  C.GROUND_Y - 130,  170),
            (710,  C.GROUND_Y - 90,   200),  # <-- puzzle 1 nearby
            (950,  C.GROUND_Y - 160,  160),
            (1150, C.GROUND_Y - 100,  200),
            (1390, C.GROUND_Y - 150,  170),
            (1600, C.GROUND_Y - 90,   220),
            (1860, C.GROUND_Y - 140,  170),  # <-- puzzle 2 nearby
            (2070, C.GROUND_Y - 80,   240),
            (2350, C.GROUND_Y - 110,  170),  # <-- exit nearby
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(340,  C.GROUND_Y - 32, 220,  520,  "drone"),
            Enemy(660,  C.GROUND_Y - 32, 500,  880,  "guard"),
            Enemy(1050, C.GROUND_Y - 32, 880,  1270, "drone"),
            Enemy(1500, C.GROUND_Y - 32, 1320, 1730, "guard"),
            Enemy(1960, C.GROUND_Y - 32, 1800, 2150, "turret"),
            Enemy(2220, C.GROUND_Y - 32, 2080, 2400, "drone"),
        ]

        # Collectibles
        for px, py in [(430, C.GROUND_Y - 40), (840, C.GROUND_Y - 150),
                       (1250, C.GROUND_Y - 40), (1760, C.GROUND_Y - 110),
                       (2150, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — pattern recognition
        p1 = Interactable(730, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Sand Gate")
        p1.puzzle_type = "pattern"
        self.interactables.append(p1)
        self.puzzles_queue.append("pattern")

        # Puzzle 2 — tic tac toe
        p2 = Interactable(1880, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Desert Oracle")
        p2.puzzle_type = "ttt"
        self.interactables.append(p2)
        self.puzzles_queue.append("ttt")

        # Exit
        ex = Interactable(2400, C.GROUND_Y - 80, 60, 80, "exit", "[E] To Beach")
        self.interactables.append(ex)

        self.puzzles_needed = 2
        companion.say("The desert stretches endlessly. Follow the ruins east — that's our path.")
