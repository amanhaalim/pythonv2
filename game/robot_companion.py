# game/robot_companion.py
import pygame
import math
import constants as C


HINT_MESSAGES = {
    "slum": [
        "AXIOM: The slums hold secrets. Look for glowing terminals!",
        "AXIOM: Enemies patrol in patterns — time your movement.",
        "AXIOM: Math puzzles unlock sealed doors. Think carefully!",
    ],
    "desert": [
        "AXIOM: The desert sun is harsh. Find shade near tall structures.",
        "AXIOM: Tic-tac-toe isn't just a game — it's a cipher here.",
        "AXIOM: Pattern sequences control the sand gates.",
    ],
    "beach": [
        "AXIOM: Something is buried on the beach. Use your eyes!",
        "AXIOM: Connect the nodes to restore power to the lighthouse.",
        "AXIOM: The missing object reveals the path forward.",
    ],
    "battlefield": [
        "AXIOM: The boss has three phases. Survive each one!",
        "AXIOM: Something feels wrong about this robot commander...",
        "AXIOM: Moo? Did that robot just... moo?",
    ],
}


class RobotCompanion:
    def __init__(self, x, y, dialogue, story_engine):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.width = 24
        self.height = 40
        self.on_ground = False
        self.dialogue = dialogue
        self.story_engine = story_engine
        self.anim_tick = 0
        self.hover_offset = 0.0
        self.hint_cooldown = 0
        self.current_level_name = "slum"
        self.hint_index = 0
        self.eye_blink = 0

    def update(self, dt, player, level):
        self.anim_tick += dt
        self.hover_offset = math.sin(self.anim_tick * 2) * 6

        # Follow player smoothly
        target_x = player.x - 60 if player.facing == 1 else player.x + 80
        target_y = player.y

        dx = target_x - self.x
        self.x += dx * dt * 4
        self.y = player.y + self.hover_offset - 8

        self.vx = 0.0

        # Auto hints
        self.hint_cooldown -= dt
        if self.hint_cooldown <= 0:
            self.hint_cooldown = 20.0  # hint every 20s

        self.eye_blink += dt
        if self.eye_blink > 4.0:
            self.eye_blink = 0.0

    def give_hint(self, level_name=None):
        if level_name:
            self.current_level_name = level_name
        hints = HINT_MESSAGES.get(self.current_level_name, ["AXIOM: Stay alert!"])
        msg = hints[self.hint_index % len(hints)]
        self.hint_index += 1
        self.dialogue.show_dialogue("AXIOM", msg, portrait="robot")

    def say(self, message):
        self.dialogue.show_dialogue("AXIOM", message, portrait="robot")

    def draw(self, screen, sx, sy):
        sx, sy = int(sx), int(sy)
        # Body — metallic box
        pygame.draw.rect(screen, (70, 130, 180), (sx, sy + 14, 24, 26))
        pygame.draw.rect(screen, (90, 160, 210), (sx + 2, sy + 16, 20, 22))
        # Head
        pygame.draw.rect(screen, (60, 110, 160), (sx + 2, sy, 20, 16))
        # Eyes — glow cyan
        eye_col = C.CYAN if self.eye_blink < 3.5 else (20, 40, 60)
        pygame.draw.circle(screen, eye_col, (sx + 8, sy + 8), 4)
        pygame.draw.circle(screen, eye_col, (sx + 16, sy + 8), 4)
        pygame.draw.circle(screen, C.WHITE, (sx + 8, sy + 7), 2)
        pygame.draw.circle(screen, C.WHITE, (sx + 16, sy + 7), 2)
        # Antenna
        pygame.draw.line(screen, C.CYAN, (sx + 12, sy), (sx + 12, sy - 10), 2)
        pygame.draw.circle(screen, C.YELLOW, (sx + 12, sy - 11), 3)
        # Legs (floating, no legs shown — hover effect)
        # Thruster glow
        glow = int(abs(math.sin(self.anim_tick * 3)) * 80) + 60
        pygame.draw.ellipse(screen, (glow, glow // 2, 0),
                            (sx + 4, sy + 38, 16, 6))
        # Name tag
        font = pygame.font.SysFont("monospace", 10, bold=True)
        tag = font.render("AXIOM", True, C.CYAN)
        screen.blit(tag, (sx + 12 - tag.get_width() // 2, sy - 22))
