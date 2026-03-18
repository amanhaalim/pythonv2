# game/player.py
import pygame
import constants as C
import math


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 28
        self.height = 48
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1  # 1=right, -1=left
        self.health = 100
        self.max_health = 100
        self.anim_tick = 0
        self.hurt_timer = 0
        self.score = 0
        self.puzzles_solved = 0

    def handle_input(self, inp):
        # Horizontal movement
        if inp.left():
            self.vx = -C.PLAYER_SPEED
            self.facing = -1
        elif inp.right():
            self.vx = C.PLAYER_SPEED
            self.facing = 1
        else:
            self.vx *= 0.75  # friction

        # Jump
        if inp.jump() and self.on_ground:
            self.vy = C.JUMP_SPEED
            self.on_ground = False

    def take_damage(self, amount):
        if self.hurt_timer <= 0:
            self.health -= amount
            self.hurt_timer = 1.2  # invincibility frames
            self.health = max(0, self.health)

    def update(self, dt):
        self.anim_tick += dt * 8
        if self.hurt_timer > 0:
            self.hurt_timer -= dt

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, screen, sx, sy):
        # Hurt flash
        if self.hurt_timer > 0 and int(self.hurt_timer * 10) % 2 == 0:
            return

        sx, sy = int(sx), int(sy)
        # Body
        pygame.draw.rect(screen, (60, 120, 200), (sx, sy + 16, 28, 32))
        # Head
        pygame.draw.rect(screen, (220, 180, 130), (sx + 4, sy, 20, 20))
        # Hair
        pygame.draw.rect(screen, (80, 50, 20), (sx + 4, sy, 20, 7))
        # Eyes
        pygame.draw.circle(screen, (30, 30, 30), (sx + 10, sy + 10), 3)
        pygame.draw.circle(screen, (30, 30, 30), (sx + 18, sy + 10), 3)
        # Legs walk animation
        leg_off = int(math.sin(self.anim_tick) * 6) if abs(self.vx) > 10 else 0
        pygame.draw.rect(screen, (40, 80, 160), (sx + 4, sy + 36, 8, 12 + leg_off))
        pygame.draw.rect(screen, (40, 80, 160), (sx + 16, sy + 36, 8, 12 - leg_off))
        # Direction indicator
        if self.facing == 1:
            pygame.draw.polygon(screen, C.YELLOW, [(sx + 28, sy + 8), (sx + 34, sy + 11), (sx + 28, sy + 14)])
        else:
            pygame.draw.polygon(screen, C.YELLOW, [(sx, sy + 8), (sx - 6, sy + 11), (sx, sy + 14)])
