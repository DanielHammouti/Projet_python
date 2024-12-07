# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/Projet_python\Controller\init_sprites.py
# Controller/init_sprites.py

import re
import pygame
import os
from collections import OrderedDict
from Settings.setup import *


Entity_Acronym = {
# Mapping of resources acronyms to their full names
    'resources' : {
        ' ' : 'grass',
        'W' : 'wood',
        'G' : 'gold',
        'F' : 'food'
    },

    # Mapping of building acronyms to their full names
    'buildings' : {
        'A': 'archeryrange',
        'B': 'barracks',
        'C': 'camp',
        'F': 'farm',
        'H': 'house',
        'K': 'keep',
        'S': 'stable',
        'T': 'towncenter'
    },

    # Mapping of unit acronyms to their full names
    'units' : {
        'a' : 'archer',
        'h' : 'horseman',
        's' : 'swordsman',
        'v' : 'villager'
    }
}

teams = {
    0 : 'blue',
    1 : 'red' 
}

states = {
    0 : 'idle',
    1 : 'walk',
    2 : 'attack',
    3 : 'death'
}

sprite_config = {
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'adjust_scale': TILE_SIZE / 400  
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'adjust_scale': TILE_SIZE / 400
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'adjust_scale': TILE_SIZE / 400,
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'adjust_scale': TILE_SIZE / 400
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'adjust_scale': TILE_SIZE / 400
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'adjust_scale': TILE_SIZE / 400
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'adjust_scale': TILE_SIZE / 400
        }
    },
    'resources': {
        'grass': {
            'directory': 'assets/resources/grass/',
            'scale': (10*TILE_SIZE // 2, 10*TILE_SIZE // 4)
            # Static sprite
        },
        'gold': {
            'directory': 'assets/resources/gold/',
            'scale': (TILE_SIZE, TILE_SIZE)
        },
        'wood': {
            'directory': 'assets/resources/tree/',
            'scale': (TILE_SIZE, TILE_SIZE)
            # Static sprite
        },
        'food': {
            'directory': 'assets/resources/food/',
            'scale': (TILE_SIZE, TILE_SIZE)
            # Static sprite
        }
    },
    'units': {
        'swordsman': {
            'directory': 'assets/units/swordsman/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        },
        'villager': {
            'directory': 'assets/units/villager/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        },
        'archer': {
            'directory': 'assets/units/archer/',
            'states': 4,
            'adjust_scale': TILE_SIZE / 400,
            'sheet_config' : {
                'columns' : 30,
                'rows' : 16        
            },
        }
    }
}

sprites = {}
zoom_cache = {}
MAX_ZOOM_CACHE_PER_SPRITE = 60

grass_group = pygame.sprite.Group()

# Function to load a sprite with conditional scaling
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
    # Conversion en format interne optimisé
    sprite = sprite.convert_alpha()
    return sprite

# Extracts frames from a sprite sheet based on rows and columns, and scales them by a factor.
def extract_frames(sheet, rows, columns, scale=TILE_SIZE / 400):
    frames = []
    sheet_width, sheet_height = sheet.get_size()

    frame_width = sheet_width // columns
    frame_height = sheet_height // rows

    target_width = int(frame_width * scale)
    target_height = int(frame_height * scale)

    # Calculate Frame Step
    frame_step = columns // FRAMES_PER_UNIT

    for row in range(rows):
        for col in range(columns):
            # Compute the position of the frame in the sprite sheet
            if col%frame_step==0:
                x = col * frame_width
                y = row * frame_height
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                
                # Resize frame to the new dimensions
                frame = pygame.transform.smoothscale(frame, (target_width, target_height))
                frames.append(frame)
    return frames

def load_sprites(sprite_config=sprite_config):
    for category in sprite_config:
        sprites[category] = {}
        for sprite_name, value in sprite_config[category].items():
            directory = value['directory']
            scale = value.get('scale')
            adjust = value.get('adjust_scale')
            
            if 'sheet_config' in sprite_config[category][sprite_name]:
                sheet_cols = sprite_config[category][sprite_name]['sheet_config'].get('columns', 0)
                sheet_rows = sprite_config[category][sprite_name]['sheet_config'].get('rows', 0)

            if category == 'resources':
                # Initialize resources category
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
                        sprites[category][sprite_name].append(sprite)  # Append sprite to list
                        print(f'--> Loaded {sprite_name} of type : {category}')
            elif category == 'buildings':
                sprites[category][sprite_name] = {}
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    continue

                for team in dir_content:
                    team_path = os.path.join(directory, team)
                    if not os.path.isdir(team_path):
                        continue
                    if team not in sprites[category][sprite_name]:
                        sprites[category][sprite_name][team] = []
                    try:
                        team_content = os.listdir(team_path)
                    except FileNotFoundError:
                        continue

                    for filename in team_content:
                        if filename.lower().endswith("webp"):
                            filepath = os.path.join(team_path, filename)
                            sprite = load_sprite(filepath, scale, adjust)
                            sprites[category][sprite_name][team].append(sprite)  # Append sprite to list
                    print(f'--> Loaded {sprite_name}, type : {category}')
            elif category == 'units' :
                #Uncomment this continue to get faster loading
                #continue

                # Initialize buildings category
                sprites[category][sprite_name] = {}
                try:
                    dir_content = os.listdir(directory)
                except FileNotFoundError:
                    print(f"Directory not found: {directory}")
                    return

                for team in dir_content:
                    team_path = os.path.join(directory, team)
                    if not os.path.isdir(team_path):
                        continue
                    sprites[category][sprite_name].setdefault(team, {})

                    try:
                        team_content = os.listdir(team_path)
                    except FileNotFoundError:
                        continue

                    for state in team_content:
                        state_path = os.path.join(team_path, state)
                        if not os.path.isdir(state_path):
                            continue
                        sprites[category][sprite_name][team].setdefault(state, [])

                        try:
                            state_content = os.listdir(state_path)
                        except FileNotFoundError:
                            continue

                        for sheetname in state_content:
                            if sheetname.lower().endswith("webp"):
                                filepath = os.path.join(state_path, sheetname)
                                try:
                                    sprite_sheet = load_sprite(filepath)
                                    frames = extract_frames(sprite_sheet, sheet_rows, sheet_cols)
                                    sprites[category][sprite_name][team][state].extend(frames)
                                except Exception as e:
                                    print(f"Error loading sprite sheet {filepath}: {e}")
                                    print(f"info : category : {category}, sprite_name : {sprite_name}, team : {team}, state : {state}")
                                    exit() 
                print(f'--> Loaded {sprite_name}, type : {category}')

    print("Sprites loaded successfully.")

# Function to get a scaled sprite, handling both static and animated sprites
def get_scaled_sprite(name, category, zoom, team, state, frame_id):
    cache_key = (zoom, frame_id, team, state)
    if name not in zoom_cache:
        zoom_cache[name] = OrderedDict()
    if cache_key in zoom_cache[name]:
        zoom_cache[name].move_to_end(cache_key)
        return zoom_cache[name][cache_key]
    # Load and scale the sprite
    if category == 'resources':
        sprite_data = sprites[category][name]
    elif category == 'buildings':
        sprite_data = sprites[category][name][team]
    elif category == 'units':
        sprite_data = sprites[category][name][team][state]

    original_image = sprite_data[frame_id]
    scaled_width = int(original_image.get_width() * zoom)
    scaled_height = int(original_image.get_height() * zoom)
    scaled_image = pygame.transform.smoothscale(original_image, (scaled_width, scaled_height))
    
    # Add to cache
    zoom_cache[name][cache_key] = scaled_image
    zoom_cache[name].move_to_end(cache_key)
    
    # Evict least recently used if over capacity
    
    if len(zoom_cache[name]) > MAX_ZOOM_CACHE_PER_SPRITE:
        zoom_cache[name].popitem(last=False)
    return scaled_image
    
# Function to draw a sprite on the screen
def draw_sprite(screen, acronym, category, screen_x, screen_y, zoom, team=None, state=None, frame_id=0):
    name = Entity_Acronym[category][acronym]
    if team is not None:
        team = teams[team]
    if state is not None:
        state = states[state]

    scaled_sprite = get_scaled_sprite(name, category, zoom, team, state, frame_id)
    if scaled_sprite is None:
        return
    scaled_width = scaled_sprite.get_width()
    scaled_height = scaled_sprite.get_height()
    screen.blit(scaled_sprite, (screen_x - scaled_width // 2, screen_y - scaled_height // 2))

def fill_grass(screen, screen_x, screen_y, camera):
    draw_sprite(screen, ' ', 'resources', screen_x, screen_y, camera.zoom)