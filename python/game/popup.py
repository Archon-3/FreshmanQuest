import pygame
from pygame import Rect
from .consts import PANEL, BORDER, TEXT, WHITE, BLACK
from .widgets import Button

class Popup:
    def __init__(self, title, width=440, height=320):
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
        btn_w, btn_h = 180, 36
        self.buttons.append(Button(Rect(0,0,btn_w,btn_h), text, on_click, primary=primary, disabled=disabled))

    def draw(self, surface, fonts, screen_size):
        font = fonts['font']
        font_sm = fonts['font_sm']
        font_lg = fonts['font_lg']

        self.center_on(*screen_size)
        overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        overlay.fill((15,23,42,140))
        surface.blit(overlay, (0,0))

        pygame.draw.rect(surface, PANEL, self.rect, border_radius=14)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=14)
        surface.blit(font_lg.render(self.title, True, TEXT), (self.rect.x+14, self.rect.y+12))
        ly = self.rect.y + 52
        for text, small, color in self.lines:
            f = font_sm if small else font
            surface.blit(f.render(text, True, color), (self.rect.x+14, ly))
            ly += 22

        bx = self.rect.x + 14
        by = self.rect.bottom - 14 - 36
        gap = 12
        for btn in self.buttons:
            btn.rect.topleft = (bx, by)
            btn.draw(surface, font)
            bx += btn.rect.w + gap

    def handle_event(self, event):
        handled = False
        for btn in self.buttons:
            handled = btn.handle_event(event) or handled
        return handled
