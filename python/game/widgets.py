import pygame
from .consts import PANEL, BORDER, PRIMARY, TEXT, MUTED, WHITE

class Button:
    def __init__(self, rect, text, on_click=None, primary=False, disabled=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.primary = primary
        self.disabled = disabled

    def draw(self, surface, font):
        bg = (79,70,229) if (self.primary and not self.disabled) else PANEL
        fg = WHITE if (self.primary and not self.disabled) else (150,150,150 if self.disabled else TEXT)
        border = (79,70,229) if (self.primary and not self.disabled) else BORDER
        pygame.draw.rect(surface, bg, self.rect, border_radius=8)
        pygame.draw.rect(surface, border, self.rect, 1, border_radius=8)
        label = font.render(self.text, True, fg)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.on_click):
                    self.on_click()
                return True
        return False
