# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Settings\setup.py
# Path: Settings/setup.py
from collections import namedtuple
from Models.Resources import Resources
import os

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths relative to the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define paths relative to the base directory
SAVE_DIRECTORY = os.path.join(BASE_DIR, 'saves')
ASSETS_DIRECTORY = os.path.join(BASE_DIR, 'assets')

# Create necessary directories
os.makedirs(SAVE_DIRECTORY, exist_ok=True)
os.makedirs(ASSETS_DIRECTORY, exist_ok=True)

# -------------------
# Global Constants
# Classe Villager
# -------------------
GAME_SPEED = 5
FPS_DRAW_LIMITER = 50

BUILDING_TIME_REDUCTION = 0.75
BUILDING_ZONE_OFFSET = 1
RESOURCE_RATE_PER_SEC = 25 / 60
MAXIMUM_CARRY = 20

# -------------------
# BOT constants
# -------------------
DPS = 2 # 2 decisions per second

# -------------------
# Unit constants
# -------------------
ALLOWED_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
UPDATE_EVERY_N_MILLISECOND = 20
ONE_SECOND = 1000
FRAMES_PER_UNIT = 10
FRAMES_PER_BUILDING = 15
FRAMES_PER_PROJECTILE = 11
UNIT_HITBOX = 0.3
UNIT_ATTACKRANGE = 0.6
ATTACK_RANGE_EPSILON = 0.5

# -------------------
# Config For Teams
# -------------------
MAXIMUM_POPULATION = 200

difficulty_config = {
    'lean' : {
        'Resources' : Resources(food=50, gold=150, wood=50),
        'Units' : {
            'Villager' : 3
        },
        'Buildings' : {
            'TownCenter' : 1
        }

    },

    'mean' : {
        'Resources' : Resources(food=2000, gold=2000, wood=2000),
        'Units' : {
            'Villager' : 3
        },
        'Buildings' : {
            'TownCenter' : 1
        }

    },

    'marines' : {
        'Resources' : Resources(food=20000, gold=20000, wood=20000),
        'Units' : {
            'Villager' : 15
        },
        'Buildings' : {
            'TownCenter' : 3,
            'Barracks' : 2,
            'Stable' : 2,
            'ArcheryRange' : 2,
        }
    },

    'DEBUG' : {
        'Resources' : Resources(food=100, gold=80, wood=80),
        'Units' : {
            'Villager' : 5,
            'Archer' : 0,
            'Horseman' : 0,
            'Swordsman' : 0
        },
        'Buildings' : {
            'TownCenter' : 1,
            'House' : 0,
            'Barracks' : 0,
            'Stable' : 0,
            'ArcheryRange' : 0,
            'Farm' : 0,
            'Keep' : 0,
            'Camp' : 0,
        }
    }
}

# -------------------
# Map Configuration
# -------------------
TILE_SIZE = 200
HALF_TILE_SIZE = TILE_SIZE / 2
MAP_WIDTH = 120 * TILE_SIZE
MAP_HEIGHT = 120 * TILE_SIZE
MAX_ZOOM = 3.0
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1200
NUM_GOLD_TILES = 500
NUM_WOOD_TILES = 500
NUM_FOOD_TILES = 500
GOLD_SPAWN_MIDDLE = False
MAP_PADDING = 650

# -------------------
# Minimap Settings
# -------------------
MINIMAP_WIDTH = 600
MINIMAP_HEIGHT = 280
MINIMAP_MARGIN = 20
PANEL_RATIO = 0.25
BG_RATIO    = 0.20

# -------------------
# Save Directory
# -------------------
# SAVE_DIRECTORY = 'saves'
# if not os.path.exists(SAVE_DIRECTORY):
#     os.makedirs(SAVE_DIRECTORY)

# -------------------
# Sprites Configuration
# -------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

gui_config = {
    'loading_screen': {
        'directory': 'assets/launcher/',
        'scale': None
    },

    'ResourcesPanel' :{
        'directory' : 'assets/UI/Panels/resourcesPan',
    },

    'minimapPanel' :{
        'directory' : 'assets/UI/Panels/minimapPan',
    },

    'gold':{
        'directory' : 'assets/UI/Resources/gold',
    },

    'wood':{
        'directory' : 'assets/UI/Resources/wood',
        },

    'food':{
        'directory' : 'assets/UI/Resources/food',
    },

    'pointer':{
        'directory' : 'assets/UI/Pointer/',
    },

}

MAX_VISIBLE_ITEMS = 5
ITEM_HEIGHT = 25

