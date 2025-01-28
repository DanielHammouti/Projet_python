# Chemin de C:/Users/cyril/OneDrive/Documents/INSA/3A/PYTHON_TEST/Projet_python\Controller\Bot.py
from Models.Team import *
from Settings.setup import  RESOURCE_THRESHOLDS
from Entity.Unit import Villager, Archer, Swordsman, Horseman
from Entity.Building import *


#Priorité 5

def get_military_unit_count(player_team):
    #print(f"MUC : {sum(1 for unit in player_team.units if not isinstance(unit, Villager))}")

    return sum(1 for unit in player_team.units if not isinstance(unit, Villager))


def train_units(player_team, building):
    return building.add_to_training_queue(player_team)

def balance_units(player_team):
    villager_count = sum(1 for unit in player_team.units if isinstance(unit, Villager))
    military_count = get_military_unit_count(player_team)
    if player_team.resources.food < 100 and villager_count < 10:
        train_units(player_team, Villager, {"gold": 0, "food": 50})
    elif military_count < 20:
        train_units(player_team, (unit for unit in player_team.units if not isinstance(unit, Villager)), {"gold": 50, "food": 50})
    for b in player_team.buildings:
        train_units(player_team,b)

def choose_attack_composition(player_team):
    archers = [unit for unit in player_team.units if isinstance(unit, Archer)]
    swordsmen = [unit for unit in player_team.units if isinstance(unit, Swordsman)]
    horsemen = [unit for unit in player_team.units if isinstance(unit, Horseman)]

    if len(archers) >= 3 and len(swordsmen) >= 1 and len(horsemen) >= 1:
        return archers[:3] + swordsmen[:1] + horsemen[:1]
    elif len(archers) >= 3 and len(swordsmen) >= 1:
        return archers[:3] + swordsmen[:1]
    elif len(archers) >= 3:
        return archers[:3]
    elif len(swordsmen) >= 1:
        return swordsmen[:1]
    elif len(horsemen) >= 1:
        return horsemen[:1]
    else:
        return []

def maintain_army(player_team):
    military_count = get_military_unit_count(player_team)
    if military_count < 20:
        balance_units(player_team)
    else:
        attack_composition = choose_attack_composition(player_team)
        for unit in attack_composition:
            if not isinstance(unit, Villager):
                if unit.idle:
                    unit.seek_attack()
                elif unit.target:
                    unit.kill()
                else:
                    unit.setIdle()

def priorite_5(player_team,unit,building):
    train_units(player_team,unit,building)
    balance_units(player_team)
    choose_attack_composition(player_team)
    maintain_army(player_team)

#Priorty seven avoid ressources shortage

def get_resource_shortage(current_resources, RESOURCE_THRESHOLDS):
    for resource in ['food', 'wood', 'gold']:
        if getattr(current_resources, resource, 0) < RESOURCE_THRESHOLDS.get(resource, 0):
            return resource
def get_resource_shortage(current_resources, RESOURCE_THRESHOLDS):
    for resource in ['food', 'wood', 'gold']:
        if getattr(current_resources, resource, 0) < RESOURCE_THRESHOLDS.get(resource, 0):
            return resource
    return None


def find_resources(game_map, resource_type):
    if not resource_type:
        return []
    resource_positions = []
    for position, entities in game_map.grid.items():
        for entity in entities:
            if isinstance(entity, resource_type):
                resource_positions.append(position)
    return resource_positions


def find_resources(game_map, resource_type):
    if not resource_type:
        return []
    resource_positions = []
    for position, entities in game_map.grid.items():
        for entity in entities:
            if isinstance(entity, resource_type):
                resource_positions.append(position)
    return resource_positions


def reallocate_villagers(resource_in_shortage, team, game_map):
    for unit in team.units:  # Assuming `team.units` provides access to all units in the team
        if hasattr(unit, "carry") and unit.isAvailable() and not unit.task:
            resource_positions = find_resources(game_map, resource_in_shortage)
            if resource_positions:
                nearest_resource = min(
                    resource_positions,
                    key=lambda pos: math.sqrt((unit.x - pos[0]) ** 2 + (unit.y - pos[1]) ** 2)
                )
                unit.set_target(nearest_resource)
                return


def check_and_address_resources(team, game_map, RESOURCE_THRESHOLDS):
    resource_shortage = get_resource_shortage(team.resources, RESOURCE_THRESHOLDS)
    if resource_shortage:
        reallocate_villagers(resource_shortage, team, game_map)



#Priorité 2

def search_for_target(unit, enemy_team, attack_mode=True):
    """
    Searches for the closest enemy unit or building depending on the mode.
    vise en premier les keeps puis les units puis les villagers et buildings
    """
    closest_distance = float("inf")
    closest_entity = None

    targets=[keep for keep in enemy_team.buildings if isinstance(keep,Keep)]
    if targets!=[] and attack_mode:
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager):
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    targets=[unit for unit in enemy_team.units if not isinstance(unit,Villager)]
    for enemy in targets:
        dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
        if dist < closest_distance:
            closest_distance = dist
            closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    if attack_mode:
        targets=[unit for unit in enemy_team.units if isinstance(unit,Villager)]
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager):
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy

        for enemy_building in enemy_team.buildings:
            dist = math.dist((unit.x, unit.y), (enemy_building.x, enemy_building.y))
            if dist < closest_distance:
              closest_distance = dist
              closest_entity = enemy_building



