# ui/hud.py — Modern cinematic HUD with smooth transitions
import pygame
import math
import constants as C


def _lerp(a, b, t):
    return a + (b - a) * t

def _draw_rounded_rect(surf, color, rect, radius=8, alpha=None):
    """Draw a rounded rect, optionally with alpha via SRCALPHA surface."""
    if alpha is not None:
        s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
        surf.blit(s, (rect[0], rect[1]))
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)


class AnimatedBar:
    """Smooth-lerping bar (health, boss HP)."""
    def __init__(self, value=1.0):
        self.display = float(value)
        self.target = float(value)

    def set(self, value):
        self.target = max(0.0, min(1.0, value))

    def update(self, dt):
        self.display = _lerp(self.display, self.target, min(1.0, dt * 8))

    def draw(self, screen, x, y, w, h, fg_col, bg_col=(40, 15, 15), border=True):
        # Background
        _draw_rounded_rect(screen, bg_col, (x, y, w, h), radius=h // 2)
        # Fill
        fw = max(0, int(w * self.display))
        if fw > 0:
            _draw_rounded_rect(screen, fg_col, (x, y, fw, h), radius=h // 2)
            # Shine
            shine_h = max(1, h // 3)
            _draw_rounded_rect(screen, tuple(min(255, c + 60) for c in fg_col),
                               (x + 2, y + 2, max(0, fw - 4), shine_h), radius=shine_h // 2)
        if border:
            pygame.draw.rect(screen, (180, 180, 200), (x, y, w, h), 1, border_radius=h // 2)


class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("monospace", 15, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 18, bold=True)
        self.sm_font = pygame.font.SysFont("monospace", 12)
        self.boss_font = pygame.font.SysFont("monospace", 20, bold=True)
        self.anim_tick = 0.0
        self._player = None
        self._level_manager = None

        # Animated elements
        self.hp_bar = AnimatedBar(1.0)
        self.boss_bar = AnimatedBar(1.0)

        # Level name slide-in
        self._level_name_alpha = 0.0
        self._level_name_timer = 0.0
        self._level_name_shown = -1

        # Score pop animation
        self._score_prev = 0
        self._score_pop = 0.0

        # Puzzle indicator
        self._puzzle_pulse = 0.0

        # Exit unlock flash
        self._exit_alpha = 0.0
        self._exit_shown = False

    def update(self, player, level_manager):
        dt = 1 / C.FPS
        self.anim_tick += dt
        self._player = player
        self._level_manager = level_manager

        if player:
            self.hp_bar.set(player.health / player.max_health)
            self.hp_bar.update(dt)

            if player.score != self._score_prev:
                self._score_pop = 1.0
                self._score_prev = player.score
            if self._score_pop > 0:
                self._score_pop = max(0, self._score_pop - dt * 4)

        if level_manager and level_manager.current_level:
            boss = level_manager.current_level.boss
            if boss and boss.alive:
                self.boss_bar.set(boss.health / boss.get_max_health())
                self.boss_bar.update(dt)

        # Level name banner
        if level_manager:
            idx = level_manager.current_level_index
            if idx != self._level_name_shown:
                self._level_name_shown = idx
                self._level_name_timer = 3.5
                self._level_name_alpha = 0.0
        if self._level_name_timer > 0:
            self._level_name_timer -= dt
            if self._level_name_timer > 2.5:
                self._level_name_alpha = min(1.0, self._level_name_alpha + dt * 3)
            elif self._level_name_timer < 0.8:
                self._level_name_alpha = max(0.0, self._level_name_alpha - dt * 2)

        # Exit unlocked flash
        if level_manager and level_manager.current_level:
            if level_manager.current_level.exit_unlocked:
                if not self._exit_shown:
                    self._exit_alpha = 1.0
                    self._exit_shown = True
                self._exit_alpha = max(0.3, abs(math.sin(self.anim_tick * 2.5)))
            else:
                self._exit_shown = False

        self._puzzle_pulse += dt * 3

    def draw(self):
        if not self._player or not self._level_manager:
            return
        p = self._player
        lm = self._level_manager

        # ── Health panel (top-left) ──────────────────────────────────────────
        panel_w = 260
        _draw_rounded_rect(self.screen, (8, 8, 18), (10, 10, panel_w, 82), radius=10, alpha=190)
        pygame.draw.rect(self.screen, (0, 180, 220, 150), (10, 10, panel_w, 82), 1,
                         border_radius=10)

        # HP icon
        pygame.draw.polygon(self.screen, (220, 50, 70),
                            [(24, 26),(30, 20),(36, 26),(30, 34)])
        pygame.draw.polygon(self.screen, (255, 80, 100),
                            [(25, 25),(30, 20),(35, 25),(30, 32)])

        hp_frac = p.health / p.max_health
        if hp_frac > 0.5:
            bar_col = (50, 210, 80)
        elif hp_frac > 0.25:
            bar_col = (255, 200, 30)
        else:
            # Pulse red when low
            pulse = abs(math.sin(self.anim_tick * 6))
            bar_col = (int(180 + 75 * pulse), 20, 20)

        self.hp_bar.draw(self.screen, 46, 19, 190, 16, bar_col)
        hp_txt = self.sm_font.render(f"HP {p.health}/{p.max_health}", True, (220, 220, 240))
        self.screen.blit(hp_txt, (48, 20))

        # Score
        pop = 1.0 + self._score_pop * 0.3
        score_col = (255, 220, 50) if self._score_pop > 0.1 else (200, 195, 160)
        score_surf = self.font.render(f"SCORE  {p.score:06d}", True, score_col)
        # Scale for pop
        if pop > 1.01:
            scaled = pygame.transform.scale(score_surf,
                (int(score_surf.get_width()*pop), int(score_surf.get_height()*pop)))
            self.screen.blit(scaled, (46, 41))
        else:
            self.screen.blit(score_surf, (46, 41))

        # Puzzle counter
        if lm.current_level:
            lv = lm.current_level
            pz_col = (80, 220, 255) if lv.puzzles_solved < lv.puzzles_needed else (80, 255, 120)
            pips = ""
            for i in range(lv.puzzles_needed):
                pips += "◆ " if i < lv.puzzles_solved else "◇ "
            pz_txt = self.sm_font.render(f"PUZZLES  {pips.strip()}", True, pz_col)
            self.screen.blit(pz_txt, (18, 62))

        # ── Level name banner (top-center, fades in/out) ────────────────────
        if self._level_name_timer > 0 and lm.current_level:
            names = ["The Rusted Slums","Scorched Desert",
                     "Crystalline Beach","The Battlefield"]
            subtitles = ["Level 1","Level 2","Level 3","Level 4"]
            idx = lm.current_level_index
            if 0 <= idx < len(names):
                alpha = int(self._level_name_alpha * 255)
                name_surf = self.big_font.render(names[idx], True, (255, 255, 255))
                sub_surf = self.sm_font.render(subtitles[idx], True, (160, 200, 255))
                bw = max(name_surf.get_width(), sub_surf.get_width()) + 40
                bx = C.SCREEN_W // 2 - bw // 2
                _draw_rounded_rect(self.screen, (5, 5, 20), (bx, 8, bw, 50),
                                   radius=8, alpha=int(alpha * 0.75))
                name_surf.set_alpha(alpha)
                sub_surf.set_alpha(alpha)
                self.screen.blit(name_surf,
                    (C.SCREEN_W//2 - name_surf.get_width()//2, 12))
                self.screen.blit(sub_surf,
                    (C.SCREEN_W//2 - sub_surf.get_width()//2, 36))

        # ── Exit unlock indicator ────────────────────────────────────────────
        if lm.current_level and lm.current_level.exit_unlocked:
            alpha = int(self._exit_alpha * 255)
            ex_col = (50, int(200 * self._exit_alpha), 80)
            s = pygame.Surface((420, 30), pygame.SRCALPHA)
            s.fill((0, 0, 0, int(alpha * 0.5)))
            ex = C.SCREEN_W // 2 - 210
            self.screen.blit(s, (ex, C.SCREEN_H - 52))
            ex_txt = self.font.render("▶  EXIT UNLOCKED — Reach the green door!", True, ex_col)
            ex_txt.set_alpha(alpha)
            self.screen.blit(ex_txt, (C.SCREEN_W//2 - ex_txt.get_width()//2, C.SCREEN_H - 49))

        # ── Controls hint (bottom bar, very subtle) ──────────────────────────
        ctrl = self.sm_font.render(
            "WASD/Arrows  Move   ·   SPACE  Jump   ·   E  Interact   ·   X  Attack",
            True, (55, 55, 70))
        self.screen.blit(ctrl, (C.SCREEN_W//2 - ctrl.get_width()//2, C.SCREEN_H - 18))

        # ── Boss health bar ──────────────────────────────────────────────────
        if lm.current_level and lm.current_level.boss and lm.current_level.boss.alive:
            boss = lm.current_level.boss
            bw = 440
            bx = C.SCREEN_W // 2 - bw // 2
            by = C.SCREEN_H - 96

            # Panel
            _draw_rounded_rect(self.screen, (8, 4, 4), (bx - 14, by - 32, bw + 28, 68),
                                radius=10, alpha=200)
            pygame.draw.rect(self.screen, (180, 30, 30), (bx - 14, by - 32, bw + 28, 68), 1,
                             border_radius=10)

            # Phase name
            phases = ["COMMANDER MK-I", "COMMANDER MK-II", "THE COW?!"]
            phase_col = [(220, 80, 80), (255, 160, 40), (255, 230, 60)]
            ph = min(boss.phase, 2)
            ph_surf = self.boss_font.render(phases[ph], True, phase_col[ph])
            self.screen.blit(ph_surf, (C.SCREEN_W//2 - ph_surf.get_width()//2, by - 28))

            # Bar
            hp_col = phase_col[ph]
            self.boss_bar.draw(self.screen, bx, by, bw, 20, hp_col,
                               bg_col=(50, 10, 10))

            # Phase pips
            for i in range(3):
                pip_x = bx + bw - 22 - i * 18
                col2 = phase_col[2 - i] if (2 - i) >= ph else (40, 40, 40)
                pygame.draw.circle(self.screen, col2, (pip_x, by + 10), 6)
                pygame.draw.circle(self.screen, (200, 200, 200), (pip_x, by + 10), 6, 1)
