import os
import sys
import random
import pygame
from pygame import Rect

from game.state import GameState
from game.consts import SCREEN_W, SCREEN_H, MAP_W, MAP_H, HUD_W, FPS, WHITE, BLACK, SLATE, BG_TOP, GRASS1, GRASS2, PATH, BORDER, PANEL, TEXT, MUTED, PRIMARY, SUCCESS, ENERGY_BG, ENERGY_BAR, DOOR
from game.buildings import get_buildings, color_for
from game.widgets import Button
from game import ui as UI

pygame.init()

SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Freshman Quest — Python Edition")
CLOCK = pygame.time.Clock()

FONT = pygame.font.SysFont("Segoe UI", 18)
FONT_SM = pygame.font.SysFont("Segoe UI", 14)
FONT_LG = pygame.font.SysFont("Segoe UI", 22, bold=True)
FONTS = { 'font': FONT, 'font_sm': FONT_SM, 'font_lg': FONT_LG }

state = GameState()

MAP_SURF = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
HUD_SURF = pygame.Surface((HUD_W, MAP_H), pygame.SRCALPHA)

PLAYER_SIZE = 22
player_rect = Rect(state.x, state.y, PLAYER_SIZE, PLAYER_SIZE)

buildings = get_buildings()

# Generate decor trees not overlapping buildings
TREE_POS = []
random.seed(42)
for _ in range(26):
    for tries in range(25):
        tx = random.randint(12, MAP_W - 12)
        ty = random.randint(12, MAP_H - 12)
        pt_rect = Rect(tx-8, ty-8, 16, 16)
        if not any(pt_rect.colliderect(b['rect']) for b in buildings):
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
    surface.fill(BG_TOP)
    # simple noise-like grass
    for y in range(0, MAP_H, 16):
        for x in range(0, MAP_W, 16):
            c = GRASS1 if (x//16 + y//16) % 2 == 0 else GRASS2
            pygame.draw.rect(surface, c, Rect(x, y, 16, 16))


def draw_paths(surface: pygame.Surface):
    # main path lines
    pygame.draw.rect(surface, PATH, Rect(100, 260, 680, 40))
    pygame.draw.rect(surface, PATH, Rect(220, 120, 40, 300))
    pygame.draw.rect(surface, PATH, Rect(620, 120, 40, 300))


def draw_trees(surface: pygame.Surface):
    for (tx, ty) in TREE_POS:
        pygame.draw.circle(surface, (22, 101, 52), (tx, ty), 7)
        pygame.draw.circle(surface, (34, 197, 94), (tx, ty), 5)
        pygame.draw.rect(surface, (100, 67, 33), Rect(tx-1, ty+3, 2, 6))


def draw_building(surface: pygame.Surface, b):
    rect = b['rect']
    color = color_for(b['key'])
    # body
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (17,24,39), rect, width=2, border_radius=10)
    # roof cap
    pygame.draw.rect(surface, (17,24,39), Rect(rect.x, rect.y-6, rect.w, 6))
    # door
    door_w, door_h = 28, 36
    door_x = rect.x + rect.w//2 - door_w//2
    door_y = rect.y + rect.h - door_h - 8
    pygame.draw.rect(surface, DOOR, Rect(door_x, door_y, door_w, door_h), border_radius=4)
    pygame.draw.rect(surface, (255,255,255,120), Rect(door_x, door_y, door_w, door_h), 1, border_radius=4)
    # windows grid
    grid_rect = Rect(rect.x+10, rect.y+10, rect.w-20, rect.h-30)
    cols = max(2, rect.w // 40)
    rows = max(2, rect.h // 40)
    cell_w = grid_rect.w // cols
    cell_h = grid_rect.h // rows
    for r in range(rows):
        for c in range(cols):
            wx = grid_rect.x + c*cell_w + 6
            wy = grid_rect.y + r*cell_h + 4
            ww, wh = max(18, cell_w-12), max(14, cell_h-10)
            win_rect = Rect(wx, wy, ww, wh)
            pygame.draw.rect(surface, (250,250,255), win_rect, border_radius=3)
            pygame.draw.rect(surface, (17,24,39,30), win_rect, 1, border_radius=3)


def draw_map(surface: pygame.Surface):
    draw_grass(surface)
    draw_paths(surface)
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
    title = FONT_LG.render("Freshman Quest", True, TEXT)
    surface.blit(title, (14,y)); y += 30

    # Stats panel
    stats_y = y
    pygame.draw.rect(surface, PANEL, Rect(12, stats_y, HUD_W-24, 120), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, stats_y, HUD_W-24, 120), 1, border_radius=12)
    y += 10
    surface.blit(FONT.render(f"XP: {state.xp}", True, TEXT), (24, y)); y += 22
    surface.blit(FONT.render(f"Rank: {state.rank_for_xp()}", True, TEXT), (24, y)); y += 22
    surface.blit(FONT.render("Energy:", True, TEXT), (24, y));
    draw_energy_bar(surface, 100, y+4, HUD_W-24-100, 14, state.energy/100.0)
    surface.blit(FONT_SM.render(f"{state.energy}", True, MUTED), (HUD_W-50, y));
    y = stats_y + 120 + 12

    # Inventory panel
    inv_h = 140
    pygame.draw.rect(surface, PANEL, Rect(12, y, HUD_W-24, inv_h), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, y, HUD_W-24, inv_h), 1, border_radius=12)
    surface.blit(FONT.render("Inventory", True, TEXT), (24, y+8))
    iy = y + 36
    for item in sorted(list(state.inventory))[:8]:
        surface.blit(FONT_SM.render(f"• {item}", True, TEXT), (24, iy)); iy += 20
    y += inv_h + 12

    # Quests panel
    quests_h = MAP_H - y - 12
    pygame.draw.rect(surface, PANEL, Rect(12, y, HUD_W-24, quests_h), border_radius=12)
    pygame.draw.rect(surface, BORDER, Rect(12, y, HUD_W-24, quests_h), 1, border_radius=12)
    surface.blit(FONT.render("Quests", True, TEXT), (24, y+8))
    qy = y + 36
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
        check = '☑' if done else '☐'
        surface.blit(FONT_SM.render(f"{check} {label}", True, (6,95,70) if done else TEXT), (24, qy)); qy += 20


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def check_overlap():
    global current_overlap
    ov = None
    for b in buildings:
        if player_rect.colliderect(b['rect']):
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
    pygame.draw.rect(surface, SUCCESS, player_rect, border_radius=6)
    pygame.draw.rect(surface, WHITE, player_rect, 2, border_radius=6)


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
        player_rect.x = clamp(player_rect.x + vx, 0, MAP_W - PLAYER_SIZE)
        player_rect.y = clamp(player_rect.y + vy, 0, MAP_H - PLAYER_SIZE)


