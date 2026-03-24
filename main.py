"""
RUST & RUIN: The Last Child — Cinematic Edition
"""

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.renderer   import Renderer
from engine.input      import InputHandler
from engine.physics    import PhysicsEngine
from engine.particles  import ParticleSystem
from engine.screen_fx  import ScreenFX, DynamicLighting, LightSource
from engine.timeline   import TimelineCutscene
from systems.story_engine    import StoryEngine
from systems.level_manager   import LevelManager
from systems.cutscene_scripts import SCRIPTS
from systems.dialogue_system import DialogueSystem
from systems.puzzle_engine   import PuzzleEngine
from systems.ai_system       import AISystem
from game.player         import Player
from game.robot_companion import RobotCompanion
from ui.menu import MainMenu
from ui.hud  import HUD
import constants as C


# Level-specific ambient lights (world coords)
LEVEL_LIGHTS = [
    # Slum — flickering neon lamps along the path
    [LightSource( 350, C.GROUND_Y - 80,  120, (200, 100, 255), 0.9, 0.6),
     LightSource( 900, C.GROUND_Y - 60,  100, (255, 120, 40),  0.7, 0.8),
     LightSource(1500, C.GROUND_Y - 90,  130, (80, 160, 255),  0.8, 0.4),
     LightSource(2000, C.GROUND_Y - 70,  110, (255, 80, 120),  0.7, 0.7)],
    # Desert — warm sun pools
    [LightSource( 600, C.GROUND_Y - 20,  200, (255, 210, 80),  0.5, 0.0),
     LightSource(1400, C.GROUND_Y - 20,  200, (255, 200, 60),  0.5, 0.0),
     LightSource(2100, C.GROUND_Y - 20,  200, (255, 190, 50),  0.5, 0.0)],
    # Beach — lighthouse beam + bioluminescence
    [LightSource( 500, C.GROUND_Y - 30,  180, (140, 220, 255), 0.6, 0.1),
     LightSource(1200, C.GROUND_Y - 40,  150, (80,  255, 200), 0.5, 0.3),
     LightSource(1900, C.GROUND_Y - 30,  160, (140, 220, 255), 0.6, 0.2)],
    # Battlefield — fire pits
    [LightSource( 700, C.GROUND_Y - 20,  160, (255, 100, 20),  1.0, 0.9),
     LightSource(1300, C.GROUND_Y - 20,  140, (255, 80,  10),  0.9, 0.8),
     LightSource(2000, C.GROUND_Y - 20,  180, (255, 120, 30),  1.0, 1.0)],
]

