import pygame
import os
from classes import Button, Menu

def new_game():
    pass #TODO: put the log here

def load_game():
    pass #TODO: put the log here (or maybe in the log.py file)

def quit_game():
    #TODO: log here quit before quitting
    pygame.quit()
    exit()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # go up from src/
ASSETS = os.path.join(BASE_DIR, "assets")

pygame.init()

font = pygame.font.Font(None, 40)

background = pygame.image.load(os.path.join(ASSETS, "main_menu_noncut.png"))
background = pygame.transform.scale(background, (800, 600))

new_game_btn = Button(300, 200, 200, 60, font, "New Game", "c8ab83", "eec584", "ffffff")
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "c8ab83", "eec584", "ffffff")  
quit_btn     = Button(300, 400, 200, 60, font, "Quit Game", "c8ab83", "eec584", "ffffff", on_click = quit_game)

buttons = [new_game_btn, load_game_btn, quit_btn]

home_menu = Menu(background, buttons)

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Cozy Cove the App")

is_running = True # for easier identification of app state

while is_running:
    for event in pygame.event.get():
        home_menu.handle_event(event)
    
    home_menu.draw(screen)

    pygame.display.flip()

pygame.quit()