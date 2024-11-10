from Models.Building.Building import Building
from Models.Unit.Archer import Archer

import time
class ArcheryRange(Building):
    def __init__(self):
        super().__init__(
            acronym='A',
            woodCost=175,
            goldCost=0,
            buildTime=50,
            hp=500,
            size1=3,
            size2=3,
            spawnsUnits=True
        )
    def entraine(self):
        a.Archer()
        time.sleep(h.training_time)
        return a
