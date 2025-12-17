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
        # Enhanced button styling with shadows and gradients
        if self.primary and not self.disabled:
            bg = (79, 70, 229)
            bg_light = (99, 90, 249)
            fg = WHITE
            border = (59, 50, 209)
        elif self.disabled:
            bg = (240, 240, 240)
            bg_light = bg
            fg = (180, 180, 180)
            border = (220, 220, 220)
        else:
            bg = PANEL
            bg_light = (250, 250, 250)
            fg = TEXT
            border = BORDER
        
        # Button shadow
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.w, self.rect.h)
        shadow_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 40))
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Main button background
        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        
        # Top highlight for 3D effect
        if not self.disabled:
            highlight_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, self.rect.h // 2)
            highlight_surf = pygame.Surface((self.rect.w, self.rect.h // 2), pygame.SRCALPHA)
            highlight_surf.fill((*bg_light[:3], 60))
            surface.blit(highlight_surf, (highlight_rect.x, highlight_rect.y), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Enhanced border
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=10)
        
        # Text with better centering
        label = font.render(self.text, True, fg)
        label_rect = label.get_rect(center=self.rect.center)
        surface.blit(label, label_rect)

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.on_click):
                    self.on_click()
                return True
        return False
