import pygame
import os
import sys
import threading
import time
import platform
try:
    import msvcrt
except ImportError:
    msvcrt = None

from select import select

from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Controller.init_player import init_players
# --- NOUVEAU import pour surveiller le chargement des assets
from Controller.init_assets import load_sprites, ASSETS_LOADED, get_assets_progress, is_assets_loaded

from Settings.setup import SAVE_DIRECTORY
from Controller.gui import run_gui_menu, user_choices, VALID_GRID_SIZES, VALID_BOTS_COUNT, VALID_LEVELS
from Controller.Bot import *

# Import du curses terminal display
from Controller.terminal_display import start_terminal_interface


def get_input_non_blocking():
    if platform.system() == "Windows" and msvcrt:
        if msvcrt.kbhit():
            return msvcrt.getwche()
        return None
    else:
        rlist, _, _ = select([sys.stdin], [], [], 0)
        if rlist:
            return sys.stdin.readline()
        return None


def ask_terminal_inputs_non_blocking():
    """
    Menu Terminal non-bloquant.
    [1] GUI only / [2] Terminal only / [3] Both (défaut=3)
    puis [1] nouvelle partie / [2] load, etc.

    => On stocke le résultat dans user_choices et on met user_choices["validated"] = True à la fin.
    """
    step = 0
    saves = []

    while True:
        if user_choices["validated"]:
            return  # On arrête dès que c'est validé

        if step == 0:
            print("\n--- Choisir le mode d'affichage ---")
            print("[1] GUI only / [2] Terminal only / [3] Both ? (défaut=3)")
            step = 1

        elif step == 2:
            print("\n--- Menu Terminal ---")
            print("[1] Nouvelle partie / [2] Charger une sauvegarde ?")
            step = 3

        elif step == 4:
            print("\n--- Paramètres de la nouvelle partie : ---")
            print("Tailles possibles :", VALID_GRID_SIZES)
            print(f"Taille (défaut={user_choices['grid_size']}) : ")
            step = 5

        elif step == 6:
            print(f"Nb bots possibles : 1..55 (défaut={user_choices['num_bots']})")
            print("Nb bots : ")
            step = 7

        elif step == 8:
            print("Niveaux possibles :", VALID_LEVELS)
            print(f"Niveau bots (défaut={user_choices['bot_level']}) : ")
            step = 9

        elif step == 10:
            print("Or au centre ? (oui/non, défaut=non) : ")
            step = 11

        # Lecture non bloquante
        line_in = get_input_non_blocking()
        if line_in is not None:
            line = line_in.strip()

            if step == 1:
                if line == "":
                    user_choices["index_terminal_display"] = 2  # Both
                    print("Aucun choix => Both.")
                elif line in ['1', '2', '3']:
                    val = int(line)
                    if val == 1:
                        user_choices["index_terminal_display"] = 0
                        print("Mode choisi : GUI only.")
                    elif val == 2:
                        user_choices["index_terminal_display"] = 1
                        print("Mode choisi : Terminal only.")
                    else:
                        user_choices["index_terminal_display"] = 2
                        print("Mode choisi : Both (GUI+Terminal).")
                else:
                    user_choices["index_terminal_display"] = 2
                    print("Choix invalide => Both.")
                step = 2

            elif step == 3:
                if line == '2':
                    user_choices["load_game"] = True
                    if os.path.isdir(SAVE_DIRECTORY):
                        saves = [f for f in os.listdir(SAVE_DIRECTORY) if f.endswith('.pkl')]
                        if saves:
                            print("Saves disponibles :")
                            for idx, sf in enumerate(saves):
                                print(f"{idx+1} - {sf}")
                            print("Sélection de la sauvegarde : ")
                            step = 12
                        else:
                            print("Aucune sauvegarde => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4
                    else:
                        print("Pas de répertoire => nouvelle partie.")
                        user_choices["load_game"] = False
                        step = 4
                else:
                    user_choices["load_game"] = False
                    step = 4

            elif step == 12:
                if line == "":
                    print("Pas de saisie => nouvelle partie.")
                    user_choices["load_game"] = False
                    step = 4
                else:
                    try:
                        sel_idx = int(line) - 1
                        if 0 <= sel_idx < len(saves):
                            user_choices["chosen_save"] = os.path.join(SAVE_DIRECTORY, saves[sel_idx])
                            user_choices["validated"] = True
                            return
                        else:
                            print("Index invalide => nouvelle partie.")
                            user_choices["load_game"] = False
                            step = 4
                    except:
                        print("Choix invalide => nouvelle partie.")
                        user_choices["load_game"] = False
                        step = 4

            elif step == 5:
                if line == "":
                    print(f"Pas de saisie => taille par défaut {user_choices['grid_size']}")
                    step = 6
                else:
                    if line.isdigit():
                        val = int(line)
                        if val in VALID_GRID_SIZES:
                            user_choices["grid_size"] = val
                            print(f"Taille : {val}")
                    step = 6

            elif step == 7:
                if line == "":
                    print(f"Pas de saisie => nb bots par défaut {user_choices['num_bots']}")
                    step = 8
                else:
                    if line.isdigit():
                        val = int(line)
                        if 1 <= val <= 55:
                            user_choices["num_bots"] = val
                            print(f"Nb bots : {val}")
                    step = 8

            elif step == 9:
                if line == "":
                    print(f"Pas de saisie => niveau bots par défaut {user_choices['bot_level']}")
                    step = 10
                else:
                    if line in VALID_LEVELS:
                        user_choices["bot_level"] = line
                        print(f"Niveau bots : {line}")
                    step = 10

            elif step == 11:
                if line == "":
                    step = 13
                else:
                    if line.lower() == "oui":
                        user_choices["gold_at_center"] = True
                    step = 13

            if step == 13:
                user_choices["validated"] = True
                return

        time.sleep(0.01)


def background_load_assets(screen, sw, sh):
    """
    Cette fonction sera appelée en thread pour charger
    tous les assets sans bloquer la boucle principale.
    On ne dessine pas la progress_bar directement ici (thread).
    """
    load_sprites(screen, sw, sh, show_progress=False)


def show_loading_screen_until_done(screen, sw, sh):
    """
    Tant que tous les assets ne sont pas chargés,
    on affiche la barre de progression.
    """
    from Controller.init_assets import draw_progress_bar
    clock = pygame.time.Clock()

    running = True
    while running:
        # Gestion d'événements : on autorise par ex. à fermer la fenêtre
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        progress = get_assets_progress()

        # draw_progress_bar(progress, screen, sw, sh, "Loading", loading_screen_image)
        # On utilise la version existante qui attend un param `progress_text`
        # + l'image de fond (loading_screen)
        # => Comme dans init_assets, on peut récupérer "loading_screen" via get_scaled_gui
        from Controller.init_assets import get_scaled_gui
        loading_screen = get_scaled_gui('loading_screen', variant=0, target_height=sh)

        draw_progress_bar(screen, progress, sw, sh, "Chargement en cours", loading_screen)

        if is_assets_loaded():
            running = False

        clock.tick(60)


def main():
    """
    Nouvelle logique :
    1) On initialise Pygame et la fenêtre
    2) On lance un thread pour charger les assets en arrière-plan
    3) On lance le menu (GUI + terminal)
    4) Lorsque le joueur valide le lancement de la partie, si le
       chargement n'est pas fini, on affiche l'écran de chargement
       jusqu'à la fin du thread. Sinon on lance directement la partie.
    """
    while True:
        screen, sw, sh = init_pygame()

        # Lancement du chargement asynchrone des assets
        t_assets = threading.Thread(target=background_load_assets, args=(screen, sw, sh))
        t_assets.start()

        # On lance le menu terminal en thread (non-bloquant)
        t_menu = threading.Thread(target=ask_terminal_inputs_non_blocking)
        t_menu.start()

        # On lance le menu GUI
        from Controller.gui import run_gui_menu
        run_gui_menu(screen, sw, sh)

        # On attend la fin du thread menu (pour être sûr que user_choices est bien figé)
        if t_menu.is_alive():
            t_menu.join()

        # => user_choices est fixé : on lit ce qu'il faut
        mode_index  = user_choices["index_terminal_display"]
        load_game   = user_choices["load_game"]
        chosen_save = user_choices["chosen_save"]
        grid_size   = user_choices["grid_size"]
        nb_bots     = user_choices["num_bots"]
        bot_level   = user_choices["bot_level"]
        gold_c      = user_choices["gold_at_center"]

        # Si le joueur valide et que tout n'est pas encore chargé,
        # on lance l'écran de progression bloquant
        if not is_assets_loaded():
            show_loading_screen_until_done(screen, sw, sh)

        # Puisqu'on est potentiellement sorti du chargement,
        # on est sûr que tout est dispo => on termine le thread de chargement
        if t_assets.is_alive():
            t_assets.join()

        # On se base ensuite sur le choix mode_index pour éventuellement
        # fermer la fenêtre Pygame si Terminal only
        if mode_index == 1:
            # Terminal only => on ferme l'affichage
            pygame.display.quit()
            screen = None

        # Création ou chargement de la map
        from Models.Map import GameMap
        from Controller.init_assets import ASSETS_LOADED
        from Controller.init_player import init_players

        if load_game and chosen_save:
            game_map = GameMap(0, False, [], generate=False)
            game_map.load_map(chosen_save)
            players = game_map.players
        else:
            players = init_players(nb_bots, bot_level)
            game_map = GameMap(grid_size, gold_c, players)
  

        # Si Terminal ou Both => on lance curses
        if mode_index in [1, 2]:
            from Controller.terminal_display import start_terminal_interface
            t_curses = threading.Thread(target=start_terminal_interface, args=(game_map,), daemon=True)
            t_curses.start()

        # Boucle de jeu
        from Controller.game_loop import game_loop
        game_loop(screen, game_map, sw, sh, players)
        menu_result = user_choices.get("menu_result")
        if menu_result == "main_menu":
            from Controller.terminal_display import stop_curses
            stop_curses()
            pygame.quit()
            user_choices.clear()
            user_choices["menu_result"] = None
            user_choices.update({
                "index_terminal_display": 2,
                "load_game": False,
                "chosen_save": "",
                "grid_size": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False
            })
            continue
        elif menu_result == "quit":
            break

        # Check si le joueur veut un retour au menu
        if game_map.game_state.get('return_to_menu'):
            from Controller.terminal_display import stop_curses
            stop_curses()
            pygame.quit()

            user_choices.clear()
            user_choices.update({
                "index_terminal_display": 2,
                "load_game": False,
                "chosen_save": "",
                "grid_size": 120,
                "num_bots": 2,
                "bot_level": "lean",
                "gold_at_center": False,
                "validated": False
            })
            continue
        else:
            break


if __name__ == "__main__":
    main()
