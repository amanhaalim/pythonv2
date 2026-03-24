# engine/anim_state.py — Animation state machine for player & enemies
import pygame
import math


class AnimState:
    """
    State machine with states: idle, run, jump, fall, attack, hurt, dead
    Each state drives frame selection for procedural draw calls.
    """
    VALID = ("idle", "run", "jump", "fall", "attack", "hurt", "dead")

    def __init__(self):
        self.state = "idle"
        self.prev = "idle"
        self.timer = 0.0    # time in current state
        self.anim_tick = 0.0
        self.attack_timer = 0.0
        self.hurt_timer = 0.0

    def update(self, dt, vx, vy, on_ground, is_hurt=False, is_attacking=False, is_dead=False):
        self.timer += dt
        self.anim_tick += dt

        prev = self.state

        if is_dead:
            self._set("dead")
        elif is_hurt:
            self._set("hurt")
            self.hurt_timer = 0.25
        elif is_attacking:
            self._set("attack")
            self.attack_timer = 0.25
        else:
            # Decay hurt / attack
            if self.state == "hurt":
                self.hurt_timer -= dt
                if self.hurt_timer <= 0:
                    self._set("idle")
            elif self.state == "attack":
                self.attack_timer -= dt
                if self.attack_timer <= 0:
                    self._set("idle")
            elif not on_ground:
                if vy < -50:
                    self._set("jump")
                else:
                    self._set("fall")
            elif abs(vx) > 20:
                self._set("run")
            else:
                self._set("idle")

    def _set(self, new_state):
        if self.state != new_state:
            self.prev = self.state
            self.state = new_state
            self.timer = 0.0

    # Helpers for draw code
    def leg_offset(self):
        if self.state == "run":
            return math.sin(self.anim_tick * 12) * 7
        return 0.0

    def body_bob(self):
        if self.state == "idle":
            return math.sin(self.anim_tick * 2.5) * 1.5
        if self.state == "run":
            return abs(math.sin(self.anim_tick * 12)) * 2
        return 0.0

    def arm_angle(self):
        if self.state == "run":
            return math.sin(self.anim_tick * 12) * 0.4
        if self.state == "attack":
            t = 1.0 - self.attack_timer / 0.25
            return math.sin(t * math.pi) * 1.2
        if self.state == "idle":
            return math.sin(self.anim_tick * 1.5) * 0.1
        return 0.0

    def squash(self):
        """Returns (scale_x, scale_y) for squash-and-stretch."""
        if self.state == "jump" and self.timer < 0.1:
            return (0.85, 1.2)
        if self.state == "fall" and self.timer > 0.3:
            return (1.1, 0.9)
        if self.state == "attack":
            t = self.attack_timer / 0.25
            return (1.0 + 0.2 * t, 1.0 - 0.1 * t)
        return (1.0, 1.0)
