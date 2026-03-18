# engine/renderer.py
import pygame
import math
import constants as C


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.camera_x = 0
        self.camera_y = 0

    def set_camera(self, target_x, target_y, level_width):
        self.camera_x = target_x - C.SCREEN_W // 2
        self.camera_x = max(0, min(self.camera_x, max(0, level_width - C.SCREEN_W)))
        self.camera_y = 0

    def world_to_screen(self, x, y):
        return x - self.camera_x, y - self.camera_y

    def draw_level(self, level, player, companion):
        palette = C.LEVEL_PALETTES[level.level_index]
        self.screen.fill(palette["sky"])

        if player:
            self.set_camera(player.x, player.y, level.width)

        self._draw_parallax(level, palette)

        for plat in level.platforms:
            sx, sy = self.world_to_screen(plat.x, plat.y)
            if -plat.w < sx < C.SCREEN_W + plat.w:
                pygame.draw.rect(self.screen, palette["ground"], (int(sx), int(sy), plat.w, plat.h))
                pygame.draw.rect(self.screen, palette["accent"], (int(sx), int(sy), plat.w, 4))

        for obj in level.interactables:
            sx, sy = self.world_to_screen(obj.x, obj.y)
            if -80 < sx < C.SCREEN_W + 80:
                obj.draw(self.screen, sx, sy)

        for enemy in level.enemies:
            if enemy.alive:
                sx, sy = self.world_to_screen(enemy.x, enemy.y)
                if -80 < sx < C.SCREEN_W + 80:
                    enemy.draw(self.screen, sx, sy)

        for item in level.collectibles:
            if not item.collected:
                sx, sy = self.world_to_screen(item.x, item.y)
                pygame.draw.circle(self.screen, C.YELLOW, (int(sx), int(sy)), 10)
                pygame.draw.circle(self.screen, C.ORANGE, (int(sx), int(sy)), 8)

        if player:
            sx, sy = self.world_to_screen(player.x, player.y)
            player.draw(self.screen, sx, sy)

        if companion:
            sx, sy = self.world_to_screen(companion.x, companion.y)
            companion.draw(self.screen, sx, sy)

        if level.boss and level.boss.alive:
            level.boss.draw(self.screen, 0, 0, self.camera_x, self.camera_y)
            for m in level.boss.missiles:
                mx = int(m["x"] - self.camera_x)
                my = int(m["y"] - self.camera_y)
                if -20 < mx < C.SCREEN_W + 20 and -20 < my < C.SCREEN_H + 20:
                    pygame.draw.circle(self.screen, (255, 140, 0), (mx, my), 6)
                    pygame.draw.circle(self.screen, (255, 220, 50), (mx, my), 3)

    def _draw_parallax(self, level, palette):
        idx = level.level_index
        if idx == 0:
            for i in range(10):
                bx = int(i * 160 - self.camera_x * 0.3) % (C.SCREEN_W + 160) - 80
                bh = 80 + (i * 37) % 120
                pygame.draw.rect(self.screen, (35, 30, 45),
                                 (bx, C.SCREEN_H - bh - 120, 70, bh))
                for wy in range(C.SCREEN_H - bh - 110, C.SCREEN_H - 130, 20):
                    for wx in range(bx + 8, bx + 65, 15):
                        col = C.YELLOW if (i + wy) % 7 == 0 else (50, 45, 60)
                        pygame.draw.rect(self.screen, col, (wx, wy, 8, 10))
        elif idx == 1:
            for i in range(5):
                dx = int(i * 280 - self.camera_x * 0.2) % (C.SCREEN_W + 280) - 140
                pts = [(dx, C.SCREEN_H - 100),
                       (dx + 140, C.SCREEN_H - 180),
                       (dx + 280, C.SCREEN_H - 100)]
                pygame.draw.polygon(self.screen, (180, 140, 60), pts)
            pygame.draw.circle(self.screen, (255, 220, 80), (C.SCREEN_W - 120, 80), 50)
            pygame.draw.circle(self.screen, (255, 200, 40), (C.SCREEN_W - 120, 80), 40)
        elif idx == 2:
            pygame.draw.rect(self.screen, (30, 80, 160),
                             (0, C.SCREEN_H - 160, C.SCREEN_W, 100))
            for i in range(8):
                wx = int(i * 180 - self.camera_x * 0.15) % (C.SCREEN_W + 180) - 90
                pygame.draw.ellipse(self.screen, (40, 110, 190),
                                    (wx, C.SCREEN_H - 135, 180, 35))
        elif idx == 3:
            for i in range(6):
                fx = int(i * 210 - self.camera_x * 0.25) % (C.SCREEN_W + 210) - 100
                pulse = int(abs(math.sin(i * 1.3)) * 30)
                pygame.draw.circle(self.screen, (80 + pulse, 30, 10),
                                   (fx, C.SCREEN_H - 130), 44)
                pygame.draw.circle(self.screen, (160 + pulse, 60, 10),
                                   (fx, C.SCREEN_H - 130), 28)
