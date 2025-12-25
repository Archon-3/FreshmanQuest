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
        # Calculate button width based on text length to prevent text overflow
        font = pygame.font.SysFont("Segoe UI", 18)
        text_width = font.size(text)[0]
        btn_w = max(160, min(240, text_width + 28))  # Min 160, max 240, or fit text + padding
        btn_h = 38
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
        # Title shadow for depth
        title_shadow = font_lg.render(self.title, True, (0, 0, 0, 100))
        surface.blit(title_shadow, (self.rect.x + 19, title_y + 1))
        # Add subtle underline decoration
        pygame.draw.line(surface, (79, 70, 229), 
                        (self.rect.x + 18, title_y + title_text.get_height() + 4),
                        (self.rect.x + 18 + title_text.get_width(), title_y + title_text.get_height() + 4), 2)
        # Main title text
        surface.blit(title_text, (self.rect.x + 18, title_y))
        
        # Content area with better spacing and background
        content_padding = 20
        content_x = self.rect.x + content_padding
        content_y = self.rect.y + 55
        content_width = self.rect.w - (content_padding * 2)
        content_height = self.rect.bottom - 20 - 50 - content_y  # Space for buttons
        
        content_bg = Rect(content_x, content_y, content_width, content_height)
        content_surf = pygame.Surface((content_bg.w, content_bg.h), pygame.SRCALPHA)
        content_surf.fill((248, 250, 252, 180))
        surface.blit(content_surf, (content_bg.x, content_bg.y), special_flags=pygame.BLEND_ALPHA_SDL2)
        
        # Text rendering with word wrapping
        ly = content_y + 12
        max_text_width = content_width - 40  # Leave padding on both sides
        
        for text, small, color in self.lines:
            f = font_sm if small else font
            line_height = f.get_height() + 4
            
            # Word wrap text if it's too long
            words = text.split(' ')
            lines = []
            current_line = []
            current_width = 0
            
            for word in words:
                word_surf = f.render(word + ' ', True, color)
                word_width = word_surf.get_width()
                
                if current_width + word_width > max_text_width and current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width
                else:
                    current_line.append(word)
                    current_width += word_width
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Render each line
            for line_text in lines:
                if ly + line_height > content_bg.bottom - 10:
                    break  # Don't draw outside content area
                
                # Bullet point for first line of each item
                if line_text == lines[0] and not small:
                    bullet_color = (79, 70, 229)
                    pygame.draw.circle(surface, bullet_color, (content_x + 12, ly + line_height//2), 3)
                    text_x = content_x + 24
                else:
                    text_x = content_x + 12 if small else content_x + 24
                
                # Render text with enhanced shadow for better readability
                text_surf = f.render(line_text, True, color)
                # Enhanced shadow with better contrast
                shadow_surf = f.render(line_text, True, (0, 0, 0, 100))
                surface.blit(shadow_surf, (text_x + 1, ly + 1))
                # Main text
                surface.blit(text_surf, (text_x, ly))
                
                ly += line_height
            
            # Add spacing between items
            ly += 4

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
