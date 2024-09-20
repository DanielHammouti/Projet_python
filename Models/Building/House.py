from Models.Building.Building import Building

class House(Building):
    def __init__(self):
        super().__init__(
            acronym='H',
            woodCost=25,
            goldCost=0,
            buildTime=25,
            hp=200,
            size1=2,
            size2=2,
            population=5
        )
