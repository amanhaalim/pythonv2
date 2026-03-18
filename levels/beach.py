# levels/beach.py
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy


class BeachLevel(BaseLevel):
    name = "beach"
    level_index = 2
    width = 3200

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()

        # Beach rocks / wreckage platforms
        layout = [
            (300,  C.GROUND_Y - 80,  180),
            (560,  C.GROUND_Y - 150, 140),
            (780,  C.GROUND_Y - 90,  200),
            (1060, C.GROUND_Y - 200, 120),
            (1240, C.GROUND_Y - 110, 200),
            (1500, C.GROUND_Y - 160, 160),
            (1740, C.GROUND_Y - 80,  240),
            (2040, C.GROUND_Y - 190, 140),
            (2240, C.GROUND_Y - 120, 200),
            (2500, C.GROUND_Y - 160, 180),
            (2760, C.GROUND_Y - 100, 260),
            (3020, C.GROUND_Y - 150, 160),
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies
        self.enemies = [
            Enemy(380,  C.GROUND_Y - 32, 280, 560,  "guard"),
            Enemy(700,  C.GROUND_Y - 32, 560, 900,  "drone"),
            Enemy(1150, C.GROUND_Y - 32, 950, 1300, "turret"),
            Enemy(1600, C.GROUND_Y - 32, 1400, 1800, "drone"),
            Enemy(2100, C.GROUND_Y - 32, 1900, 2300, "guard"),
            Enemy(2650, C.GROUND_Y - 32, 2450, 2850, "drone"),
        ]

        # Collectibles (sea glass)
        for px, py in [(450, C.GROUND_Y - 40), (850, C.GROUND_Y - 170),
                       (1350, C.GROUND_Y - 40), (1800, C.GROUND_Y - 100),
                       (2300, C.GROUND_Y - 40), (2800, C.GROUND_Y - 40)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — missing object (lighthouse clue)
        p1 = Interactable(850, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Lighthouse")
        p1.puzzle_type = "missing"
        self.interactables.append(p1)
        self.puzzles_queue.append("missing")

        # Puzzle 2 — power connections (generator)
        p2 = Interactable(2400, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Generator")
        p2.puzzle_type = "power"
        self.interactables.append(p2)
        self.puzzles_queue.append("power")

        # Exit — boat dock
        ex = Interactable(3060, C.GROUND_Y - 80, 60, 80, "exit", "[E] To Battlefield")
        self.interactables.append(ex)

        self.puzzles_needed = 2
        companion.say("The beach... I can smell salt water. Life signs are strong here. Stay alert.")
