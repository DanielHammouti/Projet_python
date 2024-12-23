from Entity.Building import Building
from Settings.setup import Resources

class House(Building):
    def __init__(self, team, x=0, y=0):
        super().__init__(
            x=x,
            y=y,
            team=team,
            acronym='H',
            size=2,
            max_hp=200,
            cost=Resources(food=0, gold=0, wood=25),
            buildTime=25,
            population=5
        )
