# ============================================================
# obstacle.py
# Child Classes: Obstacle, Banana  (both inherit GameObject)
# Obstacle types: Fire, Rock, Spike
# ============================================================

import pygame
import random
from src.game_object import GameObject


# ── SCREEN WIDTH used for spawning off-screen to the right ──
SCREEN_WIDTH = 800


class Obstacle(GameObject):
    """
    OBSTACLE — moves from right to left across the screen.

    Types  : "fire" | "rock" | "spike"
    Inherits from GameObject.

    Demonstrates inheritance by reusing x, y, image,
    rect, and draw() from the parent, while overriding move().
    """

    # Ground Y positions per type (bottom of the sprite)
    GROUND_Y = {
        "fire":  370,
        "rock":  390,
        "spike": 400,
    }

    # Sprite sizes per type
    SIZES = {
        "fire":  (55, 70),
        "rock":  (60, 50),
        "spike": (50, 50),
    }

    def __init__(self, obstacle_type, image, speed=5):
        size = Obstacle.SIZES.get(obstacle_type, (60, 60))
        ground_y = Obstacle.GROUND_Y.get(obstacle_type, 390)

        super().__init__(
            x=SCREEN_WIDTH + random.randint(100, 400),
            y=ground_y,
            width=size[0],
            height=size[1],
            image=image,
            name=obstacle_type
        )

        self.obstacle_type = obstacle_type
        self._speed = speed           # protected, inherited from GameObject

    # ──────────────────────────────────────────────────────────
    # move() — override: slides left across the screen
    # ──────────────────────────────────────────────────────────
    def move(self):
        """Move the obstacle from right to left."""
        self.x -= self._speed
        self.update_rect()

    # ──────────────────────────────────────────────────────────
    # reset() — reposition off-screen to the right
    # ──────────────────────────────────────────────────────────
    def reset(self):
        """Send obstacle back off the right edge to re-enter."""
        self.x = SCREEN_WIDTH + random.randint(200, 600)
        self.y = Obstacle.GROUND_Y.get(self.obstacle_type, 390)
        self.update_rect()

    # ──────────────────────────────────────────────────────────
    # is_off_screen() — True when obstacle has passed the left
    # ──────────────────────────────────────────────────────────
    def is_off_screen(self):
        return self.x + self.width < 0

    # ──────────────────────────────────────────────────────────
    # draw() — fallback colours if image failed to load
    # ──────────────────────────────────────────────────────────
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Colour-coded fallback shapes
            colours = {"fire": (255, 80, 0), "rock": (128, 128, 128), "spike": (255, 220, 0)}
            colour = colours.get(self.obstacle_type, (200, 0, 0))
            pygame.draw.rect(screen, colour, self.rect)


# ============================================================
# Banana — collectible item (also inherits GameObject)
# ============================================================

class Banana(GameObject):
    """
    BANANA — floats in the air; the monkey collects these for points.
    Also inherits from GameObject.
    """

    def __init__(self, image, speed=5):
        # Bananas appear at varying heights
        spawn_y = random.choice([280, 310, 340])

        super().__init__(
            x=SCREEN_WIDTH + random.randint(50, 300),
            y=spawn_y,
            width=40,
            height=45,
            image=image,
            name="Banana"
        )

        self._speed = speed   # moves with the world

    # ──────────────────────────────────────────────────────────
    # move() — slides left just like obstacles
    # ──────────────────────────────────────────────────────────
    def move(self):
        self.x -= self._speed
        self.update_rect()

    # ──────────────────────────────────────────────────────────
    # reset() — reposition off-screen to the right
    # ──────────────────────────────────────────────────────────
    def reset(self):
        self.x = SCREEN_WIDTH + random.randint(300, 700)
        self.y = random.choice([280, 310, 340])
        self.update_rect()

    # ──────────────────────────────────────────────────────────
    # is_off_screen()
    # ──────────────────────────────────────────────────────────
    def is_off_screen(self):
        return self.x + self.width < 0

    # ──────────────────────────────────────────────────────────
    # draw() — yellow rectangle fallback
    # ──────────────────────────────────────────────────────────
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (255, 230, 0), self.rect)
