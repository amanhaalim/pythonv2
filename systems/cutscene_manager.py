# systems/cutscene_manager.py
import pygame
import math
import constants as C


# All cutscene scripts
CUTSCENES = {
    "intro": [
        {"type": "fade_in", "duration": 1.5},
        {"type": "title_card", "text": "RUST & RUIN\nThe Last Child", "duration": 3.0,
         "bg": (5, 5, 20), "col": (255, 200, 50)},
        {"type": "narration", "text": "Year 2087. The machines rose in silence.", "duration": 3.5},
        {"type": "narration", "text": "They called themselves The Collective.", "duration": 3.0},
        {"type": "narration", "text": "Humanity scattered. Cities burned.", "duration": 3.0},
        {"type": "narration", "text": "But one child survived the slums of New Rust City...", "duration": 3.5},
        {"type": "dialogue", "speaker": "KAI", "text": "Is... is someone there?", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Unit AXIOM-7, reporting. I am... different. I do not serve The Collective.", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "A robot? You're going to hurt me!", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Negative. I want to help you find other survivors. Will you trust me?", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "...I don't have a choice, do I?", "portrait": "player"},
        {"type": "narration", "text": "And so began the journey through the broken world...", "duration": 3.0},
        {"type": "fade_out", "duration": 1.0},
    ],
    "slum_complete": [
        {"type": "fade_in", "duration": 0.8},
        {"type": "dialogue", "speaker": "AXIOM", "text": "You did it! The slum gate is open. I'm detecting life signs to the east.", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "People? Real people?!", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Possibly. The desert lies ahead. Prepare yourself.", "portrait": "robot"},
        {"type": "narration", "text": "The Rusted Slums — cleared.", "duration": 2.0},
        {"type": "fade_out", "duration": 0.8},
    ],
    "desert_complete": [
        {"type": "fade_in", "duration": 0.8},
        {"type": "narration", "text": "The desert heat was merciless. But Kai pressed on.", "duration": 3.0},
        {"type": "dialogue", "speaker": "AXIOM", "text": "There — a coastal settlement! Survivors confirmed!", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "I can hear them! Come on AXIOM!", "portrait": "player"},
        {"type": "narration", "text": "The Scorched Desert — survived.", "duration": 2.0},
        {"type": "fade_out", "duration": 0.8},
    ],
    "beach_complete": [
        {"type": "fade_in", "duration": 0.8},
        {"type": "dialogue", "speaker": "SURVIVOR", "text": "A child! And... a robot? Is it safe?", "portrait": "survivor"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "I am AXIOM-7. Defect unit. I protect the child.", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "You're all alive! I thought I was the last one!", "portrait": "player"},
        {"type": "dialogue", "speaker": "SURVIVOR", "text": "There are more of us. But the robot army commander is near — the Battlefield.", "portrait": "survivor"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "If we destroy the commander, The Collective loses its core directive.", "portrait": "robot"},
        {"type": "narration", "text": "The Crystalline Beach — conquered.", "duration": 2.0},
        {"type": "fade_out", "duration": 0.8},
    ],
    "boss_intro": [
        {"type": "fade_in", "duration": 0.8},
        {"type": "title_card", "text": "BOSS FIGHT\nCOLLECTIVE COMMANDER", "duration": 2.5,
         "bg": (15, 5, 5), "col": (255, 50, 50)},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Warning! Massive combat unit detected. This is the commander!", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "It's huge! How do we fight that?!", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Hit it three times. Each phase it will adapt. Be ready!", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "Right. Let's end this.", "portrait": "player"},
        {"type": "fade_out", "duration": 0.5},
    ],
    "boss_phase2": [
        {"type": "dialogue", "speaker": "AXIOM", "text": "Phase 2! It's getting faster. Watch the missiles!", "portrait": "robot"},
    ],
    "boss_cow_reveal": [
        {"type": "fade_in", "duration": 0.5},
        {"type": "narration", "text": "The robot's chest cracked open...", "duration": 2.5},
        {"type": "dialogue", "speaker": "AXIOM", "text": "...Wait. I'm reading... bovine life signs?!", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "Is that... a COW? Inside the robot?!", "portrait": "player"},
        {"type": "dialogue", "speaker": "???", "text": "MOOOOOO!", "portrait": "cow"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Scanning... The Collective was controlled by cows the entire time. This is unprecedented.", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "I... I don't even know what to say.", "portrait": "player"},
        {"type": "dialogue", "speaker": "???", "text": "...moo.", "portrait": "cow"},
        {"type": "fade_out", "duration": 0.8},
    ],
    "ending": [
        {"type": "fade_in", "duration": 1.0},
        {"type": "narration", "text": "With the Bovine Commander defeated, The Collective shut down.", "duration": 3.5},
        {"type": "narration", "text": "Humanity emerged from hiding, blinking in the sunlight.", "duration": 3.0},
        {"type": "dialogue", "speaker": "KAI", "text": "We did it, AXIOM. We actually did it!", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "Correction: YOU did it. I merely calculated the optimal path.", "portrait": "robot"},
        {"type": "dialogue", "speaker": "KAI", "text": "You're more human than you think.", "portrait": "player"},
        {"type": "dialogue", "speaker": "AXIOM", "text": "...That is the nicest thing anyone has ever said to me.", "portrait": "robot"},
        {"type": "narration", "text": "Then — a light from the sky.", "duration": 2.0},
        {"type": "alien_abduction", "duration": 6.0},
        {"type": "narration", "text": "The cows... were taken home.", "duration": 3.0},
        {"type": "narration", "text": "Some questions are better left unanswered.", "duration": 3.0},
        {"type": "title_card", "text": "THE END\n\nThanks for playing!", "duration": 4.0,
         "bg": (5, 5, 20), "col": (255, 220, 80)},
        {"type": "fade_out", "duration": 1.5},
    ],
}


class CutsceneManager:
    def __init__(self, screen, dialogue_system):
        self.screen = screen
        self.dialogue = dialogue_system
        self.active = False
        self.current_name = None
        self.script = []
        self.step_index = 0
        self.step_timer = 0
        self.callback = None
        self.alpha = 0
        self.fade_surface = pygame.Surface((C.SCREEN_W, C.SCREEN_H))
        self.fade_surface.fill(C.BLACK)
        self.font = pygame.font.SysFont("monospace", 26)
        self.title_font = pygame.font.SysFont("monospace", 46, bold=True)
        self.narr_font = pygame.font.SysFont("monospace", 22)
        self.anim_tick = 0
        self.alien_beam_y = -200
        self.skip_flag = False

    def play(self, name, callback=None):
        if name not in CUTSCENES:
            if callback:
                callback()
            return
        self.current_name = name
        self.script = CUTSCENES[name]
        self.step_index = 0
        self.step_timer = 0
        self.callback = callback
        self.active = True
        self.alpha = 0
        self.anim_tick = 0
        self.skip_flag = False
        self._begin_step()

    def _begin_step(self):
        if self.step_index >= len(self.script):
            self._finish()
            return
        step = self.script[self.step_index]
        self.step_timer = step.get("duration", 0)
        if step["type"] == "dialogue":
            self.dialogue.show_dialogue(step["speaker"], step["text"], step.get("portrait", "player"))
        elif step["type"] in ("fade_in", "fade_out"):
            self.alpha = 255 if step["type"] == "fade_in" else 0

    def _finish(self):
        self.active = False
        if self.callback:
            self.callback()

    def update(self, events, dt):
        if not self.active:
            return
        self.anim_tick += dt

        # Skip keybind
        for ev in events:
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_TAB:
                self._finish()
                return

        step = self.script[self.step_index]
        stype = step["type"]

        if stype == "dialogue":
            self.dialogue.update(events)
            if not self.dialogue.is_active():
                self._advance()

        elif stype in ("narration", "title_card", "alien_abduction"):
            self.step_timer -= dt
            if self.step_timer <= 0:
                self._advance()

        elif stype == "fade_in":
            self.step_timer -= dt
            dur = step.get("duration", 1.0)
            self.alpha = max(0, int(255 * (self.step_timer / dur)))
            if self.step_timer <= 0:
                self.alpha = 0
                self._advance()

        elif stype == "fade_out":
            self.step_timer -= dt
            dur = step.get("duration", 1.0)
            self.alpha = int(255 * (1 - self.step_timer / dur))
            if self.step_timer <= 0:
                self.alpha = 255
                self._advance()

    def _advance(self):
        self.step_index += 1
        self.step_timer = 0
        self._begin_step()

    def draw(self):
        if not self.active:
            return

        step = self.script[self.step_index] if self.step_index < len(self.script) else {}
        stype = step.get("type", "")

        if stype == "title_card":
            self.screen.fill(step.get("bg", (5, 5, 20)))
            col = step.get("col", C.YELLOW)
            lines = step.get("text", "").split("\n")
            total_h = len(lines) * 60
            start_y = C.SCREEN_H // 2 - total_h // 2
            for i, line in enumerate(lines):
                surf = self.title_font.render(line, True, col)
                self.screen.blit(surf, (C.SCREEN_W // 2 - surf.get_width() // 2, start_y + i * 60))
            # Pulse border
            pulse = int(abs(math.sin(self.anim_tick * 2)) * 80) + 80
            pygame.draw.rect(self.screen, (col[0] // 2, col[1] // 2, pulse), (20, 20, C.SCREEN_W - 40, C.SCREEN_H - 40), 3)

        elif stype == "narration":
            self.screen.fill((8, 8, 22))
            txt = step.get("text", "")
            surf = self.narr_font.render(txt, True, C.LIGHT_GREY)
            # Fade in/out based on step timer
            self.screen.blit(surf, (C.SCREEN_W // 2 - surf.get_width() // 2, C.SCREEN_H // 2))
            # Italic line decoration
            pygame.draw.line(self.screen, (60, 60, 100),
                             (C.SCREEN_W // 2 - 200, C.SCREEN_H // 2 - 20),
                             (C.SCREEN_W // 2 + 200, C.SCREEN_H // 2 - 20), 1)
            pygame.draw.line(self.screen, (60, 60, 100),
                             (C.SCREEN_W // 2 - 200, C.SCREEN_H // 2 + 36),
                             (C.SCREEN_W // 2 + 200, C.SCREEN_H // 2 + 36), 1)

        elif stype == "dialogue":
            self.screen.fill((8, 8, 22))
            self.dialogue.draw()

        elif stype == "alien_abduction":
            self._draw_alien_abduction()

        elif stype in ("fade_in", "fade_out"):
            self.screen.fill((8, 8, 22))

        # Fade overlay
        if self.alpha > 0:
            self.fade_surface.set_alpha(self.alpha)
            self.screen.blit(self.fade_surface, (0, 0))

        # Skip hint
        skip = pygame.font.SysFont("monospace", 13).render("[TAB] Skip Cutscene", True, (80, 80, 80))
        self.screen.blit(skip, (C.SCREEN_W - skip.get_width() - 10, 10))

    def _draw_alien_abduction(self):
        """Animated alien beam abducting the cow."""
        self.screen.fill((5, 5, 20))
        t = self.anim_tick

        # Stars
        for i in range(60):
            sx = (i * 127 + int(i * 0.5)) % C.SCREEN_W
            sy = (i * 83) % (C.SCREEN_H // 2)
            pygame.draw.circle(self.screen, C.WHITE, (sx, sy), 1)

        # UFO
        ufo_x = C.SCREEN_W // 2
        ufo_y = 100 + int(math.sin(t * 2) * 15)
        pygame.draw.ellipse(self.screen, (120, 120, 140), (ufo_x - 80, ufo_y - 14, 160, 28))
        pygame.draw.ellipse(self.screen, (180, 180, 220), (ufo_x - 40, ufo_y - 30, 80, 30))
        for i in range(5):
            lx = ufo_x - 60 + i * 30
            col = [(255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 200, 0), (255, 0, 200)][i]
            pygame.draw.circle(self.screen, col, (lx, ufo_y + 10), 5)

        # Beam
        beam_progress = min(t / 3.0, 1.0)
        beam_bottom = ufo_y + 30 + int(beam_progress * (C.SCREEN_H - 200))
        s = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        beam_pts = [(ufo_x - 30, ufo_y + 30), (ufo_x + 30, ufo_y + 30),
                    (ufo_x + 60, beam_bottom), (ufo_x - 60, beam_bottom)]
        pygame.draw.polygon(s, (200, 255, 200, 60), beam_pts)
        self.screen.blit(s, (0, 0))

        # Cow being abducted (rises with beam)
        cow_y = C.SCREEN_H - 200 - int(beam_progress * (C.SCREEN_H - 300))
        cow_x = ufo_x - 25
        pygame.draw.ellipse(self.screen, (220, 210, 200), (cow_x, cow_y, 50, 30))
        pygame.draw.ellipse(self.screen, (50, 50, 50), (cow_x + 6, cow_y + 6, 14, 10))
        pygame.draw.circle(self.screen, (30, 30, 30), (cow_x + 16, cow_y + 12), 3)
        pygame.draw.circle(self.screen, (30, 30, 30), (cow_x + 34, cow_y + 12), 3)
        # Legs
        for lx in [cow_x + 8, cow_x + 16, cow_x + 28, cow_x + 38]:
            pygame.draw.line(self.screen, (200, 190, 180), (lx, cow_y + 28), (lx, cow_y + 44), 4)
        # MOO
        if beam_progress < 0.8:
            moo_font = pygame.font.SysFont("monospace", 18, bold=True)
            moo_surf = moo_font.render("MOO!", True, C.YELLOW)
            self.screen.blit(moo_surf, (cow_x + 50, cow_y - 20))
