# Models/Map.py

import random
from Models.Building import Building
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_MOUNTAIN_TILES, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type  # 'grass', 'mountain', 'gold', 'wood', 'food'
        self.building = None  # Pas de bâtiment
        self.unit = None      # Pas d'unité

    def is_walkable(self):
        return self.building is None

class GameMap:
    def __init__(self, players, width=MAP_WIDTH, height=MAP_HEIGHT):
        self.width = width
        self.height = height
        self.num_tiles_x = width // TILE_SIZE
        self.num_tiles_y = height // TILE_SIZE
        self.players = players
        self.grid = self.random_map(width, height, players)  

    def place_building(self, x, y, building):
        pass

    def place_unit(self, x, y, unit):
        pass

    def building_generation(self, grid, players):
        for player in players:
            for building in player.buildings:
                attempts = 0
                max_attempts = MAP_WIDTH*MAP_HEIGHT*TILE_SIZE  # Nombre maximum de tentatives pour placer un bâtiment
                x, y = 0, 0  # initialisation
                while attempts < max_attempts:
                    x = random.randint(0, self.width // TILE_SIZE - 1)
                    y = random.randint(0, self.height // TILE_SIZE - 1)
                    if self.can_place_building(grid, x, y, building):
                        break
                    attempts += 1
                if attempts == max_attempts:
                    raise ValueError("Unable to place building, grid might be fully occupied.")
                
                for i in range(building.size1):
                    for j in range(building.size2):
                        grid[y + j][x + i].building = building
                        grid[y + j][x + i].terrain_type = building.acronym

    def can_place_building(self, grid, x, y, building):
        if x + building.size1 > self.width // TILE_SIZE or y + building.size2 > self.height // TILE_SIZE:
            return False
        for i in range(building.size1):
            for j in range(building.size2):
                if grid[y + j][x + i].building is not None:
                    return False
        return True
                
                

    def random_map(self, width, height, players):
        # Créer une grille vide initiale
        grid = [[Tile('empty') for _ in range(width // TILE_SIZE)] for _ in range(height // TILE_SIZE)]

        # Générer les bâtiments sur cette grille vide
        self.building_generation(grid, players)

        # Liste des types de terrain à placer
        tiles = (
            ['mountain'] * NUM_MOUNTAIN_TILES +
            ['gold'] * NUM_GOLD_TILES +
            ['wood'] * NUM_WOOD_TILES +
            ['food'] * NUM_FOOD_TILES
        )


        # Nombre total de tuiles
        
        total_tiles = self.num_tiles_x * self.num_tiles_y
        remaining_tiles = total_tiles - len(tiles)
        tiles += ['grass'] * remaining_tiles  # Ajoute des tuiles d'herbe pour combler les espaces

        # Mélanger les tuiles
        random.shuffle(tiles)

        # Remplir la grille avec les types de terrain
        for y in range(height // TILE_SIZE):
            for x in range(width // TILE_SIZE):
                terrain_type = tiles.pop()  # Prendre une tuile de la liste mélangée
                grid[y][x].terrain_type = terrain_type

        return grid


    def print_map(self):
        terrain_acronyms = {
            'grass': ' ',
            'mountain': 'M',
            'gold': 'G',
            'wood': 'W',
            'food': 'F',
        }

        for row in self.grid:
            row_display = []
            for tile in row:
                if tile.building is not None:
                    row_display.append(tile.building.acronym)
                else:
                    row_display.append(terrain_acronyms.get(tile.terrain_type, '??'))
            print(''.join(row_display))

           
    