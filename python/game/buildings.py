import pygame
from .consts import COLORS_BY_BUILDING

BUILDINGS = [
    { 'key': 'dorm', 'name': 'Dormitory',  'rect': pygame.Rect(40, 420, 160, 120) },
    { 'key': 'classroom', 'name': 'Classroom', 'rect': pygame.Rect(80, 70, 200, 120) },
    { 'key': 'library', 'name': 'Library', 'rect': pygame.Rect(600, 60, 220, 140) },
    { 'key': 'cafeteria', 'name': 'Cafeteria', 'rect': pygame.Rect(540, 320, 220, 140) },
    { 'key': 'admin', 'name': 'Admin Office', 'rect': pygame.Rect(260, 320, 220, 120) },
]


def get_buildings():
    return BUILDINGS


def color_for(key):
    return COLORS_BY_BUILDING.get(key, (100, 116, 139))
