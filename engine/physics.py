# engine/physics.py
import constants as C


class PhysicsEngine:
    def update(self, entity, platforms, level_width=None):
        """Apply gravity and resolve platform collisions."""
        dt = 1 / C.FPS

        entity.vy += C.GRAVITY * dt
        # Clamp fall speed to prevent tunnelling
        entity.vy = min(entity.vy, 900)

        entity.x += entity.vx * dt
        entity.y += entity.vy * dt

        entity.on_ground = False

        for plat in platforms:
            if self._collides(entity, plat):
                # Determine overlap on each axis
                overlap_x_left  = (entity.x + entity.width) - plat.x
                overlap_x_right = (plat.x + plat.w) - entity.x
                overlap_y_top   = (entity.y + entity.height) - plat.y
                overlap_y_bot   = (plat.y + plat.h) - entity.y

                min_x = min(overlap_x_left, overlap_x_right)
                min_y = min(overlap_y_top,  overlap_y_bot)

                if min_y < min_x:
                    # Vertical collision
                    if entity.vy >= 0 and overlap_y_top < overlap_y_bot:
                        entity.y = plat.y - entity.height
                        entity.vy = 0
                        entity.on_ground = True
                    elif entity.vy < 0 and overlap_y_bot < overlap_y_top:
                        entity.y = plat.y + plat.h
                        entity.vy = 0
                else:
                    # Horizontal collision — push out sideways
                    if overlap_x_left < overlap_x_right:
                        entity.x = plat.x - entity.width
                    else:
                        entity.x = plat.x + plat.w
                    entity.vx = 0

        # World left boundary
        if entity.x < 0:
            entity.x = 0
            entity.vx = 0

        # World right boundary (clamp to level width when provided)
        if level_width is not None:
            right_limit = level_width - entity.width
            if entity.x > right_limit:
                entity.x = right_limit
                entity.vx = 0

        # World bottom (fell off) — respawn on ground
        if entity.y > C.SCREEN_H + 200:
            entity.y = C.GROUND_Y - entity.height
            entity.vy = 0
            entity.vx = 0

    def _collides(self, entity, plat):
        return (entity.x < plat.x + plat.w and
                entity.x + entity.width > plat.x and
                entity.y < plat.y + plat.h and
                entity.y + entity.height > plat.y)
