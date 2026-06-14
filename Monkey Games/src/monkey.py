# ============================================================
# monkey.py
# Child Class: Monkey  (inherits from GameObject)
# ============================================================

import pygame
from src.game_object import GameObject


class Monkey(GameObject):
    """
    MONKEY — the player character.

    Inherits from GameObject and adds:
    - Jumping physics
    - Score management (via inherited getter/setter)
    - Running animation state
    - Banana collection counter
    """

    # ── Constants ─────────────────────────────────────────────
    GRAVITY = 0.6          # pulls monkey downward each frame
    JUMP_STRENGTH = -14    # upward velocity when jumping
    GROUND_Y = 370         # y-position of the ground

    def __init__(self, x, y, image):
        # Call the parent __init__ with monkey-specific values
        super().__init__(
            x=x,
            y=y,
            width=80,
            height=80,
            image=image,
            name="Monkey"
        )

        # ── Movement state ────────────────────────────────────
        self.velocity_y = 0        # current vertical speed
        self.is_jumping = False    # True while in the air
        self.is_alive = True       # False = game over

        # ── Score & collectibles ──────────────────────────────
        self.bananas_collected = 0

        # Initialise the inherited private __score to 0
        self.set_score(0)

    # ──────────────────────────────────────────────────────────
    # run() — called when the player presses SPACE / UP
    # ──────────────────────────────────────────────────────────
    def run(self):
        """Make the monkey jump if it is on the ground."""
        if not self.is_jumping:
            self.velocity_y = Monkey.JUMP_STRENGTH
            self.is_jumping = True

    # ──────────────────────────────────────────────────────────
    # move() — overrides GameObject.move()
    # ──────────────────────────────────────────────────────────
    def move(self):
        """Apply gravity and update vertical position."""
        self.velocity_y += Monkey.GRAVITY   # gravity increases velocity
        self.y += self.velocity_y

        # Land on the ground
        if self.y >= Monkey.GROUND_Y:
            self.y = Monkey.GROUND_Y
            self.velocity_y = 0
            self.is_jumping = False

        self.update_rect()

    # ──────────────────────────────────────────────────────────
    # update() — full update each frame
    # ──────────────────────────────────────────────────────────
    def update(self):
        """Update physics every game frame."""
        self.move()

    # ──────────────────────────────────────────────────────────
    # draw() — overrides GameObject.draw()
    # ──────────────────────────────────────────────────────────
    def draw(self, screen):
        """Draw the monkey sprite."""
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, (139, 90, 43), self.rect)

    # ──────────────────────────────────────────────────────────
    # collect_banana() — adds points and tracks bananas
    # ──────────────────────────────────────────────────────────
    def collect_banana(self):
        """Called when the monkey touches a banana."""
        self.bananas_collected += 1
        new_score = self.get_score() + 10   # +10 points per banana
        self.set_score(new_score)

    # ──────────────────────────────────────────────────────────
    # add_level_bonus() — bonus points for finishing a level
    # ──────────────────────────────────────────────────────────
    def add_level_bonus(self, level):
        """Add a bonus equal to level × 50 when a level is cleared."""
        bonus = level * 50
        self.set_score(self.get_score() + bonus)

    # ──────────────────────────────────────────────────────────
    # reset() — restart monkey for a new level/run
    # ──────────────────────────────────────────────────────────
    def reset_position(self):
        """Put the monkey back at its starting position."""
        self.x = 100
        self.y = Monkey.GROUND_Y
        self.velocity_y = 0
        self.is_jumping = False
        self.is_alive = True
        self.update_rect()