#Priorité 2

def search_for_target(unit, enemy_team, attack_mode=True):
    """
    Searches for the closest enemy unit or building depending on the mode.
    vise en premier les keeps puis les units puis les villagers et buildings
    """
    closest_distance = float("inf")
    closest_entity = None

    targets=[keep for keep in enemy_team.buildings if isinstance(keep,Keep)]
    if targets!=[] and attack_mode:
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager):
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    targets=[unit for unit in enemy_team.units if not isinstance(unit,Villager)]
    for enemy in targets:
        dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
        if dist < closest_distance:
            closest_distance = dist
            closest_entity = enemy
    if closest_entity!=None:
        unit.set_target(closest_entity)
        return unit.attack_target is not None

    if attack_mode:
        targets=[unit for unit in enemy_team.units if isinstance(unit,Villager)]
        for enemy in targets:
            dist = math.dist((unit.x, unit.y), (enemy.x, enemy.y))
            if attack_mode or not isinstance(enemy,Villager):
                if dist < closest_distance:
                    closest_distance = dist
                    closest_entity = enemy

        for enemy_building in enemy_team.buildings:
            dist = math.dist((unit.x, unit.y), (enemy_building.x, enemy_building.y))
            if dist < closest_distance:
              closest_distance = dist
              closest_entity = enemy_building

    unit.set_target(closest_entity)
    return unit.attack_target is not None


def priority_2(players,selected_player,players_target):
    #lance l'attaque en essayant de choisir une cible
    #si elle réussi vise en premier les keeps ou les units
    if players_target[selected_player.teamID]!=None:
        #attaque déjà en cours
        return False
    return choose_target(players,selected_player,players_target)


def modify_target(player,target,players_target):
    """
    Met à jour la cible de l'équipe (arrête toutes les attaques de la team)
    pour la remplacer par la nouvelle 'target'.
    """
    players_target[player.teamID]=target
    for unit in player.units:
        if not isinstance(unit,Villager):
            unit.target=None
            unit.task=True
            if unit.target:
                unit.attack(target,map)

def choose_target(players,selected_player,players_target):
    #testé
    count_max=201
    target=None
    for enemy_team in players:
        if enemy_team!=selected_player:
            count = sum(1 for unit in enemy_team.units if not isinstance(unit, Villager))
            if count<count_max:
                target=enemy_team
                count_max=count
    if target!=None:
        modify_target(selected_player,target,players_target)
    return target!=None

def is_under_attack():
    return True

def manage_battle(selected_player, players_target, players, game_map, dt):
    # Add safety checks at the start of the function
    if not selected_player or not players_target or len(players_target) != len(players):
        # Resize players_target if needed
        players_target[:] = [None for _ in range(len(players))]
        return

    if selected_player.teamID >= len(players_target):
        print(f"Warning: Invalid teamID {selected_player.teamID}. Skipping battle management.")
        return

    enemy = players_target[selected_player.teamID]  # Initialize enemy with current target
    attack_mode = True

    # defense
    if is_under_attack():
        # on cherche la team qui est entrain de nous attaquer si les frontieres on été violer:
        for i in range(0, len(players_target)):
            if players_target[i] == selected_player:
                for team in players:
                    if team.teamID == i:
                        players_target[selected_player.teamID] = None
                        enemy = team
                        attack_mode = False
                        break  # Added break to exit loop once enemy is found

    if enemy is not None and (len(enemy.units) != 0 or len(enemy.buildings) != 0):
        for unit in selected_player.units:
            if not isinstance(unit, Villager) or (len(selected_player.units) == 0 and not attack_mode):
                if unit.attack_target is not None and unit.attack_target.state != 'death':
                    unit.seekAttack(game_map, dt)
                else:
                    search_for_target(unit, enemy, attack_mode)
    else:
        modify_target(selected_player, None, players_target)
    if get_military_unit_count(selected_player) == 0:
        modify_target(selected_player, None, players_target)


#Priorité 6

def get_damaged_buildings(player_team, critical_threshold=0.5):
    return [
        building for building in player_team.buildings
        if building.hp / building.max_hp < critical_threshold
    ]

def can_repair_building(player_team, repair_cost):
    return player_team.resources["wood"] >= repair_cost["wood"]

def assign_villager_to_repair(player_team, building):
    for villager in player_team.units:
        if isinstance(villager, Villager) and villager.isAvailable():
            villager.repair(building)
            print(f"Villageois assigné à la réparation de {building}.")
            return True
    print("Aucun villageois disponible pour réparer.")
    return False

def repair_critical_buildings(player_team):
    damaged_buildings = get_damaged_buildings(player_team)
    for building in damaged_buildings:
        repair_cost = {"wood": 50}
        if can_repair_building(player_team, repair_cost):
            if not assign_villager_to_repair(player_team, building):
                print("Réparation différée faute de ressources ou de main-d'œuvre.")