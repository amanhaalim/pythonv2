# engine/screen_fx.py — Screen shake, color grading, vignette, dynamic lighting
import pygame
import math
import random
import constants as C


# Per-level color grade: (r_mult, g_mult, b_mult, overlay_rgba)
LEVEL_GRADES = [
    # Slum — desaturated blue-purple, dark vignette
    {"tint": (0.75, 0.70, 1.0), "overlay": (20, 10, 40, 60), "vignette": 0.65},
    # Desert — warm orange-yellow
    {"tint": (1.0, 0.90, 0.65), "overlay": (40, 20, 0, 40), "vignette": 0.45},
    # Beach — cool blue-green, bright
    {"tint": (0.80, 1.0, 1.0), "overlay": (0, 20, 30, 30), "vignette": 0.35},
    # Battlefield — red tint, heavy vignette
    {"tint": (1.0, 0.60, 0.55), "overlay": (40, 0, 0, 80), "vignette": 0.75},
]


class ScreenFX:
    def __init__(self, screen):
        self.screen = screen
        self.shake_x = 0
        self.shake_y = 0
        self._shake_timer = 0.0
        self._shake_intensity = 0.0
        self._shake_trauma = 0.0   # 0-1 trauma value
        self.current_level = 0
        self._grade_alpha = 0.0    # 0-1, lerps in on level load
        self._vignette_surf = None
        self._grade_surf = None
        self._cached_level = -1
        self.flash_timer = 0.0
        self.flash_color = (255, 255, 255)
        self._noise_x = 0.0        # perlin-like shake offsets
        self._noise_y = 0.5

    # ── Shake ────────────────────────────────────────────────────────────────
    def add_trauma(self, amount):
        """Add trauma (0-1). Trauma decays over time; shake = trauma²."""
        self._shake_trauma = min(1.0, self._shake_trauma + amount)

    def shake(self, intensity=8, duration=0.3):
        """Legacy direct shake call."""
        self.add_trauma(intensity / 20.0)

    def flash(self, color=(255,255,255), duration=0.12):
        self.flash_timer = duration
        self.flash_color = color

    def update(self, dt):
        # Trauma decay
        self._shake_trauma = max(0.0, self._shake_trauma - dt * 1.8)
        shake_mag = self._shake_trauma ** 2 * 18
        if shake_mag > 0.1:
            self._noise_x = (self._noise_x * 0.8 + random.uniform(-1, 1) * 0.2)
            self._noise_y = (self._noise_y * 0.8 + random.uniform(-1, 1) * 0.2)
            self.shake_x = int(self._noise_x * shake_mag)
            self.shake_y = int(self._noise_y * shake_mag)
        else:
            self.shake_x = 0
            self.shake_y = 0

        # Grade lerp in
        self._grade_alpha = min(1.0, self._grade_alpha + dt * 1.5)

        # Flash decay
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Rebuild cache if level changed
        if self._cached_level != self.current_level:
            self._build_grade_surf()
            self._build_vignette()
            self._cached_level = self.current_level
            self._grade_alpha = 0.0

    def _build_grade_surf(self):
        grade = LEVEL_GRADES[self.current_level % len(LEVEL_GRADES)]
        ov = grade["overlay"]
        self._grade_surf = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        self._grade_surf.fill((ov[0], ov[1], ov[2], ov[3]))

    def _build_vignette(self):
        grade = LEVEL_GRADES[self.current_level % len(LEVEL_GRADES)]
        strength = grade["vignette"]
        self._vignette_surf = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        cx, cy = C.SCREEN_W // 2, C.SCREEN_H // 2
        max_r = math.hypot(cx, cy)
        # Draw concentric rings with increasing alpha
        steps = 40
        for i in range(steps, 0, -1):
            t = i / steps
            r = int(max_r * t)
            alpha = int(strength * 220 * (1.0 - t) ** 1.5)
            if alpha <= 0:
                continue
            ring = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
            ring.fill((0, 0, 0, 0))
            pygame.draw.ellipse(ring, (0, 0, 0, alpha),
                                (cx - r, cy - int(r * 0.7), r * 2, int(r * 1.4)))
            self._vignette_surf.blit(ring, (0, 0))

    def apply_post(self, level_idx=None):
        """Call after drawing everything — applies grading + vignette + flash."""
        if level_idx is not None:
            self.current_level = level_idx

        alpha = int(self._grade_alpha * 255)

        # Color grade overlay
        if self._grade_surf and alpha > 0:
            self._grade_surf.set_alpha(alpha)
            self.screen.blit(self._grade_surf, (0, 0))

        # Vignette
        if self._vignette_surf and alpha > 0:
            self._vignette_surf.set_alpha(alpha)
            self.screen.blit(self._vignette_surf, (0, 0))

        # Flash
        if self.flash_timer > 0:
            fa = int((self.flash_timer / 0.12) * 160)
            fs = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
            r, g, b = self.flash_color
            fs.fill((r, g, b, min(fa, 160)))
            self.screen.blit(fs, (0, 0))


class LightSource:
    """A dynamic light drawn as a soft radial gradient."""
    def __init__(self, x, y, radius, color=(255, 220, 120), intensity=1.0, flicker=0.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.intensity = intensity
        self.flicker = flicker   # 0-1 how much it flickers
        self._tick = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self._tick += dt * (3 + random.uniform(0, 4) * self.flicker)

    def draw(self, surf, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        flicker_scale = 1.0 + math.sin(self._tick) * self.flicker * 0.15
        r = int(self.radius * flicker_scale)
        if sx < -r or sx > C.SCREEN_W + r or sy < -r or sy > C.SCREEN_H + r:
            return
        light = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        cr, cg, cb = self.color
        steps = 12
        for i in range(steps, 0, -1):
            t = i / steps
            ring_r = int(r * t)
            alpha = int(self.intensity * 120 * (1.0 - t) ** 1.8)
            pygame.draw.circle(light, (cr, cg, cb, alpha), (r, r), ring_r)
        surf.blit(light, (sx - r, sy - r), special_flags=pygame.BLEND_RGBA_ADD)


class DynamicLighting:
    """Manages a dark overlay with punched-out light sources (subtract blend)."""
    def __init__(self, screen):
        self.screen = screen
        self.sources = []
        self.darkness = 0.0   # 0=bright, 1=very dark
        self._dark_surf = None
        self._light_surf = None
        self._build_surfs()

    def _build_surfs(self):
        self._dark_surf = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)
        self._light_surf = pygame.Surface((C.SCREEN_W, C.SCREEN_H), pygame.SRCALPHA)

    def set_darkness(self, level, dt=None):
        """0=day, 1=pitch dark. dt for smooth lerp."""
        # Per-level darkness
        darknesses = [0.55, 0.20, 0.10, 0.70]
        target = darknesses[level % 4]
        if dt:
            self.darkness += (target - self.darkness) * dt * 2
        else:
            self.darkness = target

    def add_source(self, light):
        self.sources.append(light)

    def clear_sources(self):
        self.sources = []

    def update(self, dt):
        for s in self.sources:
            s.update(dt)

    def draw(self, camera_x, camera_y):
        if self.darkness < 0.02:
            return
        # Dark overlay
        dark_alpha = int(self.darkness * 210)
        self._dark_surf.fill((0, 0, 0, dark_alpha))
        # Punch out lights
        for src in self.sources:
            src.draw(self._dark_surf, camera_x, camera_y)
        self.screen.blit(self._dark_surf, (0, 0))
