import json
import os
from datetime import datetime
from classes import Creature, Less_Decay, More_Satisfaction
from typing import Any

class Persistence:
    @staticmethod
    def save_to_slot(
        file_slot: str,
        world_score: int | float,
        creatures: list[Creature],
        foods: dict[str, int],
        potions: dict[str, int],
        cleanse: dict[str, int]
    ) -> None:

        # Clean filename
        safe_filename = file_slot.replace("\n", "").replace("\r", "")
        filename = f"save_files/{safe_filename}"

        # Base save structure
        state: dict[str, Any] = {
            "world_name": file_slot,
            "world_score": world_score,
            "creatures": [],
            "inventory": {
                "foods": {},
                "potions": {},
                "cleanse": {}
            },
            "last_saved": datetime.now().strftime("%B %d, %Y %I:%M:%S %p")
        }

        # -------------------------
        # Save creatures
        # -------------------------
        for creature in creatures:
            state["creatures"].append({
                "name": creature.name,
                "x": creature.x,
                "y": creature.y,
                "sprite": creature.frames_paths,
                "type": creature.type,
                "satisfaction_level": creature.satisfaction_level,
                "satisfaction_multiplier": creature.satisfaction_multiplier,
                "satisfaction_decay": creature.satisfaction_decay,
                "effects": [effect.to_dict(creature) for effect in creature.effects]
            })

        # -------------------------
        # Save inventory (dict[str, int])
        # -------------------------
        state["inventory"]["foods"] = foods
        state["inventory"]["potions"] = potions
        state["inventory"]["cleanse"] = cleanse

        # -------------------------
        # Write to file
        # -------------------------
        with open(filename, "w") as f:
            json.dump(state, f, indent=4)

    # ----------------------------------------------------------------------

    @staticmethod
    def load_slot(file_slot: str) -> dict[str, Any] | None:
        filename = f"save_files/{file_slot}"
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            print("Error loading save:", e)
            return None

    # ----------------------------------------------------------------------

    @staticmethod
    def unpack_creatures(data: dict[str, Any]) -> Creature:
        # ✅ Rebuild creature
        c = Creature(
            name=data["name"],
            type=data["type"],
            x=data["x"],
            y=data["y"],
            sprite=data["sprite"],
            satisfaction_multiplier=data.get("satisfaction_multiplier", 1),
            satisfaction_decay=data.get("satisfaction_decay", 0.01),
            satisfaction_level=data.get("satisfaction_level", 100)
        )

        # ✅ Restore effects
        for eff_data in data.get("effects", []):
            eff_type = eff_data.get("type")

            if eff_type == "More_Satisfaction":
                effect = More_Satisfaction()
            elif eff_type == "Less_Decay":
                effect = Less_Decay()
            else:
                continue

            effect.duration = eff_data.get("duration", 0)
            effect.consume(
                c,
                getattr(c, "satisfaction_multiplier", 1),
                effect.duration
            )

        return c

    # ----------------------------------------------------------------------

    @staticmethod
    def taken_name() -> list[str]:
        folder = "save_files"
        filenames: list[str] = []
        for filename in os.listdir(folder):
            filenames.append(filename)
        return filenames
