# engine/renderer.py — Cinematic renderer with particles, lighting, color grading
import pygame
import math
import constants as C


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.camera_x = 0.0
        self.camera_y = 0.0
        # Injected by main.py after construction
        self.particles = None
        self.lighting = None
        self.fx = None

    def set_camera(self, target_x, target_y, level_width, shake_x=0, shake_y=0):
        cx = target_x - C.SCREEN_W // 2
        self.camera_x = max(0, min(float(cx), max(0, level_width - C.SCREEN_W))) + shake_x
        self.camera_y = shake_y

    def world_to_screen(self, x, y):
        return x - self.camera_x, y - self.camera_y

    def draw_level(self, level, player, companion, fx=None):
        palette = C.LEVEL_PALETTES[level.level_index]
        sx_off = getattr(self.fx, "shake_x", 0) if self.fx else 0
        sy_off = getattr(self.fx, "shake_y", 0) if self.fx else 0

        # Sky fill
        self.screen.fill(palette["sky"])

        if player:
            self.set_camera(player.x, player.y, level.width, sx_off, sy_off)

        self._draw_parallax(level, palette)
        self._draw_platforms(level, palette)
        self._draw_interactables(level)
        self._draw_collectibles(level)

        # Particles (world-space, under characters)
        if self.particles:
            self.particles.draw(self.screen, self.camera_x, self.camera_y)

        self._draw_enemies(level)

        if player:
            spx, spy = self.world_to_screen(player.x, player.y)
            player.draw(self.screen, spx, spy)

        if companion:
            scx, scy = self.world_to_screen(companion.x, companion.y)
            companion.draw(self.screen, scx, scy)

        if level.boss and level.boss.alive:
            level.boss.draw(self.screen, 0, 0, self.camera_x, self.camera_y)

        # Dynamic lighting overlay
        if self.lighting:
            self.lighting.draw(self.camera_x, self.camera_y)

        # Post-process: color grade + vignette + flash
        if self.fx:
            self.fx.apply_post(level.level_index)

    # ── Parallax ─────────────────────────────────────────────────────────────
    def _draw_parallax(self, level, palette):
        idx = level.level_index
        cx = self.camera_x
        if idx == 0:   # Slum — neon city silhouette
            for i in range(12):
                bx = int(i * 160 - cx * 0.25) % (C.SCREEN_W + 200) - 100
                bh = 90 + (i * 37) % 130
                pygame.draw.rect(self.screen, (28, 22, 40),
                                 (bx, C.SCREEN_H - bh - 110, 68, bh))
                # Windows
                for wy in range(C.SCREEN_H - bh - 100, C.SCREEN_H - 120, 18):
                    for wx in range(bx + 6, bx + 62, 14):
                        flicker = ((i * 7 + wy // 18) % 13 == 0)
                        col = (255, 220, 50) if flicker else (50, 40, 65)
                        pygame.draw.rect(self.screen, col, (wx, wy, 7, 9))
            # Distant haze
            haze = pygame.Surface((C.SCREEN_W, 80), pygame.SRCALPHA)
            haze.fill((60, 30, 80, 40))
            self.screen.blit(haze, (0, C.SCREEN_H - 200))

        elif idx == 1:   # Desert — dunes + sun
            sun_x = int(C.SCREEN_W * 0.8 - cx * 0.05) % C.SCREEN_W
            pygame.draw.circle(self.screen, (255, 220, 80), (sun_x, 70), 55)
            pygame.draw.circle(self.screen, (255, 240, 120), (sun_x, 70), 42)
            # Heat shimmer line
            haze = pygame.Surface((C.SCREEN_W, 40), pygame.SRCALPHA)
            haze.fill((200, 150, 60, 25))
            self.screen.blit(haze, (0, C.SCREEN_H - 180))
            for i in range(6):
                dx = int(i * 280 - cx * 0.18) % (C.SCREEN_W + 300) - 150
                pts = [(dx, C.SCREEN_H - 80),(dx+150, C.SCREEN_H - 175),(dx+300, C.SCREEN_H - 80)]
                pygame.draw.polygon(self.screen, (175, 135, 55), pts)
                pygame.draw.polygon(self.screen, (195, 155, 70), pts, 3)

        elif idx == 2:   # Beach — ocean waves
            # Ocean body
            pygame.draw.rect(self.screen, (25, 70, 155), (0, C.SCREEN_H - 165, C.SCREEN_W, 110))
            # Wave crests
            for i in range(9):
                wx = int(i * 180 - cx * 0.12) % (C.SCREEN_W + 200) - 100
                t = math.sin(cx * 0.005 + i * 0.7) * 8
                pygame.draw.ellipse(self.screen, (50, 115, 200),
                                    (wx, int(C.SCREEN_H - 145 + t), 190, 30))
                pygame.draw.ellipse(self.screen, (120, 200, 240),
                                    (wx + 10, int(C.SCREEN_H - 140 + t), 170, 14))
            # Distant birds
            for i in range(4):
                bx = int(i * 320 - cx * 0.08) % (C.SCREEN_W + 320) - 40
                by = 80 + i * 22
                pygame.draw.arc(self.screen, (60, 80, 100),
                                pygame.Rect(bx, by, 22, 9), 0, math.pi, 2)
                pygame.draw.arc(self.screen, (60, 80, 100),
                                pygame.Rect(bx + 22, by, 22, 9), 0, math.pi, 2)

        elif idx == 3:   # Battlefield — fire & explosions bg
            for i in range(7):
                fx2 = int(i * 200 - cx * 0.22) % (C.SCREEN_W + 220) - 110
                pulse = abs(math.sin(cx * 0.004 + i * 1.1)) * 40 + 60
                pygame.draw.circle(self.screen, (int(60+pulse), 20, 10),
                                   (fx2, C.SCREEN_H - 130), 50)
                pygame.draw.circle(self.screen, (int(120+pulse), 40, 10),
                                   (fx2, C.SCREEN_H - 130), 32)
                pygame.draw.circle(self.screen, (200, 100, 20),
                                   (fx2, C.SCREEN_H - 130), 14)
            # Smoke overlay
            sm = pygame.Surface((C.SCREEN_W, 80), pygame.SRCALPHA)
            sm.fill((30, 25, 20, 45))
            self.screen.blit(sm, (0, C.SCREEN_H - 220))

    # ── Platforms ─────────────────────────────────────────────────────────────
    def _draw_platforms(self, level, palette):
        idx = level.level_index
        for plat in level.platforms:
            sx, sy = self.world_to_screen(plat.x, plat.y)
            if sx > C.SCREEN_W + plat.w or sx + plat.w < 0:
                continue
            sx, sy = int(sx), int(sy)
            w, h = plat.w, plat.h
            # Main fill
            pygame.draw.rect(self.screen, palette["ground"], (sx, sy, w, h))
            # Top accent stripe
            pygame.draw.rect(self.screen, palette["accent"], (sx, sy, w, 4))
            # Side depth shading
            dark = tuple(max(0, c - 30) for c in palette["ground"])
            pygame.draw.rect(self.screen, dark, (sx, sy + 4, 4, h - 4))
            # Level-specific detail
            if idx == 0:   # Slum: rust streaks
                for i in range(sx, sx + w, 40):
                    pygame.draw.line(self.screen, (100, 50, 20), (i, sy + 4), (i + 8, sy + h - 2), 1)
            elif idx == 1:  # Desert: sand ripples
                for i in range(sx + 8, sx + w - 8, 24):
                    pygame.draw.arc(self.screen, (190, 160, 80),
                                    pygame.Rect(i, sy + 6, 16, 6), 0, math.pi, 1)
            elif idx == 2:  # Beach: wet sheen
                pygame.draw.rect(self.screen, (80, 160, 120), (sx, sy, w, 2))
            elif idx == 3:  # Battlefield: cracked concrete
                for i in range(sx + 10, sx + w - 10, 35):
                    pygame.draw.line(self.screen, (30, 25, 20),
                                     (i, sy + 4), (i + 15, sy + h - 2), 1)

    # ── Interactables ────────────────────────────────────────────────────────
    def _draw_interactables(self, level):
        for obj in level.interactables:
            sx, sy = self.world_to_screen(obj.x, obj.y)
            if -80 < sx < C.SCREEN_W + 80:
                obj.draw(self.screen, sx, sy)

    # ── Collectibles ──────────────────────────────────────────────────────────
    def _draw_collectibles(self, level):
        t = pygame.time.get_ticks() / 1000.0
        for item in level.collectibles:
            if item.collected:
                continue
            sx, sy = self.world_to_screen(item.x, item.y)
            if sx < -20 or sx > C.SCREEN_W + 20:
                continue
            bob = math.sin(t * 3 + item.x * 0.01) * 4
            # Glow ring
            gs = pygame.Surface((28, 28), pygame.SRCALPHA)
            ga = int(120 + math.sin(t * 4 + item.x) * 60)
            pygame.draw.circle(gs, (255, 200, 0, ga), (14, 14), 12)
            self.screen.blit(gs, (int(sx) - 14, int(sy + bob) - 14))
            pygame.draw.circle(self.screen, C.YELLOW, (int(sx), int(sy + bob)), 9)
            pygame.draw.circle(self.screen, C.ORANGE, (int(sx), int(sy + bob)), 6)
            pygame.draw.circle(self.screen, (255, 240, 180), (int(sx) - 2, int(sy + bob) - 2), 2)

    # ── Enemies ───────────────────────────────────────────────────────────────
    def _draw_enemies(self, level):
        for enemy in level.enemies:
            if not enemy.alive:
                continue
            sx, sy = self.world_to_screen(enemy.x, enemy.y)
            if -80 < sx < C.SCREEN_W + 80:
                enemy.draw(self.screen, sx, sy)
