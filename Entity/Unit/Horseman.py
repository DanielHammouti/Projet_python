from Entity.Unit import Unit
from Settings.setup import Resources

class Horseman(Unit):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym="h",
            max_hp=45,
            cost=Resources(food=80, gold=20, wood=0),
            attack_power=10,
            attack_range=1,
            attack_speed=1.90,
            speed=1.2,
            training_time=30
        )
