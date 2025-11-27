class Creature:
    def __init__(self, name : str, x : int, y : int, 
                satisfaction_multiplier : int = 1, 
                satisfaction_decay : int = 1,
                satisfaction_level : int = 50):
        self.name = name
        self.x = x
        self.y = y
        self.satisfaction_multiplier  = satisfaction_multiplier
        self.satisfaction_decay  = satisfaction_decay
        self.satisfaction_level = satisfaction_level
        self.effects : list[Effect] = []

    def move(self, new_x : int, new_y : int):
        self.x = new_x
        self.y = new_y

    def pet(self, action): #type: ignore ; anong datatype ang action?
        # int? para pwedeng action1 or action2
        pass
    
    def update_effects(self):
        pass

class Effect():
    def __init__(self, name : str):
        self.name = name
        self.duration = 0
        self.active = True

    def remove(self, creature : Creature):
        if self in creature.effects:
            creature.effects.remove(self)
        pass

    def update(self, creature : Creature):
        if self.duration > 0:
            self.duration -= 1
        else:
            self.active = False
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
        effect_copy = type(self.effect)(name)
        effect_copy.consume(creature, multiplier, duration) 

class Cleanse(Consumable): # dev2: Clear Effects
    """Clear Effects"""
    def __init__(self):
        super().__init__(name = self.name)

    def consume(self, creature : Creature):
        for effect in creature.effects:
            effect.remove(creature)