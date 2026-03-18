# game/enemy.py
import pygame
import math
import constants as C


class Enemy:
    def __init__(self, x, y, patrol_left=0, patrol_right=200, enemy_type="drone"):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.vx = 80.0
        self.vy = 0.0
        self.width = 32
        self.height = 32
        self.health = 3
        self.alive = True
        self.anim_tick = 0
        self.enemy_type = enemy_type  # drone, guard, turret
        self.alert = False
        self.attack_timer = 0
        self.damage = 10

    def update(self, dt, player, platforms):
        if not self.alive:
            return
        self.anim_tick += dt

        if self.enemy_type == "drone":
            self._update_drone(dt, player)
        elif self.enemy_type == "guard":
            self._update_guard(dt, player, platforms)
        elif self.enemy_type == "turret":
            self._update_turret(dt, player)

        self.attack_timer -= dt

    def _update_drone(self, dt, player):
        # Drone: hover and patrol, rush toward player if close
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 200:
            self.alert = True
        if self.alert and dist < 300:
            self.x += (dx / max(dist, 1)) * 100 * dt
            self.y += (dy / max(dist, 1)) * 60 * dt
        else:
            self.alert = False
            # Patrol horizontally
            self.x += self.vx * dt
            if self.x > self.patrol_right:
                self.vx = -abs(self.vx)
            if self.x < self.patrol_left:
                self.vx = abs(self.vx)
        self.y = self.start_x * 0 + (self.y - self.start_x * 0)  # keep y

    def _update_guard(self, dt, player, platforms):
        self.x += self.vx * dt
        if self.x > self.patrol_right:
            self.vx = -abs(self.vx)
        if self.x < self.patrol_left:
            self.vx = abs(self.vx)
        # Simple gravity
        self.vy += C.GRAVITY * dt
        self.y += self.vy * dt
        for plat in platforms:
            if (self.x < plat.x + plat.w and self.x + self.width > plat.x and
                    self.y + self.height > plat.y and self.y < plat.y + plat.h):
                if self.vy >= 0:
                    self.y = plat.y - self.height
                    self.vy = 0

    def _update_turret(self, dt, player):
        # Stationary, shoots periodically (attack handled by level)
        pass

    def check_player_collision(self, player):
        if not self.alive:
            return False
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

    def take_hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False

    def draw(self, screen, sx, sy):
        sx, sy = int(sx), int(sy)
        if self.enemy_type == "drone":
            col = (200, 50, 50) if not self.alert else (255, 80, 0)
            pygame.draw.circle(screen, col, (sx + 16, sy + 16), 16)
            pygame.draw.circle(screen, (255, 50, 50), (sx + 16, sy + 16), 10)
            # Eye
            pygame.draw.circle(screen, C.RED, (sx + 16, sy + 14), 5)
            # Wings
            t = int(self.anim_tick * 20) % 3
            for i, wx in enumerate([sx - 10, sx + 32]):
                wing_h = [8, 12, 8][t if i == 0 else (t + 1) % 3]
                pygame.draw.ellipse(screen, (150, 30, 30), (wx, sy + 8, 10, wing_h))
        elif self.enemy_type == "guard":
            pygame.draw.rect(screen, (120, 60, 40), (sx, sy, 32, 32))
            pygame.draw.rect(screen, (180, 80, 50), (sx + 4, sy + 4, 24, 14))
            pygame.draw.circle(screen, C.RED, (sx + 16, sy + 10), 6)
        elif self.enemy_type == "turret":
            pygame.draw.rect(screen, (80, 80, 100), (sx, sy + 12, 32, 20))
            pygame.draw.rect(screen, (120, 120, 140), (sx + 8, sy, 16, 16))
            pygame.draw.rect(screen, (60, 60, 80), (sx + 14, sy - 10, 6, 12))

        # Health bar
        if self.alive and self.health < 3:
            pygame.draw.rect(screen, C.RED, (sx, sy - 8, 32, 4))
            pygame.draw.rect(screen, C.GREEN, (sx, sy - 8, int(32 * self.health / 3), 4))
