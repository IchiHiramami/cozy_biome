import pygame
import os
from game_manager import Menu, Button, InputField, MenuManager, GameSetupMenu

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

if __name__ == "__main__":
    pygame.init()

def new_game():
    menu_manager.push(new_game_menu)
    pass #TODO: put the log here

def load_game():
    pass #TODO: put the log here (or maybe in the log.py file)
         # 

def quit_game():
    #TODO: log here quit before quitting
    pygame.quit()
    exit()

font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Cozy Cove the App")

# New Game Buttons
start_game_btn = Button(300, 400, 200, 60, font, "Start", "c8ab83", "eec584", "ffffff")

# Home Buttons
new_game_btn = Button(300, 200, 200, 60, font, "New Game", "c8ab83", "eec584", "ffffff", on_click = new_game)
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "c8ab83", "eec584", "ffffff")  
quit_btn = Button(300, 400, 200, 60, font, "Quit Game", "c8ab83", "eec584", "ffffff", on_click = quit_game)

# Input Fields
name_Field = InputField(300, 200, 200, 60, font)

menu_manager = MenuManager()

home_screen_buttons = [new_game_btn, load_game_btn, quit_btn]
new_game_buttons = [start_game_btn]
new_game_fields = []

background = pygame.image.load(os.path.join(ASSETS, "main_menu_noncut.png"))
background = pygame.transform.scale(background, (800, 600))

# New Game Setup Menu
new_game_menu = GameSetupMenu(screen, new_game_buttons, [name_Field])

# Splash Screen Menu
home_menu = Menu(background, home_screen_buttons)
menu_manager.push(home_menu)

is_running = True # for easier identification of app state

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
    
        menu_manager.handle_event(event)

    menu_manager.draw(screen)

    pygame.display.flip()

pygame.quit()