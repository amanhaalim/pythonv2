# engine/physics.py
import constants as C


class PhysicsEngine:
    def update(self, entity, platforms):
        """Apply gravity and resolve platform collisions."""
        entity.vy += C.GRAVITY * (1 / C.FPS)
        entity.x += entity.vx * (1 / C.FPS)
        entity.y += entity.vy * (1 / C.FPS)

        entity.on_ground = False

        for plat in platforms:
            if self._collides(entity, plat):
                # Resolve vertically
                if entity.vy >= 0:
                    bottom = entity.y + entity.height
                    plat_top = plat.y
                    if bottom - plat_top < entity.height * 0.6 + abs(entity.vy) * (1/C.FPS) + 4:
                        entity.y = plat.y - entity.height
                        entity.vy = 0
                        entity.on_ground = True
                elif entity.vy < 0:
                    entity.y = plat.y + plat.h
                    entity.vy = 0

        # World boundary
        if entity.x < 0:
            entity.x = 0
            entity.vx = 0

    def _collides(self, entity, plat):
        return (entity.x < plat.x + plat.w and
                entity.x + entity.width > plat.x and
                entity.y < plat.y + plat.h and
                entity.y + entity.height > plat.y)
