# systems/puzzle_engine.py
import pygame
import random
import math
import constants as C


class PuzzleEngine:
    """Manages all puzzle types: math, ttt, connect4, pattern, missing_obj, power."""

    def __init__(self, screen, ai_system):
        self.screen = screen
        self.ai = ai_system
        self.active = False
        self.puzzle_type = None
        self.result = None  # "complete" / "close" / None
        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont("monospace", 32, bold=True)
        self.sm_font = pygame.font.SysFont("monospace", 15)

        # Math puzzle state
        self.math_question = ""
        self.math_answer = 0
        self.math_input = ""
        self.math_feedback = ""

        # Tic-tac-toe state
        self.ttt_board = [[0]*3 for _ in range(3)]
        self.ttt_turn = 1  # 1=player, 2=AI
        self.ttt_winner = 0
        self.ttt_msg = ""
        self.ttt_ai_timer = 0

        # Connect four state
        self.c4_board = [[0]*7 for _ in range(6)]
        self.c4_turn = 1
        self.c4_winner = 0
        self.c4_msg = ""
        self.c4_ai_timer = 0

        # Pattern state
        self.pattern_seq = []
        self.pattern_player_seq = []
        self.pattern_display_index = -1
        self.pattern_display_timer = 0
        self.pattern_phase = "show"  # show / input
        self.pattern_msg = ""
        self.pattern_length = 5

        # Missing object state
        self.missing_items = []
        self.missing_answer = -1
        self.missing_selected = -1
        self.missing_msg = ""

        # Power connections state
        self.power_nodes = []
        self.power_connections = []
        self.power_target = []
        self.power_selected = -1
        self.power_msg = ""
        self.power_solved = False

        self.anim_tick = 0
        self.complete_timer = 0

    def start(self, puzzle_type):
        self.active = True
        self.puzzle_type = puzzle_type
        self.result = None
        self.complete_timer = 0
        self.anim_tick = 0

        if puzzle_type == "math":
            self._init_math()
        elif puzzle_type == "ttt":
            self._init_ttt()
        elif puzzle_type == "connect4":
            self._init_c4()
        elif puzzle_type == "pattern":
            self._init_pattern()
        elif puzzle_type == "missing":
            self._init_missing()
        elif puzzle_type == "power":
            self._init_power()

    def _init_math(self):
        ops = ['+', '-', '*']
        op = random.choice(ops)
        a = random.randint(2, 12)
        b = random.randint(2, 12)
        if op == '+':
            self.math_answer = a + b
            self.math_question = f"{a} + {b} = ?"
        elif op == '-':
            a, b = max(a, b), min(a, b)
            self.math_answer = a - b
            self.math_question = f"{a} - {b} = ?"
        else:
            self.math_answer = a * b
            self.math_question = f"{a} x {b} = ?"
        self.math_input = ""
        self.math_feedback = ""

    def _init_ttt(self):
        self.ttt_board = [[0]*3 for _ in range(3)]
        self.ttt_turn = 1
        self.ttt_winner = 0
        self.ttt_msg = "Your turn! You are X."
        self.ttt_ai_timer = 0

    def _init_c4(self):
        self.c4_board = [[0]*7 for _ in range(6)]
        self.c4_turn = 1
        self.c4_winner = 0
        self.c4_msg = "Your turn! Click a column."
        self.c4_ai_timer = 0

    def _init_pattern(self):
        colors = [(255, 50, 50), (50, 200, 80), (50, 100, 220), (255, 200, 0), (200, 50, 200)]
        self.pattern_seq = [random.randint(0, 4) for _ in range(self.pattern_length)]
        self.pattern_player_seq = []
        self.pattern_display_index = 0
        self.pattern_display_timer = 0.8
        self.pattern_phase = "show"
        self.pattern_colors = colors
        self.pattern_msg = "Watch the pattern..."

    def _init_missing(self):
        # 6 objects, one is "missing" (shown as question mark)
        all_shapes = ["circle", "square", "triangle", "diamond", "star", "hexagon"]
        random.shuffle(all_shapes)
        self.missing_items = all_shapes[:6]
        self.missing_answer = random.randint(0, 5)
        self.missing_cols = [
            (220, 80, 80), (80, 200, 80), (80, 80, 220),
            (220, 200, 50), (200, 80, 200), (80, 200, 200)
        ]
        self.missing_selected = -1
        self.missing_msg = "Find the missing object! One slot is hidden — which shape belongs there?"
        self.missing_options = random.sample(all_shapes, 6)
        if self.missing_items[self.missing_answer] not in self.missing_options:
            self.missing_options[0] = self.missing_items[self.missing_answer]
        random.shuffle(self.missing_options)

    def _init_power(self):
        # Node positions
        self.power_nodes = [
            {"x": 200, "y": 200, "powered": True, "id": 0},
            {"x": 380, "y": 150, "powered": False, "id": 1},
            {"x": 500, "y": 280, "powered": False, "id": 2},
            {"x": 320, "y": 340, "powered": False, "id": 3},
            {"x": 180, "y": 360, "powered": False, "id": 4},
            {"x": 440, "y": 420, "powered": False, "id": 5},
        ]
        self.power_target = [1, 2, 3, 4, 5]  # all need power
        self.power_connections = []
        self.power_selected = -1
        self.power_solved = False
        self.power_msg = "Connect all nodes to the power source! Click a node, then click another."

    # ── UPDATE ──────────────────────────────────────────────────────────────

    def update(self, events):
        if not self.active:
            return None
        self.anim_tick += 1 / C.FPS

        # Global skip/close
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.active = False
                return "close"

        if self.complete_timer > 0:
            self.complete_timer -= 1 / C.FPS
            if self.complete_timer <= 0:
                self.active = False
                return "complete"
            return None

        if self.puzzle_type == "math":
            return self._update_math(events)
        elif self.puzzle_type == "ttt":
            return self._update_ttt(events)
        elif self.puzzle_type == "connect4":
            return self._update_c4(events)
        elif self.puzzle_type == "pattern":
            return self._update_pattern(events)
        elif self.puzzle_type == "missing":
            return self._update_missing(events)
        elif self.puzzle_type == "power":
            return self._update_power(events)
        return None

    def _update_math(self, events):
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    try:
                        ans = int(self.math_input)
                        if ans == self.math_answer:
                            self.math_feedback = "CORRECT! Door unlocked!"
                            self.complete_timer = 1.5
                        else:
                            self.math_feedback = f"Wrong! Try again. (Hint: {self.math_answer // 2}?)"
                            self.math_input = ""
                    except ValueError:
                        self.math_feedback = "Enter a number!"
                        self.math_input = ""
                elif ev.key == pygame.K_BACKSPACE:
                    self.math_input = self.math_input[:-1]
                elif ev.unicode.lstrip('-').isdigit() or (ev.unicode == '-' and not self.math_input):
                    if len(self.math_input) < 6:
                        self.math_input += ev.unicode
        return None

    def _update_ttt(self, events):
        if self.ttt_winner != 0:
            for ev in events:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    self.complete_timer = 0.1
            return None

        if self.ttt_ai_timer > 0:
            self.ttt_ai_timer -= 1 / C.FPS
            if self.ttt_ai_timer <= 0 and self.ttt_turn == 2:
                move = self.ai.ttt_best_move(self.ttt_board)
                if move:
                    self.ttt_board[move[0]][move[1]] = 2
                    w = self.ai.ttt_get_winner(self.ttt_board)
                    if w:
                        self.ttt_winner = w
                        self.ttt_msg = "AXIOM wins! But you still get the door code..." if w == 2 else "You win!"
                        self.complete_timer = 2.0
                    elif all(self.ttt_board[r][c] != 0 for r in range(3) for c in range(3)):
                        self.ttt_winner = -1
                        self.ttt_msg = "Draw! Door unlocks anyway."
                        self.complete_timer = 2.0
                    else:
                        self.ttt_turn = 1
                        self.ttt_msg = "Your turn!"

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and self.ttt_turn == 1:
                mx, my = ev.pos
                # Map mouse to board cell
                bx, by = C.SCREEN_W // 2 - 130, C.SCREEN_H // 2 - 130
                cell_size = 86
                for r in range(3):
                    for c in range(3):
                        cx = bx + c * cell_size
                        cy = by + r * cell_size
                        if cx < mx < cx + cell_size and cy < my < cy + cell_size:
                            if self.ttt_board[r][c] == 0:
                                self.ttt_board[r][c] = 1
                                w = self.ai.ttt_get_winner(self.ttt_board)
                                if w:
                                    self.ttt_winner = w
                                    self.ttt_msg = "You win! Door opens!"
                                    self.complete_timer = 2.0
                                elif all(self.ttt_board[rr][cc] != 0 for rr in range(3) for cc in range(3)):
                                    self.ttt_winner = -1
                                    self.ttt_msg = "Draw! Door unlocks anyway."
                                    self.complete_timer = 2.0
                                else:
                                    self.ttt_turn = 2
                                    self.ttt_msg = "AXIOM is thinking..."
                                    self.ttt_ai_timer = 0.6
        return None

    def _update_c4(self, events):
        if self.c4_winner != 0:
            for ev in events:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN:
                    self.complete_timer = 0.1
            return None

        if self.c4_ai_timer > 0:
            self.c4_ai_timer -= 1 / C.FPS
            if self.c4_ai_timer <= 0 and self.c4_turn == 2:
                col = self.ai.c4_best_move(self.c4_board)
                if col is not None and self.ai.c4_is_valid(self.c4_board, col):
                    self.ai.c4_drop(self.c4_board, col, 2)
                    w = self.ai.c4_get_winner(self.c4_board)
                    if w:
                        self.c4_winner = w
                        self.c4_msg = "AXIOM wins! Gate opens anyway." if w == 2 else "YOU WIN!"
                        self.complete_timer = 2.0
                    elif all(self.c4_board[0][c] != 0 for c in range(7)):
                        self.c4_winner = -1
                        self.c4_msg = "Draw! Gate opens."
                        self.complete_timer = 2.0
                    else:
                        self.c4_turn = 1
                        self.c4_msg = "Your turn!"

        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN and self.c4_turn == 1:
                mx, my = ev.pos
                bx = C.SCREEN_W // 2 - 175
                cell_w = 50
                col = (mx - bx) // cell_w
                if 0 <= col < 7 and self.ai.c4_is_valid(self.c4_board, col):
                    self.ai.c4_drop(self.c4_board, col, 1)
                    w = self.ai.c4_get_winner(self.c4_board)
                    if w:
                        self.c4_winner = w
                        self.c4_msg = "YOU WIN! Gate opens!"
                        self.complete_timer = 2.0
                    elif all(self.c4_board[0][c] != 0 for c in range(7)):
                        self.c4_winner = -1
                        self.c4_msg = "Draw! Gate opens."
                        self.complete_timer = 2.0
                    else:
                        self.c4_turn = 2
                        self.c4_msg = "AXIOM thinking..."
                        self.c4_ai_timer = 0.5
        return None

    def _update_pattern(self, events):
        if self.pattern_phase == "show":
            self.pattern_display_timer -= 1 / C.FPS
            if self.pattern_display_timer <= 0:
                self.pattern_display_index += 1
                self.pattern_display_timer = 0.7
                if self.pattern_display_index >= len(self.pattern_seq):
                    self.pattern_phase = "input"
                    self.pattern_display_index = -1
                    self.pattern_msg = "Repeat the pattern! Click the colored buttons."
        elif self.pattern_phase == "input":
            for ev in events:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos
                    # 5 color buttons
                    btn_y = C.SCREEN_H // 2 + 60
                    for i in range(5):
                        bx = C.SCREEN_W // 2 - 200 + i * 80
                        if bx < mx < bx + 60 and btn_y < my < btn_y + 60:
                            self.pattern_player_seq.append(i)
                            n = len(self.pattern_player_seq)
                            if self.pattern_seq[:n] != self.pattern_player_seq:
                                self.pattern_msg = "Wrong! Try again."
                                self.pattern_player_seq = []
                                # Replay
                                self.pattern_display_index = 0
                                self.pattern_display_timer = 0.8
                                self.pattern_phase = "show"
                            elif n == len(self.pattern_seq):
                                self.pattern_msg = "Pattern matched! Gate open!"
                                self.complete_timer = 1.5
        return None

    def _update_missing(self, events):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                opt_y = C.SCREEN_H // 2 + 80
                for i, opt in enumerate(self.missing_options):
                    ox = C.SCREEN_W // 2 - 240 + i * 80
                    if ox < mx < ox + 64 and opt_y < my < opt_y + 64:
                        self.missing_selected = i
                        if self.missing_options[i] == self.missing_items[self.missing_answer]:
                            self.missing_msg = "Correct! The missing object revealed!"
                            self.complete_timer = 1.5
                        else:
                            self.missing_msg = f"Wrong! That's a {self.missing_options[i]}. Try again!"
        return None

    def _update_power(self, events):
        for ev in events:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                # Offset for panel
                off_x, off_y = C.SCREEN_W // 2 - 320, C.SCREEN_H // 2 - 250
                for i, node in enumerate(self.power_nodes):
                    nx = node["x"] + off_x
                    ny = node["y"] + off_y
                    if math.hypot(mx - nx, my - ny) < 22:
                        if self.power_selected == -1:
                            self.power_selected = i
                            self.power_msg = f"Node {i} selected. Click another node."
                        else:
                            pair = tuple(sorted([self.power_selected, i]))
                            if pair not in self.power_connections and self.power_selected != i:
                                self.power_connections.append(pair)
                                self._power_propagate()
                                if all(n["powered"] for n in self.power_nodes):
                                    self.power_msg = "All nodes powered! System online!"
                                    self.complete_timer = 1.5
                            self.power_selected = -1
        return None

    def _power_propagate(self):
        # BFS from powered nodes
        powered = {i for i, n in enumerate(self.power_nodes) if n["powered"]}
        changed = True
        while changed:
            changed = False
            for a, b in self.power_connections:
                if a in powered and b not in powered:
                    powered.add(b)
                    changed = True
                elif b in powered and a not in powered:
                    powered.add(a)
                    changed = True
        for i, node in enumerate(self.power_nodes):
            node["powered"] = i in powered

    # ── DRAW ────────────────────────────────────────────────────────────────

    def draw(self):
        if not self.active:
            return
        # Overlay
        s = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        s.fill((0, 0, 0, 180))
        self.screen.blit(s, (0, 0))

        if self.puzzle_type == "math":
            self._draw_math()
        elif self.puzzle_type == "ttt":
            self._draw_ttt()
        elif self.puzzle_type == "connect4":
            self._draw_c4()
        elif self.puzzle_type == "pattern":
            self._draw_pattern()
        elif self.puzzle_type == "missing":
            self._draw_missing()
        elif self.puzzle_type == "power":
            self._draw_power()

        # Skip hint
        skip = self.sm_font.render("[ESC] Close Puzzle", True, (100, 100, 100))
        self.screen.blit(skip, (C.SCREEN_W - skip.get_width() - 10, 10))

    def _panel(self, w, h, title, title_col=C.CYAN):
        x = C.SCREEN_W // 2 - w // 2
        y = C.SCREEN_H // 2 - h // 2
        pygame.draw.rect(self.screen, (8, 8, 24), (x, y, w, h))
        pygame.draw.rect(self.screen, C.CYAN, (x, y, w, h), 2)
        t = self.big_font.render(title, True, title_col)
        self.screen.blit(t, (C.SCREEN_W // 2 - t.get_width() // 2, y + 12))
        return x, y

    def _draw_math(self):
        x, y = self._panel(500, 300, "⚡ DOOR CIPHER", C.YELLOW)
        q = self.big_font.render(self.math_question, True, C.WHITE)
        self.screen.blit(q, (C.SCREEN_W // 2 - q.get_width() // 2, y + 80))
        # Input box
        pygame.draw.rect(self.screen, (20, 30, 60), (x + 120, y + 160, 260, 44))
        pygame.draw.rect(self.screen, C.CYAN, (x + 120, y + 160, 260, 44), 2)
        inp = self.big_font.render(self.math_input + ("_" if int(self.anim_tick * 2) % 2 == 0 else " "), True, C.WHITE)
        self.screen.blit(inp, (x + 130, y + 165))
        if self.math_feedback:
            col = C.GREEN if "CORRECT" in self.math_feedback else C.RED
            fb = self.font.render(self.math_feedback, True, col)
            self.screen.blit(fb, (C.SCREEN_W // 2 - fb.get_width() // 2, y + 220))
        hint = self.sm_font.render("Type your answer and press ENTER", True, C.LIGHT_GREY)
        self.screen.blit(hint, (C.SCREEN_W // 2 - hint.get_width() // 2, y + 255))

    def _draw_ttt(self):
        x, y = self._panel(560, 460, "TIC-TAC-TOE", C.CYAN)
        bx, by = C.SCREEN_W // 2 - 130, y + 70
        cell = 86
        # Grid
        for r in range(3):
            for c in range(3):
                cx, cy = bx + c * cell, by + r * cell
                pygame.draw.rect(self.screen, (15, 20, 50), (cx + 2, cy + 2, cell - 4, cell - 4))
                pygame.draw.rect(self.screen, (40, 60, 120), (cx + 2, cy + 2, cell - 4, cell - 4), 2)
                val = self.ttt_board[r][c]
                if val == 1:
                    # X
                    pygame.draw.line(self.screen, C.RED, (cx + 16, cy + 16), (cx + cell - 16, cy + cell - 16), 6)
                    pygame.draw.line(self.screen, C.RED, (cx + cell - 16, cy + 16), (cx + 16, cy + cell - 16), 6)
                elif val == 2:
                    # O
                    pygame.draw.circle(self.screen, C.CYAN, (cx + cell // 2, cy + cell // 2), 28, 6)

        msg = self.font.render(self.ttt_msg, True, C.YELLOW)
        self.screen.blit(msg, (C.SCREEN_W // 2 - msg.get_width() // 2, y + 345))
        leg = self.sm_font.render("You = X (Red)   AXIOM = O (Cyan)", True, C.LIGHT_GREY)
        self.screen.blit(leg, (C.SCREEN_W // 2 - leg.get_width() // 2, y + 375))
        if self.ttt_winner:
            cont = self.sm_font.render("Press ENTER to continue", True, C.GREEN)
            self.screen.blit(cont, (C.SCREEN_W // 2 - cont.get_width() // 2, y + 405))

    def _draw_c4(self):
        x, y = self._panel(660, 520, "CONNECT FOUR", C.YELLOW)
        bx = C.SCREEN_W // 2 - 175
        by = y + 70
        cell_w, cell_h = 50, 50
        pygame.draw.rect(self.screen, (20, 40, 120), (bx - 4, by - 4, 7 * cell_w + 8, 6 * cell_h + 8))
        for r in range(6):
            for c in range(7):
                cx, cy = bx + c * cell_w, by + r * cell_h
                pygame.draw.circle(self.screen, (8, 8, 30), (cx + 25, cy + 25), 20)
                val = self.c4_board[r][c]
                if val == 1:
                    pygame.draw.circle(self.screen, C.RED, (cx + 25, cy + 25), 18)
                    pygame.draw.circle(self.screen, (255, 120, 120), (cx + 19, cy + 19), 6)
                elif val == 2:
                    pygame.draw.circle(self.screen, C.YELLOW, (cx + 25, cy + 25), 18)
                    pygame.draw.circle(self.screen, (255, 255, 150), (cx + 19, cy + 19), 6)
        msg = self.font.render(self.c4_msg, True, C.WHITE)
        self.screen.blit(msg, (C.SCREEN_W // 2 - msg.get_width() // 2, y + 385))
        leg = self.sm_font.render("You = RED   AXIOM = YELLOW   Click column to drop", True, C.LIGHT_GREY)
        self.screen.blit(leg, (C.SCREEN_W // 2 - leg.get_width() // 2, y + 415))
        if self.c4_winner:
            cont = self.sm_font.render("Press ENTER to continue", True, C.GREEN)
            self.screen.blit(cont, (C.SCREEN_W // 2 - cont.get_width() // 2, y + 450))

    def _draw_pattern(self):
        x, y = self._panel(640, 380, "PATTERN LOCK", C.PURPLE)
        # Show sequence display (which color is lit)
        display_y = y + 80
        for i, color_idx in enumerate(self.pattern_seq):
            col = self.pattern_colors[color_idx]
            bx = C.SCREEN_W // 2 - (len(self.pattern_seq) * 35) // 2 + i * 35
            lit = (self.pattern_phase == "show" and i == self.pattern_display_index)
            dim = tuple(max(c // 4, 0) for c in col)
            pygame.draw.rect(self.screen, lit_or_dim(col, dim, lit), (bx, display_y, 28, 28))
            pygame.draw.rect(self.screen, C.WHITE, (bx, display_y, 28, 28), 1)

        # Color buttons
        btn_y = y + 180
        for i in range(5):
            bx = C.SCREEN_W // 2 - 220 + i * 88
            col = self.pattern_colors[i]
            pygame.draw.rect(self.screen, col, (bx, btn_y, 70, 70))
            pygame.draw.rect(self.screen, C.WHITE, (bx, btn_y, 70, 70), 2)

        # Player progress
        prog_y = y + 270
        for i, ci in enumerate(self.pattern_player_seq):
            col = self.pattern_colors[ci]
            bx = C.SCREEN_W // 2 - (len(self.pattern_seq) * 30) // 2 + i * 30
            pygame.draw.rect(self.screen, col, (bx, prog_y, 22, 22))

        msg = self.font.render(self.pattern_msg, True, C.YELLOW)
        self.screen.blit(msg, (C.SCREEN_W // 2 - msg.get_width() // 2, y + 310))

    def _draw_missing(self):
        x, y = self._panel(700, 420, "FIND THE MISSING", C.ORANGE)
        item_y = y + 80
        # Draw 6 items with one hidden
        for i, shape in enumerate(self.missing_items):
            ix = C.SCREEN_W // 2 - 260 + i * 88
            col = self.missing_cols[i]
            if i == self.missing_answer:
                # Hidden — draw question mark
                pygame.draw.rect(self.screen, (30, 30, 30), (ix, item_y, 70, 70))
                pygame.draw.rect(self.screen, C.YELLOW, (ix, item_y, 70, 70), 2)
                q = self.big_font.render("?", True, C.YELLOW)
                self.screen.blit(q, (ix + 35 - q.get_width() // 2, item_y + 18))
            else:
                self._draw_shape(shape, col, ix + 35, item_y + 35, 28)

        # Options
        opt_y = y + 210
        opt_label = self.font.render("Choose the missing shape:", True, C.WHITE)
        self.screen.blit(opt_label, (C.SCREEN_W // 2 - opt_label.get_width() // 2, opt_y - 30))
        for i, opt in enumerate(self.missing_options):
            ox = C.SCREEN_W // 2 - 265 + i * 88
            col = self.missing_cols[i % 6]
            border_col = C.GREEN if self.missing_selected == i else (60, 60, 80)
            pygame.draw.rect(self.screen, (20, 20, 40), (ox, opt_y, 70, 70))
            pygame.draw.rect(self.screen, border_col, (ox, opt_y, 70, 70), 2)
            self._draw_shape(opt, col, ox + 35, opt_y + 35, 24)

        msg = self.sm_font.render(self.missing_msg, True, C.YELLOW)
        self.screen.blit(msg, (C.SCREEN_W // 2 - msg.get_width() // 2, y + 305))

    def _draw_shape(self, shape, color, cx, cy, size):
        if shape == "circle":
            pygame.draw.circle(self.screen, color, (cx, cy), size)
        elif shape == "square":
            pygame.draw.rect(self.screen, color, (cx - size, cy - size, size * 2, size * 2))
        elif shape == "triangle":
            pygame.draw.polygon(self.screen, color, [
                (cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)])
        elif shape == "diamond":
            pygame.draw.polygon(self.screen, color, [
                (cx, cy - size), (cx + size, cy), (cx, cy + size), (cx - size, cy)])
        elif shape == "star":
            pts = []
            for i in range(10):
                r = size if i % 2 == 0 else size // 2
                a = math.radians(i * 36 - 90)
                pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
            pygame.draw.polygon(self.screen, color, pts)
        elif shape == "hexagon":
            pts = [(cx + int(size * math.cos(math.radians(i * 60))),
                    cy + int(size * math.sin(math.radians(i * 60)))) for i in range(6)]
            pygame.draw.polygon(self.screen, color, pts)

    def _draw_power(self):
        x, y = self._panel(640, 500, "POWER GRID", C.CYAN)
        off_x, off_y = C.SCREEN_W // 2 - 320, C.SCREEN_H // 2 - 250

        # Draw connections
        for a, b in self.power_connections:
            na, nb = self.power_nodes[a], self.power_nodes[b]
            col = C.GREEN if na["powered"] and nb["powered"] else C.GREY
            pygame.draw.line(self.screen,
                             col,
                             (na["x"] + off_x, na["y"] + off_y),
                             (nb["x"] + off_x, nb["y"] + off_y), 3)

        # Draw nodes
        for i, node in enumerate(self.power_nodes):
            nx, ny = node["x"] + off_x, node["y"] + off_y
            col = C.GREEN if node["powered"] else C.GREY
            if i == self.power_selected:
                col = C.YELLOW
            pygame.draw.circle(self.screen, col, (nx, ny), 20)
            pygame.draw.circle(self.screen, C.WHITE, (nx, ny), 20, 2)
            if node["powered"]:
                pygame.draw.circle(self.screen, C.CYAN, (nx, ny), 10)
            label = self.sm_font.render(str(i), True, C.WHITE)
            self.screen.blit(label, (nx - 4, ny - 8))

        msg = self.sm_font.render(self.power_msg, True, C.YELLOW)
        self.screen.blit(msg, (C.SCREEN_W // 2 - msg.get_width() // 2, y + 440))


def lit_or_dim(col, dim, lit):
    return col if lit else dim
