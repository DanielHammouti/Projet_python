# main.py

from Controller.init_map import init_pygame, game_loop
from Models.Map import GameMap
from Models.Team import Team
from Controller.init_player import init_players
from Settings.setup import NUMBER_OF_PLAYERS
from Models.Unit.Swordsman import *
from Models.Building.Barracks import Barracks
from Models.Building.ArcheryRange import ArcheryRange
from Models.Building.Stable import Stable

def main():
    b=Barracks()
    t=Team("lean")
    s1=b.entraine(t)
    s2=b.entraine(t)
    #s1.SeDeplacer(2,2,game_map)
    s1.attaquer(s2)

    print(s2.hp,"ok")
    ###TEST HTML###
    
    t.units.append(s1)
    t.units.append(s2)
    print(t.builds(False,"B"))
    #t.write_html()
    print("fin")


     # Déballer les retours de init_pygame
    screen, screen_width, screen_height = init_pygame()
    players = init_players(NUMBER_OF_PLAYERS)

    # Initialiser la carte de jeu
    game_map = GameMap(players)
    #game_map.print_map()  
    
    # Lancer la boucle de jeu avec tous les arguments requis
    game_loop(screen, game_map, screen_width, screen_height, players)  
 


if __name__ == "__main__":
    main()