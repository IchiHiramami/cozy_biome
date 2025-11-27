# ----------------------------------------------------------------
# Contained here are classes and methods related to MAIN GAMEPLAY
# ----------------------------------------------------------------

# Imports
import os
import pygame
from random import randint
from classes import Creature, Food, Potion, Cleanse #type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

class GameScene:
    def __init__(self, world_name : str):
        self.word_name = world_name

        self.background = pygame.image.load(os.path.join(ASSETS, "Background/main_world.png"))
        self.background = pygame.transform.scale(self.background, (800, 600))

        self.creatures : list[Creature] = [Creature(f"creature{i}",
                                                    randint(0, 800),
                                                    randint(0,600),
                                                    [f"assets/Sprites/cat_animation_1.png",
                                                    f"assets/Sprites/cat_animation_2.png",
                                                    f"assets/Sprites/cat_animation_3.png",
                                                    f"assets/Sprites/cat_animation_4.png"]
                                                    ) for i in range(randint(2,4))]

        self.selected : Creature | None = None # currently selected creature (cannot exceed 1 unless we magically make 2 mouse pointers and at that point, this ain't 111 level na)

    def handle_event(self, event : pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for creature in self.creatures:
                if creature.rect.collidepoint(event.pos):
                    self.selected = creature
                    self.drag_offset = (creature.rect.x - event.pos[0], creature.rect.y - event.pos[1])
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected = None

        elif event.type == pygame.MOUSEMOTION and self.selected:
            self.selected.rect.x = event.pos[0] + self.drag_offset[0]
            self.selected.rect.y = event.pos[1] + self.drag_offset[1]
            self.selected.x, self.selected.y = self.selected.rect.center

    def update(self):
        for creature in self.creatures:
            creature.update_effects()
            creature.satisfaction_level = max(0, creature.satisfaction_level - creature.satisfaction_decay) # bottom cap min = 0

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0,0))
        for creature in self.creatures:
            creature.update_animation()
            creature.draw(screen)