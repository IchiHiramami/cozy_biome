from enum import Enum
from non_essential import hex_to_rgb
import pygame
from logger import log
from typing import Any
from collections import defaultdict
import random


class PetAction(Enum):
    PET = 1
    FEED = 2


class SatisfactionBar:
    def __init__(self, 
                 width : int = 50, 
                 height : int = 5, 
                 offset_x : int = -20, 
                 offset_y : int = -30):
            
        self.width = width
        self.height = height
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        self.bg_color = hex_to_rgb("#ffffff")

        self.color_green = hex_to_rgb("#00e774")      
        self.color_lime = hex_to_rgb("#d0ff00")
        self.color_yellow = hex_to_rgb("#ffe600")
        self.color_orange = hex_to_rgb("#ffa600")
        self.color_red = hex_to_rgb("#e06614") 
        self.color_critical = hex_to_rgb("#ff0000") 


    def get_satbar_color(self, value : float):
        """coloring of the value"""
        if 100 >= value > 89:
            return self.color_green
        elif 89 >= value > 59:
            return self.color_lime
        elif 59 >= value > 39:
            return self.color_yellow
        elif 39 >= value > 29:
            return self.color_orange
        elif 29 >= value > 9:
            return self.color_red
        elif 9 >= value >= 0:
            return self.color_critical
        return self.color_critical

    def draw(self, screen : pygame.Surface, x : int, y : int, value : float):
        """
        x, y - coordinate placement
        value - satisfaction level
        """
        pygame.draw.rect(screen, self.bg_color, (x +  self.offset_x, y + self.offset_y, self.width, self.height))
        
        fill_width = int((value/100) * self.width)

        pygame.draw.rect(
            screen,
            self.get_satbar_color(value), 
            (x + self.offset_x, y + self.offset_y, fill_width, self.height)
        )

class Creature:
    def __init__(self, name : str, type : str, x : int, y : int, sprite: list[str],
                satisfaction_multiplier : int = 1,
                satisfaction_decay : float = 0.01,
                satisfaction_level : float = 100,
                dragging : bool = True):
        self.name = name
        self.x = x
        self.y = y
        self.type = type
        self.satisfaction_multiplier  = satisfaction_multiplier
        self.satisfaction_decay  = satisfaction_decay
        self.satisfaction_level = satisfaction_level
        self.satisfaction_bar = SatisfactionBar()
        self.effects : list[Effect] = []
        self.hovered = False
        self.isalive = True
        

        # Reactive Sprite Image
        self.frames_paths = sprite
        self.frames = [pygame.image.load(path).convert_alpha() for path in sprite]
        self.sprite = self.frames[0]
        self.rect = self.frames[0].get_rect(center = (x,y))

    def move(self, new_x : int, new_y : int):
        self.x = new_x
        self.y = new_y
        self.rect.center = (new_x, new_y)

    def update_sprite(self, spritestyle: int):
        if not self.isalive and spritestyle != 3:
            return  # dead creatures cannot change sprite

        if spritestyle == 3:
            if self.isalive:  # only log once
                log(2, f"Creature '{self.name}' has reached 0 satisfaction and is now dead.")
            self.sprite = pygame.image.load("assets/Sprites/Dead.png").convert_alpha()
            self.isalive = False
        else:
            self.sprite = self.frames[spritestyle]




    def draw(self, screen: pygame.Surface, is_selected : bool = False):
        if is_selected:
            pygame.draw.rect(screen, (255,255, 0), self.rect.inflate(10,10), width = 3)
        screen.blit(self.sprite, self.rect)

        self.satisfaction_bar.draw(
            screen,
            self.rect.centerx,
            self.rect.top,
            self.satisfaction_level
        )

    def pet(self, action : PetAction):
        if action == PetAction.PET and self.satisfaction_level > 0:
            self.satisfaction_level = min(100, (self.satisfaction_level + 0.5 * self.satisfaction_multiplier))
    
    def resolve_soft_collisions(self, other : "Creature", push_strength : float = 0.5) -> None:
        """Soft separation force between creature and other creature"""

        if self is other:
            return
        
        if self.rect.colliderect(other.rect):
            self.satisfaction_level = max(0, self.satisfaction_level - 0.1)
            other.satisfaction_level = max(0, other.satisfaction_level - 0.1)
            delta_x = float(self.rect.centerx - other.rect.centerx)
            delta_y = float(self.rect.centery - other.rect.centery)

            if delta_x == 0 and delta_y == 0:
                delta_x = 1.0

            distance : float = max(1.0, (delta_x  * delta_x + delta_y * delta_y) ** 0.5)

            normal_x: float = delta_x / distance
            normal_y: float = delta_y / distance

            self.rect.x += int(normal_x * push_strength)
            self.rect.y += int(normal_y * push_strength)

            other.rect.x -= int(normal_x * push_strength)
            other.rect.y -= int(normal_y * push_strength)


    def update_effects(self):
        for effects in self.effects[:]:
            effects.update(self)
    
    def update_hover(self, mouse_pos : tuple[int, int]):
        mx, my = mouse_pos
        self.hovered = self.rect.collidepoint(mx, my)

