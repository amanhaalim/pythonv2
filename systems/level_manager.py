# systems/level_manager.py
from levels.slum import SlumLevel
from levels.desert import DesertLevel
from levels.beach import BeachLevel
from levels.battlefield import BattlefieldLevel


LEVEL_CLASSES = [SlumLevel, DesertLevel, BeachLevel, BattlefieldLevel]

# Cutscene names that mean "level complete, load next level after this"
LEVEL_COMPLETE_CUTSCENES = {"slum_complete", "desert_complete", "beach_complete"}


class LevelManager:
    def __init__(self, physics, ai_system):
        self.physics = physics
        self.ai_system = ai_system
        self.current_level = None
        self.current_level_index = -1
        self._pending_cutscene = None
        self._pending_puzzle = None
        self._next_level_ready = False
        self._transitioning = False  # prevent double-triggers

    def load_level(self, index, player, companion):
        self.current_level_index = index
        cls = LEVEL_CLASSES[index]
        self.current_level = cls()
        self.current_level.setup(player, companion)
        self._pending_cutscene = None
        self._pending_puzzle = None
        self._next_level_ready = False
        self._transitioning = False
        companion.current_level_name = self.current_level.name

    def update(self, player, companion, dt):
        if not self.current_level or self._transitioning:
            return None

        level = self.current_level
        player.update(dt)

        # Enemy updates + collision
        for enemy in level.enemies:
            enemy.update(dt, player, level.platforms)
            if enemy.alive and enemy.check_player_collision(player):
                player.take_damage(enemy.damage)

        # Boss update
        if level.boss and level.boss.alive:
            level.boss.update(dt, player, level.platforms)
            if level.boss.check_player_collision(player):
                player.take_damage(20)
            for m in list(level.boss.missiles):
                mx, my = m["x"], m["y"]
                if (player.x < mx < player.x + player.width and
                        player.y < my < player.y + player.height):
                    player.take_damage(8)

        # Collectibles
        for item in level.collectibles:
            if not item.collected:
                if abs(item.x - player.x) < 24 and abs(item.y - player.y) < 24:
                    item.collected = True
                    player.score += 10

        # Physics — pass level width to clamp player on both sides
        self.physics.update(player, level.platforms, level.width)

        # Level logic / interactables
        trigger = level.update(player, companion, dt)

        # Player attack (X or Z near enemy / boss)
        import pygame
        keys = pygame.key.get_pressed()
        if keys[pygame.K_x] or keys[pygame.K_z]:
            for enemy in level.enemies:
                if (enemy.alive and
                        abs(enemy.x - player.x) < 60 and
                        abs(enemy.y - player.y) < 50):
                    enemy.take_hit()
            if level.boss and level.boss.alive:
                if (abs(level.boss.x - player.x) < 80 and
                        abs(level.boss.y - player.y) < 80):
                    level.boss.take_hit()
                    if not level.boss.alive or level.boss.reveal_cow:
                        if not self._transitioning:
                            self._transitioning = True
                            self._pending_cutscene = "boss_cow_reveal"
                            return "cutscene"

        if trigger == "puzzle":
            self._pending_puzzle = level.get_next_puzzle()
            return "puzzle"
        elif trigger == "cutscene":
            cs = level.get_pending_cutscene()
            if cs:
                self._pending_cutscene = cs
                if cs in LEVEL_COMPLETE_CUTSCENES:
                    self._next_level_ready = True
                self._transitioning = True
                return "cutscene"
        elif trigger == "next_level":
            return "next_level"
        elif trigger == "boss":
            return "boss"

        return None

    def get_pending_cutscene(self):
        cs = self._pending_cutscene
        self._pending_cutscene = None
        return cs

    def get_puzzle_type(self):
        pt = self._pending_puzzle
        self._pending_puzzle = None
        return pt

    def on_puzzle_complete(self, player, companion, story_engine):
        if self.current_level:
            self.current_level.on_puzzle_complete(player, companion, story_engine)

    def advance_level(self):
        """Reset transition lock after cutscene ends."""
        self._next_level_ready = False
        self._transitioning = False
