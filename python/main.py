import os
import sys
import random
import pygame
from pygame import Rect

from game.state import GameState
from game.consts import SCREEN_W, SCREEN_H, MAP_W, MAP_H, HUD_W, FPS, WHITE, BLACK, SLATE, BG_TOP, GRASS1, GRASS2, ASPHALT, ASPHALT_DARK, ROAD_LINE, ROAD_EDGE, BORDER, PANEL, TEXT, MUTED, PRIMARY, SUCCESS, ENERGY_BG, ENERGY_BAR, DOOR
from game.buildings import get_buildings, color_for
from game.widgets import Button
from game import ui as UI

pygame.init()

SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Freshman Quest — Python Edition")
CLOCK = pygame.time.Clock()

# Font initialization with fallback handling
def get_font(size, bold=False):
    """Get font with fallback options."""
    font_list = ["Segoe UI", "Arial", "Helvetica", "sans-serif"]
    for font_name in font_list:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            # Test if font loaded correctly
            if font.size("Test")[0] > 0:
                return font
        except:
            continue
    # Ultimate fallback
    return pygame.font.Font(None, size)

FONT = get_font(18, bold=False)
FONT_SM = get_font(16, bold=True)  # Increased size and made bold for better clarity
FONT_LG = get_font(24, bold=True)
FONTS = { 'font': FONT, 'font_sm': FONT_SM, 'font_lg': FONT_LG }

state = GameState()

MAP_SURF = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
HUD_SURF = pygame.Surface((HUD_W, MAP_H), pygame.SRCALPHA)

PLAYER_SIZE = 22
player_rect = Rect(state.x, state.y, PLAYER_SIZE, PLAYER_SIZE)

buildings = get_buildings()

def is_on_road(x, y, road_width=50, side_road_width=40, margin=0):
    """Check if a point (or player center) is on a road."""
    main_road_y = MAP_H // 2
    main_road_margin = road_width // 2 + margin
    
    # Check if on main horizontal road
    if abs(y - main_road_y) < main_road_margin:
        return True
    
    # Check if on any vertical road connecting to buildings
    for b in buildings:
        building_rect = b['rect']
        gate_x = building_rect.centerx
        gate_y = building_rect.bottom
        
        road_margin = side_road_width // 2 + margin
        if abs(x - gate_x) < road_margin:
            if gate_y < main_road_y:
                if gate_y <= y <= main_road_y:
                    return True
            else:
                if main_road_y <= y <= gate_y:
                    return True
        
        # Allow player to be near building doors (extend road area around doors)
        door_proximity = 40  # Extended area around doors for entry
        distance_to_door = ((x - gate_x)**2 + (y - gate_y)**2)**0.5
        if distance_to_door <= door_proximity:
            return True
    
    return False

def is_player_on_road(player_rect, road_width=50, side_road_width=40):
    """Check if player (using center point) is on a road."""
    px, py = player_rect.centerx, player_rect.centery
    return is_on_road(px, py, road_width, side_road_width, margin=2)

# Generate decor trees not overlapping buildings or roads
TREE_POS = []
random.seed(42)
for _ in range(26):
    for tries in range(50):
        tx = random.randint(12, MAP_W - 12)
        ty = random.randint(12, MAP_H - 12)
        pt_rect = Rect(tx-8, ty-8, 16, 16)
        if not any(pt_rect.colliderect(b['rect']) for b in buildings) and not is_on_road(tx, ty):
            TREE_POS.append((tx, ty))
            break

# Popup state
active_popup = None
suppress_until_exit = False
current_overlap = None

# Buttons managed globally (popup and HUD)
buttons = []


def toast(text, color=(30,30,30)):
    # simple console placeholder (can be extended to visual toasts)
    print("[Toast]", text)


