# levels/battlefield.py
import pygame
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy
from game.boss import Boss


class BattlefieldLevel(BaseLevel):
    name = "battlefield"
    level_index = 3
    width = 2560

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()
        self._make_walls()

        # War-torn terrain + wide boss arena
        layout = [
            (260,  C.GROUND_Y - 80,   200),
            (500,  C.GROUND_Y - 150,  160),
            (700,  C.GROUND_Y - 90,   200),  # <-- puzzle 1 nearby
            (940,  C.GROUND_Y - 170,  150),
            (1130, C.GROUND_Y - 90,   200),
            (1370, C.GROUND_Y - 150,  170),  # <-- puzzle 2 nearby
            (1580, C.GROUND_Y - 80,   220),
            # Boss arena — wide flat ground extension (handled by main ground + walls)
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies before boss
        self.enemies = [
            Enemy(340,  C.GROUND_Y - 32, 240,  540,  "guard"),
            Enemy(650,  C.GROUND_Y - 32, 500,  870,  "drone"),
            Enemy(1010, C.GROUND_Y - 32, 860,  1230, "turret"),
            Enemy(1460, C.GROUND_Y - 32, 1300, 1680, "guard"),
        ]

        # Collectibles
        for px, py in [(420, C.GROUND_Y - 40), (860, C.GROUND_Y - 170),
                       (1300, C.GROUND_Y - 40), (1680, C.GROUND_Y - 110)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — connect four
        p1 = Interactable(720, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Tactical AI")
        p1.puzzle_type = "connect4"
        self.interactables.append(p1)
        self.puzzles_queue.append("connect4")

        # Puzzle 2 — math
        p2 = Interactable(1400, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Artillery Code")
        p2.puzzle_type = "math"
        self.interactables.append(p2)
        self.puzzles_queue.append("math")

        # Boss arena entry trigger
        boss_trigger = Interactable(1860, C.GROUND_Y - 60, 40, 60, "story", "[E] Enter Arena")
        boss_trigger.puzzle_type = "boss_intro"
        self.interactables.append(boss_trigger)

        # Boss — starts further right in the arena
        self.boss = Boss(2200, C.GROUND_Y - 110)
        self.boss_active = False
        self.boss_defeated = False

        self.puzzles_needed = 2
        companion.say("This is the Battlefield. I can sense the commander's presence. Be careful, Kai.")

    def update(self, player, companion, dt):
        # Activate boss when player enters the arena area AND puzzles are solved
        if not self.boss_active and player.x > 1850 and self.exit_unlocked:
            self.boss_active = True
            self.boss.x = 2200
            self.boss.y = C.GROUND_Y - 110

        # Companion phase commentary (only once each)
        if self.boss_active and self.boss and self.boss.alive:
            if self.boss.phase == 1 and not getattr(self, '_phase2_announced', False):
                self._phase2_announced = True
                companion.say("Phase 2! It's adapting — watch the missile patterns!")
            if self.boss.phase == 2 and not getattr(self, '_phase3_announced', False):
                self._phase3_announced = True
                companion.say("Wait... something is wrong with the boss. A biological signal?!")

        # Boss defeated → trigger cow reveal cutscene
        if self.boss and not self.boss.alive and not self.boss_defeated:
            self.boss_defeated = True
            self._pending_cutscene = "boss_cow_reveal"
            return "cutscene"

        result = super().update(player, companion, dt)
        return result
