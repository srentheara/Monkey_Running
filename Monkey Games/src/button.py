# ============================================================
# button.py
# Button class — used on the Main Menu and Pause screen
# ============================================================

import pygame


class Button:
    """
    A clickable UI button.

    Demonstrates encapsulation:
    - Public:    label, rect
    - Protected: _colour, _hover_colour
    - Private:   __font
    """

    # ── Default colour palette ─────────────────────────────────
    DEFAULT_COLOUR       = (60, 160, 60)
    DEFAULT_HOVER_COLOUR = (80, 200, 80)
    TEXT_COLOUR          = (255, 255, 255)

    def __init__(self, x, y, width, height, label,
                 colour=None, hover_colour=None):
        # Public
        self.label = label
        self.rect  = pygame.Rect(x, y, width, height)

        # Protected
        self._colour       = colour       or Button.DEFAULT_COLOUR
        self._hover_colour = hover_colour or Button.DEFAULT_HOVER_COLOUR

        # Private
        self.__font = pygame.font.SysFont("Arial", 26, bold=True)

        self._is_hovered = False

    # ──────────────────────────────────────────────────────────
    # draw() — render the button with hover effect
    # ──────────────────────────────────────────────────────────
    def draw(self, screen):
        """Draw the button; highlight when mouse is over it."""
        mouse_pos = pygame.mouse.get_pos()
        self._is_hovered = self.rect.collidepoint(mouse_pos)

        colour = self._hover_colour if self._is_hovered else self._colour

        # Shadow
        shadow_rect = self.rect.move(3, 3)
        pygame.draw.rect(screen, (20, 80, 20), shadow_rect, border_radius=12)

        # Main button body
        pygame.draw.rect(screen, colour, self.rect, border_radius=12)

        # Border
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)

        # Label text (centred)
        text_surf = self.__font.render(self.label, True, Button.TEXT_COLOUR)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    # ──────────────────────────────────────────────────────────
    # click() — True if left mouse button pressed on button
    # ──────────────────────────────────────────────────────────
    def click(self, event):
        """Return True if this button was clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
