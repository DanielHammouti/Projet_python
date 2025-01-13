import pygame
import math
import colorsys
import time
from Settings.setup import (
    HALF_TILE_SIZE,
    MAP_PADDING,
    HEALTH_BAR_WIDTH,
    HEALTH_BAR_HEIGHT,
    HEALTH_BAR_OFFSET_Y,
    UNIT_HITBOX
)
from Controller.utils import (
    to_isometric,
    get_color_for_terrain,
    screen_to_tile,
    tile_to_screen,
)
from Controller.init_assets import fill_grass
from Controller.gui import get_scaled_gui

def generate_team_colors(num_players):
    color_list = []
    step = 1.0 / num_players
    for i in range(num_players):
        hue = (i * step) % 1.0
        if 0.25 <= hue <= 0.4167:
            hue = (hue + 0.2) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.7)
        color_list.append((int(r * 255), int(g * 255), int(b * 255)))
    return color_list

def draw_map(
    screen,
    screen_width,
    screen_height,
    game_map,
    camera,
    players,
    team_colors,
    game_state,
    delta_time
):
    corners_screen = [
        (0, 0),
        (screen_width, 0),
        (0, screen_height),
        (screen_width, screen_height)
    ]
    tile_indices = [
        screen_to_tile(
            sx, sy, 
            screen_width, screen_height, 
            camera,
            HALF_TILE_SIZE / 2, 
            HALF_TILE_SIZE / 4
        ) 
        for sx, sy in corners_screen
    ]

    x_candidates = [t[0] for t in tile_indices]
    y_candidates = [t[1] for t in tile_indices]

    margin = 5
    min_tile_x = max(0, min(x_candidates) - margin)
    max_tile_x = min(game_map.num_tiles_x - 1, max(x_candidates) + margin)
    min_tile_y = max(0, min(y_candidates) - margin)
    max_tile_y = min(game_map.num_tiles_y - 1, max(y_candidates) + margin)

    visible_entities = set()
    for tile_y in range(min_tile_y, max_tile_y):
        for tile_x in range(min_tile_x, max_tile_x):
            # Fill grass
            if tile_x % 10 == 0 and tile_y % 10 == 0:
                grass_sx, grass_sy = tile_to_screen(
                    tile_x + 4.5, 
                    tile_y + 4.5, 
                    HALF_TILE_SIZE, 
                    HALF_TILE_SIZE / 2,
                    camera,
                    screen_width,
                    screen_height
                )
                fill_grass(screen, grass_sx, grass_sy, camera)

            entity_set_active = game_map.grid.get((tile_x, tile_y), None)
            entity_set_inactive = game_map.inactive_matrix.get((tile_x, tile_y), None)

            if entity_set_active:
                for ent in entity_set_active:
                    visible_entities.add(ent)
            if entity_set_inactive:
                for ent_inactive in entity_set_inactive:
                    visible_entities.add(ent_inactive)

    visible_list = list(visible_entities)
    visible_list.sort(key=lambda e: (e.y, e.x))

    game_state['train_button_rects'] = {}
    current_time = time.time()

    # Draw entities
    for entity in visible_list:
        entity.display_hitbox(screen, screen_width, screen_height, camera)
        entity.display(screen, screen_width, screen_height, camera, delta_time)
        entity.display_range(screen, screen_width, screen_height, camera)

        if hasattr(entity, 'spawnsUnits') and entity.spawnsUnits:
            ent_screen_x, ent_screen_y = tile_to_screen(
                entity.x, 
                entity.y, 
                HALF_TILE_SIZE, 
                HALF_TILE_SIZE / 2,
                camera,
                screen_width,
                screen_height
            )
            
            # Always show training progress if there's an active training
            if entity.current_training_unit:
                bar_width = 80
                bar_height = 6
                button_width = 120
                offset_y = 12 * entity.size
                button_x = int(ent_screen_x - button_width / 2)
                button_y = int(ent_screen_y - offset_y - 10)
                bar_x = button_x
                bar_y = button_y - 10

                # Draw progress bar
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                fill_w = int(bar_width * entity.training_progress)
                pygame.draw.rect(screen, (0, 220, 0), (bar_x, bar_y, fill_w, bar_height))

                # Draw queue length
                font_obj = pygame.font.Font(None, 18)
                queue_len = len(entity.training_queue)
                queue_text = f"Q:{queue_len}"
                queue_surf = font_obj.render(queue_text, True, (255, 255, 255))
                screen.blit(queue_surf, (bar_x + bar_width + 5, bar_y - 2))

            # Only show training button and feedback when selected
            if 'selected_entities' in game_state and entity in game_state['selected_entities']:
                button_width = 120
                button_height = 25
                ent_screen_x, ent_screen_y = tile_to_screen(
                    entity.x, 
                    entity.y, 
                    HALF_TILE_SIZE, 
                    HALF_TILE_SIZE / 2,
                    camera,
                    screen_width,
                    screen_height
                )
                offset_y = 12 * entity.size
                button_x = int(ent_screen_x - button_width / 2)
                button_y = int(ent_screen_y - offset_y - 10)

                button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
                pygame.draw.rect(screen, (120, 120, 180), button_rect)
                font_obj = pygame.font.Font(None, 18)

                from Entity.Building.Building import UNIT_TRAINING_MAP
                if entity.acronym in UNIT_TRAINING_MAP:
                    unit_key = UNIT_TRAINING_MAP[entity.acronym]
                    button_text = f"Train {unit_key.capitalize()}"
                else:
                    button_text = "Train ???"

                text_surf = font_obj.render(button_text, True, (255, 255, 255))
                screen.blit(text_surf, text_surf.get_rect(center=button_rect.center))

                game_state['train_button_rects'][entity.entity_id] = button_rect

                # If not enough resources feedback
                if 'insufficient_resources_feedback' in game_state:
                    if entity.entity_id in game_state['insufficient_resources_feedback']:
                        start_time = game_state['insufficient_resources_feedback'][entity.entity_id]
                        if current_time - start_time < 3:
                            warn_text = "Not enough resources"
                            warn_surf = font_obj.render(warn_text, True, (255, 50, 50))
                            screen.blit(warn_surf, (button_x, button_y - 22))
                        else:
                            game_state['insufficient_resources_feedback'].pop(entity.entity_id, None)

    # Draw selection rectangle if needed
    if game_state.get('selecting_entities', False):
        start_pos = game_state.get('selection_start')
        end_pos = game_state.get('selection_end')
        if start_pos and end_pos:
            x1, y1 = start_pos
            x2, y2 = end_pos
            selection_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            selection_rect.normalize()
            pygame.draw.rect(screen, (255, 255, 255), selection_rect, 1)

    # Health bars
    show_all_bars = game_state.get('show_all_health_bars', False)
    if show_all_bars:
        for entity in visible_list:
            color_val = get_entity_bar_color(entity, game_state, team_colors)
            entity.display_healthbar(screen, screen_width, screen_height, camera, color_val)
    else:
        selected_entities = game_state.get('selected_entities', [])
        for entity in visible_list:
            if entity in selected_entities or entity.hp < entity.max_hp:
                color_val = get_entity_bar_color(entity, game_state, team_colors)
                entity.display_healthbar(screen, screen_width, screen_height, camera, color_val)

