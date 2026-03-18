# levels/base_level.py
import pygame
import constants as C

# Module-level flag set by main.py each frame
_JUST_E = False


class Platform:
    def __init__(self, x, y, w, h=20):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class Collectible:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.collected = False


class Interactable:
    """A puzzle trigger or story trigger in the world."""
    def __init__(self, x, y, w, h, itype, label="[E] Interact"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.itype = itype  # "puzzle", "story", "exit"
        self.label = label
        self.activated = False
        self.visible = True
        self.puzzle_type = None
        self.anim_tick = 0

    def draw(self, screen, sx, sy):
        if not self.visible:
            return
        self.anim_tick += 0.05
        import math
        bob = int(math.sin(self.anim_tick * 4) * 4)
        if self.itype == "puzzle":
            col = (200, 180, 50) if not self.activated else (60, 60, 60)
            pygame.draw.rect(screen, col, (sx, sy + bob, self.w, self.h))
            pygame.draw.rect(screen, C.YELLOW, (sx, sy + bob, self.w, self.h), 2)
            font = pygame.font.SysFont("monospace", 11, bold=True)
            t = font.render("?", True, C.BLACK)
            screen.blit(t, (sx + self.w // 2 - 4, sy + self.h // 2 - 8 + bob))
        elif self.itype == "exit":
            col = (50, 200, 80) if not self.activated else (60, 60, 60)
            pygame.draw.rect(screen, col, (sx, sy, self.w, self.h))
            pygame.draw.rect(screen, C.GREEN, (sx, sy, self.w, self.h), 2)
            font = pygame.font.SysFont("monospace", 11, bold=True)
            t = font.render("EXIT", True, C.WHITE)
            screen.blit(t, (sx + self.w // 2 - t.get_width() // 2, sy + self.h // 2 - 8))
        elif self.itype == "story":
            col = (50, 100, 200)
            pygame.draw.rect(screen, col, (sx, sy + bob, self.w, self.h))
            pygame.draw.rect(screen, C.CYAN, (sx, sy + bob, self.w, self.h), 2)

        if not self.activated:
            lbl_font = pygame.font.SysFont("monospace", 11)
            lbl = lbl_font.render(self.label, True, C.WHITE)
            screen.blit(lbl, (sx + self.w // 2 - lbl.get_width() // 2, sy - 18 + bob))

    def player_nearby(self, player):
        return (abs(player.x - self.x) < self.w + 30 and
                abs(player.y - self.y) < self.h + 30)


class BaseLevel:
    name = "level"
    level_index = 0
    width = 3200

    def __init__(self):
        self.platforms = []
        self.enemies = []
        self.collectibles = []
        self.interactables = []
        self.boss = None
        self.puzzles_queue = []
        self._pending_cutscene = None
        self._trigger = None
        self.puzzles_solved = 0
        self.puzzles_needed = 2
        self.level_complete = False
        self.exit_unlocked = False
        self.companion_hint_given = False

    def setup(self, player, companion):
        """Override to build the level."""
        pass

    def update(self, player, companion, dt):
        """Check triggers. Return 'puzzle'/'cutscene'/'next_level'/None."""
        return self._check_triggers(player, companion, dt)

    def _check_triggers(self, player, companion, dt):
        import levels.base_level as bl
        just_e = bl._JUST_E

        for obj in self.interactables:
            if obj.activated or not obj.visible:
                continue
            if obj.player_nearby(player):
                if obj.itype == "puzzle" and just_e:
                    obj.activated = True
                    return "puzzle"
                elif obj.itype == "exit" and self.exit_unlocked and just_e:
                    obj.activated = True
                    self._pending_cutscene = self.name + "_complete"
                    return "cutscene"
                elif obj.itype == "story" and just_e:
                    obj.activated = True
                    self._pending_cutscene = obj.puzzle_type
                    return "cutscene"

        return None

    def on_puzzle_complete(self, player, companion, story_engine):
        self.puzzles_solved += 1
        player.puzzles_solved += 1
        player.score += 50
        if self.puzzles_solved >= self.puzzles_needed:
            self.exit_unlocked = True
            # Unlock exit door
            for obj in self.interactables:
                if obj.itype == "exit":
                    obj.activated = False  # re-enable
            companion.say("The exit is now open! Head to the green door.")

    def get_next_puzzle(self):
        if self.puzzles_queue:
            return self.puzzles_queue.pop(0)
        return "math"

    def get_pending_cutscene(self):
        cs = self._pending_cutscene
        self._pending_cutscene = None
        return cs

    def _make_ground(self, y=None):
        if y is None:
            y = C.GROUND_Y
        self.platforms.append(Platform(0, y, self.width, 60))

    def _make_platform(self, x, y, w, h=20):
        self.platforms.append(Platform(x, y, w, h))
