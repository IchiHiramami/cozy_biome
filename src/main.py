import pygame
import os
from game_manager import Menu, Button, InputField, MenuManager, GameSetupMenu, BackgroundManager
from datetime import datetime

# Path and Assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
# asset pack from https://mandinhart.itch.io/garden-cozy-ui-kit-buttons-icons <<< to credit later

# Game INIT
if __name__ == "__main__":
    pygame.init()

clock = pygame.time.Clock()

# Managers
menu_manager = MenuManager()
bg_manager = BackgroundManager()

font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Cozy Cove the App")

# Callbacks
def new_game():
    menu_manager.switch(new_game_menu)
    new_game_menu.activate()
    pass #TODO: put the log here

def load_game():
    pass #TODO: put the log here (or maybe in the log.py file)
        #

def quit_game():
    #TODO: log here quit before quitting
    pygame.quit()
    exit()

def start_game():
    today = datetime.today
    world_name = name_Field.return_input()
    print(f"World Name:{world_name}")
    print(f"Time of Creation: {str(today)}")
    #TODO: transitioning to actual gameplay scene
    #TODO: log here
    pass

def go_back():
    menu_manager.back()
    if menu_manager.current:
        menu_manager.current.activate()
        # TODO: fix bug on main menu not returning

# Global Variables
return_to : Menu | None = None

# Button Lists

# Home Buttons
new_game_btn = Button(300, 200, 200, 60, font, "New Game", "c8ab83", "eec584", "ffffff", on_click = new_game)
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "c8ab83", "eec584", "ffffff", on_click = load_game)  
quit_btn = Button(300, 400, 200, 60, font, "Quit Game", "c8ab83", "eec584", "ffffff", on_click = quit_game)

# New Game Buttons
start_game_btn = Button(300, 300, 200, 60, font, "Start", "c8ab83", "eec584", "ffffff", on_click = start_game)

# All purpose Buttons:
back_btn = Button(300, 500, 200, 60, font, "Back", "e8ab83", "eec584", "ffffff", on_click = go_back)

# Input Fields
name_Field = InputField(300, 200, 200, 60, font)

# ---------------------------------------------
# Note: Menu Creation Syntax:
# Menu (<filepath to bg>, <button list>, <field list> [for gamesetup only], bg_manager [ALWAYS])

# Splash Screen Menu
home_menu = Menu(os.path.join(ASSETS, "Background/main_menu_noncut.png"), [new_game_btn, load_game_btn, quit_btn], bg_manager)

# New Game Setup Menu
new_game_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"), [start_game_btn, back_btn], [name_Field], bg_manager)

menu_manager.push(home_menu) # Start app with home menu first
home_menu.activate()

is_running = True # for easier identification of app state

# Main Loop
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        else:
            menu_manager.handle_event(event)
        
    screen.fill((0,0,0))
    menu_manager.draw(screen)
    pygame.display.flip()
    
    clock.tick(60)
pygame.quit()