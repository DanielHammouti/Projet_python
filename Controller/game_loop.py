import time
import pygame
import sys
import random
from Models.Map import *
from Entity.Building import *
from Entity.Unit import *
from Models.Team import Team
from Controller.camera import Camera
from Controller.drawing import (
    draw_map,
    compute_map_bounds,
    create_minimap_background,
    display_fps,
    update_minimap_entities,
    draw_minimap_viewport,
    generate_team_colors,
    draw_pointer
)
import copy
from Controller.event_handler import handle_events
from Controller.update import update_game_state
from Controller.isometric_utils import tile_to_screen
from Controller.gui import create_player_selection_surface, create_player_info_surface, get_scaled_gui, draw_gui_elements
from Settings.setup import HALF_TILE_SIZE, MINIMAP_MARGIN, UPDATE_EVERY_N_MILLISECOND

PANEL_RATIO = 0.25
BG_RATIO    = 0.20

def get_centered_rect_in_bottom_right(width, height, screen_width, screen_height, margin=10):
    rect = pygame.Rect(0, 0, width, height)
    center_x = screen_width - margin - (width // 2)
    center_y = screen_height - margin - (height // 2)
    rect.center = (center_x, center_y)
    return rect

def game_loop(screen, game_map, screen_width, screen_height, players):
    """Main game loop handling updates, drawing, and event processing."""
    clock = pygame.time.Clock()
    pygame.key.set_repeat(0, 0)
    camera = Camera(screen_width, screen_height)
    team_colors = generate_team_colors(len(players))
    pygame.mouse.set_visible(False)

    min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
    camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)

    panel_width  = int(screen_width * PANEL_RATIO)
    panel_height = int(screen_height * PANEL_RATIO)
    minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
    minimap_panel_rect   = get_centered_rect_in_bottom_right(
        panel_width, panel_height, screen_width, screen_height, MINIMAP_MARGIN
    )

    bg_width  = int(screen_width * BG_RATIO)
    bg_height = int(screen_height * BG_RATIO)
    (minimap_background_surface,
     minimap_scale,
     minimap_offset_x,
     minimap_offset_y,
     minimap_min_iso_x,
     minimap_min_iso_y) = create_minimap_background(game_map, bg_width, bg_height)

    minimap_background_rect = minimap_background_surface.get_rect()
    minimap_background_rect.center = minimap_panel_rect.center
    minimap_background_rect.y -= panel_height / 50
    minimap_background_rect.x += panel_width / 18
    minimap_entities_surface = pygame.Surface(
        (minimap_background_rect.width, minimap_background_rect.height),
        pygame.SRCALPHA
    )
    minimap_entities_surface.fill((0, 0, 0, 0))

    selected_player = players[0] if players else None
    fullscreen = False

    game_state = {
        'camera': camera,
        'players': players,
        'selected_player': selected_player,
        'team_colors': team_colors,
        'game_map': game_map,
        'minimap_panel_sprite': minimap_panel_sprite,
        'minimap_panel_rect': minimap_panel_rect,
        'minimap_background': minimap_background_surface,
        'minimap_background_rect': minimap_background_rect,
        'minimap_entities_surface': minimap_entities_surface,
        'minimap_scale': minimap_scale,
        'minimap_offset_x': minimap_offset_x,
        'minimap_offset_y': minimap_offset_y,
        'minimap_min_iso_x': minimap_min_iso_x,
        'minimap_min_iso_y': minimap_min_iso_y,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'screen': screen,
        'fullscreen': fullscreen,
        'minimap_dragging': False,
        'player_selection_updated': True,
        'player_info_updated': True,
        'last_terminal_update': 0,
        'selected_entities': [],
        'selecting_entities': False,
        'selection_start': None,
        'selection_end': None,
        'rectangle_additive': False,
        'paused': False,
        'force_full_redraw': False,
        'show_all_health_bars': False
    }

    player_selection_surface = None
    player_info_surface = None

    running = True
    update_interval = 60
    frame_counter = 0

    while running:
        raw_dt = clock.tick(120) / 1000.0
        dt = 0 if game_state['paused'] else raw_dt
        frame_counter += 1

        for event in pygame.event.get():
            handle_events(event, game_state)
            if event.type == pygame.QUIT:
                running = False

        update_game_state(game_state, dt)

        screen = game_state['screen']
        screen_width = game_state['screen_width']
        screen_height = game_state['screen_height']
        selected_player = game_state['selected_player']
        players = game_state['players']
        team_colors = game_state['team_colors']
        game_map = game_state['game_map']
        camera = game_state['camera']

        if time.time() - game_state.get('last_terminal_update', 0) >= 2:
            start_time = time.time()
            game_map.update_terminal()
            game_state['last_terminal_update'] = start_time

        if game_state.get('recompute_camera', False):
            min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_map)
            camera.set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
            game_state['recompute_camera'] = False

        if (not game_state.get('paused', False)) and (frame_counter % update_interval == 0):
            update_minimap_entities(game_state)

        if game_state.get('player_selection_updated', False):
            player_selection_surface = create_player_selection_surface(
                players,
                selected_player,
                game_state['minimap_background_rect'],
                team_colors
            )
            game_state['player_selection_updated'] = False

        if game_state.get('player_info_updated', False):
            player_info_surface = create_player_info_surface(
                selected_player, screen_width, team_colors
            )
            game_state['player_info_updated'] = False

        screen.fill((0, 0, 0))

        draw_map(screen, screen_width, screen_height, game_map, camera, players, team_colors, game_state, dt)

        screen.blit(game_state['minimap_panel_sprite'], game_state['minimap_panel_rect'].topleft)
        screen.blit(game_state['minimap_background'], game_state['minimap_background_rect'].topleft)
        screen.blit(game_state['minimap_entities_surface'], game_state['minimap_background_rect'].topleft)
        draw_minimap_viewport(
            screen,
            camera,
            game_state['minimap_background_rect'],
            game_state['minimap_scale'],
            game_state['minimap_offset_x'],
            game_state['minimap_offset_y'],
            game_state['minimap_min_iso_x'],
            game_state['minimap_min_iso_y']
        )

        draw_gui_elements(screen, screen_width, screen_height)

        if not game_state['paused']:
            for p in players:
                for u in p.units:
                    u.move(game_map, dt)

        for p in players:
            for u in p.units:
                if u.path:
                    for (px, py) in u.path:
                        sx, sy = tile_to_screen(px, py, HALF_TILE_SIZE, HALF_TILE_SIZE/2, camera, screen_width, screen_height)
                        pygame.draw.circle(screen, (255,0,0), (sx, sy), 3)
                    ux, uy = tile_to_screen(u.x, u.y, HALF_TILE_SIZE, HALF_TILE_SIZE/2, camera, screen_width, screen_height)
                    pygame.draw.circle(screen, (0,0,255), (ux, uy), 3)

        if player_selection_surface:
            sel_h = player_selection_surface.get_height()
            bg_rect = game_state['minimap_background_rect']
            screen.blit(player_selection_surface, (bg_rect.x, bg_rect.y - sel_h - 20))

        if player_info_surface:
            inf_h = player_info_surface.get_height()
            screen.blit(player_info_surface, (0, screen_height - inf_h))

        display_fps(screen, clock)
        draw_pointer(screen)

        if game_state.get('force_full_redraw', False):
            pygame.display.flip()
            game_state['force_full_redraw'] = False
        else:
            pygame.display.flip()

    # End of loop
