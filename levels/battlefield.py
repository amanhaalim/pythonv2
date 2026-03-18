# levels/battlefield.py
import pygame
import constants as C
from levels.base_level import BaseLevel, Platform, Collectible, Interactable
from game.enemy import Enemy
from game.boss import Boss


class BattlefieldLevel(BaseLevel):
    name = "battlefield"
    level_index = 3
    width = 3000

    def setup(self, player, companion):
        player.x, player.y = 80, C.GROUND_Y - 64
        companion.x, companion.y = 140, C.GROUND_Y - 64

        self._make_ground()

        # War-torn terrain
        layout = [
            (300,  C.GROUND_Y - 80,  200),
            (580,  C.GROUND_Y - 160, 140),
            (800,  C.GROUND_Y - 100, 180),
            (1060, C.GROUND_Y - 200, 120),
            (1260, C.GROUND_Y - 100, 200),
            (1540, C.GROUND_Y - 170, 160),
            (1780, C.GROUND_Y - 100, 240),
            # Boss arena — wide flat area
            (2100, C.GROUND_Y - 20,  700),
        ]
        for x, y, w in layout:
            self._make_platform(x, y, w)

        # Enemies before boss
        self.enemies = [
            Enemy(380,  C.GROUND_Y - 32, 280, 580,  "guard"),
            Enemy(700,  C.GROUND_Y - 32, 580, 900,  "drone"),
            Enemy(1100, C.GROUND_Y - 32, 900, 1300, "turret"),
            Enemy(1600, C.GROUND_Y - 32, 1400, 1900, "guard"),
        ]

        # Collectibles (dog tags)
        for px, py in [(450, C.GROUND_Y - 40), (900, C.GROUND_Y - 180),
                       (1400, C.GROUND_Y - 40), (1800, C.GROUND_Y - 120)]:
            self.collectibles.append(Collectible(px, py))

        # Puzzle 1 — connect four (tactical AI)
        p1 = Interactable(600, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Tactical AI")
        p1.puzzle_type = "connect4"
        self.interactables.append(p1)
        self.puzzles_queue.append("connect4")

        # Puzzle 2 — math (artillery code)
        p2 = Interactable(1500, C.GROUND_Y - 60, 40, 60, "puzzle", "[E] Artillery Code")
        p2.puzzle_type = "math"
        self.interactables.append(p2)
        self.puzzles_queue.append("math")

        # Boss arena trigger
        boss_trigger = Interactable(2080, C.GROUND_Y - 60, 40, 60, "story", "[E] Enter Arena")
        boss_trigger.puzzle_type = "boss_intro"  # used as cutscene name
        self.interactables.append(boss_trigger)

        # Boss
        self.boss = Boss(2400, C.GROUND_Y - 110)
        self.boss_active = False

        # No traditional exit — boss defeat triggers ending
        self.puzzles_needed = 2
        self.boss_defeated = False

        companion.say("This is the Battlefield. I can sense the commander's presence. Be careful, Kai.")

    def update(self, player, companion, dt):
        # Activate boss when player reaches arena
        if not self.boss_active and player.x > 2050:
            if self.exit_unlocked:
                self.boss_active = True
                self.boss.x = 2400
                self.boss.y = C.GROUND_Y - 110

        # Check boss phases for companion hints
        if self.boss_active and self.boss and self.boss.alive:
            if self.boss.phase == 1 and not hasattr(self, '_phase2_announced'):
                self._phase2_announced = True
                companion.say("Phase 2! It's adapting — watch the missile patterns!")
            if self.boss.phase == 2 and not hasattr(self, '_phase3_announced'):
                self._phase3_announced = True
                companion.say("Wait... something is wrong with the boss. A biological signal?!")

        # Boss defeated → ending
        if self.boss and not self.boss.alive and not self.boss_defeated:
            self.boss_defeated = True
            self._pending_cutscene = "boss_cow_reveal"
            return "cutscene"

        result = super().update(player, companion, dt)

        # After both puzzles solved + boss dead → trigger ending
        if self.boss_defeated and result is None:
            self._pending_cutscene = "ending"
            return "cutscene"

        return result

    def draw_boss(self, screen, camera_x, camera_y):
        if self.boss and self.boss_active:
            self.boss.draw(screen, 0, 0, camera_x, camera_y)
            # Draw boss missiles
            for m in self.boss.missiles:
                mx = int(m["x"] - camera_x)
                my = int(m["y"] - camera_y)
                if 0 < mx < C.SCREEN_W and 0 < my < C.SCREEN_H:
                    pygame.draw.circle(screen, C.ORANGE, (mx, my), 6)
                    pygame.draw.circle(screen, C.YELLOW, (mx, my), 3)
