# ui/menu.py
import pygame
import math
import constants as C

CUTSCENE_LIST = [
    ("intro",           "Intro — The Beginning"),
    ("slum_complete",   "Level 1 Complete — Slums"),
    ("desert_complete", "Level 2 Complete — Desert"),
    ("beach_complete",  "Level 3 Complete — Beach"),
    ("boss_intro",      "Boss Intro — The Commander"),
    ("boss_cow_reveal", "Boss Twist — The Cow!"),
    ("ending",          "Ending — Alien Abduction"),
]


class Button:
    def __init__(self, x, y, w, h, label, col=(30, 50, 100), hover_col=(60, 100, 200)):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.col = col
        self.hover_col = hover_col
        self.hovered = False
        self.font = pygame.font.SysFont("monospace", 18, bold=True)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, events):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.rect.collidepoint(ev.pos):
                    return True
        return False

    def draw(self, screen):
        col = self.hover_col if self.hovered else self.col
        pygame.draw.rect(screen, col, self.rect, border_radius=6)
        pygame.draw.rect(screen, C.CYAN if self.hovered else C.GREY, self.rect, 2, border_radius=6)
        surf = self.font.render(self.label, True, C.WHITE)
        screen.blit(surf, (self.rect.centerx - surf.get_width() // 2,
                           self.rect.centery - surf.get_height() // 2))


class MainMenu:
    SCREENS = ["main", "instructions", "controls", "cutscenes"]

    def __init__(self, screen, cutscene_manager):
        self.screen = screen
        self.cutscene_manager = cutscene_manager
        self.current_screen = "main"
        self.anim_tick = 0
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 52, bold=True)
        self.sub_font = pygame.font.SysFont("monospace", 16)
        self.sm_font = pygame.font.SysFont("monospace", 14)

        cx = C.SCREEN_W // 2

        # Main buttons
        self.main_buttons = [
            Button(cx - 140, 320, 280, 52, "▶  NEW GAME",    (20, 80, 40),  (40, 160, 80)),
            Button(cx - 140, 388, 280, 52, "📖  INSTRUCTIONS", (30, 40, 100), (60, 80, 180)),
            Button(cx - 140, 456, 280, 52, "🎮  CONTROLS",    (60, 30, 80),  (120, 60, 160)),
            Button(cx - 140, 524, 280, 52, "🎬  CUTSCENES",   (80, 40, 20),  (160, 80, 40)),
            Button(cx - 140, 610, 280, 44, "✕  QUIT",         (80, 20, 20),  (160, 40, 40)),
        ]

        # Cutscene viewer buttons
        self.cs_buttons = []
        for i, (key, label) in enumerate(CUTSCENE_LIST):
            row = i % 4
            col_idx = i // 4
            bx = cx - 380 + col_idx * 400
            by = 200 + row * 68
            btn = Button(bx, by, 380, 54, label, (30, 30, 60), (60, 60, 130))
            btn._cs_key = key
            self.cs_buttons.append(btn)

        self.back_button = Button(cx - 100, 640, 200, 44, "← BACK", (50, 30, 30), (100, 60, 60))
        self.viewing_cutscene = False
        self._result = None

    def update(self, events):
        self.anim_tick += 1 / C.FPS
        mouse = pygame.mouse.get_pos()
        self._result = None

        if self.viewing_cutscene:
            self.cutscene_manager.update(events, 1 / C.FPS)
            if not self.cutscene_manager.active:
                self.viewing_cutscene = False
            return None

        if self.current_screen == "main":
            for btn in self.main_buttons:
                btn.update(mouse)
            if self.main_buttons[0].clicked(events):
                return "new_game"
            if self.main_buttons[1].clicked(events):
                self.current_screen = "instructions"
            if self.main_buttons[2].clicked(events):
                self.current_screen = "controls"
            if self.main_buttons[3].clicked(events):
                self.current_screen = "cutscenes"
            if self.main_buttons[4].clicked(events):
                return "quit"

        elif self.current_screen in ("instructions", "controls", "cutscenes"):
            self.back_button.update(mouse)
            if self.back_button.clicked(events):
                self.current_screen = "main"
            if self.current_screen == "cutscenes":
                for btn in self.cs_buttons:
                    btn.update(mouse)
                    if btn.clicked(events):
                        self.viewing_cutscene = True
                        self.cutscene_manager.play(btn._cs_key, callback=lambda: None)

        return None

    def draw(self):
        if self.viewing_cutscene:
            self.cutscene_manager.draw()
            return

        if self.current_screen == "main":
            self._draw_main()
        elif self.current_screen == "instructions":
            self._draw_instructions()
        elif self.current_screen == "controls":
            self._draw_controls()
        elif self.current_screen == "cutscenes":
            self._draw_cutscenes()

    def _draw_main(self):
        # Animated background
        self.screen.fill((5, 5, 18))
        t = self.anim_tick

        # Scrolling stars
        for i in range(80):
            sx = (i * 157 + int(t * (i % 3 + 1) * 8)) % C.SCREEN_W
            sy = (i * 89 + int(t * (i % 2 + 0.5) * 4)) % C.SCREEN_H
            r = 1 + i % 2
            pygame.draw.circle(self.screen, (100 + i % 100, 100 + i % 80, 150), (sx, sy), r)

        # Silhouette cityscape
        for i in range(12):
            bx = i * 120 - 40
            bh = 80 + (i * 53) % 160
            col = (20, 15, 30)
            pygame.draw.rect(self.screen, col, (bx, C.SCREEN_H - bh, 90, bh))
            # Windows
            for wy in range(C.SCREEN_H - bh + 10, C.SCREEN_H - 10, 22):
                for wx in range(bx + 8, bx + 82, 18):
                    wc = (180, 160, 60) if (i + wy // 22) % 4 != 0 else (20, 20, 30)
                    pygame.draw.rect(self.screen, wc, (wx, wy, 10, 12))

        # Title
        pulse = abs(math.sin(t * 1.2))
        title_col = (
            int(200 + 55 * pulse),
            int(150 + 50 * pulse),
            int(30 + 20 * pulse)
        )
        title = self.big_font.render("RUST & RUIN", True, title_col)
        self.screen.blit(title, (C.SCREEN_W // 2 - title.get_width() // 2, 140))

        sub = self.font.render("The Last Child", True, (160, 160, 200))
        self.screen.blit(sub, (C.SCREEN_W // 2 - sub.get_width() // 2, 210))

        tagline = self.sm_font.render("A post-apocalyptic puzzle adventure", True, (80, 80, 100))
        self.screen.blit(tagline, (C.SCREEN_W // 2 - tagline.get_width() // 2, 248))

        # Buttons
        for btn in self.main_buttons:
            btn.draw(self.screen)

        # Version
        ver = self.sm_font.render("v1.0  |  [TAB] Skip Cutscenes", True, (50, 50, 70))
        self.screen.blit(ver, (10, C.SCREEN_H - 22))

    def _draw_instructions(self):
        self.screen.fill((5, 8, 20))
        t = self.big_font.render("INSTRUCTIONS", True, C.CYAN)
        self.screen.blit(t, (C.SCREEN_W // 2 - t.get_width() // 2, 60))

        lines = [
            ("STORY", C.YELLOW),
            ("You are KAI, a child survivor in a robot apocalypse.", C.WHITE),
            ("Your companion AXIOM guides you through 4 levels.", C.WHITE),
            ("", None),
            ("OBJECTIVE", C.YELLOW),
            ("• Explore each level and solve 2 puzzles per zone.", C.WHITE),
            ("• Defeat or dodge enemies along the way.", C.WHITE),
            ("• Once both puzzles are solved, the EXIT unlocks.", C.WHITE),
            ("• Reach the Battlefield and defeat the boss!", C.WHITE),
            ("", None),
            ("PUZZLES", C.YELLOW),
            ("• Math Cipher — solve the equation.", C.WHITE),
            ("• Tic-Tac-Toe — beat (or draw with) AXIOM-AI.", C.WHITE),
            ("• Pattern Lock — repeat the color sequence.", C.WHITE),
            ("• Missing Object — identify the hidden shape.", C.WHITE),
            ("• Power Grid — connect all nodes to the source.", C.WHITE),
            ("• Connect Four — outplay the tactical AI.", C.WHITE),
            ("", None),
            ("ENEMIES", C.YELLOW),
            ("• Drones chase you, Guards patrol, Turrets shoot.", C.WHITE),
            ("• Press [X/Z] near an enemy to attack.", C.WHITE),
            ("• You have 100 HP. Avoid hits!", C.WHITE),
        ]

        y = 130
        for text, col in lines:
            if col is None:
                y += 10
                continue
            f = self.font if col == C.YELLOW else self.sm_font
            surf = f.render(text, True, col)
            self.screen.blit(surf, (80, y))
            y += 28 if col == C.YELLOW else 22

        self.back_button.draw(self.screen)

    def _draw_controls(self):
        self.screen.fill((5, 8, 20))
        t = self.big_font.render("CONTROLS", True, C.CYAN)
        self.screen.blit(t, (C.SCREEN_W // 2 - t.get_width() // 2, 60))

        controls = [
            ("MOVEMENT",        C.YELLOW,  True),
            ("Arrow Left / A",  "Move Left",  False),
            ("Arrow Right / D", "Move Right", False),
            ("Space / W / Up",  "Jump",       False),
            ("",                "",           False),
            ("INTERACTION",     C.YELLOW,  True),
            ("E / Enter",       "Interact / Confirm", False),
            ("X / Z",           "Attack nearby enemy", False),
            ("",                "",           False),
            ("GAME",            C.YELLOW,  True),
            ("ESC",             "Pause / Exit Puzzle", False),
            ("TAB",             "Skip cutscene",       False),
            ("",                "",                    False),
            ("PUZZLE SPECIFIC", C.YELLOW,  True),
            ("Mouse Click",     "Select in all puzzles",  False),
            ("Enter",           "Confirm math answer",    False),
            ("Backspace",       "Delete math digit",      False),
        ]

        y = 140
        for col0, col1, is_header in controls:
            if not col0:
                y += 8
                continue
            if is_header:
                surf = self.font.render(col0, True, col1)
                self.screen.blit(surf, (80, y))
                y += 32
            else:
                k = self.sm_font.render(col0, True, C.CYAN)
                v = self.sm_font.render(col1, True, C.WHITE)
                self.screen.blit(k, (80, y))
                self.screen.blit(v, (340, y))
                y += 24

        self.back_button.draw(self.screen)

    def _draw_cutscenes(self):
        self.screen.fill((5, 8, 20))
        t = self.big_font.render("CUTSCENE VIEWER", True, C.ORANGE)
        self.screen.blit(t, (C.SCREEN_W // 2 - t.get_width() // 2, 40))

        note = self.sm_font.render(
            "DEV MODE: Click any cutscene to preview it. [TAB] to skip.", True, (120, 120, 80))
        self.screen.blit(note, (C.SCREEN_W // 2 - note.get_width() // 2, 105))

        for btn in self.cs_buttons:
            btn.draw(self.screen)

        self.back_button.draw(self.screen)