def render():
    MAP_SURF.fill((0,0,0,0))
    draw_map(MAP_SURF)
    draw_player(MAP_SURF)

    HUD_SURF.fill((0,0,0,0))
    draw_hud(HUD_SURF)

    # blit map and hud
    SCREEN.blit(MAP_SURF, (12, 20))
    SCREEN.blit(HUD_SURF, (12 + MAP_W + 20, 20))

    # interact hint
    if current_overlap and not state.popup_open:
        bx = 12 + current_overlap['rect'].x + current_overlap['rect'].w//2
        by = 20 + current_overlap['rect'].y - 12
        tip = FONT_SM.render("Press E or Click", True, WHITE)
        pad = 6
        bg_rect = Rect(bx - tip.get_width()//2 - pad, by - tip.get_height()//2 - pad, tip.get_width()+pad*2, tip.get_height()+pad*2)
        pygame.draw.rect(SCREEN, BLACK, bg_rect, border_radius=12)
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
        SCREEN.blit(FONT_LG.render("Freshman Master Badge Earned!", True, TEXT), (card.x+18, card.y+16))
        SCREEN.blit(FONT.render("All orientation tasks completed. +100 XP", True, MUTED), (card.x+18, card.y+58))
        btn = Button(Rect(card.x+18, card.y+140, 150, 38), "Play Again", on_click=lambda: state.reset(), primary=True)
        btn.draw(SCREEN, FONT)


def handle_mouse(event):
    # popup buttons
    if active_popup and active_popup.handle_event(event):
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
    while running:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state.popup_open:
                        close_popup()
                if event.key == pygame.K_e:
                    if current_overlap and not state.popup_open:
                        open_popup_for(current_overlap['key'])
            elif event.type in (pygame.MOUSEBUTTONUP,):
                handle_mouse(event)

        keys = pygame.key.get_pressed()
        update_player(keys)

        ov = check_overlap()
        if ov is None:
            if suppress_until_exit:
                suppress_until_exit = False
            current_overlap = None
        else:
            if suppress_until_exit:
                pass
            else:
                if not state.popup_open:
                    # auto-open on new overlap
                    if current_overlap is None or ov['key'] != current_overlap['key']:
                        open_popup_for(ov['key'])
            current_overlap = ov

        render()
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
