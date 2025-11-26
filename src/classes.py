from abc import ABC, abstractmethod

class Creatures:
    def __init__(self, name, location : list[str, str], satisfaction_level=50):
        self.name = name
        self.location = location
        self.satisfaction_level = satisfaction_level

    def move(self, new_location):
        self.location = new_location
        self.location = new_location

    def pet(self, action):
        pass

class Food:
    pass

class Potion:
    pass