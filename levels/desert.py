# levels/desert.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class DesertLevel(BaseLevel):
    name = "desert"
    level_index = 1
    width = 3400

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()

        # Sand dune platforms
        layout = [
            (280, C.GROUND_Y - 80, 200),
            (560, C.GROUND_Y - 140, 160),
            (800, C.GROUND_Y - 100, 180),
            (1060, C.GROUND_Y - 180, 140),
            (1280, C.GROUND_Y - 110, 200),
            (1540, C.GROUND_Y - 170, 160),
            (1780, C.GROUND_Y - 100, 220),
            (2080, C.GROUND_Y - 160, 160),
            (2320, C.GROUND_Y - 80, 240),
            (2600, C.GROUND_Y - 150, 180),
            (2860, C.GROUND_Y - 120, 220),
            (3100, C.GROUND_Y - 160, 200),
            (3300, C.GROUND_Y - 80, 100),
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(350,  C.GROUND_Y - 32, 200, 550,  "drone"),
            Enemy(700,  C.GROUND_Y - 32, 550, 950,  "guard"),
            Enemy(1100, C.GROUND_Y - 32, 900, 1350, "drone"),
            Enemy(1600, C.GROUND_Y - 32, 1400, 1850, "guard"),
            Enemy(2100, C.GROUND_Y - 32, 1950, 2300, "turret"),
            Enemy(2700, C.GROUND_Y - 32, 2500, 2950, "drone"),
            Enemy(3000, C.GROUND_Y - 32, 2850, 3250, "guard"),
        ]

        # Collectibles (ancient coins)
        for px, py in [(450, C.GROUND_Y - 40), (900, C.GROUND_Y - 160),
                       (1400, C.GROUND_Y - 40), (1800, C.GROUND_Y - 120),
                       (2400, C.GROUND_Y - 40), (2900, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — pattern recognition (sand gate)
        p1 = Interactable(900, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Sand Gate")
        p1.puzzle_type = "pattern"
        self.interactables.append(p1)
        self.puzzles_queue.append("pattern")

        # Puzzle 2 — tic tac toe (ancient AI guardian)
        p2 = Interactable(2300, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Desert Oracle")
        p2.puzzle_type = "ttt"
        self.interactables.append(p2)
        self.puzzles_queue.append("ttt")

        # Exit
        ex = Interactable(3300, C.GROUND_Y - 80, 60, 80, "exit", "[E] To Beach")
        self.interactables.append(ex)

        self.puzzles_needed = 2
        companion.say("The desert stretches endlessly. Follow the ruins east — that's our path.")
