# systems/dialogue_system.py
import pygame
import constants as C


class DialogueSystem:
    def __init__(self, screen):
        self.screen = screen
        self.queue = []
        self.active = False
        self.current = None
        self.display_text = ""
        self.char_index = 0
        self.char_timer = 0
        self.char_speed = 0.03  # seconds per character
        self.done = False
        self.font = pygame.font.SysFont("monospace", 18)
        self.name_font = pygame.font.SysFont("monospace", 20, bold=True)
        self.skip_font = pygame.font.SysFont("monospace", 13)

    def show_dialogue(self, speaker, text, portrait="player"):
        self.queue.append({"speaker": speaker, "text": text, "portrait": portrait})
        if not self.active:
            self._next()

    def _next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.display_text = ""
            self.char_index = 0
            self.char_timer = 0
            self.done = False
            self.active = True
        else:
            self.active = False
            self.current = None

    def update(self, events):
        if not self.active or not self.current:
            return
        # Type out text
        self.char_timer += 1 / C.FPS
        while self.char_timer >= self.char_speed and self.char_index < len(self.current["text"]):
            self.display_text += self.current["text"][self.char_index]
            self.char_index += 1
            self.char_timer -= self.char_speed

        if self.char_index >= len(self.current["text"]):
            self.done = True

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                    if self.done:
                        self._next()
                    else:
                        # Skip to end
                        self.display_text = self.current["text"]
                        self.char_index = len(self.current["text"])
                        self.done = True

    def draw(self):
        if not self.active or not self.current:
            return

        # Box at bottom of screen
        box_x, box_y = 80, C.SCREEN_H - 150
        box_w, box_h = C.SCREEN_W - 160, 130
        s = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        s.fill((8, 8, 20, 210))
        self.screen.blit(s, (box_x, box_y))
        pygame.draw.rect(self.screen, C.CYAN, (box_x, box_y, box_w, box_h), 2)

        # Portrait
        p = self.current["portrait"]
        self._draw_portrait(box_x + 10, box_y + 10, p)

        # Speaker name
        name_surf = self.name_font.render(self.current["speaker"], True, C.YELLOW)
        self.screen.blit(name_surf, (box_x + 90, box_y + 10))

        # Text (word-wrapped)
        self._draw_wrapped(self.display_text, box_x + 90, box_y + 36, box_w - 110, C.WHITE)

        # Skip hint
        if self.done:
            skip = self.skip_font.render("[E / SPACE] Continue", True, C.LIGHT_GREY)
            self.screen.blit(skip, (box_x + box_w - skip.get_width() - 10, box_y + box_h - 20))
        else:
            skip = self.skip_font.render("[E / SPACE] Skip", True, (100, 100, 120))
            self.screen.blit(skip, (box_x + box_w - skip.get_width() - 10, box_y + box_h - 20))

    def _draw_portrait(self, x, y, portrait_type):
        pygame.draw.rect(self.screen, (20, 20, 40), (x, y, 70, 70))
        pygame.draw.rect(self.screen, C.CYAN, (x, y, 70, 70), 2)
        if portrait_type == "robot":
            pygame.draw.rect(self.screen, (60, 110, 160), (x + 15, y + 20, 40, 30))
            pygame.draw.rect(self.screen, (70, 130, 180), (x + 18, y + 8, 34, 16))
            pygame.draw.circle(self.screen, C.CYAN, (x + 28, y + 16), 5)
            pygame.draw.circle(self.screen, C.CYAN, (x + 42, y + 16), 5)
        elif portrait_type == "player":
            pygame.draw.rect(self.screen, (220, 180, 130), (x + 20, y + 10, 30, 28))
            pygame.draw.rect(self.screen, (80, 50, 20), (x + 20, y + 10, 30, 9))
            pygame.draw.circle(self.screen, (30, 30, 30), (x + 30, y + 23), 4)
            pygame.draw.circle(self.screen, (30, 30, 30), (x + 42, y + 23), 4)
        elif portrait_type == "survivor":
            pygame.draw.rect(self.screen, (180, 130, 90), (x + 20, y + 10, 30, 28))
            pygame.draw.rect(self.screen, (60, 40, 20), (x + 20, y + 10, 30, 9))
            pygame.draw.circle(self.screen, C.WHITE, (x + 30, y + 23), 4)
            pygame.draw.circle(self.screen, C.WHITE, (x + 42, y + 23), 4)
        elif portrait_type == "cow":
            pygame.draw.ellipse(self.screen, (220, 210, 200), (x + 10, y + 15, 50, 30))
            pygame.draw.ellipse(self.screen, (50, 50, 50), (x + 15, y + 18, 14, 10))
            pygame.draw.circle(self.screen, (30, 30, 30), (x + 26, y + 23), 3)
            pygame.draw.circle(self.screen, (30, 30, 30), (x + 44, y + 23), 3)

    def _draw_wrapped(self, text, x, y, max_width, color):
        words = text.split(" ")
        line = ""
        dy = 0
        for word in words:
            test = line + word + " "
            if self.font.size(test)[0] > max_width:
                surf = self.font.render(line.rstrip(), True, color)
                self.screen.blit(surf, (x, y + dy))
                line = word + " "
                dy += 22
            else:
                line = test
        if line:
            surf = self.font.render(line.rstrip(), True, color)
            self.screen.blit(surf, (x, y + dy))

    def is_active(self):
        return self.active
