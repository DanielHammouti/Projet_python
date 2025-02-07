# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST\Projet_python\Controller\event_handler.py
import pygame
import sys
import os
import time
from tkinter import Tk, filedialog
from Entity.Building import Building, TownCentre
from Settings.setup import HALF_TILE_SIZE, SAVE_DIRECTORY, MINIMAP_MARGIN, PANEL_RATIO, BG_RATIO
from Controller.utils import *
from Controller.drawing import compute_map_bounds, generate_team_colors
from Models.html import write_full_html
from AiUtils.aStar import a_star
from Entity.Unit.Unit import Unit
from Controller.terminal_display_debug import debug_print


def resolve_save_path(relative_path):
    """Helper function to resolve save paths relative to project root"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(project_root, relative_path)


def clean_and_reset_display(game_state):
    """Helper function for proper display cleanup during loads"""
    if not game_state.get('screen'):
        return
        
    screen = game_state['screen']
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # Reset GUI surfaces
    panel_width = int(game_state['screen_width'] * PANEL_RATIO)
    panel_height = int(game_state['screen_height'] * PANEL_RATIO)
    
    from Controller.init_assets import get_scaled_gui
    game_state['minimap_panel_sprite'] = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
    
    from Controller.drawing import create_minimap_background
    bg_width = int(game_state['screen_width'] * BG_RATIO)
    bg_height = int(game_state['screen_height'] * BG_RATIO)
    
    mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
        game_state['game_map'], bg_width, bg_height
    )
    
    game_state['minimap_background'] = mb
    game_state['minimap_scale'] = ms
    game_state['minimap_offset_x'] = mo_x
    game_state['minimap_offset_y'] = mo_y
    game_state['minimap_min_iso_x'] = mi_x
    game_state['minimap_min_iso_y'] = mi_y
    
    game_state['minimap_entities_surface'] = pygame.Surface(
        (mb.get_width(), mb.get_height()),
        pygame.SRCALPHA
    )
    game_state['minimap_entities_surface'].fill((0, 0, 0, 0))
    
    # Force refresh des éléments GUI
    game_state['player_selection_updated'] = True
    game_state['player_info_updated'] = True
    game_state['force_full_redraw'] = True

def handle_load_game(game_state, chosen_path):
    try:
        print("[GUI] Starting load game process...")
        from Controller.drawing import create_minimap_background, compute_map_bounds, generate_team_colors
        from Models.Map import GameMap
        from Controller.sync_manager import save_for_sync
        
        # Backup current GUI state
        old_gui_state = {
            'screen': game_state.get('screen'),
            'screen_width': game_state.get('screen_width'),
            'screen_height': game_state.get('screen_height'),
            'camera': game_state.get('camera'),
            'minimap_panel_sprite': game_state.get('minimap_panel_sprite'),
            'minimap_background': game_state.get('minimap_background'),
            'minimap_entities_surface': game_state.get('minimap_entities_surface'),
            'player_selection_surface': game_state.get('player_selection_surface')
        }

        # Clean display before loading
        clean_and_reset_display(game_state)
        
        # Load the new map state
        game_state['game_map'].load_map(chosen_path)
        
        # Update all game state components
        game_state['players'] = game_state['game_map'].players
        game_state['selected_player'] = game_state['players'][0] if game_state['players'] else None
        game_state['team_colors'] = generate_team_colors(len(game_state['players']))
        game_state['old_resources'] = {p.teamID: p.resources.copy() for p in game_state['players']}
        game_state['players_target'] = [None for _ in range(len(game_state['players']))]
        
        # Restore GUI components
        for key, value in old_gui_state.items():
            if value is not None:
                game_state[key] = value

        # Reset camera and bounds
        min_iso_x, max_iso_x, min_iso_y, max_iso_y = compute_map_bounds(game_state['game_map'])
        game_state['camera'].set_bounds(min_iso_x, max_iso_x, min_iso_y, max_iso_y)
        game_state['camera'].zoom_out_to_global()

        # Force GUI refresh
        game_state['force_full_redraw'] = True
        game_state['player_selection_updated'] = True
        game_state['player_info_updated'] = True

        # Update notification
        game_state['notification_message'] = "Partie chargée avec succès"
        game_state['notification_start_time'] = time.time()

        # Sync with terminal if needed
        save_for_sync(game_state['game_map'])
        print("[GUI] Game loaded successfully")
        
    except Exception as e:
        print(f"[GUI] Error loading game: {e}")
        game_state['notification_message'] = f"Erreur de chargement: {str(e)}"
        game_state['notification_start_time'] = time.time()

def handle_save_game(game_state):
    try:
        print("[GUI] Starting save game process...")
        game_state['game_map'].save_map()
        game_state['notification_message'] = "Partie sauvegardée"
        game_state['notification_start_time'] = time.time()
        print("[GUI] Game saved successfully")
        return True
    except Exception as e:
        print(f"[GUI] Error saving game: {e}")
        game_state['notification_message'] = f"Erreur de sauvegarde: {str(e)}"
        game_state['notification_start_time'] = time.time()
        return False

def handle_events(event, game_state):
    """
    Gère les événements côté GUI/Pygame. 
    (Touches Pygame, clic souris, resize fenêtre, etc.)
    """
    camera = game_state['camera']
    players = game_state['players']
    selected_player = game_state['selected_player']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']

    if event.type == pygame.QUIT:
        # On supprime éventuellement la snapshot HTML
        try:
            os.remove('full_snapshot.html')
        except:
            pass
        pygame.quit()
        sys.exit()

    elif event.type == pygame.VIDEORESIZE:
        sw, sh = event.size
        camera.width = sw
        camera.height = sh

        panel_width  = int(sw * PANEL_RATIO)
        panel_height = int(sh * PANEL_RATIO)

        from Controller.init_assets import get_scaled_gui
        minimap_panel_sprite = get_scaled_gui('minimapPanel', 0, target_width=panel_width)
        game_state['minimap_panel_sprite'] = minimap_panel_sprite

        from Controller.drawing import create_minimap_background
        from Controller.utils import get_centered_rect_in_bottom_right

        new_panel_rect = get_centered_rect_in_bottom_right(
            panel_width, 
            panel_height, 
            sw, 
            sh, 
            MINIMAP_MARGIN
        )
        game_state['minimap_panel_rect'] = new_panel_rect

        bg_width  = int(sw * BG_RATIO)
        bg_height = int(sh * BG_RATIO)
        mb, ms, mo_x, mo_y, mi_x, mi_y = create_minimap_background(
            game_state['game_map'], bg_width, bg_height
        )

        game_state['minimap_background']     = mb
        game_state['minimap_scale']          = ms
        game_state['minimap_offset_x']       = mo_x
        game_state['minimap_offset_y']       = mo_y
        game_state['minimap_min_iso_x']      = mi_x
        game_state['minimap_min_iso_y']      = mi_y

        new_bg_rect = mb.get_rect()
        new_bg_rect.center = new_panel_rect.center
        new_bg_rect.y -= panel_height / 50
        new_bg_rect.x += panel_width / 18
        game_state['minimap_background_rect'] = new_bg_rect

        game_state['minimap_entities_surface'] = pygame.Surface(
            (mb.get_width(), mb.get_height()),
            pygame.SRCALPHA
        )
        game_state['minimap_entities_surface'].fill((0, 0, 0, 0))

        game_state['screen_width']  = sw
        game_state['screen_height'] = sh

        game_state['force_full_redraw'] = True
        game_state['player_selection_updated'] = True

        camera.limit_camera()
        return

    elif event.type == pygame.KEYDOWN:
        # --- NOUVEAU : gestion de F9 pour switch d’affichage ---
        if event.key == pygame.K_F9:
            # On ne bascule que si on est en mode "GUI only" (0) ou "Terminal only" (1).
            from Settings.setup import user_choices
            if user_choices["index_terminal_display"] in [0, 1]:
                debug_print("[GUI] F9 => Switch display mode requested")
                game_state['switch_display'] = True
                # Pas besoin d'en faire plus ici : la boucle de jeu s’arrêtera.

        elif event.key == pygame.K_F1:
            game_state['show_gui_elements'] = not game_state['show_gui_elements']
            debug_print(f"[GUI] F1 => Show/Hide GUI elements={game_state['show_gui_elements']}")

        elif event.key == pygame.K_F3:
            game_state['show_all_health_bars'] = not game_state['show_all_health_bars']
            debug_print(f"[GUI] F3 => show_all_health_bars={game_state['show_all_health_bars']}")

        elif event.key in [pygame.K_k, pygame.K_F11]:
            handle_save_game(game_state)

        elif event.key in [pygame.K_l, pygame.K_F12]:
            try:
                root = Tk()
                root.withdraw()
                chosen_path = filedialog.askopenfilename(
                    initialdir=resolve_save_path('saves'),
                    filetypes=[("Pickle","*.pkl")]
                )
                root.destroy()
                if chosen_path:
                    handle_load_game(game_state, chosen_path)
            except Exception as e:
                debug_print(f"[GUI] Error in load dialog: {e}")

        elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS):
            camera.set_zoom(camera.zoom * 1.1)
            debug_print("[GUI] Zoom avant via +")

        elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
            camera.set_zoom(camera.zoom / 1.1)
            debug_print("[GUI] Zoom arrière via -")

        elif event.key == pygame.K_m:
            camera.zoom_out_to_global()
            debug_print("[GUI] m => Camera zoom out global.")

        elif event.key == pygame.K_ESCAPE:
            game_state['pause_menu_active'] = not game_state.get('pause_menu_active', False)
            game_state['paused'] = game_state['pause_menu_active']
            debug_print("[GUI] ESC => Pause menu toggled.")

        elif event.key == pygame.K_F2:
            game_state['show_player_info'] = not game_state['show_player_info']

        elif event.key == pygame.K_F4:
            game_state['show_unit_and_building_health_bars'] = not game_state.get('show_unit_and_building_health_bars', False)
            debug_print(f"[GUI] F4 => show_unit_and_building_health_bars={game_state['show_unit_and_building_health_bars']}")

        elif event.key == pygame.K_j:
            screen = game_state['screen']
            if game_state['fullscreen']:
                display_info = pygame.display.Info()
                window_width = int(display_info.current_w * 0.9)
                window_height = int(display_info.current_h * 0.9)
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
            else:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            
            game_state['fullscreen'] = not game_state['fullscreen']
            game_state['screen'] = screen
            game_state['screen_width'] = screen.get_width()
            game_state['screen_height'] = screen.get_height()
            game_state['force_full_redraw'] = True
            debug_print(f"[GUI] J => Toggle fullscreen: {game_state['fullscreen']}")

        else:
            # Mouvement terminal si mode Terminal or Both
            from Settings.setup import user_choices
            if user_choices["index_terminal_display"] in [1, 2]:
                if game_state['game_map'] and game_state['game_map'].game_state:
                    terminal_map = game_state['game_map']
                    move_amount = 1
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_SHIFT:
                        move_amount = 5
                        debug_print("[CURSES] SHIFT => scroll accéléré")

                    if event.key in [pygame.K_z, pygame.K_UP]:
                        terminal_map.terminal_view_y -= move_amount
                    elif event.key in [pygame.K_s, pygame.K_DOWN]:
                        terminal_map.terminal_view_y += move_amount
                    elif event.key in [pygame.K_q, pygame.K_LEFT]:
                        terminal_map.terminal_view_x -= move_amount
                    elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                        terminal_map.terminal_view_x += move_amount
                    elif event.key == pygame.K_m:
                        debug_print("[CURSES] M => recentrage curses")
                        half_w = terminal_map.num_tiles_x // 2
                        half_h = terminal_map.num_tiles_y // 2
                        terminal_map.terminal_view_x = max(0, half_w - 40)
                        terminal_map.terminal_view_y = max(0, half_h - 15)

    elif event.type == pygame.KEYUP:
        if event.key == pygame.K_TAB:
            game_state['paused'] = not game_state.get('paused', False)
            if game_state['paused']:
                write_full_html(game_state['players'], game_state['game_map'])
                debug_print("[GUI] TAB => Pause activée, snapshot générée.")
            else:
                debug_print("[GUI] TAB => Unpause => reprise du jeu.")

        elif event.key == pygame.K_p:
            game_state['paused'] = not game_state.get('paused', False)
            if game_state['paused']:
                debug_print("[GUI] 'p' => Pause activée.")
            else:
                debug_print("[GUI] 'p' => Unpause => reprise du jeu.")

    elif event.type == pygame.MOUSEBUTTONDOWN:
        if game_state.get('pause_menu_active', False):
            button_rects = game_state.get('pause_menu_button_rects', {})
            mx, my = event.pos
            for label, rect in button_rects.items():
                if rect.collidepoint(mx, my):
                    if label == "Resume":
                        game_state['pause_menu_active'] = False
                        game_state['paused'] = False
                    elif label == "Load Game":
                        try:
                            root = Tk()
                            root.withdraw()
                            chosen_path = filedialog.askopenfilename(
                                initialdir=resolve_save_path('saves'),
                                filetypes=[("Pickle","*.pkl")]
                            )
                            root.destroy()
                            if chosen_path:
                                handle_load_game(game_state, chosen_path)
                        except Exception as e:
                            debug_print(f"[GUI] Error in pause menu load: {e}")
                        pass
                    elif label == "Save Game":
                        game_state['game_map'].save_map()
                        debug_print("[GUI] L => Sauvegarde effectuée.")
                        game_state['notification_message'] = "Partie sauvegardée."
                        game_state['notification_start_time'] = time.time()
                    elif label == "Exit":
                        try:
                            os.remove('full_snapshot.html')
                        except:
                            pass
                        pygame.quit()
                        sys.exit()
            return  # Do not process other events while pause menu is active
        mouse_x, mouse_y = event.pos
        mods = pygame.key.get_mods()
        ctrl_pressed = (mods & pygame.KMOD_CTRL)

        if event.button == 1:
            if game_state['minimap_background_rect'].collidepoint(mouse_x, mouse_y):
                game_state['minimap_dragging'] = True
            else:
                train_rects = game_state.get('train_button_rects', {})
                clicked_building_id = None
                for bld_id, rect in train_rects.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        clicked_building_id = bld_id
                        break

                if clicked_building_id is not None:
                    building_clicked = find_entity_by_id(game_state, clicked_building_id)
                    if building_clicked and selected_player:
                        if building_clicked.team == selected_player.teamID:
                            success = building_clicked.add_to_training_queue(selected_player)
                            game_state['player_info_updated'] = True
                            if success in {-1, 0}:
                                if 'insufficient_resources_feedback' not in game_state:
                                    game_state['insufficient_resources_feedback'] = {}
                                if success == -1:
                                    game_state['insufficient_resources_feedback'][building_clicked.entity_id] = (time.time(), "Not enought resources")
                                elif success == 0:
                                    game_state['insufficient_resources_feedback'][building_clicked.entity_id] = (time.time(), "Maximum population reached")
                else:
                    entity = closest_entity(game_state, mouse_x, mouse_y)
                    if entity:
                        select_single_entity(entity, game_state, ctrl_pressed)
                        if hasattr(entity, 'notify_clicked'):
                            entity.notify_clicked()
                    else:
                        handle_left_click_on_panels_or_start_box_selection(
                            mouse_x, 
                            mouse_y, 
                            game_state, 
                            ctrl_pressed
                        )

        elif event.button == 3:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                mouse_x, mouse_y = screen_to_2_5d(
                    mouse_x, mouse_y, screen_width, screen_height,
                    camera, HALF_TILE_SIZE, HALF_TILE_SIZE / 2
                )

                if keys[pygame.K_1]:
                    selected_player.build("TownCenter", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_2]:
                    selected_player.build("House", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_3]:
                    selected_player.build("ArcheryRange", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_4]:
                    selected_player.build("Barracks", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_5]:
                    selected_player.build("Camp", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_6]:
                    selected_player.build("House", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_7]:
                    selected_player.build("Keep", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_8]:
                    selected_player.build("Stable", mouse_x, mouse_y, 3, game_state['game_map'])
                elif keys[pygame.K_9]:
                    selected_player.build("Stable", mouse_x, mouse_y, 3, game_state['game_map'])

            else:
                if selected_player and 'selected_units' in game_state and len(game_state['selected_units']) > 0:
                    entity_target = closest_entity(game_state, mouse_x, mouse_y)
                    for unit_selected in game_state['selected_units']:
                        unit_selected.path = None
                        unit_selected.set_target(entity_target)
                    mouse_x, mouse_y = screen_to_2_5d(
                        mouse_x, mouse_y, screen_width, screen_height,
                        camera, HALF_TILE_SIZE, HALF_TILE_SIZE / 2
                    )
                    for unit_selected in game_state['selected_units']:
                        unit_selected.set_destination((mouse_x, mouse_y), game_state['game_map'])

        elif event.button == 4:
            camera.set_zoom(camera.zoom * 1.1)
            debug_print("[GUI] molette haut => zoom avant")

        elif event.button == 5:
            camera.set_zoom(camera.zoom / 1.1)
            debug_print("[GUI] molette bas => zoom arrière")

    elif event.type == pygame.MOUSEMOTION:
        if game_state['minimap_dragging']:
            current_x, current_y = event.pos
            mini_rect = game_state['minimap_background_rect']
            local_x = current_x - mini_rect.x
            local_y = current_y - mini_rect.y

            scale = game_state['minimap_scale']
            offset_x = game_state['minimap_offset_x']
            offset_y = game_state['minimap_offset_y']
            map_min_iso_x = game_state['minimap_min_iso_x']
            map_min_iso_y = game_state['minimap_min_iso_y']

            iso_x = (local_x - offset_x) / scale + map_min_iso_x
            iso_y = (local_y - offset_y) / scale + map_min_iso_y

            camera.offset_x = -iso_x
            camera.offset_y = -iso_y
            camera.limit_camera()
        else:
            if game_state.get('selecting_entities', False):
                game_state['selection_end'] = event.pos

    elif event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:
            game_state['minimap_dragging'] = False
            if game_state.get('selecting_entities'):
                finalize_box_selection(game_state)


def select_single_entity(entity, game_state, ctrl_pressed):
    if 'selected_entities' not in game_state:
        game_state['selected_entities'] = []
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []

    if not ctrl_pressed:
        game_state['selected_entities'].clear()
        game_state['selected_units'].clear()

    if entity not in game_state['selected_entities']:
        game_state['selected_entities'].append(entity)

    selected_player = game_state['selected_player']
    if selected_player and isinstance(entity, Unit):
        if entity.team == selected_player.teamID:
            if entity not in game_state['selected_units']:
                game_state['selected_units'].append(entity)


def handle_left_click_on_panels_or_start_box_selection(mouse_x, mouse_y, game_state, ctrl_pressed=False):
    players = game_state['players']
    screen_height = game_state['screen_height']
    minimap_rect = game_state['minimap_background_rect']
    button_height = 30
    padding = 5
    max_display_height = screen_height / 3

    columns = 1
    while columns <= 4:
        rows = (len(players) + columns - 1) // columns
        total_height = button_height * rows + padding * (rows - 1)
        if total_height <= max_display_height or columns == 4:
            break
        columns += 1

    button_width = (minimap_rect.width - padding * (columns - 1)) // columns
    rows = (len(players) + columns - 1) // columns
    total_height = button_height * rows + padding * (rows - 1)

    base_x = minimap_rect.x
    base_y = minimap_rect.y - total_height - padding

    camera = game_state['camera']
    clicked_player_panel = False

    from Entity.Building import TownCentre

    for index, player_obj in enumerate(reversed(players)):
        col = index % columns
        row = index // columns
        rect_x = base_x + col * (button_width + padding)
        rect_y = base_y + row * (button_height + padding)
        panel_rect = pygame.Rect(rect_x, rect_y, button_width, button_height)

        if panel_rect.collidepoint(mouse_x, mouse_y):
            if game_state['selected_player'] != player_obj:
                game_state['selected_player'] = player_obj
                game_state['player_selection_updated'] = True
                game_state['player_info_updated'] = True
                
                # S'assurer que le joueur a une entrée dans old_resources
                if 'old_resources' not in game_state:
                    game_state['old_resources'] = {}
                if player_obj.teamID not in game_state['old_resources']:
                    game_state['old_resources'][player_obj.teamID] = player_obj.resources.copy()
                
                # Centrer la caméra sur son TownCentre si possible
                for building_obj in player_obj.buildings:
                    if isinstance(building_obj, TownCentre):
                        iso_x, iso_y = to_isometric(
                            building_obj.x, 
                            building_obj.y, 
                            HALF_TILE_SIZE, 
                            HALF_TILE_SIZE / 2
                        )
                        camera.offset_x = -iso_x
                        camera.offset_y = -iso_y
                        camera.limit_camera()
                        break
            clicked_player_panel = True
            break

    if not clicked_player_panel:
        game_state['selecting_entities'] = True
        game_state['selection_start'] = (mouse_x, mouse_y)
        game_state['selection_end'] = (mouse_x, mouse_y)
        game_state['box_additive'] = ctrl_pressed


def finalize_box_selection(game_state):
    import pygame
    from Controller.utils import tile_to_screen

    x1, y1 = game_state['selection_start']
    x2, y2 = game_state['selection_end']
    select_rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    select_rect.normalize()

    game_state['selecting_entities'] = False
    game_state['selection_start'] = None
    game_state['selection_end'] = None

    if 'selected_entities' not in game_state:
        game_state['selected_entities'] = []
    if 'selected_units' not in game_state:
        game_state['selected_units'] = []

    if not game_state.get('box_additive', False):
        game_state['selected_entities'].clear()
        game_state['selected_units'].clear()

    selected_player = game_state['selected_player']
    if not selected_player:
        return

    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    camera = game_state['camera']
    game_map = game_state['game_map']

    all_entities = set()
    for entities_set in game_map.grid.values():
        for entity_obj in entities_set:
            all_entities.add(entity_obj)

    for entity_obj in all_entities:
        screen_x, screen_y = tile_to_screen(
            entity_obj.x, 
            entity_obj.y,
            HALF_TILE_SIZE, 
            HALF_TILE_SIZE / 2,
            camera, 
            screen_width, 
            screen_height
        )
        if select_rect.collidepoint(screen_x, screen_y):
            if entity_obj not in game_state['selected_entities']:
                game_state['selected_entities'].append(entity_obj)

            if isinstance(entity_obj, Unit) and entity_obj.team == selected_player.teamID:
                if entity_obj not in game_state['selected_units']:
                    game_state['selected_units'].append(entity_obj)


def closest_entity(game_state, mouse_x, mouse_y, search_radius=2):
    game_map = game_state['game_map']
    camera = game_state['camera']
    screen_width = game_state['screen_width']
    screen_height = game_state['screen_height']
    mouse_2_5d = screen_to_2_5d(mouse_x, mouse_y, screen_width, screen_height, camera, HALF_TILE_SIZE, HALF_TILE_SIZE/2)

    tile_x, tile_y = screen_to_tile(
        mouse_x, mouse_y, 
        screen_width, screen_height, 
        camera, 
        HALF_TILE_SIZE / 2, 
        HALF_TILE_SIZE / 4
    )
    entity_set = game_map.grid.get((tile_x, tile_y), [])
    print(f'found : {entity_set}')
    shortest_distance = 999999
    closest_ent = None
    for entity in entity_set:
        distance = math.dist(mouse_2_5d, (entity.x, entity.y)) - entity.hitbox
        if distance < shortest_distance:
            shortest_distance = distance
            closest_ent = entity
    return closest_ent


def find_entity_by_id(game_state, entity_id):
    game_map = game_state['game_map']
    for position, entity_set in game_map.grid.items():
        for entity_obj in entity_set:
            if entity_obj.entity_id == entity_id:
                return entity_obj

    for position, entity_set in game_map.inactive_matrix.items():
        for entity_obj in entity_set:
            if entity_obj.entity_id == entity_id:
                return entity_obj
    return None
