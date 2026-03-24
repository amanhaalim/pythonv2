# game/enemy.py
import pygame
import math
import constants as C


class Enemy:
    def __init__(self, x, y, patrol_left=0, patrol_right=200, enemy_type="drone"):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.start_y = float(y)
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
        self._just_died = False

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
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        if dist < 200:
            self.alert = True
        if self.alert and dist < 350:
            speed = 100
            self.x += (dx / max(dist, 1)) * speed * dt
            self.y += (dy / max(dist, 1)) * 60 * dt
            # Clamp drone y so it doesn't sink into ground
            if self.y > C.GROUND_Y - self.height:
                self.y = C.GROUND_Y - self.height
        else:
            self.alert = False
            self.x += self.vx * dt
            if self.x > self.patrol_right:
                self.vx = -abs(self.vx)
            if self.x < self.patrol_left:
                self.vx = abs(self.vx)
            # Drones hover ~64px above ground
            self.y = self.start_y

    def _update_guard(self, dt, player, platforms):
        # Alert: chase player when close
        dx = player.x - self.x
        dist = abs(dx)
        if dist < 250 and abs(player.y - self.y) < 80:
            self.alert = True
        else:
            self.alert = False

        if self.alert:
            self.vx = 100 if dx > 0 else -100
        else:
            # Patrol
            if self.x > self.patrol_right:
                self.vx = -abs(self.vx)
            if self.x < self.patrol_left:
                self.vx = abs(self.vx)

        self.x += self.vx * dt

        # Gravity
        self.vy += C.GRAVITY * dt
        self.vy = min(self.vy, 900)
        self.y += self.vy * dt

        # Platform collision
        for plat in platforms:
            if (self.x < plat.x + plat.w and self.x + self.width > plat.x and
                    self.y + self.height > plat.y and self.y < plat.y + plat.h):
                if self.vy >= 0:
                    self.y = plat.y - self.height
                    self.vy = 0

        # Keep within patrol bounds (no cliff walking)
        if self.x < self.patrol_left:
            self.x = self.patrol_left
            self.vx = abs(self.vx)
        if self.x > self.patrol_right:
            self.x = self.patrol_right
            self.vx = -abs(self.vx)

    def _update_turret(self, dt, player):
        # Stationary; damage handled via collision in level_manager
        pass

    def check_player_collision(self, player):
        if not self.alive:
            return False
        # Turrets use a slightly smaller hitbox
        margin = 8 if self.enemy_type == "turret" else 0
        return (self.x + margin < player.x + player.width and
                self.x + self.width - margin > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

    def take_hit(self):
        self.health -= 1
        if self.health <= 0:
            self.alive = False
            self._just_died = True

    def draw(self, screen, sx, sy):
        sx, sy = int(sx), int(sy)
        if self.enemy_type == "drone":
            col = (200, 50, 50) if not self.alert else (255, 80, 0)
            pygame.draw.circle(screen, col, (sx + 16, sy + 16), 16)
            pygame.draw.circle(screen, (255, 50, 50), (sx + 16, sy + 16), 10)
            pygame.draw.circle(screen, C.RED, (sx + 16, sy + 14), 5)
            t = int(self.anim_tick * 20) % 3
            for i, wx in enumerate([sx - 10, sx + 32]):
                wing_h = [8, 12, 8][t if i == 0 else (t + 1) % 3]
                pygame.draw.ellipse(screen, (150, 30, 30), (wx, sy + 8, 10, wing_h))
        elif self.enemy_type == "guard":
            col = (180, 80, 50) if not self.alert else (220, 100, 30)
            pygame.draw.rect(screen, (120, 60, 40), (sx, sy, 32, 32))
            pygame.draw.rect(screen, col, (sx + 4, sy + 4, 24, 14))
            pygame.draw.circle(screen, C.RED, (sx + 16, sy + 10), 6)
        elif self.enemy_type == "turret":
            pygame.draw.rect(screen, (80, 80, 100), (sx, sy + 12, 32, 20))
            pygame.draw.rect(screen, (120, 120, 140), (sx + 8, sy, 16, 16))
            pygame.draw.rect(screen, (60, 60, 80), (sx + 14, sy - 10, 6, 12))

        # Health bar
        if self.alive and self.health < 3:
            pygame.draw.rect(screen, C.RED, (sx, sy - 8, 32, 4))
            pygame.draw.rect(screen, C.GREEN, (sx, sy - 8, int(32 * self.health / 3), 4))