class GlobalSatisfactionBar(SatisfactionBar):
    def __init__(self, screen_width : int=800, y : int=20, height : int=12, margin : int =40):
        width = screen_width - 2 * margin
        x = margin  # start at left margin

        super().__init__(width=width, height=height, offset_x=0, offset_y=0)

        self.x = x
        self.y = y

    def compute_average(self, creatures : list[Creature]):
        if not creatures:
            return 0
        total = sum(c.satisfaction_level for c in creatures)
        return total / len(creatures)

    def draw(self, screen : pygame.Surface, creatures : list[Creature]): #type: ignore
        avg = self.compute_average(creatures)
        super().draw(screen, self.x, self.y, avg)

class Effect():
    def __init__(self, name : str):
        self.name = name
        self.duration = 0

    def remove(self, creature : Creature):
        if self in creature.effects:
            creature.effects.remove(self)

    def update(self, creature : Creature):
        if self.duration > 0:
            self.duration -= 1
        else:
            self.remove(creature)

    def consume(self, creature : Creature, multiplier : int, duration_frames : int):
        for effect in creature.effects[:]:
            if type(effect) == type(self):
                creature.effects.remove(effect)
        self.duration = duration_frames
        creature.effects.append(self)

    def to_dict(self, creature : Creature | None = None):
        data : dict[str, Any] = {
            "name": self.name,
            "duration": self.duration,
            "type": self.__class__.__name__
        }

        if creature:
            if isinstance(self, More_Satisfaction):
                data["satisfaction_decay"] = creature.satisfaction_decay
            elif isinstance(self, Less_Decay):
                data["satisfaction_multiplier"] = creature.satisfaction_multiplier
        return data
        
class More_Satisfaction(Effect):
    """Increases Satisfaction sensitivity"""
    def __init__(self):
        super().__init__(name="More Satisfaction")
    
    def consume(self, creature: Creature, multiplier: int, duration_frames: int):
        super().consume(creature, multiplier, duration_frames)
        creature.satisfaction_multiplier = multiplier
    
    def remove(self, creature : Creature):
        super().remove(creature)
        creature.satisfaction_multiplier = 1
    
class Less_Decay(Effect):
    """Reduce Decay Rate of Creature"""
    def __init__(self):
        super().__init__(name="Less Decay")
    
    def consume(self, creature : Creature, multiplier : int, duration_frames : int):
        super().consume(creature, multiplier, duration_frames)
        creature.satisfaction_decay /= multiplier
    
    def remove(self, creature : Creature):
        super().remove(creature)
        creature.satisfaction_decay = 0.01

class Consumable():
    def __init__(self, name : str):
        self.name = name

class Food(Consumable): # dev2 : Add Satisfaction
    """Add Satisfaction"""
    def __init__(self, name : str, for_type : str, satisfaction : int):
        super().__init__(name)
        self.for_type = for_type
        self.satisfaction = satisfaction
        
    def consume(self, creature : Creature):
        if creature.satisfaction_level + (creature.satisfaction_multiplier * self.satisfaction) >= 100:
            creature.satisfaction_level = 100
        else:
            creature.satisfaction_level += creature.satisfaction_multiplier * self.satisfaction

class Potion(Consumable): # dev2 : Add Effects
    """Add Effects"""
    def __init__(self, name : str, for_type : str):
        super().__init__(name)
        self.for_type = for_type

class Cleanse(Consumable): # dev2: Clear Effects
    """Clear Effects"""
    def __init__(self):
        super().__init__(name = "Cleanse")

class Inventory:
    def __init__(self):
        self.foods : defaultdict[str, int] = defaultdict(int)
        self.potions : defaultdict[str, int] = defaultdict(int)
        self.cleanse : defaultdict[str, int] = defaultdict(int)
    
    def add_inventory(self, item : Food | Potion | Cleanse):
        """
            Adds an item to inventory.
        """
        if isinstance(item, Food):
            self.foods[item.name] += 1
        elif isinstance(item, Potion):
            self.potions[item.name] += 1
        else:
            self.cleanse[item.name] += 1
        log(2, f"Acquired an item: {item.name}")

    def remove_inventory(self, item_name: str, on_consumed): #type: ignore
        """
            Decrements inventory by one
        """
        
        consumed = False
        
        if item_name in self.foods and self.foods[item_name] > 0:
            self.foods[item_name] -= 1
            consumed = True
        elif item_name in self.potions and self.potions[item_name] > 0:
            self.potions[item_name] -= 1
            consumed = True
        elif item_name in self.cleanse and self.cleanse[item_name] > 0:
            self.cleanse[item_name] -= 1
            consumed = True
            
        if consumed:
            log(2, f"Consumed an item: {item_name}")

            if on_consumed is not None:
                on_consumed(item_name)

class Money:
    def __init__(self, money : int = 0):
        self.money : int = money
        
    def add_money(self, flappypoints : int | float):
        self.money += int(flappypoints) * random.randint(6, 10)
        print(self.money)
    
    def remove_money(self, item : dict[str, int]):
        self.money -= item["price"]
    
    def draw(self, screen: pygame.Surface):
        """Draw current money amount to the provided surface."""

        from game_manager import Text

        text = Text(630, 470, 140, 36, pygame.font.Font(None, 30), f"${str(self.money)}", "#e8ab83", "#ffffff")
        text.draw(screen)