def draw_grass(surface: pygame.Surface):
    """Draw grass covering the entire campus area."""
    # Fill entire surface with base grass color
    surface.fill(GRASS1)
    
    # Create a more realistic grass pattern with variation
    for y in range(0, MAP_H, 8):
        for x in range(0, MAP_W, 8):
            # Create a more organic checkerboard pattern
            pattern = (x//8 + y//8) % 2
            if pattern == 0:
                c = GRASS2
            else:
                c = GRASS1
            pygame.draw.rect(surface, c, Rect(x, y, 8, 8))
    
    # Add some random grass texture spots for realism
    for _ in range(50):
        tx = random.randint(0, MAP_W - 4)
        ty = random.randint(0, MAP_H - 4)
        # Slightly darker or lighter grass patches
        patch_color = GRASS2 if random.random() > 0.5 else (220, 245, 210)
        pygame.draw.rect(surface, patch_color, Rect(tx, ty, 4, 4))


def draw_gates(surface: pygame.Surface):
    """Draw yellow gates at the left and right edges of the main road."""
    main_road_y = MAP_H // 2
    gate_width = 100  # Larger gate
    gate_height = 120  # Taller gate
    
    # Left gate
    left_gate_x = 0
    left_gate_rect = Rect(left_gate_x, main_road_y - gate_height//2, gate_width, gate_height)
    
    # Gate structure - yellow archway
    gate_color = (255, 215, 0)  # Gold/Yellow
    gate_dark = (200, 170, 0)  # Darker yellow
    gate_light = (255, 235, 100)  # Lighter yellow
    
    # Left pillar
    pygame.draw.rect(surface, gate_color, Rect(left_gate_x, main_road_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(left_gate_x + 3, main_road_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_dark, Rect(left_gate_x, main_road_y - gate_height//2, 18, gate_height//3))
    
    # Right pillar
    pygame.draw.rect(surface, gate_color, Rect(left_gate_x + gate_width - 18, main_road_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(left_gate_x + gate_width - 15, main_road_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_dark, Rect(left_gate_x + gate_width - 18, main_road_y - gate_height//2, 18, gate_height//3))
    
    # Arch top
    arch_top = main_road_y - gate_height//2
    pygame.draw.arc(surface, gate_color, Rect(left_gate_x, arch_top - 20, gate_width, 40), 0, 3.14, 12)
    pygame.draw.arc(surface, gate_dark, Rect(left_gate_x + 2, arch_top - 18, gate_width - 4, 36), 0, 3.14, 8)
    
    # Gate sign
    sign_text = FONT.render("EXIT", True, BLACK)
    sign_bg = Rect(left_gate_x + gate_width//2 - sign_text.get_width()//2 - 6, arch_top - 8, 
                  sign_text.get_width() + 12, sign_text.get_height() + 6)
    pygame.draw.rect(surface, WHITE, sign_bg, border_radius=4)
    pygame.draw.rect(surface, BLACK, sign_bg, 2, border_radius=4)
    # Text shadow for depth
    sign_shadow = FONT.render("EXIT", True, (100, 100, 100, 100))
    surface.blit(sign_shadow, (left_gate_x + gate_width//2 - sign_text.get_width()//2 + 1, arch_top - 4))
    surface.blit(sign_text, (left_gate_x + gate_width//2 - sign_text.get_width()//2, arch_top - 5))
    
    # Right gate
    right_gate_x = MAP_W - gate_width
    right_gate_rect = Rect(right_gate_x, main_road_y - gate_height//2, gate_width, gate_height)
    
    # Right gate structure
    pygame.draw.rect(surface, gate_color, Rect(right_gate_x, main_road_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(right_gate_x + 3, main_road_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_dark, Rect(right_gate_x, main_road_y - gate_height//2, 18, gate_height//3))
    
    pygame.draw.rect(surface, gate_color, Rect(right_gate_x + gate_width - 18, main_road_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(right_gate_x + gate_width - 15, main_road_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_dark, Rect(right_gate_x + gate_width - 18, main_road_y - gate_height//2, 18, gate_height//3))
    
    pygame.draw.arc(surface, gate_color, Rect(right_gate_x, arch_top - 20, gate_width, 40), 0, 3.14, 12)
    pygame.draw.arc(surface, gate_dark, Rect(right_gate_x + 2, arch_top - 18, gate_width - 4, 36), 0, 3.14, 8)
    
    sign_text2 = FONT.render("EXIT", True, BLACK)
    sign_bg2 = Rect(right_gate_x + gate_width//2 - sign_text2.get_width()//2 - 6, arch_top - 8, 
                   sign_text2.get_width() + 12, sign_text2.get_height() + 6)
    pygame.draw.rect(surface, WHITE, sign_bg2, border_radius=4)
    pygame.draw.rect(surface, BLACK, sign_bg2, 2, border_radius=4)
    # Text shadow for depth
    sign_shadow2 = FONT.render("EXIT", True, (100, 100, 100, 100))
    surface.blit(sign_shadow2, (right_gate_x + gate_width//2 - sign_text2.get_width()//2 + 1, arch_top - 4))
    surface.blit(sign_text2, (right_gate_x + gate_width//2 - sign_text2.get_width()//2, arch_top - 5))
    
    return left_gate_rect, right_gate_rect


def update_city_player(keys):
    """Update player movement in city view - restricted to city road."""
    road_y = SCREEN_H - 100
    road_center_y = road_y + 50  # Center of the road
    
    dx = dy = 0
    if keys[pygame.K_LEFT]: dx -= 1
    if keys[pygame.K_RIGHT]: dx += 1
    if keys[pygame.K_UP]: dy -= 1
    if keys[pygame.K_DOWN]: dy += 1
    
    if dx or dy:
        length = max(1, (dx*dx + dy*dy) ** 0.5)
        vx = (dx/length) * state.speed
        vy = (dy/length) * state.speed
        
        # New position
        new_x = state.city_player_x + vx
        new_y = state.city_player_y + vy
        
        # Allow movement to edges (including gates) - allow reaching gate areas
        new_x = clamp(new_x, -50, SCREEN_W + 50)
        
        # Keep player on the road (center Y should be near road center)
        road_margin = 20  # Allow some vertical movement on road
        if abs(new_y - road_center_y) < road_margin:
            state.city_player_x = new_x
            state.city_player_y = new_y
        else:
            # Only allow horizontal movement if trying to go off road
            state.city_player_x = new_x
            # Snap back to road center
            if new_y < road_center_y - road_margin:
                state.city_player_y = road_center_y - road_margin
            elif new_y > road_center_y + road_margin:
                state.city_player_y = road_center_y + road_margin


def check_city_gate_collision():
    """Check if player collides with city gate to return to campus."""
    if not state.show_city_view:
        return
    
    # Prevent immediate re-triggering after entering city
    if state.city_entry_cooldown > 0:
        state.city_entry_cooldown -= 1
        return
    
    px = state.city_player_x
    
    # Check if player is actually at the gate edges (more strict boundaries)
    # Gate width is 100, so check if player is at the actual gate areas
    # Left gate: x < 120, Right gate: x > SCREEN_W - 120
    left_gate_threshold = 120
    right_gate_threshold = SCREEN_W - 120
    
    if px < left_gate_threshold or px > right_gate_threshold:
        # Return to campus
        state.show_city_view = False
        state.transition_alpha = 255
        state.city_entry_cooldown = 60  # 1 second cooldown at 60 FPS
        toast("Returning to campus...")
        
        # Set campus player position
        if px < SCREEN_W // 2:
            player_rect.x = 50  # Left gate
            state.x = 50
        else:
            player_rect.x = MAP_W - 50  # Right gate
            state.x = MAP_W - 50
        player_rect.y = MAP_H // 2 - PLAYER_SIZE // 2
        state.y = MAP_H // 2 - PLAYER_SIZE // 2
        
        # Reset for next city visit
        state.city_player_x = 600
        state.city_player_y = 525


def draw_city_gates(surface: pygame.Surface):
    """Draw yellow gates at the edges of city road for returning to campus."""
    road_y = SCREEN_H - 100
    road_center_y = road_y + 50
    gate_width = 100
    gate_height = 80
    
    gate_color = (255, 215, 0)  # Yellow/Gold
    gate_dark = (200, 170, 0)
    gate_light = (255, 235, 100)
    
    # Left gate
    left_gate_x = 0
    pygame.draw.rect(surface, gate_color, Rect(left_gate_x, road_center_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(left_gate_x + 3, road_center_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_color, Rect(left_gate_x + gate_width - 18, road_center_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(left_gate_x + gate_width - 15, road_center_y - gate_height//2, 12, gate_height))
    
    arch_top = road_center_y - gate_height//2
    pygame.draw.arc(surface, gate_color, Rect(left_gate_x, arch_top - 15, gate_width, 30), 0, 3.14, 10)
    
    sign_text = FONT_SM.render("CAMPUS", True, BLACK)
    sign_bg = Rect(left_gate_x + gate_width//2 - sign_text.get_width()//2 - 6, arch_top - 5, 
                  sign_text.get_width() + 12, sign_text.get_height() + 4)
    pygame.draw.rect(surface, WHITE, sign_bg, border_radius=4)
    pygame.draw.rect(surface, BLACK, sign_bg, 2, border_radius=4)
    # Text shadow
    sign_shadow = FONT_SM.render("CAMPUS", True, (100, 100, 100, 100))
    surface.blit(sign_shadow, (left_gate_x + gate_width//2 - sign_text.get_width()//2 + 1, arch_top - 2))
    surface.blit(sign_text, (left_gate_x + gate_width//2 - sign_text.get_width()//2, arch_top - 3))
    
    # Right gate
    right_gate_x = SCREEN_W - gate_width
    pygame.draw.rect(surface, gate_color, Rect(right_gate_x, road_center_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(right_gate_x + 3, road_center_y - gate_height//2, 12, gate_height))
    pygame.draw.rect(surface, gate_color, Rect(right_gate_x + gate_width - 18, road_center_y - gate_height//2, 18, gate_height))
    pygame.draw.rect(surface, gate_light, Rect(right_gate_x + gate_width - 15, road_center_y - gate_height//2, 12, gate_height))
    
    pygame.draw.arc(surface, gate_color, Rect(right_gate_x, arch_top - 15, gate_width, 30), 0, 3.14, 10)
    
    sign_text2 = FONT_SM.render("CAMPUS", True, BLACK)
    sign_bg2 = Rect(right_gate_x + gate_width//2 - sign_text2.get_width()//2 - 6, arch_top - 5, 
                   sign_text2.get_width() + 12, sign_text2.get_height() + 4)
    pygame.draw.rect(surface, WHITE, sign_bg2, border_radius=4)
    pygame.draw.rect(surface, BLACK, sign_bg2, 2, border_radius=4)
    # Text shadow
    sign_shadow2 = FONT_SM.render("CAMPUS", True, (100, 100, 100, 100))
    surface.blit(sign_shadow2, (right_gate_x + gate_width//2 - sign_text2.get_width()//2 + 1, arch_top - 2))
    surface.blit(sign_text2, (right_gate_x + gate_width//2 - sign_text2.get_width()//2, arch_top - 3))


def draw_city_player(surface: pygame.Surface):
    """Draw player sprite in city view."""
    px, py = state.city_player_x, state.city_player_y
    size = PLAYER_SIZE
    
    # Shadow
    shadow_rect = Rect(px - size//2 + 2, py + size//2 - 1, size - 4, 5)
    shadow_surf = pygame.Surface((size, 5), pygame.SRCALPHA)
    for i in range(5):
        alpha = max(0, 50 - i * 10)
        shadow_surf.fill((0, 0, 0, alpha), Rect(0, i, size, 1))
    surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    # Head
    head_radius = 8
    head_y = py - size // 2 + head_radius + 3
    pygame.draw.circle(surface, (255, 220, 177), (px, head_y), head_radius)
    pygame.draw.circle(surface, (240, 200, 157), (px - 2, head_y - 1), head_radius - 1)
    pygame.draw.circle(surface, (200, 180, 150), (px, head_y), head_radius, 1)
    
    # Hair
    hair_color = (50, 30, 15)
    hair_light = (70, 45, 25)
    hair_rect = Rect(px - head_radius + 1, head_y - head_radius - 3, 
                     head_radius * 2 - 2, head_radius + 3)
    pygame.draw.ellipse(surface, hair_color, hair_rect)
    pygame.draw.ellipse(surface, hair_light, Rect(px - head_radius + 2, head_y - head_radius - 2, 
                                                  head_radius * 2 - 4, head_radius))
    
    # Neck
    neck_rect = Rect(px - 2, head_y + head_radius - 1, 4, 3)
    pygame.draw.rect(surface, (255, 220, 177), neck_rect)
    
    # Body
    body_top = head_y + head_radius + 2
    body_height = 10
    body_width = 10
    body_rect = Rect(px - body_width//2, body_top, body_width, body_height)
    shirt_color = (255, 80, 60)  # Bright red-orange shirt for visibility
    shirt_dark = (220, 50, 40)
    shirt_light = (255, 120, 100)
    pygame.draw.rect(surface, shirt_color, body_rect, border_radius=2)
    pygame.draw.rect(surface, shirt_dark, Rect(body_rect.x, body_rect.y, body_rect.w, body_rect.h//2), border_radius=2)
    pygame.draw.line(surface, shirt_light, (body_rect.x + 1, body_rect.y + body_rect.h//2), 
                    (body_rect.x + body_rect.w - 1, body_rect.y + body_rect.h//2), 1)
    pygame.draw.rect(surface, (180, 30, 20), body_rect, 1, border_radius=2)
    
    # Arms
    arm_width = 3
    arm_length = 8
    arm_y = body_top + 1
    left_arm_rect = Rect(px - body_width//2 - arm_width, arm_y, arm_width, arm_length)
    pygame.draw.rect(surface, (255, 220, 177), left_arm_rect, border_radius=1)
    pygame.draw.rect(surface, (240, 200, 157), Rect(left_arm_rect.x, left_arm_rect.y, arm_width, arm_length//2))
    right_arm_rect = Rect(px + body_width//2, arm_y, arm_width, arm_length)
    pygame.draw.rect(surface, (255, 220, 177), right_arm_rect, border_radius=1)
    pygame.draw.rect(surface, (240, 200, 157), Rect(right_arm_rect.x, right_arm_rect.y, arm_width, arm_length//2))
    
    # Hands
    hand_size = 2
    pygame.draw.circle(surface, (255, 220, 177), (px - body_width//2 - arm_width//2, arm_y + arm_length), hand_size)
    pygame.draw.circle(surface, (255, 220, 177), (px + body_width//2 + arm_width//2, arm_y + arm_length), hand_size)
    
    # Legs
    leg_top = body_top + body_height
    leg_width = 4
    leg_height = 9
    pants_color = (255, 220, 0)  # Yellow trousers
    pants_dark = (220, 190, 0)
    left_leg_rect = Rect(px - leg_width - 1, leg_top, leg_width, leg_height)
    pygame.draw.rect(surface, pants_color, left_leg_rect, border_radius=1)
    pygame.draw.rect(surface, pants_dark, Rect(left_leg_rect.x, left_leg_rect.y, leg_width, leg_height//2))
    right_leg_rect = Rect(px + 1, leg_top, leg_width, leg_height)
    pygame.draw.rect(surface, pants_color, right_leg_rect, border_radius=1)
    pygame.draw.rect(surface, pants_dark, Rect(right_leg_rect.x, right_leg_rect.y, leg_width, leg_height//2))
    
    # Feet
    foot_y = leg_top + leg_height
    foot_width = 5
    foot_height = 3
    shoe_color = (255, 255, 255)  # White shoes
    shoe_sole = (200, 200, 200)
    foot_rect_l = Rect(px - foot_width - 1, foot_y, foot_width, foot_height)
    pygame.draw.rect(surface, shoe_color, foot_rect_l, border_radius=1)
    pygame.draw.rect(surface, shoe_sole, Rect(foot_rect_l.x, foot_rect_l.y + foot_height - 1, foot_width, 1))
    foot_rect_r = Rect(px + 1, foot_y, foot_width, foot_height)
    pygame.draw.rect(surface, shoe_color, foot_rect_r, border_radius=1)
    pygame.draw.rect(surface, shoe_sole, Rect(foot_rect_r.x, foot_rect_r.y + foot_height - 1, foot_width, 1))
    
    # Face
    eye_y = head_y - 2
    eye_size = 2
    pygame.draw.circle(surface, (255, 255, 255), (px - 3, eye_y), eye_size)
    pygame.draw.circle(surface, (0, 0, 0), (px - 3, eye_y), 1)
    pygame.draw.circle(surface, (255, 255, 255), (px + 3, eye_y), eye_size)
    pygame.draw.circle(surface, (0, 0, 0), (px + 3, eye_y), 1)
    pygame.draw.circle(surface, (240, 200, 157), (px, head_y + 1), 1)
    pygame.draw.arc(surface, (180, 100, 100), Rect(px - 3, head_y + 2, 6, 3), 0, 3.14, 1)


def draw_city_view(surface: pygame.Surface):
    """Draw city view with named buildings and moving cars when player reaches gate."""
    # Update car positions for animation
    if state.show_city_view:
        for i in range(len(state.city_car_positions)):
            state.city_car_positions[i] += 2  # Move cars to the right
            if state.city_car_positions[i] > SCREEN_W + 100:
                state.city_car_positions[i] = -100  # Reset to left side
    
    # Sky gradient
    for y in range(SCREEN_H):
        sky_color = (135 - y//8, 206 - y//8, 250 - y//8)
        pygame.draw.line(surface, sky_color, (0, y), (SCREEN_W, y))
    
    # City buildings with names
    buildings_data = [
        {'name': 'Geda Hotel', 'x': 50, 'color': (100, 80, 80), 'height': 240, 'width': 100},
        {'name': 'Stationary', 'x': 180, 'color': (80, 100, 80), 'height': 200, 'width': 90},
        {'name': 'Supermarket', 'x': 300, 'color': (80, 80, 100), 'height': 220, 'width': 110},
    ]
    
    for building in buildings_data:
        building_rect = Rect(building['x'], SCREEN_H - building['height'], building['width'], building['height'])
        # Building body
        pygame.draw.rect(surface, building['color'], building_rect)
        # Building border
        pygame.draw.rect(surface, (60, 60, 60), building_rect, 2)
        
        # Windows
        for wy in range(building_rect.top + 25, building_rect.bottom - 35, 30):
            for wx in range(building_rect.left + 10, building_rect.right - 10, 25):
                if random.random() > 0.3:  # Some windows lit
                    window_color = (255, 255, 200) if random.random() > 0.5 else (200, 200, 150)
                    pygame.draw.rect(surface, window_color, Rect(wx, wy, 15, 20))
        
        # Building name sign with improved styling
        name_text = FONT_SM.render(building['name'], True, WHITE)
        name_bg = Rect(building_rect.centerx - name_text.get_width()//2 - 8, 
                      building_rect.bottom - 30, name_text.get_width() + 16, name_text.get_height() + 6)
        # Enhanced background
        name_bg_surf = pygame.Surface((name_bg.w, name_bg.h), pygame.SRCALPHA)
        name_bg_surf.fill((0, 0, 0, 220))
        surface.blit(name_bg_surf, name_bg)
        # Border
        pygame.draw.rect(surface, (255, 255, 255, 200), name_bg, 2, border_radius=4)
        # Text shadow
        shadow_text = FONT_SM.render(building['name'], True, (0, 0, 0, 150))
        surface.blit(shadow_text, (building_rect.centerx - name_text.get_width()//2 + 1, building_rect.bottom - 27))
        # Main text
        surface.blit(name_text, (building_rect.centerx - name_text.get_width()//2, building_rect.bottom - 28))
    
    # More buildings on right side
    building_x = SCREEN_W - 350
    building_colors = [(90, 90, 110), (70, 70, 90), (60, 60, 80)]
    for i, color in enumerate(building_colors):
        height = 180 + i * 50
        width = 70 + i * 15
        building_rect = Rect(building_x, SCREEN_H - height, width, height)
        pygame.draw.rect(surface, color, building_rect)
        pygame.draw.rect(surface, (60, 60, 60), building_rect, 2)
        # Windows
        for wy in range(building_rect.top + 20, building_rect.bottom - 10, 30):
            for wx in range(building_rect.left + 10, building_rect.right - 10, 25):
                if random.random() > 0.3:
                    window_color = (255, 255, 200) if random.random() > 0.5 else (200, 200, 150)
                    pygame.draw.rect(surface, window_color, Rect(wx, wy, 15, 20))
        building_x += width + 25
    
    # Road in city
    road_y = SCREEN_H - 100
    road_rect = Rect(0, road_y, SCREEN_W, 100)
    pygame.draw.rect(surface, ASPHALT, road_rect)
    
    # Road center line (moving for animation effect)
    dash_length = 30
    dash_gap = 20
    offset = (pygame.time.get_ticks() // 20) % (dash_length + dash_gap)
    x = -offset
    while x < SCREEN_W:
        pygame.draw.line(surface, ROAD_LINE, (x, road_y + 50), (x + dash_length, road_y + 50), 4)
        x += dash_length + dash_gap
    
    # Draw gates on the road
    draw_city_gates(surface)
    
    # Moving cars on the road
    car_colors = [(200, 50, 50), (50, 50, 200), (50, 150, 50), (200, 150, 50), (150, 50, 200)]
    for i, car_x in enumerate(state.city_car_positions[:5]):
        if -100 <= car_x <= SCREEN_W + 100:  # Only draw if visible
            car_y = road_y + 25 + (i % 2) * 35
            car_color = car_colors[i % len(car_colors)]
            # Car body
            car_rect = Rect(car_x, car_y, 60, 30)
            pygame.draw.rect(surface, car_color, car_rect, border_radius=5)
            # Car windows
            pygame.draw.rect(surface, (100, 150, 200), Rect(car_x + 5, car_y + 5, 50, 20), border_radius=3)
            # Car wheels
            pygame.draw.circle(surface, (30, 30, 30), (car_x + 12, car_y + 30), 8)
            pygame.draw.circle(surface, (30, 30, 30), (car_x + 48, car_y + 30), 8)
            # Wheel highlights
            pygame.draw.circle(surface, (60, 60, 60), (car_x + 12, car_y + 30), 5)
            pygame.draw.circle(surface, (60, 60, 60), (car_x + 48, car_y + 30), 5)
    
    # Draw player in city
    draw_city_player(surface)
    
    # Show hint when player is near a gate
    px, py = state.city_player_x, state.city_player_y
    road_center_y = SCREEN_H - 50
    near_left = px < 150 and abs(py - road_center_y) < 60
    near_right = px > SCREEN_W - 150 and abs(py - road_center_y) < 60
    
    if near_left or near_right:
        hint_text = FONT_SM.render("Returning to campus...", True, WHITE)
        hint_bg = Rect(px - hint_text.get_width()//2 - 10, py - 40, 
                      hint_text.get_width() + 20, hint_text.get_height() + 8)
        pygame.draw.rect(surface, (0, 0, 0, 220), hint_bg, border_radius=6)
        pygame.draw.rect(surface, (255, 215, 0), hint_bg, 2, border_radius=6)
        surface.blit(hint_text, (px - hint_text.get_width()//2, py - 36))
    
    # Title text with enhanced styling
    title_text = FONT_LG.render("Welcome to the City!", True, WHITE)
    title_shadow = FONT_LG.render("Welcome to the City!", True, (0, 0, 0, 150))
    title_bg = Rect(SCREEN_W//2 - title_text.get_width()//2 - 20, 50, 
                   title_text.get_width() + 40, title_text.get_height() + 20)
    title_bg_surf = pygame.Surface((title_bg.w, title_bg.h), pygame.SRCALPHA)
    title_bg_surf.fill((0, 0, 0, 200))
    surface.blit(title_bg_surf, title_bg)
    pygame.draw.rect(surface, (255, 255, 255, 180), title_bg, 2, border_radius=10)
    # Shadow
    surface.blit(title_shadow, (SCREEN_W//2 - title_text.get_width()//2 + 2, 62))
    # Main text
    surface.blit(title_text, (SCREEN_W//2 - title_text.get_width()//2, 60))
    
    # Instructions with enhanced styling
    return_text = FONT_SM.render("Walk to gate to return to campus", True, WHITE)
    return_shadow = FONT_SM.render("Walk to gate to return to campus", True, (0, 0, 0, 150))
    return_bg = Rect(SCREEN_W//2 - return_text.get_width()//2 - 20, SCREEN_H - 40, 
                    return_text.get_width() + 40, return_text.get_height() + 10)
    return_bg_surf = pygame.Surface((return_bg.w, return_bg.h), pygame.SRCALPHA)
    return_bg_surf.fill((0, 0, 0, 200))
    surface.blit(return_bg_surf, return_bg)
    pygame.draw.rect(surface, (255, 255, 255, 150), return_bg, 2, border_radius=8)
    # Shadow
    surface.blit(return_shadow, (SCREEN_W//2 - return_text.get_width()//2 + 1, SCREEN_H - 34))
    # Main text
    surface.blit(return_text, (SCREEN_W//2 - return_text.get_width()//2, SCREEN_H - 35))


def draw_paths(surface: pygame.Surface):
    """Draw realistic asphalt roads with white center lines."""
    road_width = 50  # Width of main roads
    side_road_width = 40  # Width of roads connecting to buildings
    
    # Main horizontal road from left to right edge (through the middle)
    main_road_y = MAP_H // 2  # Center vertically
    main_road_rect = Rect(0, main_road_y - road_width//2, MAP_W, road_width)
    
    # Draw main road asphalt
    pygame.draw.rect(surface, ASPHALT, main_road_rect)
    # Road edge lines
    pygame.draw.line(surface, ROAD_EDGE, (0, main_road_rect.top), (MAP_W, main_road_rect.top), 2)
    pygame.draw.line(surface, ROAD_EDGE, (0, main_road_rect.bottom), (MAP_W, main_road_rect.bottom), 2)
    
    # White center line (dashed) on main road
    dash_length = 20
    dash_gap = 15
    center_y = main_road_y
    x = 0
    while x < MAP_W:
        pygame.draw.line(surface, ROAD_LINE, (x, center_y), (x + dash_length, center_y), 3)
        x += dash_length + dash_gap
    
    # Vertical roads connecting to buildings
    for b in buildings:
        building_rect = b['rect']
        # Determine gate position (center bottom of building - where door is)
        gate_x = building_rect.centerx
        gate_y = building_rect.bottom
        
        # Calculate road start position (where it meets the main road)
        road_start_x = gate_x
        road_start_y = main_road_y
        
        # Determine if building is above or below main road
        if gate_y < main_road_y:
            # Building is above main road - road goes up from main road to building gate
            road_top = gate_y
            road_bottom = main_road_y
            road_rect = Rect(road_start_x - side_road_width//2, road_top, 
                           side_road_width, road_bottom - road_top)
        else:
            # Building is below main road - road goes down from main road to building gate
            road_top = main_road_y
            road_bottom = gate_y
            road_rect = Rect(road_start_x - side_road_width//2, road_top, 
                           side_road_width, road_bottom - road_top)
        
        # Draw vertical road asphalt (only if road has height)
        if road_rect.height > 0:
            pygame.draw.rect(surface, ASPHALT, road_rect)
            # Road edge lines
            pygame.draw.line(surface, ROAD_EDGE, (road_rect.left, road_rect.top), 
                            (road_rect.left, road_rect.bottom), 2)
            pygame.draw.line(surface, ROAD_EDGE, (road_rect.right, road_rect.top), 
                            (road_rect.right, road_rect.bottom), 2)
            
            # White center line (dashed) on vertical roads
            center_x = road_start_x
            y = road_rect.top
            while y < road_rect.bottom:
                end_y = min(y + dash_length, road_rect.bottom)
                pygame.draw.line(surface, ROAD_LINE, (center_x, y), (center_x, end_y), 3)
                y += dash_length + dash_gap
    
    # Add some texture/shading to roads for realism
    # Subtle darker patches on asphalt
    for i in range(0, MAP_W, 30):
        for j in range(main_road_rect.top, main_road_rect.bottom, 30):
            if (i + j) % 60 == 0:
                pygame.draw.circle(surface, ASPHALT_DARK, (i, j), 3)
    
    # Draw intersection markings (stop lines) where vertical roads meet main road
    for b in buildings:
        building_rect = b['rect']
        gate_x = building_rect.centerx
        stop_line_width = 30
        stop_line_thickness = 4
        # Stop line on vertical road before main road
        pygame.draw.line(surface, ROAD_LINE, 
                        (gate_x - stop_line_width//2, main_road_y - stop_line_thickness//2),
                        (gate_x + stop_line_width//2, main_road_y - stop_line_thickness//2), 
                        stop_line_thickness)
        pygame.draw.line(surface, ROAD_LINE, 
                        (gate_x - stop_line_width//2, main_road_y + stop_line_thickness//2),
                        (gate_x + stop_line_width//2, main_road_y + stop_line_thickness//2), 
                        stop_line_thickness)


def draw_trees(surface: pygame.Surface):
    for (tx, ty) in TREE_POS:
        # Trunk - more realistic brown with texture
        trunk_color = (101, 67, 33)
        trunk_dark = (80, 50, 25)
        trunk_rect = Rect(tx-2, ty+6, 4, 10)
        pygame.draw.rect(surface, trunk_color, trunk_rect)
        pygame.draw.line(surface, trunk_dark, (tx, ty+6), (tx, ty+16), 1)
        
        # Foliage - layered circles for depth
        # Bottom layer (darker, larger)
        pygame.draw.circle(surface, (15, 80, 40), (tx, ty-2), 9)
        # Middle layer
        pygame.draw.circle(surface, (22, 101, 52), (tx-3, ty-4), 7)
        pygame.draw.circle(surface, (22, 101, 52), (tx+3, ty-4), 7)
        # Top layer (lighter, smaller)
        pygame.draw.circle(surface, (34, 197, 94), (tx, ty-6), 6)
        # Highlights
        pygame.draw.circle(surface, (56, 211, 106), (tx-2, ty-5), 4)
        pygame.draw.circle(surface, (56, 211, 106), (tx+2, ty-5), 4)


def draw_building(surface: pygame.Surface, b):
    rect = b['rect']
    color = color_for(b['key'])
    
    # Building shadow for depth
    shadow_offset = 3
    shadow_rect = Rect(rect.x + shadow_offset, rect.y + shadow_offset, rect.w, rect.h)
    shadow_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    shadow_surf.fill((0, 0, 0, 40))
    surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    # Main building body with texture effect
    pygame.draw.rect(surface, color, rect, border_radius=8)
    # Add subtle texture lines
    for i in range(rect.y + 15, rect.y + rect.h - 15, 8):
        pygame.draw.line(surface, tuple(max(0, c-15) for c in color), (rect.x+2, i), (rect.x+rect.w-2, i), 1)
    
    # Building border
    pygame.draw.rect(surface, (17,24,39), rect, width=2, border_radius=8)
    
    # Realistic roof with shingles
    roof_height = 12
    roof_rect = Rect(rect.x-2, rect.y-roof_height, rect.w+4, roof_height)
    roof_color = (40, 30, 20)  # Dark brown shingles
    pygame.draw.polygon(surface, roof_color, [
        (rect.x-2, rect.y),
        (rect.x + rect.w//2, rect.y - roof_height - 2),
        (rect.x + rect.w + 2, rect.y)
    ])
    # Roof shingle lines
    for i in range(0, roof_height, 3):
        y_offset = rect.y - i
        x1 = rect.x - 2 + (i * 2)
        x2 = rect.x + rect.w + 2 - (i * 2)
        if x1 < x2:
            pygame.draw.line(surface, (30, 20, 15), (x1, y_offset), (x2, y_offset), 1)
    
    # Realistic door with frame and handle
    door_w, door_h = 32, 42
    door_x = rect.x + rect.w//2 - door_w//2
    door_y = rect.y + rect.h - door_h - 10
    
    # Door frame
    frame_thickness = 3
    frame_rect = Rect(door_x - frame_thickness, door_y - frame_thickness, 
                      door_w + frame_thickness*2, door_h + frame_thickness*2)
    pygame.draw.rect(surface, (60, 50, 40), frame_rect, border_radius=5)
    
    # Door itself
    door_color = (55, 45, 35)
    pygame.draw.rect(surface, door_color, Rect(door_x, door_y, door_w, door_h), border_radius=4)
    # Door panels
    pygame.draw.rect(surface, (45, 35, 25), Rect(door_x+2, door_y+2, door_w-4, door_h//2-2), border_radius=2)
    pygame.draw.rect(surface, (45, 35, 25), Rect(door_x+2, door_y+door_h//2, door_w-4, door_h//2-2), border_radius=2)
    # Door handle
    handle_x = door_x + door_w - 8
    handle_y = door_y + door_h//2
    pygame.draw.circle(surface, (180, 180, 180), (handle_x, handle_y), 3)
    pygame.draw.circle(surface, (100, 100, 100), (handle_x, handle_y), 2)
    
    # Realistic windows with frames and glass
    grid_rect = Rect(rect.x+12, rect.y+15, rect.w-24, rect.h-50)
    cols = max(2, rect.w // 45)
    rows = max(2, rect.h // 45)
    cell_w = grid_rect.w // cols
    cell_h = grid_rect.h // rows
    
    for r in range(rows):
        for c in range(cols):
            wx = grid_rect.x + c*cell_w + 4
            wy = grid_rect.y + r*cell_h + 4
            ww, wh = max(20, cell_w-8), max(18, cell_h-8)
            
            # Window frame (outer)
            frame_color = (80, 70, 60)
            win_frame = Rect(wx-2, wy-2, ww+4, wh+4)
            pygame.draw.rect(surface, frame_color, win_frame, border_radius=2)
            
            # Window glass with reflection
            glass_color = (200, 220, 240)
            win_rect = Rect(wx, wy, ww, wh)
            pygame.draw.rect(surface, glass_color, win_rect, border_radius=2)
            
            # Glass reflection highlight
            highlight = Rect(wx+2, wy+2, ww//2, wh//2)
            pygame.draw.rect(surface, (240, 250, 255), highlight, border_radius=1)
            
            # Window cross (mullions)
            mid_x, mid_y = wx + ww//2, wy + wh//2
            pygame.draw.line(surface, frame_color, (wx, mid_y), (wx+ww, mid_y), 2)
            pygame.draw.line(surface, frame_color, (mid_x, wy), (mid_x, wy+wh), 2)
            
            # Window sill
            pygame.draw.rect(surface, (100, 90, 80), Rect(wx-2, wy+wh, ww+4, 2))
    
    # Building name sign with improved styling
    building_name = b.get('name', 'Building')
    name_text = FONT_SM.render(building_name, True, WHITE)
    # Position name above the door or on the building front
    name_y = rect.y + 25
    name_bg = Rect(rect.centerx - name_text.get_width()//2 - 8, 
                  name_y - 3, name_text.get_width() + 16, name_text.get_height() + 6)
    # Enhanced semi-transparent background for better readability
    name_bg_surf = pygame.Surface((name_bg.w, name_bg.h), pygame.SRCALPHA)
    name_bg_surf.fill((0, 0, 0, 220))
    surface.blit(name_bg_surf, name_bg)
    # Border with rounded corners
    pygame.draw.rect(surface, (255, 255, 255, 200), name_bg, 2, border_radius=4)
    # Text shadow for depth
    shadow_text = FONT_SM.render(building_name, True, (0, 0, 0, 150))
    surface.blit(shadow_text, (rect.centerx - name_text.get_width()//2 + 1, name_y + 1))
    # Main text
    surface.blit(name_text, (rect.centerx - name_text.get_width()//2, name_y))


def draw_map(surface: pygame.Surface):
    draw_grass(surface)
    draw_paths(surface)
    draw_gates(surface)  # Draw gates at road edges
    for b in buildings:
        draw_building(surface, b)
    draw_trees(surface)


def draw_energy_bar(surface, x, y, w, h, pct):
    pygame.draw.rect(surface, ENERGY_BG, Rect(x, y, w, h), border_radius=8)
    fill_w = int((w-2) * max(0, min(1.0, pct)))
    if fill_w > 0:
        pygame.draw.rect(surface, ENERGY_BAR, Rect(x+1, y+1, fill_w, h-2), border_radius=8)
    pygame.draw.rect(surface, BORDER, Rect(x, y, w, h), 1, border_radius=8)


def draw_hud(surface: pygame.Surface):
    surface.fill((0,0,0,0))
    # panel base
    pygame.draw.rect(surface, PANEL, Rect(0,0,HUD_W, MAP_H), border_radius=14)
    pygame.draw.rect(surface, BORDER, Rect(0,0,HUD_W, MAP_H), 1, border_radius=14)

    y = 12
    # Title - clear and sharp, no shadow
    title = FONT_LG.render("Freshman Quest", True, (31, 41, 55))  # Use TEXT color, not deep black
    surface.blit(title, (14, y)); y += 32

    # Stats panel
    stats_y = y
    pygame.draw.rect(surface, PANEL, Rect(12, stats_y, HUD_W-24, 120), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, stats_y, HUD_W-24, 120), 1, border_radius=12)
    y += 12
    # XP - clear and sharp, no shadow
    xp_text = FONT.render(f"XP: {state.xp}", True, (0, 0, 0))  # Pure black for clarity
    surface.blit(xp_text, (24, y)); y += 24
    # Rank - clear and sharp, no shadow
    rank_text = FONT.render(f"Rank: {state.rank_for_xp()}", True, (0, 0, 0))  # Pure black for clarity
    surface.blit(rank_text, (24, y)); y += 24
    # Energy - clear and sharp, no shadow
    energy_label = FONT.render("Energy:", True, (0, 0, 0))  # Pure black for clarity
    surface.blit(energy_label, (24, y));
    draw_energy_bar(surface, 100, y+4, HUD_W-24-100, 14, state.energy/100.0)
    energy_val = FONT_SM.render(f"{state.energy}", True, (0, 0, 0))  # Pure black for clarity, no shadow
    surface.blit(energy_val, (HUD_W-50, y));
    y = stats_y + 120 + 12

    # Inventory panel
    inv_h = 140
    pygame.draw.rect(surface, PANEL, Rect(12, y, HUD_W-24, inv_h), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, y, HUD_W-24, inv_h), 1, border_radius=12)
    inv_title = FONT.render("Inventory", True, (0, 0, 0))  # Pure black for clarity, no shadow
    surface.blit(inv_title, (24, y+8))
    iy = y + 38
    for item in sorted(list(state.inventory))[:8]:
        item_text = FONT_SM.render(f"• {item}", True, (0, 0, 0))  # Pure black for clarity, no shadow
        surface.blit(item_text, (24, iy)); iy += 22
    y += inv_h + 12

    # Quests panel
    quests_h = MAP_H - y - 12
    pygame.draw.rect(surface, PANEL, Rect(12, y, HUD_W-24, quests_h), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, y, HUD_W-24, quests_h), 1, border_radius=12)
    quests_title = FONT.render("Quests", True, (0, 0, 0))  # Pure black for clarity, no shadow
    surface.blit(quests_title, (24, y+8))
    qy = y + 38
    quest_item_height = 28
    quest_item_width = HUD_W - 36
    
    for key, label in [
        ('firstClass','Attend your first class'),
        ('studentId','Get your student ID'),
        ('libraryVisit','Visit the library'),
        ('timetable','Collect your timetable'),
        ('eatMeal','Eat at the cafeteria'),
        ('chooseSchool','Choose your school'),
        ('programOrientation','Complete program orientation'),
        ('completeProgramCourses','Finish program core courses'),
        ('chooseDepartment','Choose your department'),
        ('completeDepartmentCourses','Finish department courses'),
    ]:
        done = state.quests.get(key, False)
        
        # Button background rectangle
        quest_rect = Rect(18, qy, quest_item_width, quest_item_height)
        
        # Different styling for completed vs incomplete quests
        if done:
            # Completed quest - green tinted background
            bg_color = (240, 253, 250)  # Light green background
            border_color = (16, 185, 129)  # Success green border
            text_color = (6, 95, 70)  # Dark green text
            check_symbol = '✓'
        else:
            # Incomplete quest - light gray background
            bg_color = (249, 250, 251)  # Very light gray background
            border_color = (229, 231, 235)  # Light gray border
            text_color = (31, 41, 55)  # Dark gray text
            check_symbol = '○'
        
        # Draw button background with rounded corners
        pygame.draw.rect(surface, bg_color, quest_rect, border_radius=6)
        # Draw border
        pygame.draw.rect(surface, border_color, quest_rect, width=1, border_radius=6)
        
        # Add subtle highlight at top for depth
        highlight_rect = Rect(quest_rect.x, quest_rect.y, quest_rect.w, 2)
        highlight_color = (255, 255, 255, 100) if done else (255, 255, 255, 60)
        highlight_surf = pygame.Surface((quest_rect.w, 2), pygame.SRCALPHA)
        highlight_surf.fill(highlight_color)
        surface.blit(highlight_surf, highlight_rect)
        
        # Render checkbox/checkmark with better styling
        check_text = FONT_SM.render(check_symbol, True, border_color if done else (156, 163, 175))
        surface.blit(check_text, (24, qy + 6))
        
        # Render quest label text
        quest_text = FONT_SM.render(label, True, text_color)
        surface.blit(quest_text, (42, qy + 6))
        
        qy += quest_item_height + 4  # Spacing between quest items


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def check_overlap():
    global current_overlap
    ov = None
    px, py = player_rect.centerx, player_rect.centery
    # Check proximity to building doors (doors are at bottom center of buildings)
    for b in buildings:
        building_rect = b['rect']
        door_x = building_rect.centerx
        door_y = building_rect.bottom
        # Check if player is near the door (within reasonable distance)
        # Allow entry if player is close to door or overlapping building
        door_proximity = 35  # Distance threshold for door entry
        distance_to_door = ((px - door_x)**2 + (py - door_y)**2)**0.5
        
        if distance_to_door <= door_proximity or player_rect.colliderect(building_rect):
            ov = b
            break
    if ov is None:
        return None
    current_overlap = ov
    return ov




def open_popup_for(key: str):
    global active_popup, suppress_until_exit
    helpers = {
        'addXP': state.add_xp,
        'addItem': state.add_item,
        'completeQuest': state.complete_quest,
        'setEnergy': state.set_energy,
        'state': state,
        'toast': toast,
        'close': close_popup,
        'rebuild': rebuild_popup
    }
    if key == 'dorm':
        active_popup = UI.dorm.build_popup(helpers)
    elif key == 'classroom':
        active_popup = UI.classroom.build_popup(helpers)
    elif key == 'library':
        active_popup = UI.library.build_popup(helpers)
    elif key == 'cafeteria':
        active_popup = UI.cafeteria.build_popup(helpers)
    elif key == 'admin':
        active_popup = UI.admin.build_popup(helpers)
    else:
        return
    state.popup_open = True
    suppress_until_exit = True


def rebuild_popup():
    # For UIs that want to refresh, re-open based on current_overlap
    global current_overlap
    if current_overlap:
        open_popup_for(current_overlap['key'])


def close_popup():
    global active_popup
    active_popup = None
    state.popup_open = False


def draw_player(surface: pygame.Surface):
    px, py = player_rect.centerx, player_rect.centery
    size = PLAYER_SIZE
    
    # Enhanced shadow with blur effect
    shadow_rect = Rect(px - size//2 + 2, py + size//2 - 1, size - 4, 5)
    shadow_surf = pygame.Surface((size, 5), pygame.SRCALPHA)
    # Create gradient shadow
    for i in range(5):
        alpha = max(0, 50 - i * 10)
        shadow_surf.fill((0, 0, 0, alpha), Rect(0, i, size, 1))
    surface.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
    
    # Head with better proportions
    head_radius = 8
    head_y = py - size // 2 + head_radius + 3
    
    # Head base (skin tone)
    pygame.draw.circle(surface, (255, 220, 177), (px, head_y), head_radius)
    # Head shading for depth
    pygame.draw.circle(surface, (240, 200, 157), (px - 2, head_y - 1), head_radius - 1)
    pygame.draw.circle(surface, (200, 180, 150), (px, head_y), head_radius, 1)
    
    # Hair with texture
    hair_color = (50, 30, 15)  # Dark brown hair
    hair_light = (70, 45, 25)
    hair_rect = Rect(px - head_radius + 1, head_y - head_radius - 3, 
                     head_radius * 2 - 2, head_radius + 3)
    pygame.draw.ellipse(surface, hair_color, hair_rect)
    # Hair highlights
    pygame.draw.ellipse(surface, hair_light, Rect(px - head_radius + 2, head_y - head_radius - 2, 
                                                  head_radius * 2 - 4, head_radius))
    
    # Neck
    neck_rect = Rect(px - 2, head_y + head_radius - 1, 4, 3)
    pygame.draw.rect(surface, (255, 220, 177), neck_rect)
    
    # Body (torso) - shirt with better proportions
    body_top = head_y + head_radius + 2
    body_height = 10
    body_width = 10
    body_rect = Rect(px - body_width//2, body_top, body_width, body_height)
    
    # Shirt with shading - bright red/orange for visibility on dark road
    shirt_color = (255, 80, 60)  # Bright red-orange shirt
    shirt_dark = (220, 50, 40)
    shirt_light = (255, 120, 100)
    pygame.draw.rect(surface, shirt_color, body_rect, border_radius=2)
    # Shirt shading
    pygame.draw.rect(surface, shirt_dark, Rect(body_rect.x, body_rect.y, body_rect.w, body_rect.h//2), border_radius=2)
    pygame.draw.line(surface, shirt_light, (body_rect.x + 1, body_rect.y + body_rect.h//2), 
                    (body_rect.x + body_rect.w - 1, body_rect.y + body_rect.h//2), 1)
    pygame.draw.rect(surface, (180, 30, 20), body_rect, 1, border_radius=2)
    
    # Arms with better positioning and shading
    arm_width = 3
    arm_length = 8
    arm_y = body_top + 1
    # Left arm
    left_arm_rect = Rect(px - body_width//2 - arm_width, arm_y, arm_width, arm_length)
    pygame.draw.rect(surface, (255, 220, 177), left_arm_rect, border_radius=1)
    pygame.draw.rect(surface, (240, 200, 157), Rect(left_arm_rect.x, left_arm_rect.y, arm_width, arm_length//2))
    # Right arm
    right_arm_rect = Rect(px + body_width//2, arm_y, arm_width, arm_length)
    pygame.draw.rect(surface, (255, 220, 177), right_arm_rect, border_radius=1)
    pygame.draw.rect(surface, (240, 200, 157), Rect(right_arm_rect.x, right_arm_rect.y, arm_width, arm_length//2))
    
    # Hands
    hand_size = 2
    pygame.draw.circle(surface, (255, 220, 177), (px - body_width//2 - arm_width//2, arm_y + arm_length), hand_size)
    pygame.draw.circle(surface, (255, 220, 177), (px + body_width//2 + arm_width//2, arm_y + arm_length), hand_size)
    
    # Legs (pants) with better proportions
    leg_top = body_top + body_height
    leg_width = 4
    leg_height = 9
    pants_color = (255, 220, 0)  # Yellow trousers
    pants_dark = (220, 190, 0)
    # Left leg
    left_leg_rect = Rect(px - leg_width - 1, leg_top, leg_width, leg_height)
    pygame.draw.rect(surface, pants_color, left_leg_rect, border_radius=1)
    pygame.draw.rect(surface, pants_dark, Rect(left_leg_rect.x, left_leg_rect.y, leg_width, leg_height//2))
    # Right leg
    right_leg_rect = Rect(px + 1, leg_top, leg_width, leg_height)
    pygame.draw.rect(surface, pants_color, right_leg_rect, border_radius=1)
    pygame.draw.rect(surface, pants_dark, Rect(right_leg_rect.x, right_leg_rect.y, leg_width, leg_height//2))
    
    # Feet (shoes) - more detailed
    foot_y = leg_top + leg_height
    foot_width = 5
    foot_height = 3
    shoe_color = (255, 255, 255)  # White shoes
    shoe_sole = (200, 200, 200)
    # Left foot
    foot_rect_l = Rect(px - foot_width - 1, foot_y, foot_width, foot_height)
    pygame.draw.rect(surface, shoe_color, foot_rect_l, border_radius=1)
    pygame.draw.rect(surface, shoe_sole, Rect(foot_rect_l.x, foot_rect_l.y + foot_height - 1, foot_width, 1))
    # Right foot
    foot_rect_r = Rect(px + 1, foot_y, foot_width, foot_height)
    pygame.draw.rect(surface, shoe_color, foot_rect_r, border_radius=1)
    pygame.draw.rect(surface, shoe_sole, Rect(foot_rect_r.x, foot_rect_r.y + foot_height - 1, foot_width, 1))
    
    # Enhanced face features
    # Eyes with whites
    eye_y = head_y - 2
    eye_size = 2
    # Left eye
    pygame.draw.circle(surface, (255, 255, 255), (px - 3, eye_y), eye_size)
    pygame.draw.circle(surface, (0, 0, 0), (px - 3, eye_y), 1)
    # Right eye
    pygame.draw.circle(surface, (255, 255, 255), (px + 3, eye_y), eye_size)
    pygame.draw.circle(surface, (0, 0, 0), (px + 3, eye_y), 1)
    
    # Nose
    pygame.draw.circle(surface, (240, 200, 157), (px, head_y + 1), 1)
    
    # Mouth
    pygame.draw.arc(surface, (180, 100, 100), Rect(px - 3, head_y + 2, 6, 3), 0, 3.14, 1)


def update_player(keys):
    dx = dy = 0
    if keys[pygame.K_LEFT]: dx -= 1
    if keys[pygame.K_RIGHT]: dx += 1
    if keys[pygame.K_UP]: dy -= 1
    if keys[pygame.K_DOWN]: dy += 1
    if dx or dy:
        length = max(1, (dx*dx + dy*dy) ** 0.5)
        vx = (dx/length) * state.speed
        vy = (dy/length) * state.speed
        
        # Try to move - only allow if new position is on road
        new_x = player_rect.x + vx
        new_y = player_rect.y + vy
        
        # Clamp to map boundaries first
        new_x = clamp(new_x, 0, MAP_W - PLAYER_SIZE)
        new_y = clamp(new_y, 0, MAP_H - PLAYER_SIZE)
        
        # Create temporary rect to check if new position is on road
        temp_rect = Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if is_player_on_road(temp_rect):
            player_rect.x = new_x
            player_rect.y = new_y
            # Synchronize state with player_rect
            state.x = new_x
            state.y = new_y
        else:
            # Try moving only horizontally or vertically if diagonal movement fails
            temp_rect_x = Rect(new_x, player_rect.y, PLAYER_SIZE, PLAYER_SIZE)
            temp_rect_y = Rect(player_rect.x, new_y, PLAYER_SIZE, PLAYER_SIZE)
            if is_player_on_road(temp_rect_x):
                player_rect.x = new_x
                state.x = new_x
            elif is_player_on_road(temp_rect_y):
                player_rect.y = new_y
                state.y = new_y


def check_gate_collision():
    """Check if player collides with gate and show city view."""
    if state.show_city_view:
        return  # Don't check if already in city view
    
    main_road_y = MAP_H // 2
    gate_width = 100  # Updated to match new gate size
    gate_height = 120  # Updated to match new gate size
    
    # Left gate
    left_gate_rect = Rect(0, main_road_y - gate_height//2, gate_width, gate_height)
    # Right gate
    right_gate_rect = Rect(MAP_W - gate_width, main_road_y - gate_height//2, gate_width, gate_height)
    
    # Check collision with gates (using center point for better detection)
    px, py = player_rect.centerx, player_rect.centery
    left_collision = left_gate_rect.collidepoint(px, py)
    right_collision = right_gate_rect.collidepoint(px, py)
    
    if left_collision or right_collision:
        if not state.show_city_view:
            state.show_city_view = True
            state.transition_alpha = 0  # Start transition
            state.city_entry_cooldown = 60  # 1 second cooldown at 60 FPS
            toast("Entering the city...")
            # Set city player position based on which gate was used
            road_center_y = SCREEN_H - 50  # City road center Y
            if left_collision:  # Left gate
                state.city_player_x = 400  # Start in safe zone, not too close to gate
            else:  # Right gate
                state.city_player_x = SCREEN_W - 400  # Start in safe zone, not too close to gate
            state.city_player_y = road_center_y  # On the road


def render():
    # Handle smooth transition
    if state.show_city_view:
        # Fade in city view smoothly
        if state.transition_alpha < 255:
            state.transition_alpha = min(255, state.transition_alpha + 20)
        
        SCREEN.fill((0, 0, 0))
        try:
            draw_city_view(SCREEN)
        except Exception as e:
            # Error handling for city view rendering
            error_text = FONT.render(f"Rendering error: {str(e)}", True, (255, 0, 0))
            SCREEN.blit(error_text, (10, 10))
        
        # Apply fade transition overlay
        if state.transition_alpha < 255:
            try:
                fade_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                fade_overlay.fill((0, 0, 0, 255 - state.transition_alpha))
                SCREEN.blit(fade_overlay, (0, 0))
            except:
                pass  # Skip fade if there's an issue
        return
    
    # Campus view - fade out transition overlay when returning
    if state.transition_alpha > 0:
        state.transition_alpha = max(0, state.transition_alpha - 25)  # Smooth fade out
    
    # Clear screen completely first
    SCREEN.fill(BG_TOP)
    
    # Draw campus map with error handling
    try:
        MAP_SURF.fill((0,0,0,0))
        draw_map(MAP_SURF)
        draw_player(MAP_SURF)
    except Exception as e:
        error_text = FONT.render(f"Map error: {str(e)}", True, (255, 0, 0))
        MAP_SURF.blit(error_text, (10, 10))

    # Draw HUD with error handling
    try:
        HUD_SURF.fill((0,0,0,0))
        draw_hud(HUD_SURF)
    except Exception as e:
        error_text = FONT.render(f"HUD error: {str(e)}", True, (255, 0, 0))
        HUD_SURF.blit(error_text, (10, 10))

    # Blit map and hud to screen
    SCREEN.blit(MAP_SURF, (12, 20))
    SCREEN.blit(HUD_SURF, (12 + MAP_W + 20, 20))
    
    # Apply fade transition overlay when returning to campus (fades from black to campus)
    if state.transition_alpha > 0:
        try:
            fade_overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            fade_overlay.fill((0, 0, 0))
            fade_overlay.set_alpha(state.transition_alpha)
            SCREEN.blit(fade_overlay, (0, 0))
        except:
            pass  # Skip fade if there's an issue

    # interact hint
    if current_overlap and not state.popup_open:
        bx = 12 + current_overlap['rect'].x + current_overlap['rect'].w//2
        by = 20 + current_overlap['rect'].y - 12
        tip = FONT_SM.render("Press E or Click", True, WHITE)
        tip_shadow = FONT_SM.render("Press E or Click", True, (0, 0, 0, 150))
        pad = 8
        bg_rect = Rect(bx - tip.get_width()//2 - pad, by - tip.get_height()//2 - pad, tip.get_width()+pad*2, tip.get_height()+pad*2)
        # Enhanced background
        bg_surf = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 220))
        SCREEN.blit(bg_surf, bg_rect)
        pygame.draw.rect(SCREEN, (255, 255, 255, 150), bg_rect, 2, border_radius=12)
        # Shadow
        SCREEN.blit(tip_shadow, (bg_rect.x+pad+1, bg_rect.y+pad+1))
        # Main text
        SCREEN.blit(tip, (bg_rect.x+pad, bg_rect.y+pad))

    # popup
    if active_popup:
        from game.popup import Popup  # noqa: F401 (ensures class available)
        active_popup.draw(SCREEN, FONTS, (SCREEN_W, SCREEN_H))

    # victory overlay
    if state.all_quests_done() and not state.victory_awarded:
        state.victory_awarded = True
        toast("Victory! +100 XP")
        state.add_xp(100)
    if state.victory_awarded:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((15,23,42,160))
        SCREEN.blit(overlay, (0,0))
        card = Rect((SCREEN_W-520)//2, (SCREEN_H-220)//2, 520, 220)
        pygame.draw.rect(SCREEN, PANEL, card, border_radius=16)
        pygame.draw.rect(SCREEN, BORDER, card, 1, border_radius=16)
        # Badge title with shadow
        badge_title = FONT_LG.render("Freshman Master Badge Earned!", True, TEXT)
        badge_title_shadow = FONT_LG.render("Freshman Master Badge Earned!", True, (0, 0, 0, 100))
        SCREEN.blit(badge_title_shadow, (card.x+19, card.y+17))
        SCREEN.blit(badge_title, (card.x+18, card.y+16))
        # Badge description with shadow
        badge_desc = FONT.render("All orientation tasks completed. +100 XP", True, MUTED)
        badge_desc_shadow = FONT.render("All orientation tasks completed. +100 XP", True, (0, 0, 0, 80))
        SCREEN.blit(badge_desc_shadow, (card.x+19, card.y+59))
        SCREEN.blit(badge_desc, (card.x+18, card.y+58))
        btn = Button(Rect(card.x+18, card.y+140, 150, 38), "Play Again", on_click=lambda: state.reset(), primary=True)
        btn.draw(SCREEN, FONT)


def handle_mouse(event):
    # popup buttons
    if active_popup and active_popup.handle_event(event, (SCREEN_W, SCREEN_H)):
        return True
    # click on building to open
    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        mx, my = event.pos
        mx -= 12; my -= 20
        for b in buildings:
            if b['rect'].collidepoint((mx, my)):
                if not state.popup_open:
                    open_popup_for(b['key'])
                return True
    return False


def main():
    global suppress_until_exit, current_overlap
    running = True
    try:
        while running:
            # Maintain consistent frame rate
            CLOCK.tick(FPS)
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if state.show_city_view:
                            state.transition_alpha = 255  # Start fade out
                            state.show_city_view = False
                            toast("Returning to campus...")
                        elif state.popup_open:
                            close_popup()
                    elif event.key == pygame.K_e:
                        if current_overlap and not state.popup_open:
                            open_popup_for(current_overlap['key'])
                elif event.type == pygame.MOUSEBUTTONUP:
                    handle_mouse(event)

            # Update game state
            try:
                keys = pygame.key.get_pressed()
                if state.show_city_view:
                    update_city_player(keys)
                    check_city_gate_collision()
                else:
                    update_player(keys)
                    check_gate_collision()

                ov = check_overlap()
                if ov is None:
                    if suppress_until_exit:
                        suppress_until_exit = False
                    current_overlap = None
                else:
                    current_overlap = ov
                    # Popups only open on E key press or click, not automatically

                # Render frame
                render()
                pygame.display.flip()
            except Exception as e:
                # Handle runtime errors gracefully
                print(f"Game loop error: {e}")
                import traceback
                traceback.print_exc()
                # Try to continue running
                try:
                    render()
                    pygame.display.flip()
                except:
                    running = False
    except KeyboardInterrupt:
        print("Game interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
