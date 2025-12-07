import json
from datetime import datetime

class Persistence:
    @staticmethod
    def save_to_slot(file_slot : int, world_name : str, world_score : int, creatures : list[object], foods : list[object], potions : list[object]):
        filename = f"checkpoint_{file_slot}"
        state = {
            "world_name" : world_name,
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
                "x": creature.x,
                "y": creature.y,
                "satisfaction": creature.satisfaction,
                "satisfaction_multiplier": creature.satisfaction_multiplier,
                "satisfaction_decay": creature.satisfaction_decay,
                "satisfaction_bar": creature.satisfaction_bar,
                "effects": creature.effects
            }
            )

        for food in foods:
            state["inventory"]["foods"].append({
                "name": food.name,
                "for_type": food.for_type,
                "satisfaction": food.satisfaction
            })
        for potion in potions:
            state["inventory"]["potions"].append({
                "name": potion.name,
                "duration": potion.effect.duration,
                "effect": potion.effect
            })

        with open(filename, "w") as f:
            json.dump(state, f, indent = 4)

    @staticmethod
    def load_slot(file_slot):
        filename = f"checkpoint_{file_slot}"

        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except json.JSONDecodeError:
            return None
        except Exception as e:
            print("Error loading:", e)
            return None


