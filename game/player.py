# game/player.py
import pygame
import math
import constants as C
from engine.anim_state import AnimState


class Player:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.width = 28
        self.height = 48
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1      # 1=right, -1=left
        self.health = 100
        self.max_health = 100
        self.anim_tick = 0.0
        self.hurt_timer = 0.0
        self.score = 0
        self.puzzles_solved = 0
        self.anim = AnimState()
        self._was_attacking = False
        self._attack_input_timer = 0.0
        self._prev_on_ground = False
        self._land_emit = False
        self._took_hit = False   # signal particle system on land

    def handle_input(self, inp):
        if inp.left():
            self.vx = -C.PLAYER_SPEED
            self.facing = -1
        elif inp.right():
            self.vx = C.PLAYER_SPEED
            self.facing = 1
        else:
            self.vx *= 0.75

        if inp.jump() and self.on_ground:
            self.vy = C.JUMP_SPEED
            self.on_ground = False

        if inp.attack():
            self._attack_input_timer = 0.25

    def take_damage(self, amount):
        if self.hurt_timer <= 0:
            self.health -= amount
            self.hurt_timer = 1.2
            self.health = max(0, self.health)
            self._took_hit = True
            return True
        return False

    def update(self, dt):
        self.anim_tick += dt * 8
        if self.hurt_timer > 0:
            self.hurt_timer -= dt
        if self._attack_input_timer > 0:
            self._attack_input_timer -= dt

        is_attacking = self._attack_input_timer > 0
        is_hurt = self.hurt_timer > 0.8   # first 0.4s of hurt
        self.anim.update(dt, self.vx, self.vy, self.on_ground,
                         is_hurt=is_hurt, is_attacking=is_attacking,
                         is_dead=self.health <= 0)

        # Land detection for particles
        self._land_emit = (not self._prev_on_ground and self.on_ground)
        self._prev_on_ground = self.on_ground

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, screen, sx, sy):
        # Hurt flash — blink
        if self.hurt_timer > 0 and int(self.hurt_timer * 10) % 2 == 0:
            return

        sx, sy = int(sx), int(sy)
        anim = self.anim

        bob = anim.body_bob()
        leg = anim.leg_offset()
        arm = anim.arm_angle()
        sx_s, sy_s = anim.squash()

        # Squash pivot at feet
        draw_y = sy + int(bob)
        h_scale = sy_s
        w_scale = sx_s

        # Shadow
        sh_a = 60
        sh = pygame.Surface((28, 8), pygame.SRCALPHA)
        sh.fill((0, 0, 0, sh_a))
        screen.blit(sh, (sx, sy + 48))

        # State-dependent tint
        if anim.state == "hurt":
            body_col = (220, 80, 80)
        elif anim.state == "attack":
            body_col = (80, 180, 255)
        elif anim.state == "dead":
            body_col = (80, 80, 80)
        else:
            body_col = (60, 120, 200)

        # Body
        bx = sx + int((1 - w_scale) * 14)
        bw = int(28 * w_scale)
        bh = int(32 * h_scale)
        pygame.draw.rect(screen, body_col, (bx, draw_y + 16, bw, bh))
        # Chest highlight
        pygame.draw.rect(screen, (min(255, body_col[0]+40), min(255, body_col[1]+40),
                                  min(255, body_col[2]+40)), (bx+3, draw_y+17, bw-6, 8))

        # Head
        hx = sx + 4
        hy = draw_y
        pygame.draw.rect(screen, (220, 180, 130), (hx, hy, 20, 20))
        # Hair
        pygame.draw.rect(screen, (80, 50, 20), (hx, hy, 20, 7))
        # Eyes
        ex_off = 1 if self.facing == 1 else -1
        pygame.draw.circle(screen, (30, 30, 30), (hx + 8 + ex_off, hy + 11), 3)
        pygame.draw.circle(screen, (30, 30, 30), (hx + 15 + ex_off, hy + 11), 3)
        # Eye shine
        pygame.draw.circle(screen, (255,255,255), (hx + 9 + ex_off, hy + 9), 1)
        pygame.draw.circle(screen, (255,255,255), (hx + 16 + ex_off, hy + 9), 1)

        # Arms
        arm_y = draw_y + 18
        if self.facing == 1:
            arm_x1, arm_x2 = sx - 6, sx + 26
        else:
            arm_x1, arm_x2 = sx + 26, sx - 6
        arm_off1 = int(math.sin(arm) * 10)
        arm_off2 = int(-math.sin(arm) * 10)
        pygame.draw.rect(screen, (50, 100, 180), (arm_x1, arm_y + arm_off1, 8, 14))
        pygame.draw.rect(screen, (50, 100, 180), (arm_x2, arm_y + arm_off2, 8, 14))

        # Attack glow
        if anim.state == "attack":
            glow_x = sx + 28 if self.facing == 1 else sx - 10
            gs = pygame.Surface((20, 20), pygame.SRCALPHA)
            t = 1.0 - anim.attack_timer / 0.25
            ga = int(180 * math.sin(t * math.pi))
            pygame.draw.circle(gs, (100, 220, 255, ga), (10, 10), 10)
            screen.blit(gs, (glow_x, draw_y + 16))

        # Legs
        leg_col = (40, 80, 160)
        pygame.draw.rect(screen, leg_col, (sx + 4,  draw_y + 36, 9, 12 + int(leg)))
        pygame.draw.rect(screen, leg_col, (sx + 15, draw_y + 36, 9, 12 - int(leg)))
        # Boots
        pygame.draw.rect(screen, (30, 50, 110), (sx + 3,  draw_y + 44 + int(leg), 11, 5))
        pygame.draw.rect(screen, (30, 50, 110), (sx + 14, draw_y + 44 - int(leg), 11, 5))

        # Direction arrow
        if anim.state not in ("dead", "hurt"):
            col = C.YELLOW
            if self.facing == 1:
                pygame.draw.polygon(screen, col,
                    [(sx+28, draw_y+10),(sx+34, draw_y+13),(sx+28, draw_y+16)])
            else:
                pygame.draw.polygon(screen, col,
                    [(sx, draw_y+10),(sx-6, draw_y+13),(sx, draw_y+16)])
