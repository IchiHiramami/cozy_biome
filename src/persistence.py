import json
import os
from datetime import datetime
from classes import Creature, Food, Potion
from typing import Any

class Persistence:
    @staticmethod
    def save_to_slot(file_slot : str, world_score : int | float, creatures : list[Creature], foods : list[Food], potions : list[Potion]):
        filename = f"save_files/{file_slot}"
        state : dict[str, Any] = {
            "world_name" : file_slot,
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
                "x": creature.x,
                "y": creature.y,
                "type": creature.type,
                "satisfaction_level": creature.satisfaction_level,
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
    def load_slot(file_slot : str):
        filename = f"save_files/{file_slot}"

        with open(filename, "r") as f:
            return json.load(f)
        
    @staticmethod
    def taken_name():
        folder = "save_files"
        filenames : list[str]= []
        for filename in os.listdir(folder):
            filenames.append(filename)
        return filenames