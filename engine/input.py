# engine/input.py
import pygame


class InputHandler:
    def __init__(self):
        self._held = {}
        self.just_pressed = set()

    def update(self, keys, events):
        # keys is a pygame key state sequence
        self.just_pressed = set()
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.just_pressed.add(event.key)
        self._keys = keys

    def left(self):
        return self._keys[pygame.K_LEFT] or self._keys[pygame.K_a]

    def right(self):
        return self._keys[pygame.K_RIGHT] or self._keys[pygame.K_d]

    def jump(self):
        return pygame.K_SPACE in self.just_pressed or pygame.K_UP in self.just_pressed or pygame.K_w in self.just_pressed

    def interact(self):
        return pygame.K_e in self.just_pressed or pygame.K_RETURN in self.just_pressed

    def attack(self):
        return self._keys[pygame.K_x] or self._keys[pygame.K_z]
