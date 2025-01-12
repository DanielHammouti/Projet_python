from Controller.terminal_display_debug import debug_print

class Resources:
    def __init__(self, food=0, gold=0, wood=0):
        self.food = food
        self.gold = gold
        self.wood = wood

    def set_resources(self, food=0, gold=0, wood=0):
        self.food = food
        self.gold = gold
        self.wood = wood

    def add_food(self, amount):
        self.food += amount
        return amount

    def remove_food(self, amount):
        removed = min(self.food, amount)
        self.food -= removed
        return removed

    def add_gold(self, amount):
        self.gold += amount
        return amount

    def remove_gold(self, amount):
        removed = min(self.gold, amount)
        self.gold -= removed
        return removed

    def add_wood(self, amount):
        self.wood += amount
        return amount

    def remove_wood(self, amount):
        removed = min(self.wood, amount)
        self.wood -= removed
        return removed

    def increase_resources(self, resources):
        food, gold, wood = resources
        self.food += food
        self.gold += gold
        self.wood += wood
        return (food, gold, wood)

    def decrease_resources(self, resources):
        food, gold, wood = resources
        removed_food = min(self.food, food)
        removed_gold = min(self.gold, gold)
        removed_wood = min(self.wood, wood)
        self.food -= removed_food
        self.gold -= removed_gold
        self.wood -= removed_wood
        return (removed_food, removed_gold, removed_wood)

    def has_enough(self, costs):
        debug_print("Resources:", self.get())  # Should debug_print a tuple of numbers
        debug_print("Costs:", costs)          # Should debug_print a tuple of numbers
        return all(resource >= cost for resource, cost in zip(self.get(), costs))

    def get(self):
        return (self.food, self.gold, self.wood)

    def total(self):
        return self.food + self.gold + self.wood

    def copy(self):
        return Resources(self.food, self.gold, self.wood)

    def __eq__(self, other):
        if isinstance(other, Resources):
            return self.food == other.food and self.gold == other.gold and self.wood == other.wood
        return False

    def __repr__(self):
        return f"Resources(food={self.food}, wood={self.wood}, gold={self.gold})"
