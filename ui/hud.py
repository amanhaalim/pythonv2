# ui/hud.py
import pygame
import math
import constants as C


class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 16, bold=True)
        self.sm_font = pygame.font.SysFont("monospace", 13)
        self.anim_tick = 0
        self._player = None
        self._level_manager = None

    def update(self, player, level_manager):
        self.anim_tick += 1 / C.FPS
        self._player = player
        self._level_manager = level_manager

    def draw(self):
        if not self._player or not self._level_manager:
            return
        p = self._player
        lm = self._level_manager

        # Top-left panel
        panel_w, panel_h = 280, 80
        s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        s.fill((0, 0, 0, 160))
        self.screen.blit(s, (10, 10))
        pygame.draw.rect(self.screen, C.CYAN, (10, 10, panel_w, panel_h), 1)

        # Health bar
        hp_frac = p.health / p.max_health
        pygame.draw.rect(self.screen, (60, 15, 15), (18, 18, 200, 16))
        bar_col = C.GREEN if hp_frac > 0.5 else (C.YELLOW if hp_frac > 0.25 else C.RED)
        pygame.draw.rect(self.screen, bar_col, (18, 18, int(200 * hp_frac), 16))
        pygame.draw.rect(self.screen, C.WHITE, (18, 18, 200, 16), 1)
        hp_txt = self.sm_font.render(f"HP  {p.health}/{p.max_health}", True, C.WHITE)
        self.screen.blit(hp_txt, (18, 19))

        # Score
        score_txt = self.font.render(f"SCORE: {p.score}", True, C.YELLOW)
        self.screen.blit(score_txt, (18, 40))

        # Puzzles solved
        if lm.current_level:
            lv = lm.current_level
            pz_txt = self.sm_font.render(
                f"PUZZLES: {lv.puzzles_solved}/{lv.puzzles_needed}", True, C.CYAN)
            self.screen.blit(pz_txt, (18, 62))

        # Level name top center
        if lm.current_level:
            names = ["Level 1: The Rusted Slums",
                     "Level 2: Scorched Desert",
                     "Level 3: Crystalline Beach",
                     "Level 4: The Battlefield"]
            idx = lm.current_level_index
            lname = names[idx] if 0 <= idx < len(names) else ""
            lsurf = self.font.render(lname, True, C.WHITE)
            lx = C.SCREEN_W // 2 - lsurf.get_width() // 2
            s2 = pygame.Surface((lsurf.get_width() + 20, 28), pygame.SRCALPHA)
            s2.fill((0, 0, 0, 140))
            self.screen.blit(s2, (lx - 10, 8))
            self.screen.blit(lsurf, (lx, 12))

        # Controls reminder bottom
        hints = self.sm_font.render(
            "Arrow/WASD Move  |  SPACE Jump  |  E Interact  |  X Attack  |  ESC Menu",
            True, (70, 70, 90))
        self.screen.blit(hints, (C.SCREEN_W // 2 - hints.get_width() // 2, C.SCREEN_H - 22))

        # Exit unlocked indicator
        if lm.current_level and lm.current_level.exit_unlocked:
            pulse = abs(math.sin(self.anim_tick * 3))
            col = (int(50 + 200 * pulse), int(200 + 55 * pulse), int(50 + 50 * pulse))
            ex_txt = self.font.render("▶ EXIT UNLOCKED — Reach the green door!", True, col)
            self.screen.blit(ex_txt, (C.SCREEN_W // 2 - ex_txt.get_width() // 2, C.SCREEN_H - 50))

        # Boss health bar if present
        if lm.current_level and lm.current_level.boss and lm.current_level.boss.alive:
            boss = lm.current_level.boss
            bw = 400
            bx = C.SCREEN_W // 2 - bw // 2
            by = C.SCREEN_H - 90
            s3 = pygame.Surface((bw + 20, 50), pygame.SRCALPHA)
            s3.fill((0, 0, 0, 180))
            self.screen.blit(s3, (bx - 10, by - 5))
            pygame.draw.rect(self.screen, (100, 15, 15), (bx, by, bw, 20))
            hf = boss.health / boss.get_max_health()
            pygame.draw.rect(self.screen, C.RED, (bx, by, int(bw * hf), 20))
            pygame.draw.rect(self.screen, C.WHITE, (bx, by, bw, 20), 1)
            ph_name = ["COMMANDER MK-I", "COMMANDER MK-II", "THE COW?!"][min(boss.phase, 2)]
            bn = self.font.render(ph_name, True, C.YELLOW)
            self.screen.blit(bn, (C.SCREEN_W // 2 - bn.get_width() // 2, by - 22))