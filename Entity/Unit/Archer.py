from Entity.Unit import Unit  

class Archer(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="a",
            cost_food=0, 
            cost_gold=45, 
            cost_wood=25, 
            hp=30, 
            attack=4, 
            speed=1, 
            training_time=35
        )
        self.range = 4  # Portée de l'archer (en tuiles) 