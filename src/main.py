import pygame
import os
from game_manager import Menu
from Buttonlist import home_screen_buttons

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

pygame.init()

background = pygame.image.load(os.path.join(ASSETS, "main_menu_noncut.png"))
background = pygame.transform.scale(background, (800, 600))

home_menu = Menu(background, home_screen_buttons)

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Cozy Cove the App")

is_running = True # for easier identification of app state

while is_running:
    for event in pygame.event.get():
        home_menu.handle_event(event)
    
    home_menu.draw(screen)

    pygame.display.flip()

pygame.quit()