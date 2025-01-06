from Entity.Unit import Unit  
from Settings.setup import Resources
from Entity.Building import TownCentre, House

class Villager(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="v", 
            max_hp=40, 
            cost=Resources(food=50, gold=0, wood=25), 
            attack_power=2,
            attack_range=1, 
            attack_speed=2.03,
            speed=1, 
            training_time=20, 
        )
        self.resources = 0
        self.carry_capacity = 20
        self.resource_rate = 25 / 60

    def isAvailable(self):
        return not self.task 

    def collectResource(self, resource_tile, duration, map):
        valid_resources = {'G': 'gold', 'W': 'wood', 'F': 'food'}
        if not self.isAvailable() or resource_tile.terrain_type not in valid_resources:
            return
        self.task = True
        self.move(resource_tile.x, resource_tile.y, map)
        self.resources += min(self.resource_rate * duration, self.carry_capacity - self.resources)
        self.task = False

    def stockResources(self, building, map):
        if not self.isAvailable() or not building.resourceDropPoint:
            return
        self.task = True
        self.move(building.x, building.y, map)
        building.addResources(self.resources)
        self.resources = 0
        self.task = False

    def build(self, map,building):
        if not self.isAvailable():
            return
        self.task = True
        self.move((building.x, building.y), map)
        building.constructors.append(self)
    

    def buildTime(self, building, num_villagers):
        return max(10, (3 * building.buildTime) / (num_villagers + 2)) if num_villagers > 0 else building.buildTime