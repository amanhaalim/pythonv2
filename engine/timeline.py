# engine/timeline.py — Timeline-based cutscene engine
# Supports: camera_move, fade, title_card, narration, dialogue, shake,
#           light_change, particle_burst, sound_trigger, wait
import pygame
import math
import constants as C


def _lerp(a, b, t):
    return a + (b - a) * t

def _ease_in_out(t):
    return t * t * (3 - 2 * t)


class TimelineEvent:
    """One keyframe event on the timeline."""
    def __init__(self, start, duration, etype, **kwargs):
        self.start = float(start)
        self.duration = float(duration)
        self.end = self.start + self.duration
        self.etype = etype
        self.data = kwargs
        self.done = False


class TimelineCutscene:
    """
    A cinematic timeline.  Events fire at absolute timestamps.
    Camera moves, fades, dialogue, shakes, light changes — all keyframed.
    """

    def __init__(self, screen, dialogue_system, screen_fx, particles):
        self.screen = screen
        self.dialogue = dialogue_system
        self.fx = screen_fx
        self.particles = particles
        self.active = False
        self.time = 0.0
        self.total_duration = 0.0
        self.events = []
        self._fired = set()
        self._callback = None
        self.skip_requested = False

        # Camera state (world coords)
        self.cam_x = 0.0
        self.cam_y = 0.0
        self._cam_start = (0.0, 0.0)
        self._cam_target = (0.0, 0.0)
        self._cam_t_start = 0.0
        self._cam_t_dur = 0.0
        self._cam_moving = False

        # Fade state
        self._fade_alpha = 0
        self._fade_surf = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self._fade_surf.fill((0, 0, 0))
        self._fade_dir = 0   # 1=fade in (to black), -1=fade out (from black)
        self._fade_start = 0.0
        self._fade_dur = 1.0

        # Narration / title card
        self._narr_text = ""
        self._narr_timer = 0.0
        self._narr_alpha = 0
        self._title_text = ""
        self._title_timer = 0.0
        self._title_col = C.YELLOW
        self._title_bg = (5, 5, 20)

        self._narr_font = pygame.font.SysFont("monospace", 24, bold=False)
        self._title_font = pygame.font.SysFont("monospace", 52, bold=True)
        self._sub_font = pygame.font.SysFont("monospace", 18)

        # alien anim
        self._alien_active = False
        self._alien_timer = 0.0

    # ── Building ──────────────────────────────────────────────────────────────
    def load(self, events_list, callback=None):
        self.events = [TimelineEvent(**e) for e in events_list]
        self.total_duration = max((e.end for e in self.events), default=0.0)
        self._callback = callback
        self.time = 0.0
        self._fired = set()
        self.active = True
        self.skip_requested = False
        self._narr_text = ""
        self._narr_alpha = 0
        self._title_text = ""
        self._alien_active = False

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, events_pygame, dt):
        if not self.active:
            return

        for ev in events_pygame:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_TAB:
                self.skip_requested = True

        if self.skip_requested:
            self._finish()
            return

        self.time += dt

        # Fire events
        for i, ev in enumerate(self.events):
            if i in self._fired:
                continue
            if self.time >= ev.start:
                self._fire(ev)
                self._fired.add(i)

        # Update continuous effects
        self._update_fade(dt)
        self._update_camera(dt)
        self._update_narration(dt)
        self._update_title(dt)

        # Dialogue advance
        self.dialogue.update(events_pygame)

        if self.time >= self.total_duration:
            # Wait for dialogue to finish
            if not self.dialogue.is_active():
                self._finish()

    def _fire(self, ev):
        d = ev.data
        t = ev.etype

        if t == "fade_in":        # black → visible
            self._start_fade(-1, ev.duration)
        elif t == "fade_out":     # visible → black
            self._start_fade(1, ev.duration)
        elif t == "camera_move":
            self._start_camera_move(d["tx"], d["ty"], ev.duration)
        elif t == "shake":
            self.fx.add_trauma(d.get("intensity", 0.4))
        elif t == "flash":
            self.fx.flash(d.get("color", (255,255,255)), d.get("dur", 0.12))
        elif t == "narration":
            self._show_narration(d["text"], ev.duration)
        elif t == "title_card":
            self._show_title(d["text"], ev.duration,
                             d.get("col", C.YELLOW), d.get("bg", (5,5,20)))
        elif t == "dialogue":
            self.dialogue.show_dialogue(d["speaker"], d["text"], d.get("portrait","player"))
        elif t == "particle_burst":
            self.particles.emit_explosion(d["x"], d["y"])
        elif t == "alien_abduction":
            self._alien_active = True
            self._alien_timer = 0.0
        elif t == "clear_narration":
            self._narr_text = ""
            self._title_text = ""

    # ── Fade ─────────────────────────────────────────────────────────────────
    def _start_fade(self, direction, duration):
        self._fade_dir = direction
        self._fade_start = self.time
        self._fade_dur = max(0.01, duration)
        self._fade_alpha = 255 if direction == -1 else 0

    def _update_fade(self, dt):
        if self._fade_dir == 0:
            return
        elapsed = self.time - self._fade_start
        t = min(elapsed / self._fade_dur, 1.0)
        et = _ease_in_out(t)
        if self._fade_dir == -1:   # fade in → go from 255→0
            self._fade_alpha = int(255 * (1.0 - et))
        else:                       # fade out → go from 0→255
            self._fade_alpha = int(255 * et)
        if t >= 1.0:
            self._fade_dir = 0

    # ── Camera ───────────────────────────────────────────────────────────────
    def _start_camera_move(self, tx, ty, dur):
        self._cam_start = (self.cam_x, self.cam_y)
        self._cam_target = (float(tx), float(ty))
        self._cam_t_start = self.time
        self._cam_t_dur = max(0.01, dur)
        self._cam_moving = True

    def _update_camera(self, dt):
        if not self._cam_moving:
            return
        elapsed = self.time - self._cam_t_start
        t = min(elapsed / self._cam_t_dur, 1.0)
        et = _ease_in_out(t)
        self.cam_x = _lerp(self._cam_start[0], self._cam_target[0], et)
        self.cam_y = _lerp(self._cam_start[1], self._cam_target[1], et)
        if t >= 1.0:
            self._cam_moving = False

    # ── Narration ────────────────────────────────────────────────────────────
    def _show_narration(self, text, duration):
        self._narr_text = text
        self._narr_timer = duration
        self._narr_alpha = 0

    def _update_narration(self, dt):
        if not self._narr_text:
            return
        self._narr_timer -= dt
        if self._narr_timer > 0.5:
            self._narr_alpha = min(255, self._narr_alpha + int(dt * 400))
        else:
            self._narr_alpha = max(0, self._narr_alpha - int(dt * 400))
        if self._narr_timer <= 0:
            self._narr_text = ""

    # ── Title Card ────────────────────────────────────────────────────────────
    def _show_title(self, text, duration, col, bg):
        self._title_text = text
        self._title_timer = duration
        self._title_col = col
        self._title_bg = bg

    def _update_title(self, dt):
        if not self._title_text:
            return
        self._title_timer -= dt
        if self._title_timer <= 0:
            self._title_text = ""

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self):
        if not self.active:
            return

        # Background
        if self._title_text:
            self.screen.fill(self._title_bg)
            self._draw_title()
        elif self._alien_active:
            self._draw_alien()
        else:
            self.screen.fill((8, 8, 22))

        # Narration
        if self._narr_text:
            self._draw_narration()

        # Dialogue
        if self.dialogue.is_active():
            self.dialogue.draw()

        # Fade overlay
        if self._fade_alpha > 0:
            self._fade_surf.set_alpha(self._fade_alpha)
            self.screen.blit(self._fade_surf, (0, 0))

        # Skip hint
        hint = self._sub_font.render("[TAB] Skip", True, (70, 70, 70))
        self.screen.blit(hint, (C.SCREEN_W - hint.get_width() - 12, 10))

    def _draw_narration(self):
        words = self._narr_text.split(" ")
        lines, line = [], ""
        for w in words:
            test = line + w + " "
            if self._narr_font.size(test)[0] > C.SCREEN_W - 200:
                lines.append(line.rstrip())
                line = w + " "
            else:
                line = test
        if line:
            lines.append(line.rstrip())

        total_h = len(lines) * 34
        y0 = C.SCREEN_H // 2 - total_h // 2

        # Box
        box_w = C.SCREEN_W - 160
        box_h = total_h + 30
        box_x = 80
        box_y = y0 - 15
        s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        s.fill((0, 0, 0, int(self._narr_alpha * 0.7)))
        self.screen.blit(s, (box_x, box_y))
        # Decorative lines
        a = self._narr_alpha
        pygame.draw.line(self.screen, (80, 80, 120, a),
                         (box_x + 20, box_y), (box_x + box_w - 20, box_y), 1)
        pygame.draw.line(self.screen, (80, 80, 120, a),
                         (box_x + 20, box_y + box_h), (box_x + box_w - 20, box_y + box_h), 1)
        for i, l in enumerate(lines):
            surf = self._narr_font.render(l, True, (220, 215, 230))
            surf.set_alpha(self._narr_alpha)
            self.screen.blit(surf, (C.SCREEN_W // 2 - surf.get_width() // 2, y0 + i * 34))

    def _draw_title(self):
        t = self._title_timer
        # Pulse
        pulse = abs(math.sin(t * 2.5)) * 0.3 + 0.7
        col = tuple(min(255, int(c * pulse)) for c in self._title_col)
        lines = self._title_text.split("\n")
        total_h = len(lines) * 68
        y0 = C.SCREEN_H // 2 - total_h // 2
        for i, ln in enumerate(lines):
            size = 52 if i == 0 else 28
            font = pygame.font.SysFont("monospace", size, bold=True)
            surf = font.render(ln, True, col)
            self.screen.blit(surf, (C.SCREEN_W // 2 - surf.get_width() // 2, y0 + i * 68))
        # Border pulse
        bw = int(pulse * 60)
        pygame.draw.rect(self.screen, col, (20, 20, C.SCREEN_W - 40, C.SCREEN_H - 40), 3)

    def _draw_alien(self):
        self._alien_timer += 1 / 60
        t = self._alien_timer
        self.screen.fill((5, 5, 20))
        # Stars
        for i in range(80):
            sx = (i * 127 + int(i * 0.7)) % C.SCREEN_W
            sy = (i * 83) % (C.SCREEN_H // 2)
            pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), 1 if i % 3 else 2)
        # UFO
        ux, uy = C.SCREEN_W // 2, 90 + int(math.sin(t * 1.8) * 12)
        pygame.draw.ellipse(self.screen, (100, 110, 140), (ux - 90, uy - 16, 180, 32))
        pygame.draw.ellipse(self.screen, (160, 180, 220), (ux - 48, uy - 32, 96, 34))
        for i, cx2 in enumerate(range(ux - 60, ux + 70, 28)):
            col2 = [(255,0,0),(0,255,0),(0,120,255),(255,200,0),(255,0,200)][i % 5]
            pygame.draw.circle(self.screen, col2, (cx2, uy + 10), 5)
        # Beam
        prog = min(t / 3.0, 1.0)
        bb = uy + 32 + int(prog * (C.SCREEN_H - 230))
        bs = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        beam_alpha = int(80 + math.sin(t * 8) * 30)
        pygame.draw.polygon(bs, (180, 255, 180, beam_alpha),
                            [(ux-30, uy+32),(ux+30, uy+32),(ux+70, bb),(ux-70, bb)])
        self.screen.blit(bs, (0, 0))
        # Cow
        cy2 = C.SCREEN_H - 220 - int(prog * (C.SCREEN_H - 300))
        cx2 = ux - 28
        pygame.draw.ellipse(self.screen, (220, 210, 200), (cx2, cy2, 56, 32))
        pygame.draw.ellipse(self.screen, (50, 50, 50), (cx2+8, cy2+8, 14, 10))
        pygame.draw.circle(self.screen, (30,30,30), (cx2+18, cy2+14), 3)
        pygame.draw.circle(self.screen, (30,30,30), (cx2+38, cy2+14), 3)
        for lx in [cx2+8, cx2+18, cx2+32, cx2+42]:
            pygame.draw.line(self.screen, (200,190,180), (lx, cy2+30), (lx, cy2+48), 4)
        if prog < 0.85:
            mf = pygame.font.SysFont("monospace", 18, bold=True)
            ms = mf.render("MOO!", True, C.YELLOW)
            self.screen.blit(ms, (cx2 + 58, cy2 - 22))

    def _finish(self):
        self.active = False
        self._narr_text = ""
        self._title_text = ""
        self._alien_active = False
        self._fade_alpha = 0
        if self._callback:
            self._callback()
