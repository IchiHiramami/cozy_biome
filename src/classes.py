from abc import ABC, abstractmethod #type: ignore

class Creatures:
    def __init__(self, name : str, location : list[str], satisfaction_level : int =50):
        self.name = name
        self.location = location
        self.satisfaction_level = satisfaction_level

    def move(self, new_location : tuple[int, int]):
        self.location = new_location

    def pet(self, action): #type: ignore ; anong datatype ang action?
        pass

class Food:
    pass

class Potion:
    pass