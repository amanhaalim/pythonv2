# levels/beach.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class BeachLevel(BaseLevel):
    name = "beach"
    level_index = 2
    width = 2560

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()
        self._make_walls()

        # Beach rocks / wreckage platforms
        layout = [
            (260,  C.GROUND_Y - 70,   200),
            (500,  C.GROUND_Y - 140,  160),
            (700,  C.GROUND_Y - 80,   200),  # <-- puzzle 1 nearby
            (940,  C.GROUND_Y - 180,  140),
            (1120, C.GROUND_Y - 100,  200),
            (1360, C.GROUND_Y - 150,  170),
            (1570, C.GROUND_Y - 80,   230),
            (1840, C.GROUND_Y - 160,  160),  # <-- puzzle 2 nearby
            (2040, C.GROUND_Y - 100,  210),
            (2290, C.GROUND_Y - 120,  190),  # <-- exit nearby
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(340,  C.GROUND_Y - 32, 240,  530,  "guard"),
            Enemy(640,  C.GROUND_Y - 32, 500,  860,  "drone"),
            Enemy(1040, C.GROUND_Y - 32, 880,  1250, "turret"),
            Enemy(1450, C.GROUND_Y - 32, 1290, 1660, "drone"),
            Enemy(1950, C.GROUND_Y - 32, 1760, 2150, "guard"),
            Enemy(2220, C.GROUND_Y - 32, 2060, 2400, "drone"),
        ]

        # Collectibles
        for px, py in [(420, C.GROUND_Y - 40), (800, C.GROUND_Y - 160),
                       (1240, C.GROUND_Y - 40), (1740, C.GROUND_Y - 100),
                       (2100, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — missing object
        p1 = Interactable(720, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Lighthouse")
        p1.puzzle_type = "missing"
        self.interactables.append(p1)
        self.puzzles_queue.append("missing")

        # Puzzle 2 — power grid
        p2 = Interactable(1860, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Generator")
        p2.puzzle_type = "power"
        self.interactables.append(p2)
        self.puzzles_queue.append("power")

        # Exit — boat dock
        ex = Interactable(2360, C.GROUND_Y - 80, 60, 80, "exit", "[E] To Battlefield")
        self.interactables.append(ex)

        self.puzzles_needed = 2
        companion.say("The beach... I can smell salt water. Life signs are strong here. Stay alert.")
