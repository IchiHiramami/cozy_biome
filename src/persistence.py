import json
from datetime import datetime

class Persistence:
    @staticmethod
    def save_to_slot(file_slot : int, world_score : int, creatures : list, foods : list, potions : list):
        filename = f"checkpoint_{file_slot}.json"
        state = {
            "world_score" : world_score,
            "creatures" : [],
            "inventory" : {
                "drawer_open" : False,
                "foods" : [],
                "potions" : []
                },
            "last_saved" : datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
            }
        
        for creature in creatures:
            state["creatures"].append({
                "name": creature.name,
                "type": creature.type,
                "position": [creature.x, creature.y],
                "satisfaction": creature.satisfaction
            })

        for food in foods:
            state["inventory"]["foods"].append({
                "name": food.name,
                "for_type": food.for_type,
                "satisfaction": food.satisfaction
            })
        for potion in potions:
            state["inventory"]["potions"].append({
                "name": potion.name,
                "effect": potion.effect
            })

        with open(filename, "w") as f:
            json.dump(state, f, indent = 4)

    @staticmethod
    def load_slot(file_slot):
        filename = f"checkpoint_{file_slot}.json"
        with open(filename, "r") as f:
            return (json.load(f))

class Creature:
    def __init__(self):
        self.name = "noob"
        self.type = "super"
        self.x = 45
        self.y = 50
        self.satisfaction = 100
    
class Food:
    def __init__(self):
        self.name = "chichaw"
        self.for_type = "dark"
        self.satisfaction = 65

class Potion:
    def __init__(self):
        self.name = "chichaw"
        self.effect = "double_points"

creature = Creature()
creature2 = Creature()

food = Food()
food2 = Food()

potion = Potion()
potion2 = Potion()

# Example save
Persistence.save_to_slot(1, 65, (creature, creature2), (food, food2), (potion, potion2))
Persistence.load_slot(1)