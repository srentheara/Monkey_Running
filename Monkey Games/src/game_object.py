# ============================================================
# game_object.py
# Parent Class: GameObject
# All game characters/items inherit from this class.
# ============================================================

import pygame


class GameObject:
    """
    BASE (PARENT) CLASS for all objects in the game.

    Demonstrates:
    - Encapsulation: public, protected (_), and private (__) variables
    - Getter and Setter methods
    - Polymorphism: child classes override draw() and move()
    """

    def __init__(self, x, y, width, height, image, name="GameObject"):
        # ── Encapsulation Example ──────────────────────────────
        # Public variable  → accessible anywhere
        self.name = name

        # Protected variable → should only be used inside the class or subclasses
        self._speed = 3

        # Private variable  → only accessible inside this class via getter/setter
        self.__score = 0

        # ── Position & size ───────────────────────────────────
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        # ── Image (sprite) ────────────────────────────────────
        self.image = image
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))

        # Rect used for collision detection
        self.rect = pygame.Rect(x, y, width, height)

    # ── Getter: read the private score ────────────────────────
    def get_score(self):
        """Return the private __score value."""
        return self.__score

    # ── Setter: update the private score safely ───────────────
    def set_score(self, value):
        """Set the private __score; value must be a non-negative integer."""
        if isinstance(value, int) and value >= 0:
            self.__score = value
        else:
            print(f"[Warning] Invalid score value: {value}")

    # ── Getter/Setter for protected speed ─────────────────────
    def get_speed(self):
        return self._speed

    def set_speed(self, value):
        if value > 0:
            self._speed = value

    # ─────────────────────────────────────────────────────────
    # draw() — Override in child classes
    # ─────────────────────────────────────────────────────────
    def draw(self, screen):
        """Draw the object on the screen."""
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback: draw a coloured rectangle if no image
            pygame.draw.rect(screen, (200, 200, 200), self.rect)

    # ─────────────────────────────────────────────────────────
    # move() — Override in child classes
    # ─────────────────────────────────────────────────────────
    def move(self):
        """Move the object. Overridden by subclasses."""
        pass

    # ─────────────────────────────────────────────────────────
    # update_rect() — keep rect in sync with x, y
    # ─────────────────────────────────────────────────────────
    def update_rect(self):
        """Sync the collision rectangle with current x/y position."""
        self.rect.x = self.x
        self.rect.y = self.y
