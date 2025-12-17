import pygame
from pygame import Rect
from .consts import PANEL, BORDER, TEXT, WHITE, BLACK
from .widgets import Button

class Popup:
    def __init__(self, title, width=500, height=360):
        self.title = title
        self.rect = Rect(0, 0, width, height)
        self.buttons = []
        self.lines = []

    def center_on(self, screen_w, screen_h):
        self.rect.x = (screen_w - self.rect.w)//2
        self.rect.y = (screen_h - self.rect.h)//2

    def add_line(self, text, small=False, color=TEXT):
        self.lines.append((text, small, color))

    def add_button(self, text, on_click, primary=False, disabled=False):
        btn_w, btn_h = 200, 40
        self.buttons.append(Button(Rect(0,0,btn_w,btn_h), text, on_click, primary=primary, disabled=disabled))

    def _update_button_positions(self, screen_size):
        """Update button positions based on current popup position."""
        self.center_on(*screen_size)
        # Better button layout - wrap if needed
        bx = self.rect.x + 20
        by = self.rect.bottom - 20 - 40
        gap = 14
        max_width = self.rect.w - 40
        current_x = bx
        current_y = by
        
        for btn in self.buttons:
            if current_x + btn.rect.w > self.rect.x + max_width:
                # Wrap to next row
                current_x = bx
                current_y -= btn.rect.h + gap
            btn.rect.topleft = (current_x, current_y)
            current_x += btn.rect.w + gap

    def draw(self, surface, fonts, screen_size):
        font = fonts['font']
        font_sm = fonts['font_sm']
        font_lg = fonts['font_lg']

        self._update_button_positions(screen_size)
        
        # Enhanced overlay with gradient effect
        overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        overlay.fill((15,23,42,160))
        surface.blit(overlay, (0,0))

        # Popup shadow for depth
        shadow_offset = 4
        shadow_rect = Rect(self.rect.x + shadow_offset, self.rect.y + shadow_offset, 
                          self.rect.w, self.rect.h)
        shadow_surf = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 80))
        surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y), special_flags=pygame.BLEND_ALPHA_SDL2)

        # Main popup background with subtle gradient effect
        pygame.draw.rect(surface, PANEL, self.rect, border_radius=16)
        
        # Add subtle inner highlight at top
        highlight_rect = Rect(self.rect.x, self.rect.y, self.rect.w, 40)
        highlight_surf = pygame.Surface((self.rect.w, 40), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 30))
        surface.blit(highlight_surf, (highlight_rect.x, highlight_rect.y), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Enhanced border
        pygame.draw.rect(surface, BORDER, self.rect, 2, border_radius=16)
        
        # Title with icon space and better styling
        title_y = self.rect.y + 18
        title_text = font_lg.render(self.title, True, TEXT)
        # Add subtle underline decoration
        pygame.draw.line(surface, (79, 70, 229), 
                        (self.rect.x + 18, title_y + title_text.get_height() + 4),
                        (self.rect.x + 18 + title_text.get_width(), title_y + title_text.get_height() + 4), 2)
        surface.blit(title_text, (self.rect.x + 18, title_y))
        
        # Content area with better spacing and background
        content_bg = Rect(self.rect.x + 18, self.rect.y + 50, self.rect.w - 36, 
                         self.rect.bottom - 20 - 40 - (self.rect.y + 50) - 10)
        content_surf = pygame.Surface((content_bg.w, content_bg.h), pygame.SRCALPHA)
        content_surf.fill((248, 250, 252, 200))
        surface.blit(content_surf, (content_bg.x, content_bg.y), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        ly = self.rect.y + 65
        for text, small, color in self.lines:
            f = font_sm if small else font
            # Add bullet point for better readability
            if not small:
                bullet_color = (79, 70, 229)
                pygame.draw.circle(surface, bullet_color, (self.rect.x + 25, ly + f.get_height()//2), 3)
                text_x = self.rect.x + 35
            else:
                text_x = self.rect.x + 25
            # Text with slight shadow for readability
            text_surf = f.render(text, True, color)
            shadow_surf = f.render(text, True, (0, 0, 0, 30))
            surface.blit(shadow_surf, (text_x + 1, ly + 1))
            surface.blit(text_surf, (text_x, ly))
            ly += 28 if not small else 22

        # Buttons with better spacing
        for btn in self.buttons:
            btn.draw(surface, font)

    def handle_event(self, event, screen_size):
        """Handle events, ensuring button positions are updated first."""
        self._update_button_positions(screen_size)
        handled = False
        for btn in self.buttons:
            handled = btn.handle_event(event) or handled
        return handled