LEVEL_COMPLETE_CUTSCENES = {"slum_complete", "desert_complete", "beach_complete"}


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
        pygame.display.set_caption("RUST & RUIN: The Last Child — Cinematic Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"

        # Core systems
        self.renderer      = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.physics       = PhysicsEngine()
        self.ai_system     = AISystem()
        self.dialogue      = DialogueSystem(self.screen)
        self.puzzle_engine = PuzzleEngine(self.screen, self.ai_system)
        self.story_engine  = StoryEngine()

        # Cinematic systems
        self.particles = ParticleSystem()
        self.fx        = ScreenFX(self.screen)
        self.lighting  = DynamicLighting(self.screen)
        self.timeline  = TimelineCutscene(self.screen, self.dialogue, self.fx, self.particles)

        # Inject into renderer
        self.renderer.particles = self.particles
        self.renderer.lighting  = self.lighting
        self.renderer.fx        = self.fx

        self.level_manager = LevelManager(self.physics, self.ai_system)

        # Game objects
        self.player    = None
        self.companion = None

        # UI
        self.menu = MainMenu(self.screen, self)   # pass self for timeline control
        self.hud  = HUD(self.screen)

        self.delta_time = 0.0
        self.total_time = 0.0

        # Particle footstep timer
        self._footstep_timer = 0.0

    # ── Game init ─────────────────────────────────────────────────────────────
    def new_game(self):
        self.player    = Player(100, C.GROUND_Y - 64)
        self.companion = RobotCompanion(160, C.GROUND_Y - 64, self.dialogue, self.story_engine)
        self.level_manager.load_level(0, self.player, self.companion)
        self.story_engine.reset()
        self._setup_level_fx(0)
        self._play_cutscene("intro")

    def _setup_level_fx(self, idx):
        self.fx.current_level = idx
        self.fx._grade_alpha = 0.0
        self.lighting.set_darkness(idx)
        self.lighting.clear_sources()
        for src in LEVEL_LIGHTS[idx % len(LEVEL_LIGHTS)]:
            # Clone so original list stays pristine
            import copy
            self.lighting.add_source(copy.copy(src))

    def start_playing(self):
        self.state = "playing"

    def _after_level_cutscene(self):
        next_idx = self.level_manager.current_level_index + 1
        self.level_manager.advance_level()
        if next_idx < 4:
            self.level_manager.load_level(next_idx, self.player, self.companion)
            self._setup_level_fx(next_idx)
        self.state = "playing"

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_events(self):
        events = pygame.event.get()
        for ev in events:
            if ev.type == pygame.QUIT:
                self.running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    elif self.state == "menu":
                        self.running = False
        return events

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, events):
        dt = self.delta_time
        keys = pygame.key.get_pressed()
        self.input_handler.update(keys, events)

        just_pressed = {ev.key for ev in events if ev.type == pygame.KEYDOWN}

        # Always update FX
        self.fx.update(dt)
        self.particles.update(dt)
        self.lighting.update(dt)

        if self.state == "menu":
            result = self.menu.update(events)
            if result == "new_game":
                self.new_game()
            elif result == "quit":
                self.running = False

        elif self.state == "cutscene":
            self.timeline.update(events, dt)

        elif self.state == "puzzle":
            result = self.puzzle_engine.update(events)
            if result == "complete":
                self.state = "playing"
                self.level_manager.on_puzzle_complete(self.player, self.companion, self.story_engine)
                cs = self.level_manager.get_pending_cutscene()
                if cs:
                    self._play_cutscene(cs)
                # Particle burst + shake for puzzle complete
                if self.player:
                    self.particles.emit_explosion(
                        self.player.x + 14,
                        self.player.y)
                    self.fx.add_trauma(0.25)
            elif result == "close":
                self.state = "playing"

        elif self.state == "playing":
            if self.player and self.level_manager.current_level:
                lv = self.level_manager.current_level

                self.player.handle_input(self.input_handler)
                self.companion.update(dt, self.player, lv)

                import levels.base_level as bl
                bl._JUST_E = (pygame.K_e in just_pressed or pygame.K_RETURN in just_pressed)

                trigger = self.level_manager.update(self.player, self.companion, dt)

                # ── Particle emission ────────────────────────────────────────
                # Footsteps
                if self.player.on_ground and abs(self.player.vx) > 30:
                    self._footstep_timer -= dt
                    if self._footstep_timer <= 0:
                        self._footstep_timer = 0.22
                        self.particles.emit_footstep(
                            self.player.x + 14, self.player.y + 46)

                # Landing
                if self.player._land_emit:
                    self.particles.emit("dust", self.player.x + 14,
                                        self.player.y + 46, count=8)
                    self.fx.add_trauma(0.08)

                # Hit particles
                if hasattr(self.player, '_took_hit') and self.player._took_hit:
                    self.particles.emit_hit(self.player.x + 14, self.player.y + 20)
                    self.fx.add_trauma(0.35)
                    self.player._took_hit = False

                # Enemy death particles
                for enemy in lv.enemies:
                    if hasattr(enemy, '_just_died') and enemy._just_died:
                        self.particles.emit_explosion(enemy.x + 16, enemy.y + 16)
                        self.fx.add_trauma(0.2)
                        enemy._just_died = False

                # ── Trigger routing ──────────────────────────────────────────
                if trigger == "puzzle":
                    pt = self.level_manager.get_puzzle_type()
                    self.puzzle_engine.start(pt)
                    self.state = "puzzle"

                elif trigger == "cutscene":
                    cs = self.level_manager.get_pending_cutscene()
                    if cs:
                        self._play_cutscene(cs)

                elif trigger == "next_level":
                    next_idx = self.level_manager.current_level_index + 1
                    if next_idx >= 4:
                        self._play_cutscene("ending")
                    else:
                        self.level_manager.advance_level()
                        self.level_manager.load_level(next_idx, self.player, self.companion)
                        self._setup_level_fx(next_idx)

                elif trigger == "boss":
                    self._play_cutscene("boss_intro")

                self.dialogue.update(events)
                self.hud.update(self.player, self.level_manager)

        elif self.state == "credits":
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    self.state = "menu"

    # ── Cutscene routing ──────────────────────────────────────────────────────
    def _play_cutscene(self, name, after=None):
        self.state = "cutscene"

        if name in LEVEL_COMPLETE_CUTSCENES:
            callback = self._after_level_cutscene
        elif name == "boss_cow_reveal":
            def callback():
                self._play_cutscene("ending")
        elif name == "ending":
            callback = after if after else lambda: self.set_state("credits")
        elif name == "boss_intro":
            callback = self.start_playing
        else:
            callback = after if after else self.start_playing

        script = SCRIPTS.get(name)
        if script is None:
            callback()
            return
        self.timeline.load(script, callback=callback)

    # Also accept calls from menu (cutscene viewer)
    def play(self, name, callback=None):
        """Called by MainMenu for cutscene viewer."""
        self.state = "cutscene"
        script = SCRIPTS.get(name)
        if script is None:
            if callback:
                callback()
            return
        cb = callback if callback else lambda: self.set_state("menu")
        self.timeline.load(script, callback=cb)

    def set_state(self, s):
        self.state = s

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self):
        self.screen.fill(C.BLACK)

        if self.state == "menu":
            self.menu.draw()

        elif self.state == "cutscene":
            self.timeline.draw()

        elif self.state == "puzzle":
            if self.level_manager.current_level:
                self.renderer.draw_level(
                    self.level_manager.current_level, self.player, self.companion)
            self.puzzle_engine.draw()

        elif self.state == "playing":
            if self.level_manager.current_level:
                self.renderer.draw_level(
                    self.level_manager.current_level, self.player, self.companion)
                self.hud.draw()
                self.dialogue.draw()

        elif self.state == "credits":
            self._draw_credits()

        pygame.display.flip()

    def _draw_credits(self):
        self.screen.fill((4, 4, 18))
        t = self.total_time
        cx = C.SCREEN_W // 2

        # Animated star field
        for i in range(80):
            sx = (i * 127) % C.SCREEN_W
            sy = (i * 83) % C.SCREEN_H
            tw = 0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(t * 40 + i * 17).x
            alpha = int(tw * 180 + 40)
            s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 210, 255, alpha), (1, 1), 1)
            self.screen.blit(s, (sx, sy))

        lines = [
            ("RUST & RUIN: The Last Child", 44, (255, 210, 60)),
            ("",                            22, (200, 200, 220)),
            ("You saved humanity.",          22, (200, 200, 220)),
            ("The robots are gone.",         22, (200, 200, 220)),
            ("The cows… remain suspicious.", 22, (180, 200, 255)),
            ("",                             22, (200, 200, 220)),
            ("Thanks for playing!",          26, (255, 255, 255)),
            ("",                             22, (200, 200, 220)),
            ("Press any key to return.",     16, (100, 110, 140)),
        ]
        y = 160
        for text, size, col in lines:
            if text:
                f = pygame.font.SysFont("monospace", size, bold=(size > 22))
                surf = f.render(text, True, col)
                self.screen.blit(surf, (cx - surf.get_width() // 2, y))
            y += size + 14

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        while self.running:
            self.delta_time = min(self.clock.tick(C.FPS) / 1000.0, 0.05)
            self.total_time += self.delta_time
            events = self.handle_events()
            self.update(events)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
