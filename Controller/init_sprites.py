import re
import pygame
import os
import time
from collections import OrderedDict
from Settings.setup import *

sprites = {}
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

def load_sprite(filepath=None, scale=None, adjust=None):
    if filepath:
        sprite = pygame.image.load(filepath).convert_alpha()
    if scale:
        sprite = pygame.transform.smoothscale(sprite, (int(scale[0]), int(scale[1])))
    if adjust:
        sprite = pygame.transform.smoothscale(sprite, (
            int(sprite.get_width() * adjust),
            int(sprite.get_height() * adjust)
        ))
    sprite = sprite.convert_alpha()
    return sprite

def extract_frames(sheet, rows, columns, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // columns
    frame_height = sheet_height // rows
    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    frame_step = columns // FRAMES_PER_UNIT
    for row in range(rows):
        if row % 2 != 0:
            continue
        for col in range(columns):
            if col % frame_step == 0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames

def draw_progress_bar(screen, progress, screen_width, screen_height, progress_text, loading_screen_image):
    screen.blit(loading_screen_image, (0, 0))

    bar_width = screen_width * PROGRESS_BAR_WIDTH_RATIO
    bar_x = (screen_width - bar_width) / 2
    bar_y = screen_height * PROGRESS_BAR_Y_RATIO

    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, BAR_HEIGHT), 2, border_radius=BAR_BORDER_RADIUS)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width * progress, BAR_HEIGHT), border_radius=BAR_BORDER_RADIUS)

    text_color = BLACK if progress >= 0.5 else WHITE

    font = pygame.font.Font(None, 36)
    percentage_text = font.render(f"{int(progress * 100)}%", True, text_color)
    percentage_text_rect = percentage_text.get_rect(center=(bar_x + bar_width / 2, bar_y + BAR_HEIGHT / 2))
    screen.blit(percentage_text, percentage_text_rect)

    progress_text_surface = font.render("Loading " + progress_text, True, WHITE)
    progress_text_rect = progress_text_surface.get_rect(centerx=(bar_x + bar_width / 2), top=(bar_y + BAR_HEIGHT))
    screen.blit(progress_text_surface, progress_text_rect)

    pygame.display.flip()

def load_sprites(screen,screen_width,screen_height, sprite_config=sprite_config, sprite_loading_screen=sprite_loading_screen):
    total_files = sum(len(files) for _, _, files in os.walk('assets'))
    loaded_files = 0
    for category, value in sprite_loading_screen.items():
        directory = value.get('directory')
        scale = (screen_width, screen_height)
        try:
            dir_content = os.listdir(directory)
        except FileNotFoundError:
            print(f"Directory not found: {directory}")
            continue

        for filename in dir_content:
            if filename.lower().endswith("webp"):
                filepath = os.path.join(directory, filename)
                loading_sprite = load_sprite(filepath, scale)
                # Afficher l'écran de chargement
                if category == 'loading_screen':
                    screen.blit(loading_sprite, (0, 0))
                    pygame.display.flip()
                loaded_files += 1
                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height, "", loading_sprite)         

    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')

            if 'sheet_config' in sprite_config[category][sprite_name]:
                sheet_cols = sprite_config[category][sprite_name]['sheet_config'].get('columns', 0)
                sheet_rows = sprite_config[category][sprite_name]['sheet_config'].get('rows', 0)

            if category == 'resources' or category == 'buildings':
                sprites[category][sprite_name] = []
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue
                for filename in dir_content:
                    if filename.lower().endswith("webp"):
                        filepath = os.path.join(directory, filename)
                        sprite = load_sprite(filepath, scale, adjust)
                        sprites[category][sprite_name].append(sprite)
                        loaded_files += 1
                        progress = loaded_files / total_files
                        draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_sprite)

            elif category == 'units':
                sprites[category][sprite_name] = {}
                sprite_path = directory
                if os.path.isdir(sprite_path):
                    state_dirs = os.listdir(sprite_path)
                    for state_dir in state_dirs:
                        state_path = os.path.join(sprite_path, state_dir)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name].setdefault(state_dir, [])
                        sheets = os.listdir(state_path)
                        for sheetname in sheets:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath, scale, adjust)
                                    frames = extract_frames(sprite_sheet, sheet_rows, sheet_cols)
                                    sprites[category][sprite_name][state_dir].extend(frames)
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")
                                    print(f"info : category : {category}, sprite_name : {sprite_name}, state : {state_dir}")
                                    exit()
                                loaded_files += 1
                                progress = loaded_files / total_files
                                draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_sprite)
                progress = loaded_files / total_files
                draw_progress_bar(screen, progress, screen_width, screen_height, sprite_name, loading_sprite)
    
    
    print("Sprites loaded successfully.")
    
# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(name, category, zoom, state, frame_id, variant):
    cache_key = (zoom, state, frame_id, variant)
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]
    # Load and scale the sprite
    if category == 'resources' or category == 'buildings':
        original_image = sprites[category][name][variant]
    elif category == 'units':
        original_image = sprites[category][name][state][frame_id]

    scaled_width = int(original_image.get_width() * zoom)
    scaled_height = int(original_image.get_height() * zoom)
    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    
    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image

def draw_sprite(screen, acronym, category, screen_x, screen_y, zoom, state=None, frame=0, variant=0):
    name = Entity_Acronym[category][acronym]
    if state is not None:
        state = states[state]

    scaled_sprite = get_scaled_sprite(name, category, zoom, state, frame, variant)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, ' ', 'resources', screen_x, screen_y, camera.zoom)
