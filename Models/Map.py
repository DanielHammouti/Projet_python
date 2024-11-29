# Models/Map.py

import random
import os
import pickle
from datetime import datetime
from Models.Building import Building
from Settings.setup import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, NUM_MOUNTAIN_TILES, NUM_GOLD_TILES, NUM_WOOD_TILES, NUM_FOOD_TILES

class Tile:
    def __init__(self, terrain_type, tile_size=TILE_SIZE):
        self.tile_size = tile_size
        self.terrain_type = terrain_type  # 'grass', 'mountain', 'gold', 'wood', 'food'
        self.building = None  # Pas de bâtiment
        self.unit = None      # Pas d'unité
        self.player = None  # Add this line to store the owning player

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
    # Sauvegarder la carte dans un fichier JSON 
    def save_map(self, directory='saves'):
        # Créer le répertoire de sauvegarde s'il n'existe pas
        if not os.path.exists(directory):
            os.makedirs(directory)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(directory, f'save_{timestamp}.pkl')
        game_state = {
            'players': self.players,
            'tiles': self.grid
        }
        try:
            with open(filename, 'wb') as file:
                pickle.dump(game_state, file)
            print(f"Game map saved successfully to {filename}.")
        except Exception as e:
            print(f"Error saving game map: {e}")

    def load_map(self, filename):
        try:
            with open(filename, 'rb') as file:
                game_state = pickle.load(file)
            self.players = game_state['players']
            self.grid = game_state['tiles']
            print(f"Game map loaded successfully from {filename}.")
        except Exception as e:
            print(f"Error loading game map: {e}")
        
    def building_generation(self, grid, players):
        num_players = len(players)
        zone_width = self.width // (num_players if num_players % 2 == 0 else 1) // TILE_SIZE
        zone_height = self.height // (num_players if num_players % 2 == 0 else 1) // TILE_SIZE

        for index, player in enumerate(players):
            # Calcul de la zone de départ du joueur
            x_start = (index % (num_players // 2)) * zone_width
            y_start = (index // (num_players // 2)) * zone_height
            x_end = x_start + zone_width
            y_end = y_start + zone_height

            for building in player.buildings:
                max_attempts = zone_width * zone_height
                attempts = 0
                placed = False

                # Tentatives aléatoires de placement
                while attempts < max_attempts:
                    x = random.randint(x_start, x_end - building.size1)
                    y = random.randint(y_start, y_end - building.size2)
                    if self.can_place_building(grid, x, y, building):
                        placed = True
                        break
                    attempts += 1

                # Si l'aléatoire échoue, recherche systématique de la première place libre
                if not placed:
                    for y in range(y_start, y_end - building.size2 + 1):
                        for x in range(x_start, x_end - building.size1 + 1):
                            if self.can_place_building(grid, x, y, building):
                                placed = True
                                break
                        if placed:
                            break

                # Si aucun placement n'est possible, lever l'exception
                if not placed:
                    raise ValueError("Unable to place building in player zone; zone might be fully occupied.")

                # Placement du bâtiment sur la grille
                for i in range(building.size1):
                    for j in range(building.size2):
                        grid[y + j][x + i].building = building
                        grid[y + j][x + i].terrain_type = building.acronym
                        grid[y + j][x + i].player = player  # Assign the player to the tile
                        building.x = x
                        building.y = y



    def can_place_building(self, grid, x, y, building):
        if x + building.size1 > self.width // TILE_SIZE or y + building.size2 > self.height // TILE_SIZE:
            return False
        for i in range(building.size1):
            for j in range(building.size2):
                if grid[y + j][x + i].building is not None or grid[y + j][x + i].terrain_type in ['gold', 'wood', 'food']:
                    return False
        return True

    def random_map(self, width, height, players):
        # Créer une grille vide initiale
        grid = [[Tile('empty') for _ in range(width // TILE_SIZE)] for _ in range(height // TILE_SIZE)]

        # Générer les bâtiments sur cette grille vide
        self.building_generation(grid, players)

        # Liste des types de terrain à placer
        tiles = (
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
