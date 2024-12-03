# Chemin de Controller/event_handler.py

import pygame
import sys
from tkinter import Tk, filedialog
from Models.Building import TownCentre
from Controller.isometric_utils import to_isometric
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY

def handle_events(event, game_state):
    """
    Gère les événements utilisateur.
    """
    camera = game_state['camera']
    players = game_state['players']  # Variable modifiée
    selected_player = game_state['selected_player']  # Variable modifiée
    minimap_rect = game_state['minimap_rect']
    minimap_dragging = game_state['minimap_dragging']
    minimap_background = game_state['minimap_background']
    minimap_scale = game_state['minimap_scale']
    minimap_offset_x = game_state['minimap_offset_x']
    minimap_offset_y = game_state['minimap_offset_y']
    minimap_min_iso_x = game_state['minimap_min_iso_x']
    minimap_min_iso_y = game_state['minimap_min_iso_y']
    game_map = game_state['game_map']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    minimap_margin = game_state['minimap_margin']
    screen = game_state['screen']
    fullscreen = game_state['fullscreen']
    
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    elif event.type == pygame.KEYDOWN:
        # Basculer entre le mode plein écran et fenêtré avec la touche 'Y'
        if event.key == pygame.K_y:
            fullscreen = not fullscreen
            if fullscreen:
                # Passer en plein écran
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                infoObject = pygame.display.Info()
                screen_width, screen_height = infoObject.current_w, infoObject.current_h
            else:
                # Passer en mode fenêtré avec une taille plus petite
                screen_width, screen_height = 800, 600
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            
            # Mettre à jour la caméra et la minimap avec la nouvelle taille d'écran
            camera.width = screen_width
            camera.height = screen_height
            minimap_width = int(screen_width * 0.25)
            minimap_height = int(screen_height * 0.25)
            minimap_rect = pygame.Rect(
                screen_width - minimap_width - minimap_margin,
                screen_height - minimap_height - minimap_margin,
                minimap_width,
                minimap_height
            )
            from Controller.drawing import create_minimap_background
            minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
            minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
                game_map, minimap_width, minimap_height
            )
        elif event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        # Sauvegarder et charger la carte
        if event.key == pygame.K_k:  # Appuyer sur 'k' pour sauvegarder
            game_map.save_map()
        elif event.key == pygame.K_l:  # Appuyer sur 'l' pour charger
            root = Tk()
            root.withdraw()  # Cacher la fenêtre principale
            filename = filedialog.askopenfilename(
                initialdir=SAVE_DIRECTORY,
                title="Select save file",
                filetypes=(("Pickle files", "*.pkl"), ("All files", "*.*"))
            )
            if filename:
                game_map.load_map(filename)
            root.destroy()
        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
            camera.set_zoom(camera.zoom * 1.1)
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
            camera.set_zoom(camera.zoom / 1.1)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = event.pos
        if event.button == 1:  # Bouton gauche de la souris
            if minimap_rect.collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                # Gérer la sélection du joueur avec clic
                for i, player in enumerate(reversed(players)):
                    rect_y = minimap_rect.y - (i + 1) * (30 + 5)
                    rect = pygame.Rect(minimap_rect.x, rect_y, minimap_rect.width, 30)
                    if rect.collidepoint(mouse_x, mouse_y):
                        game_state['selected_player'] = player
                        for building in player.buildings:
                            if isinstance(building, TownCentre):
                                iso_x, iso_y = to_isometric(building.x, building.y, HALF_TILE_SIZE, HALF_TILE_SIZE / 2)
                                
                                camera.offset_x = -iso_x
                                camera.offset_y = -iso_y
                                break
        
        elif event.button == 4:  # Molette vers le haut
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:  # Molette vers le bas
            camera.set_zoom(camera.zoom / 1.1)
    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            game_state['minimap_dragging'] = False
        if event.button == 4:  # Molette vers le haut
            camera.set_zoom(camera.zoom * 1.1)
        elif event.button == 5:  # Molette vers le bas
            camera.set_zoom(camera.zoom / 1.1)
    elif event.type == pygame.VIDEORESIZE:
        screen_width, screen_height = event.size
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE )
        camera.width = screen_width
        camera.height = screen_height

        # Mettre à jour les dimensions de la minimap lors du redimensionnement de la fenêtre
        minimap_width = int(screen_width * 0.25)
        minimap_height = int(screen_height * 0.25)
        minimap_rect = pygame.Rect(
            screen_width - minimap_width - minimap_margin,
            screen_height - minimap_height - minimap_margin,
            minimap_width,
            minimap_height
        )

        # Recréer le fond de la minimap avec la nouvelle taille
        from Controller.drawing import create_minimap_background
        minimap_background, minimap_scale, minimap_offset_x, minimap_offset_y, \
        minimap_min_iso_x, minimap_min_iso_y = create_minimap_background(
            game_map, minimap_width, minimap_height
        )

    # Mettre à jour le game_state avec les nouvelles valeurs
    game_state['camera'] = camera
    game_state['players'] = players  # Clé modifiée
    game_state['selected_player'] = game_state['selected_player']  # Clé modifiée
    game_state['minimap_rect'] = minimap_rect
    game_state['minimap_dragging'] = game_state['minimap_dragging']
    game_state['minimap_background'] = minimap_background
    game_state['minimap_scale'] = minimap_scale
    game_state['minimap_offset_x'] = minimap_offset_x
    game_state['minimap_offset_y'] = minimap_offset_y
    game_state['minimap_min_iso_x'] = minimap_min_iso_x
    game_state['minimap_min_iso_y'] = minimap_min_iso_y
    game_state['screen_width'] = screen_width
    game_state['screen_height'] = screen_height
    game_state['screen'] = screen
    game_state['fullscreen'] = fullscreen
