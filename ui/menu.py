# ui/menu.py — Modern cinematic main menu
import pygame
import math
import random
import constants as C

CUTSCENE_LIST = [
    ("intro",           "Intro — The Beginning"),
    ("slum_complete",   "Level 1 Complete"),
    ("desert_complete", "Level 2 Complete"),
    ("beach_complete",  "Level 3 Complete"),
    ("boss_intro",      "Boss Intro"),
    ("boss_cow_reveal", "The Cow Reveal"),
    ("ending",          "Ending — Alien Abduction"),
]


def _lerp(a, b, t):
    return a + (b - a) * t

def _ease_out(t):
    return 1 - (1 - t) ** 3


class MenuParticle:
    def __init__(self, w, h):
        self.reset(w, h)

    def reset(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        self.vy = random.uniform(-25, -8)
        self.vx = random.uniform(-8, 8)
        self.size = random.uniform(1, 3)
        self.life = random.uniform(0.5, 3.0)
        self.max_life = self.life
        self.col = random.choice([
            (255, 200, 50), (80, 200, 255), (200, 80, 255), (80, 255, 140)
        ])

    def update(self, dt, w, h):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life -= dt
        if self.life <= 0 or self.y < -10:
            self.reset(w, h)
            self.y = h + 5

    def draw(self, screen):
        t = self.life / self.max_life
        alpha = int(t * 180)
        if alpha <= 0:
            return
        s = pygame.Surface((int(self.size * 2 + 2), int(self.size * 2 + 2)), pygame.SRCALPHA)
        r, g, b = self.col
        pygame.draw.circle(s, (r, g, b, alpha),
                           (int(self.size + 1), int(self.size + 1)), int(self.size))
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class AnimButton:
    def __init__(self, x, y, w, h, label, icon="", accent=(60, 120, 220)):
        self.target_x = x
        self.x = x - 300   # slide in from left
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.icon = icon
        self.accent = accent
        self.hovered = False
        self._hover_t = 0.0
        self._slide_t = 0.0
        self.font = pygame.font.SysFont("monospace", 17, bold=True)
        self.clicked_flag = False

    def update(self, dt, mouse_pos, events):
        # Slide in
        self._slide_t = min(1.0, self._slide_t + dt * 3)
        self.x = _lerp(self.target_x - 300, self.target_x, _ease_out(self._slide_t))

        rx = int(self.x)
        rect = pygame.Rect(rx, self.y, self.w, self.h)
        self.hovered = rect.collidepoint(mouse_pos)
        if self.hovered:
            self._hover_t = min(1.0, self._hover_t + dt * 8)
        else:
            self._hover_t = max(0.0, self._hover_t - dt * 8)

        self.clicked_flag = False
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if rect.collidepoint(ev.pos):
                    self.clicked_flag = True

    def draw(self, screen):
        rx = int(self.x)
        t = self._hover_t
        r, g, b = self.accent
        base = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        col = (int(_lerp(base[0], r, t)),
               int(_lerp(base[1], g, t)),
               int(_lerp(base[2], b, t)))

        # Shadow
        shadow = pygame.Surface((self.w + 6, self.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 80),
                         (0, 0, self.w + 6, self.h + 6), border_radius=10)
        screen.blit(shadow, (rx + 2, self.y + 3))

        # Body
        pygame.draw.rect(screen, col, (rx, self.y, self.w, self.h), border_radius=9)

        # Top shine
        shine = pygame.Surface((self.w - 4, self.h // 2), pygame.SRCALPHA)
        shine_alpha = int(40 + t * 40)
        pygame.draw.rect(shine, (255, 255, 255, shine_alpha),
                         (0, 0, self.w - 4, self.h // 2), border_radius=7)
        screen.blit(shine, (rx + 2, self.y + 2))

        # Border glow
        border_col = tuple(min(255, c + 80) for c in col)
        pygame.draw.rect(screen, border_col, (rx, self.y, self.w, self.h), 2, border_radius=9)

        # Label
        lbl = f"{self.icon}  {self.label}" if self.icon else self.label
        surf = self.font.render(lbl, True, (240, 240, 255))
        screen.blit(surf, (rx + self.w // 2 - surf.get_width() // 2,
                            self.y + self.h // 2 - surf.get_height() // 2))

        # Hover arrow
        if t > 0.5:
            ax = rx + self.w - 20
            ay = self.y + self.h // 2
            alpha = int(t * 255)
            arrow = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.polygon(arrow, (255, 255, 255, alpha),
                                [(0, 0), (12, 6), (0, 12)])
            screen.blit(arrow, (ax, ay - 6))


class MainMenu:
    SCREENS = ["main", "instructions", "controls", "cutscenes"]

    def __init__(self, screen, game):
        self.screen = screen
        self.game = game          # whole game object for timeline cutscene calls
        self.current_screen = "main"
        self.anim_tick = 0.0
        self._trans_alpha = 0.0   # screen transition
        self._trans_in = False

        self.font = pygame.font.SysFont("monospace", 20)
        self.big_font = pygame.font.SysFont("monospace", 54, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)
        self.sm_font = pygame.font.SysFont("monospace", 13)

        # Background particles
        self.bg_particles = [MenuParticle(C.SCREEN_W, C.SCREEN_H) for _ in range(60)]

        cx = C.SCREEN_W // 2
        btn_w, btn_h = 300, 50
        bx = cx - btn_w // 2

        self.main_buttons = [
            AnimButton(bx, 310, btn_w, btn_h, "NEW GAME",     "▶", (20, 140, 60)),
            AnimButton(bx, 375, btn_w, btn_h, "INSTRUCTIONS", "📖", (30, 60, 160)),
            AnimButton(bx, 440, btn_w, btn_h, "CONTROLS",     "🎮", (100, 30, 140)),
            AnimButton(bx, 505, btn_w, btn_h, "CUTSCENES",    "🎬", (140, 60, 20)),
            AnimButton(bx, 588, btn_w, 42,    "QUIT",         "✕", (140, 20, 20)),
        ]

        self.cs_buttons = []
        for i, (key, label) in enumerate(CUTSCENE_LIST):
            col = i % 2
            row = i // 2
            bx2 = cx - 400 + col * 420
            by2 = 180 + row * 68
            btn = AnimButton(bx2, by2, 380, 52, label, "", (40, 60, 130))
            btn._cs_key = key
            self.cs_buttons.append(btn)

        self.back_button = AnimButton(cx - 110, 640, 220, 44, "BACK", "←", (100, 40, 40))

        # Star field for bg
        self.stars = [(random.randint(0, C.SCREEN_W),
                       random.randint(0, C.SCREEN_H),
                       random.uniform(0.5, 2.5)) for _ in range(120)]

    def update(self, events):
        dt = 1 / C.FPS
        self.anim_tick += dt

        mouse = pygame.mouse.get_pos()

        for p in self.bg_particles:
            p.update(dt, C.SCREEN_W, C.SCREEN_H)

        if self.current_screen == "main":
            for btn in self.main_buttons:
                btn.update(dt, mouse, events)
            if self.main_buttons[0].clicked_flag:
                return "new_game"
            if self.main_buttons[1].clicked_flag:
                self._goto("instructions")
            if self.main_buttons[2].clicked_flag:
                self._goto("controls")
            if self.main_buttons[3].clicked_flag:
                self._goto("cutscenes")
            if self.main_buttons[4].clicked_flag:
                return "quit"

        elif self.current_screen in ("instructions", "controls"):
            self.back_button.update(dt, mouse, events)
            if self.back_button.clicked_flag:
                self._goto("main")

        elif self.current_screen == "cutscenes":
            for btn in self.cs_buttons:
                btn.update(dt, mouse, events)
                if btn.clicked_flag:
                    self.game.play(btn._cs_key, callback=lambda: self.game.set_state("menu"))
            self.back_button.update(dt, mouse, events)
            if self.back_button.clicked_flag:
                self._goto("main")

        return None

    def _goto(self, screen):
        self.current_screen = screen
        # Re-animate buttons
        for btn in self.main_buttons:
            btn._slide_t = 0.0
            btn.x = btn.target_x - 300
        for btn in self.cs_buttons:
            btn._slide_t = 0.0
            btn.x = btn.target_x - 300

    def draw(self):
        # Animated dark background
        bg = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        t = self.anim_tick
        # Gradient sky (dark blue → near black)
        for y in range(0, C.SCREEN_H, 4):
            frac = y / C.SCREEN_H
            r = int(4 + frac * 8)
            g = int(4 + frac * 6)
            b = int(18 + frac * 14)
            pygame.draw.rect(bg, (r, g, b), (0, y, C.SCREEN_W, 4))
        self.screen.blit(bg, (0, 0))

        # Twinkling stars
        for sx, sy, sz in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(t * 2.1 + sx * 0.07 + sy * 0.05)
            alpha = int(twinkle * 200 + 55)
            s = pygame.Surface((int(sz*2), int(sz*2)), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 210, 255, alpha), (int(sz), int(sz)), int(sz))
            self.screen.blit(s, (sx - int(sz), sy - int(sz)))

        # Floating ambient particles
        for p in self.bg_particles:
            p.draw(self.screen)

        # Horizon glow
        glow = pygame.Surface((C.SCREEN_W, 160), pygame.SRCALPHA)
        for gy in range(160):
            alpha = int((1 - gy / 160) ** 2 * 60)
            pulse = abs(math.sin(t * 0.4)) * 20
            pygame.draw.rect(glow, (int(30 + pulse), int(15 + pulse // 2), int(80 + pulse), alpha),
                             (0, gy, C.SCREEN_W, 1))
        self.screen.blit(glow, (0, C.SCREEN_H - 160))

        if self.current_screen == "main":
            self._draw_main()
        elif self.current_screen == "instructions":
            self._draw_instructions()
        elif self.current_screen == "controls":
            self._draw_controls()
        elif self.current_screen == "cutscenes":
            self._draw_cutscenes()

    def _draw_main(self):
        t = self.anim_tick
        cx = C.SCREEN_W // 2

        # Logo glow halo
        gw = int(500 + math.sin(t * 1.2) * 20)
        gs = pygame.Surface((gw, 120), pygame.SRCALPHA)
        for i in range(40):
            alpha = int((1 - i / 40) ** 2 * 45)
            pygame.draw.ellipse(gs, (255, 200, 50, alpha),
                                (i * 6, i * 1.5, gw - i * 12, 120 - i * 3))
        self.screen.blit(gs, (cx - gw // 2, 120))

        # Title
        title = self.big_font.render("RUST & RUIN", True, (255, 210, 60))
        pulse = abs(math.sin(t * 1.5))
        col2 = (int(220 + 35 * pulse), int(180 + 40 * pulse), int(50 + 30 * pulse))
        title2 = self.big_font.render("RUST & RUIN", True, col2)
        self.screen.blit(title, (cx - title.get_width() // 2 + 2, 138))
        self.screen.blit(title2, (cx - title2.get_width() // 2, 136))

        sub = self.font.render("The Last Child", True, (160, 200, 255))
        self.screen.blit(sub, (cx - sub.get_width() // 2, 204))

        # Decorative line
        lw = int(280 + math.sin(t * 0.8) * 20)
        pygame.draw.line(self.screen, (80, 120, 220),
                         (cx - lw // 2, 232), (cx + lw // 2, 232), 1)

        for btn in self.main_buttons:
            btn.draw(self.screen)

        ver = self.sm_font.render("v2.0 CINEMATIC EDITION", True, (40, 40, 55))
        self.screen.blit(ver, (C.SCREEN_W - ver.get_width() - 8, C.SCREEN_H - 18))

    def _draw_panel(self, title_str):
        cx = C.SCREEN_W // 2
        # Panel background
        s = pygame.Surface((C.SCREEN_W - 200, C.SCREEN_H - 100), pygame.SRCALPHA)
        s.fill((5, 8, 22, 200))
        self.screen.blit(s, (100, 50))
        pygame.draw.rect(self.screen, (40, 80, 160), (100, 50, C.SCREEN_W - 200, C.SCREEN_H - 100), 2,
                         border_radius=12)
        title_surf = self.font.render(title_str, True, (200, 220, 255))
        self.screen.blit(title_surf, (cx - title_surf.get_width() // 2, 70))
        pygame.draw.line(self.screen, (40, 80, 160),
                         (120, 100), (C.SCREEN_W - 120, 100), 1)

    def _draw_instructions(self):
        self._draw_panel("INSTRUCTIONS")
        cx = C.SCREEN_W // 2
        lines = [
            "RUST & RUIN: The Last Child is a 2D puzzle-platformer.",
            "",
            "OBJECTIVE:",
            "  Survive 4 levels, solve 2 puzzles each, reach the exit.",
            "  Defeat the final boss to end the Collective's reign.",
            "",
            "ENEMIES:",
            "  Drone — hovers and rushes you when close.",
            "  Guard — patrols and chases on the ground.",
            "  Turret — stationary, hurts on contact.",
            "",
            "PUZZLES:",
            "  Math Cipher · Tic-Tac-Toe · Connect Four",
            "  Pattern Lock · Missing Object · Power Grid",
            "",
            "TIP: Solve both puzzles to unlock the level exit.",
        ]
        for i, l in enumerate(lines):
            col = (255, 220, 80) if l.endswith(":") else (180, 185, 210)
            surf = self.sm_font.render(l, True, col)
            self.screen.blit(surf, (140, 118 + i * 26))
        self.back_button.draw(self.screen)

    def _draw_controls(self):
        self._draw_panel("CONTROLS")
        cx = C.SCREEN_W // 2
        controls = [
            ("← / A",        "Move Left"),
            ("→ / D",        "Move Right"),
            ("SPACE / W / ↑","Jump"),
            ("E / ENTER",    "Interact / Confirm Puzzle"),
            ("X / Z",        "Attack"),
            ("ESC",          "Pause / Exit Puzzle"),
            ("TAB",          "Skip Cutscene"),
        ]
        for i, (key, action) in enumerate(controls):
            y = 130 + i * 52
            pygame.draw.rect(self.screen, (20, 30, 60),
                             (140, y, C.SCREEN_W - 280, 42), border_radius=7)
            pygame.draw.rect(self.screen, (50, 80, 160),
                             (140, y, C.SCREEN_W - 280, 42), 1, border_radius=7)
            k_surf = self.font.render(key, True, (255, 220, 60))
            a_surf = self.font.render(action, True, (200, 210, 240))
            self.screen.blit(k_surf, (165, y + 12))
            self.screen.blit(a_surf, (cx + 20, y + 12))
        self.back_button.draw(self.screen)

    def _draw_cutscenes(self):
        self._draw_panel("CUTSCENE VIEWER")
        for btn in self.cs_buttons:
            btn.draw(self.screen)
        self.back_button.draw(self.screen)
