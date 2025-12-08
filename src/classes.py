
from enum import Enum
from game_manager import hex_to_rgb
import pygame


class PetAction(Enum):
    STROKE = 1
    FEED = 2
    PLAY = 3

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
    def __init__(self, name : str, x : int, y : int, sprite: list[str],
                satisfaction_multiplier : int = 1, 
                satisfaction_decay : float = 0.01,
                satisfaction_level : float = 100,
                dragging : bool = True):
        self.name = name
        self.x = x
        self.y = y
        self.satisfaction_multiplier  = satisfaction_multiplier
        self.satisfaction_decay  = satisfaction_decay
        self.satisfaction_level = satisfaction_level
        self.satisfaction_bar = SatisfactionBar()
        self.effects : list[Effect] = []

        # Reactive Sprite Image
        self.frames = [pygame.image.load(path).convert_alpha() for path in sprite]
        self.sprite = self.frames[0]
        self.rect = self.frames[0].get_rect(center = (x,y))

    def move(self, new_x : int, new_y : int):
        self.x = new_x
        self.y = new_y
        self.rect.center = (new_x, new_y)

    def update_sprite(self, spritestyle : int):
        """
        spritestyle : 0-> normal, 1-> happy, 2-> sad
        """
        self.sprite = self.frames[spritestyle]

    def draw(self, screen : pygame.Surface):
        screen.blit(self.sprite, self.rect)
        self.satisfaction_bar.draw(screen, self.x, self.y, self.satisfaction_level)

    def pet(self, action : PetAction):
        if action == PetAction.STROKE:
            self.satisfaction_decay = 2
        
        if action == PetAction.PLAY:
            self.satisfaction_level = min(100, self.satisfaction_level) # to be implemented based on minigames
    
    def update_effects(self):
        for effects in self.effects[:]:
            effects.update(self)


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

    def draw(self, screen : pygame.Surface, creatures : list[Creature]):
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
        
class More_Satisfaction(Effect):
    """Increases Satisfaction sensitivity"""
    def __init__(self):
        super().__init__(name="More Satisfaction")
    
    def consume(self, creature: Creature, multiplier: int, duration_frames: int):
        super().consume(creature, multiplier, duration_frames)
        creature.satisfaction_decay = multiplier
    
    def remove(self, creature : Creature):
        super().remove(creature)
        creature.satisfaction_decay = 1
    
class Less_Decay(Effect):
    """Reduce Decay Rate of Creature"""
    def __init__(self):
        super().__init__(name="Less Decay")
    
    def consume(self, creature : Creature, multiplier : int, duration_frames : int):
        super().consume(creature, multiplier, duration_frames)
        creature.satisfaction_multiplier = multiplier
    
    def remove(self, creature : Creature):
        super().remove(creature)
        creature.satisfaction_multiplier = 1

class Consumable():
    def __init__(self, name : str):
        self.name = name

class Food(Consumable): # dev2 : Add Satisfaction
    """Add Satisfaction"""
    def __init__(self, for_type : str, satisfaction : int):
        super().__init__(name = "Food")
        self.for_type = for_type
        self.satisfaction = satisfaction
        
    def consume(self, creature : Creature):
        if creature.satisfaction_level + (creature.satisfaction_multiplier * self.satisfaction) >= 100:
            creature.satisfaction_level = 100
        else:
            creature.satisfaction_level += creature.satisfaction_multiplier * self.satisfaction

class Potion(Consumable): # dev2 : Add Effects
    """Add Effects"""
    def __init__(self, duration : int, effect : Effect, multiplier : int):
        super().__init__(name = "Potion")
        self.duration = duration
        self.effect = effect
        self.multiplier = multiplier
    
    def consume(self, name : str, creature: Creature, multiplier : int, duration : int):
        effect_copy = type(self.effect)(name) # TODO: Fix Potion.consume to handle Effect class subclasses correctly
        effect_copy.consume(creature, multiplier, duration) 

class Cleanse(Consumable): # dev2: Clear Effects
    """Clear Effects"""
    def __init__(self):
        super().__init__(name = self.name)

    def consume(self, creature : Creature):
        for effect in creature.effects[:]:
            effect.remove(creature)