BAR_HEIGHT = 30
BAR_BORDER_RADIUS = 30
PROGRESS_BAR_WIDTH_RATIO = 0.8
PROGRESS_BAR_Y_RATIO = 0.9

BUILDING_RATIO = 100
UNIT_RATIO = 100
PROJECTILE_RATIO = 75

HEALTH_BAR_WIDTH = 40
HEALTH_BAR_HEIGHT = 5
HEALTH_BAR_OFFSET_Y = 30

Acronym = {
    'resources': {
        ' ': 'grass',
        'W': 'tree',
        'G': 'gold',
        'F': 'food'
    },
    'buildings': {
        'A': 'archeryrange',
        'B': 'barracks',
        'C': 'camp',
        'F': 'farm',
        'H': 'house',
        'K': 'keep',
        'S': 'stable',
        'T': 'towncenter'
    },
    'units': {
        'a': 'archer',
        'h': 'horseman',
        's': 'swordsman',
        'v': 'villager'
    },

    'projectiles': {
        'a': 'arrow'
    }
}

states = {
     0: 'idle',
     1: 'walk',
     2: 'attack',
     3: 'death',
     4: 'decay',
     5: 'task',
     7: 'inactive'
}

villager_tasks = {
        "attack": "attack_target",
        "collect": "collect_target",
        "build": "build_target",
        "stock": "stock_target"
    }

sprite_config = {
    'projectiles':{
        'arrow': {
            'directory': 'assets/projectiles/arrow/',
            'states': 1,
            'adjust_scale': TILE_SIZE / PROJECTILE_RATIO,
            'sheet_config': {
                'columns': 11,
                'rows': 8
            },
        }
    },
    'buildings': {
        'towncenter': {
            'directory': 'assets/buildings/towncenter/',
            'states': 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'barracks': {
            'directory': 'assets/buildings/barracks/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'stable': {
            'directory': 'assets/buildings/stable/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'archeryrange': {
            'directory': 'assets/buildings/archeryrange/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'keep': {
            'directory': 'assets/buildings/keep/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'camp': {
            'directory': 'assets/buildings/camp/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'house': {
            'directory': 'assets/buildings/house/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / BUILDING_RATIO,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
        'farm': {
            'directory': 'assets/buildings/farm/',
            'states' : 2,
            'adjust_scale': TILE_SIZE / 120,
            'sheet_config': {
                'columns': 10,
                'rows': 10
            },
        },
    },
    'resources': {
        'grass': {
            'directory': 'assets/resources/grass/',
            'scale': (10 * TILE_SIZE // 2, 10 * TILE_SIZE // 4)
        },
        'gold': {
            'directory': 'assets/resources/gold/',
            'scale': (TILE_SIZE, TILE_SIZE),
            'variant': 6
        },
        'tree': {
            'directory': 'assets/resources/tree/',
            'scale': (TILE_SIZE, TILE_SIZE),
            'variant': 4
        }
    },
    'units': {
        'swordsman': {
            'directory': 'assets/units/swordsman/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'villager': {
            'directory': 'assets/units/villager/',
            'states': 6,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'archer': {
            'directory': 'assets/units/archer/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
        'horseman': {
            'directory': 'assets/units/horseman/',
            'states': 5,
            'adjust_scale': TILE_SIZE / UNIT_RATIO,
            'sheet_config': {
                'columns': 30,
                'rows': 16
            },
        },
    },
}



# ----
# Menu
# ----

# Modify user_choices to have separate width and height
user_choices = {
    "grid_width":     120, # map width
    "grid_height":    120, # map height
    "num_bots":       2,
    "bot_level":      "lean",
    "gold_at_center": False,
    "load_game":      False,
    "chosen_save":    None,
    "validated":      False,
    "index_terminal_display" : 0, # 0: GUI, 1: Terminal, 2: Both
    "bot_mode": "economique" # Default bot mode, added here
}

# Update combo scroll positions to include bot_mode
combo_scroll_positions = {
    "width": 0,  # width scroll position
    "height": 0, # height scroll position
    "nbot": 0,
    "lvl":  0,
    "bot_mode": 0 # bot_mode scroll position - AJOUTÉ
}

# Define valid grid sizes
VALID_GRID_SIZES = [i for i in range(100, 1000, 10)]
VALID_BOTS_COUNT = [i for i in range(1, 56)]
VALID_LEVELS = ["lean", "mean", "marines", "DEBUG"]
VALID_BOT_MODES = ["economique", "defensif", "offensif"] # Added valid bot modes - AJOUTÉ

RESOURCE_THRESHOLDS = Resources(food = 150, gold=150, wood = 100)