"""
RUST & RUIN: The Last Child
A post-apocalyptic 2D story-driven puzzle adventure game.
"""

import pygame
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.renderer import Renderer
from engine.input import InputHandler
from engine.physics import PhysicsEngine
from systems.story_engine import StoryEngine
from systems.level_manager import LevelManager
from systems.cutscene_manager import CutsceneManager
from systems.dialogue_system import DialogueSystem
from systems.puzzle_engine import PuzzleEngine
from systems.ai_system import AISystem
from game.player import Player
from game.robot_companion import RobotCompanion
from ui.menu import MainMenu
from ui.hud import HUD
import constants as C


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((C.SCREEN_W, C.SCREEN_H))
        pygame.display.set_caption("RUST & RUIN: The Last Child")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = "menu"  # menu, playing, cutscene, puzzle, game_over, credits

        # Core systems
        self.renderer = Renderer(self.screen)
        self.input_handler = InputHandler()
        self.physics = PhysicsEngine()
        self.ai_system = AISystem()
        self.dialogue = DialogueSystem(self.screen)
        self.puzzle_engine = PuzzleEngine(self.screen, self.ai_system)
        self.story_engine = StoryEngine()
        self.cutscene_manager = CutsceneManager(self.screen, self.dialogue)
        self.level_manager = LevelManager(self.physics, self.ai_system)

        # Game objects
        self.player = None
        self.companion = None

        # UI
        self.menu = MainMenu(self.screen, self.cutscene_manager)
        self.hud = HUD(self.screen)

        # Timers
        self.delta_time = 0
        self.total_time = 0

    def new_game(self):
        """Initialize a new game session."""
        self.player = Player(100, C.GROUND_Y - 64)
        self.companion = RobotCompanion(160, C.GROUND_Y - 64, self.dialogue, self.story_engine)
        self.level_manager.load_level(0, self.player, self.companion)
        self.story_engine.reset()
        self.state = "cutscene"
        self.cutscene_manager.play("intro", callback=self.start_playing)

    def start_playing(self):
        self.state = "playing"

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    elif self.state == "menu":
                        self.running = False
        return events

    def update(self, events):
        keys = pygame.key.get_pressed()
        self.input_handler.update(keys, events)

        # Build a set of just-pressed keys from events this frame
        just_pressed_keys = set()
        for ev in events:
            if ev.type == pygame.KEYDOWN:
                just_pressed_keys.add(ev.key)

        if self.state == "menu":
            result = self.menu.update(events)
            if result == "new_game":
                self.new_game()
            elif result == "quit":
                self.running = False

        elif self.state == "cutscene":
            self.cutscene_manager.update(events, self.delta_time)

        elif self.state == "puzzle":
            result = self.puzzle_engine.update(events)
            if result == "complete":
                self.state = "playing"
                self.level_manager.on_puzzle_complete(self.player, self.companion, self.story_engine)
                # Check if we should trigger next cutscene
                cs = self.level_manager.get_pending_cutscene()
                if cs:
                    self.state = "cutscene"
                    self.cutscene_manager.play(cs, callback=self.start_playing)
            elif result == "close":
                self.state = "playing"

        elif self.state == "playing":
            if self.player and self.level_manager.current_level:
                # Input
                self.player.handle_input(self.input_handler)
                self.companion.update(self.delta_time, self.player, self.level_manager.current_level)
                # Physics
                self.physics.update(self.player, self.level_manager.current_level.platforms)
                # Pass just_pressed info to level via a module-level flag
                import levels.base_level as bl
                bl._JUST_E = (pygame.K_e in just_pressed_keys or pygame.K_RETURN in just_pressed_keys)
                # Level
                trigger = self.level_manager.update(self.player, self.companion, self.delta_time)
                if trigger == "puzzle":
                    pt = self.level_manager.get_puzzle_type()
                    self.puzzle_engine.start(pt)
                    self.state = "puzzle"
                elif trigger == "cutscene":
                    cs = self.level_manager.get_pending_cutscene()
                    if cs:
                        self.state = "cutscene"
                        self.cutscene_manager.play(cs, callback=self.start_playing)
                elif trigger == "next_level":
                    next_idx = self.level_manager.current_level_index + 1
                    if next_idx >= 4:
                        self.state = "cutscene"
                        self.cutscene_manager.play("ending", callback=lambda: self.set_state("credits"))
                    else:
                        self.level_manager.load_level(next_idx, self.player, self.companion)
                elif trigger == "boss":
                    self.state = "cutscene"
                    self.cutscene_manager.play("boss_intro", callback=self.start_playing)
                # Dialogue
                self.dialogue.update(events)
                self.hud.update(self.player, self.level_manager)

        elif self.state == "credits":
            for ev in events:
                if ev.type == pygame.KEYDOWN:
                    self.state = "menu"

    def set_state(self, s):
        self.state = s

    def draw(self):
        self.screen.fill(C.BLACK)

        if self.state == "menu":
            self.menu.draw()
        elif self.state == "cutscene":
            self.cutscene_manager.draw()
        elif self.state == "puzzle":
            if self.level_manager.current_level:
                self.renderer.draw_level(self.level_manager.current_level, self.player, self.companion)
            self.puzzle_engine.draw()
        elif self.state == "playing":
            if self.level_manager.current_level:
                self.renderer.draw_level(self.level_manager.current_level, self.player, self.companion)
                self.hud.draw()
                self.dialogue.draw()
        elif self.state == "credits":
            self.draw_credits()

        pygame.display.flip()

    def draw_credits(self):
        self.screen.fill((5, 5, 20))
        font_big = pygame.font.SysFont("monospace", 36, bold=True)
        font = pygame.font.SysFont("monospace", 20)
        lines = [
            "RUST & RUIN: The Last Child",
            "",
            "You saved humanity.",
            "The robots are gone.",
            "The cows... remain suspicious.",
            "",
            "Thanks for playing!",
            "",
            "Press any key to return to menu.",
        ]
        y = 180
        for line in lines:
            col = (255, 200, 50) if y == 180 else (200, 200, 220)
            f = font_big if y == 180 else font
            surf = f.render(line, True, col)
            self.screen.blit(surf, (C.SCREEN_W // 2 - surf.get_width() // 2, y))
            y += 44

    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(C.FPS) / 1000.0
            self.delta_time = min(self.delta_time, 0.05)
            self.total_time += self.delta_time
            events = self.handle_events()
            self.update(events)
            self.draw()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
