# engine/particles.py — Particle system: smoke, dust, fire, sparks
import pygame
import random
import math


class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","size","color","alpha","ptype","gravity")

    def __init__(self, x, y, vx, vy, life, size, color, ptype="dust", gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.life = float(life)
        self.max_life = float(life)
        self.size = float(size)
        self.color = color
        self.alpha = 255
        self.ptype = ptype
        self.gravity = gravity


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, ptype, x, y, count=1):
        r = random
        if ptype == "dust":
            for _ in range(count):
                self.particles.append(Particle(
                    x + r.uniform(-8, 8), y,
                    r.uniform(-30, 30), r.uniform(-60, -10),
                    r.uniform(0.3, 0.7), r.uniform(3, 7),
                    (r.randint(160,200), r.randint(140,180), r.randint(100,140)),
                    "dust", gravity=120
                ))
        elif ptype == "fire":
            for _ in range(count):
                self.particles.append(Particle(
                    x + r.uniform(-12, 12), y,
                    r.uniform(-20, 20), r.uniform(-120, -50),
                    r.uniform(0.4, 0.9), r.uniform(4, 10),
                    (255, r.randint(60,160), 0),
                    "fire", gravity=-30
                ))
        elif ptype == "smoke":
            for _ in range(count):
                self.particles.append(Particle(
                    x + r.uniform(-6, 6), y,
                    r.uniform(-15, 15), r.uniform(-40, -10),
                    r.uniform(1.0, 2.0), r.uniform(6, 14),
                    (r.randint(60,90), r.randint(60,90), r.randint(60,90)),
                    "smoke", gravity=-10
                ))
        elif ptype == "spark":
            for _ in range(count):
                angle = r.uniform(0, math.pi * 2)
                spd = r.uniform(80, 220)
                self.particles.append(Particle(
                    x, y,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    r.uniform(0.2, 0.5), r.uniform(2, 5),
                    (255, r.randint(180, 255), r.randint(0, 60)),
                    "spark", gravity=300
                ))
        elif ptype == "blood":  # hit splatter (red sparks)
            for _ in range(count):
                angle = r.uniform(0, math.pi * 2)
                spd = r.uniform(40, 130)
                self.particles.append(Particle(
                    x, y,
                    math.cos(angle) * spd, math.sin(angle) * spd,
                    r.uniform(0.15, 0.35), r.uniform(2, 4),
                    (220, r.randint(20, 60), 20),
                    "spark", gravity=250
                ))

    def emit_explosion(self, x, y):
        self.emit("fire",  x, y, 20)
        self.emit("smoke", x, y, 10)
        self.emit("spark", x, y, 25)

    def emit_footstep(self, x, y):
        self.emit("dust", x, y, 4)

    def emit_hit(self, x, y):
        self.emit("spark", x, y, 8)
        self.emit("blood", x, y, 6)

    def update(self, dt):
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            # Slow down horizontally
            p.vx *= (1.0 - dt * 1.5)
            t = p.life / p.max_life
            p.alpha = int(255 * t)
            # Smoke grows; fire shrinks
            if p.ptype == "smoke":
                p.size += dt * 4
            elif p.ptype == "fire":
                p.size = max(1, p.size - dt * 8)
            alive.append(p)
        self.particles = alive

    def draw(self, screen, camera_x, camera_y):
        for p in self.particles:
            sx = int(p.x - camera_x)
            sy = int(p.y - camera_y)
            sz = max(1, int(p.size))
            if sx < -30 or sx > 1310 or sy < -30 or sy > 750:
                continue
            surf = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            r, g, b = p.color
            pygame.draw.circle(surf, (r, g, b, p.alpha), (sz, sz), sz)
            screen.blit(surf, (sx - sz, sy - sz))