def get_entity_bar_color(entity, game_state, team_colors):
    if entity.team is None:
        return (50, 255, 50)
    return team_colors[entity.team % len(team_colors)]

def compute_map_bounds(game_map):
    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    map_width = game_map.num_tiles_x
    map_height = game_map.num_tiles_y

    corners = [
        (0, 0),
        (0, map_height - 1),
        (map_width - 1, map_height - 1),
        (map_width - 1, 0)
    ]
    iso_coords = [
        to_isometric(x, y, tile_width, tile_height) 
        for (x, y) in corners
    ]

    min_iso_x = min(c[0] for c in iso_coords) - MAP_PADDING
    max_iso_x = max(c[0] for c in iso_coords) + MAP_PADDING
    min_iso_y = min(c[1] for c in iso_coords) - MAP_PADDING
    max_iso_y = max(c[1] for c in iso_coords) + MAP_PADDING

    return min_iso_x, max_iso_x, min_iso_y, max_iso_y

def create_minimap_background(game_map, minimap_width, minimap_height):
    surface_map = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    surface_map.fill((0, 0, 0, 0))

    tile_width = HALF_TILE_SIZE
    tile_height = HALF_TILE_SIZE / 2
    nx = game_map.num_tiles_x
    ny = game_map.num_tiles_y

    corner_coords = [
        to_isometric(0, 0, tile_width, tile_height),
        to_isometric(0, ny - 1, tile_width, tile_height),
        to_isometric(nx - 1, ny - 1, tile_width, tile_height),
        to_isometric(nx - 1, 0, tile_width, tile_height)
    ]
    iso_xs = [c[0] for c in corner_coords]
    iso_ys = [c[1] for c in corner_coords]
    min_iso_x = min(iso_xs)
    max_iso_x = max(iso_xs)
    min_iso_y = min(iso_ys)
    max_iso_y = max(iso_ys)

    iso_map_width = max_iso_x - min_iso_x
    iso_map_height = max_iso_y - min_iso_y
    scale_factor = min(minimap_width / iso_map_width, minimap_height / iso_map_height)
    scaled_width = iso_map_width * scale_factor
    scaled_height = iso_map_height * scale_factor
    offset_x = (minimap_width - scaled_width) / 2
    offset_y = (minimap_height - scaled_height) / 2

    return surface_map, scale_factor, offset_x, offset_y, min_iso_x, min_iso_y

def display_fps(screen, clock, font):
    fps_value = f"{clock.get_fps():.2f}"  # Format to 2 decimal places
    fps_surface = font.render(fps_value, True, (255, 255, 255))  # White text
    screen.blit(fps_surface, (10, 10))  # (x, y) coordinates for top-left

def draw_pointer(screen):
    from Controller.gui import get_scaled_gui  # Déplacé ici pour éviter l'import circulaire
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pointer_image = get_scaled_gui('pointer', 0, target_width=30)
    pointer_rect = pointer_image.get_rect(center=(mouse_x + pointer_image.get_width() //2, mouse_y + pointer_image.get_height() //2))
    screen.blit(pointer_image, pointer_rect.topleft)

def draw_healthBar(screen, screen_x, screen_y, ratio, color_val):
    bg_rect = pygame.Rect(
        screen_x - HEALTH_BAR_WIDTH // 2,
        screen_y - HEALTH_BAR_OFFSET_Y,
        HEALTH_BAR_WIDTH,
        HEALTH_BAR_HEIGHT
    )
    pygame.draw.rect(screen, (50, 50, 50), bg_rect)
    fill_width = int(HEALTH_BAR_WIDTH * ratio)
    fill_rect = pygame.Rect(bg_rect.x, bg_rect.y, fill_width, HEALTH_BAR_HEIGHT)
    pygame.draw.rect(screen, color_val, fill_rect)