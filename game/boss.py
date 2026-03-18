# game/boss.py
import pygame
import math
import constants as C


class Boss:
    """Multi-phase robot boss (secretly controlled by a cow)."""

    PHASES = ["phase1", "phase2", "phase3_cow"]

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.start_x = float(x)
        self.width = 80
        self.height = 100
        self.max_health = [150, 100, 60]
        self.phase = 0
        self.health = self.max_health[0]
        self.alive = True
        self.vx = 120.0
        self.vy = 0.0
        self.on_ground = False
        self.anim_tick = 0
        self.attack_timer = 0
        self.attack_type = "charge"
        self.reveal_cow = False  # phase 3 reveals cow
        self.phase_transition_timer = 0
        self.missiles = []  # projectiles
        self.pattern_timer = 0

    def update(self, dt, player, platforms):
        if not self.alive:
            return

        self.anim_tick += dt
        self.attack_timer -= dt
        self.pattern_timer -= dt

        # Gravity
        self.vy += C.GRAVITY * dt
        self.y += self.vy * dt
        self.x += self.vx * dt
        self.on_ground = False

        # Platform collision
        for plat in platforms:
            if (self.x < plat.x + plat.w and self.x + self.width > plat.x and
                    self.y + self.height > plat.y and self.y < plat.y + plat.h):
                if self.vy >= 0:
                    self.y = plat.y - self.height
                    self.vy = 0
                    self.on_ground = True

        # Bounce at edges
        if self.x < self.start_x - 300 or self.x > self.start_x + 300:
            self.vx *= -1

        # Phase behavior
        if self.phase == 0:
            self._phase1(dt, player)
        elif self.phase == 1:
            self._phase2(dt, player)
        elif self.phase == 2:
            self._phase3_cow(dt, player)

        # Update missiles
        for m in self.missiles:
            m["x"] += m["vx"] * dt
            m["y"] += m["vy"] * dt
            m["vy"] += 400 * dt
            m["life"] -= dt
        self.missiles = [m for m in self.missiles if m["life"] > 0]

    def _phase1(self, dt, player):
        speed = 120
        dx = player.x - self.x
        self.vx = speed if dx > 0 else -speed
        if self.attack_timer <= 0:
            self.attack_timer = 3.0
            self._shoot_missile(player)

    def _phase2(self, dt, player):
        speed = 180
        dx = player.x - self.x
        self.vx = speed if dx > 0 else -speed
        if self.attack_timer <= 0:
            self.attack_timer = 1.5
            self._shoot_missile(player)
            self._shoot_missile(player, offset=30)

    def _phase3_cow(self, dt, player):
        # The cow pilot panics — erratic movement
        self.vx = 200 * math.sin(self.anim_tick * 3)
        if self.attack_timer <= 0:
            self.attack_timer = 1.0
            self._shoot_missile(player)

    def _shoot_missile(self, player, offset=0):
        dx = (player.x + player.width / 2) - (self.x + self.width / 2 + offset)
        dy = (player.y + player.height / 2) - (self.y + self.height / 2)
        dist = max(math.hypot(dx, dy), 1)
        speed = 200
        self.missiles.append({
            "x": self.x + self.width / 2 + offset,
            "y": self.y + self.height / 2,
            "vx": dx / dist * speed,
            "vy": dy / dist * speed - 80,
            "life": 3.0
        })

    def take_hit(self):
        self.health -= 20
        if self.health <= 0:
            self.phase += 1
            if self.phase >= len(self.PHASES):
                self.alive = False
                self.reveal_cow = True
            else:
                self.health = self.max_health[min(self.phase, len(self.max_health) - 1)]
                if self.phase == 2:
                    self.reveal_cow = True

    def check_player_collision(self, player):
        if not self.alive:
            return False
        return (self.x < player.x + player.width and
                self.x + self.width > player.x and
                self.y < player.y + player.height and
                self.y + self.height > player.y)

    def get_max_health(self):
        return self.max_health[min(self.phase, len(self.max_health) - 1)]

    def draw(self, screen, sx, sy, camera_x=0, camera_y=0):
        # Convert world coords to screen if not yet done
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        if not self.reveal_cow:
            # Giant robot
            body_col = (80, 80, 100)
            pygame.draw.rect(screen, body_col, (sx, sy + 30, 80, 70))
            pygame.draw.rect(screen, (100, 100, 130), (sx + 10, sy, 60, 36))
            # Eyes
            eye_col = (255, 50, 0) if self.phase == 0 else (255, 200, 0)
            pygame.draw.circle(screen, eye_col, (sx + 24, sy + 16), 10)
            pygame.draw.circle(screen, eye_col, (sx + 56, sy + 16), 10)
            # Arms
            arm_angle = math.sin(self.anim_tick * 4) * 0.3
            pygame.draw.rect(screen, (60, 60, 80),
                             (sx - 20, sy + 30 + int(arm_angle * 20), 22, 12))
            pygame.draw.rect(screen, (60, 60, 80),
                             (sx + 78, sy + 30 + int(-arm_angle * 20), 22, 12))
            # Legs
            pygame.draw.rect(screen, (60, 60, 80), (sx + 10, sy + 90, 20, 20))
            pygame.draw.rect(screen, (60, 60, 80), (sx + 50, sy + 90, 20, 20))
        else:
            # COW REVEALED inside robot chassis
            pygame.draw.rect(screen, (80, 80, 100), (sx, sy + 30, 80, 70))
            pygame.draw.rect(screen, (60, 80, 60, 80), (sx + 10, sy, 60, 36))
            # Cow in cockpit
            pygame.draw.ellipse(screen, (220, 210, 200), (sx + 18, sy + 4, 44, 26))
            # Cow spots
            pygame.draw.ellipse(screen, (50, 50, 50), (sx + 22, sy + 8, 12, 8))
            pygame.draw.ellipse(screen, (50, 50, 50), (sx + 42, sy + 12, 10, 6))
            # Cow eyes
            pygame.draw.circle(screen, (30, 30, 30), (sx + 28, sy + 10), 3)
            pygame.draw.circle(screen, (30, 30, 30), (sx + 52, sy + 10), 3)
            # Cow ears
            pygame.draw.polygon(screen, (220, 180, 180),
                                [(sx + 18, sy + 6), (sx + 14, sy - 4), (sx + 24, sy + 4)])
            pygame.draw.polygon(screen, (220, 180, 180),
                                [(sx + 62, sy + 6), (sx + 66, sy - 4), (sx + 56, sy + 4)])
            # MOO label
            font = pygame.font.SysFont("monospace", 14, bold=True)
            moo = font.render("MOO!", True, C.YELLOW)
            screen.blit(moo, (sx + 20, sy - 18))

        # Health bar
        bar_w = 80
        hp_frac = self.health / self.get_max_health()
        pygame.draw.rect(screen, C.RED, (sx, sy - 14, bar_w, 8))
        pygame.draw.rect(screen, C.GREEN, (sx, sy - 14, int(bar_w * hp_frac), 8))
        ph_font = pygame.font.SysFont("monospace", 10)
        ph_txt = ph_font.render(f"PHASE {self.phase + 1}", True, C.WHITE)
        screen.blit(ph_txt, (sx, sy - 26))

        # Draw missiles
        for m in self.missiles:
            mx = int(m["x"] - camera_x)
            my = int(m["y"] - camera_y)
            pygame.draw.circle(screen, C.ORANGE, (mx, my), 6)
            pygame.draw.circle(screen, C.YELLOW, (mx, my), 3)
