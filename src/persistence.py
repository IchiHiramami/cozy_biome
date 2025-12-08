import json
import os
from datetime import datetime
from classes import Creature, Food, Potion, Less_Decay, More_Satisfaction
from typing import Any

class Persistence:
    @staticmethod
    def save_to_slot(file_slot : str, world_score : int | float, creatures : list[Creature], foods : list[Food], potions : list[Potion]):
        safe_filename = file_slot.replace("\n", "").replace("\r", "")
        filename = f"save_files/{safe_filename}"
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
                "sprite" : creature.frames_paths,
                "type": creature.type,
                "satisfaction_level": creature.satisfaction_level,
                "satisfaction_multiplier": creature.satisfaction_multiplier,
                "satisfaction_decay": creature.satisfaction_decay,
                "effects": [effect.to_dict(creature) for effect in creature.effects]
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
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            print("error")

    @staticmethod
    def unpack_creatures(data):
        c = Creature(
        name=data["name"],
        type=data["type"],
        x=data["x"],
        y=data["y"],
        sprite=data["sprite"], 
        satisfaction_multiplier = 1,
        satisfaction_decay = 0.01,
        satisfaction_level=data.get("satisfaction_level", 100)
        )
    
        for eff_data in data.get("effects", []):
            eff_type = eff_data["type"]
            if eff_type == "More_Satisfaction":
                effect = More_Satisfaction()
            elif eff_type == "Less_Decay":
                effect = Less_Decay()
            else:
                continue
            effect.duration = eff_data.get("duration", 0)

            effect.consume(c, getattr(c, "satisfaction_multiplier", 1), effect.duration)
        
        return c
    
    @staticmethod
    def clear(file_slot):
        try:
            with open(file_slot, "w") as f:
                pass
        except:
            print("error")


    @staticmethod
    def taken_name():
        folder = "save_files"
        filenames : list[str]= []
        for filename in os.listdir(folder):
            filenames.append(filename)
        return filenames