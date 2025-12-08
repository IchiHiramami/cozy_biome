import pygame
import os
from datetime import datetime

# Local dependencies
from game_manager import (
    Menu, Button, InputField, MenuManager,
    GameSetupMenu, BackgroundManager
)
from gameplay import GameScene
from logger import log, clear
from persistence import Persistence

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

# Initialize pygame
if __name__ == "__main__":
    pygame.init()

clock = pygame.time.Clock()
clear()  # Clear log on startup

# Managers
menu_manager = MenuManager()
bg_manager = BackgroundManager()

# Window
font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Cozy Cove the App")

# Gameplay Scene
current_scene = None


# ------------------------------------------------------
# CALLBACKS
# ------------------------------------------------------

def new_game():
    menu_manager.switch(new_game_menu)
    new_game_menu.activate()
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "New Game Set")


def load_game():
    menu_manager.switch(load_game_menu)
    load_game_menu.activate()
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "Load Game Menu Opened")


def quit_game():
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "Game Exited")
    pygame.quit()
    exit()


def start_game():
    """Start a new game with the entered world name."""
    world_name = name_Field.return_input()
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, f"World Name Set: {world_name}")

    global current_scene
    current_scene = GameScene(world_name)

    # Assign managers to the scene
    current_scene.menu_manager = menu_manager
    current_scene.bg_manager = bg_manager
    current_scene.home_menu = home_menu
    current_scene.build_pause_menu()

    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "New Game Started")


def start_loaded_game(slot: int):
    """Load a saved game from a slot."""
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, f"Selected Load Slot: {slot+1}")

    global current_scene
    loaded_data = Persistence.load_slot(slot + 1)

    if loaded_data:
        current_scene = GameScene(loaded_data["world_name"])

        # Assign managers
        current_scene.menu_manager = menu_manager
        current_scene.bg_manager = bg_manager
        current_scene.home_menu = home_menu
        current_scene.build_pause_menu()

        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "Loaded Game Started")


def go_back():
    """Return to previous menu."""
    menu_manager.back()
    if menu_manager.current:
        menu_manager.current.activate()


# ------------------------------------------------------
# UI ELEMENTS
# ------------------------------------------------------

# Home Buttons
new_game_btn = Button(300, 200, 200, 60, font, "New Game", "c8ab83", "eec584", "ffffff", on_click=new_game)
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "c8ab83", "eec584", "ffffff", on_click=load_game)
quit_btn = Button(300, 400, 200, 60, font, "Quit Game", "c8ab83", "eec584", "ffffff", on_click=quit_game)

# New Game Buttons
start_game_btn = Button(300, 300, 200, 60, font, "Start", "c8ab83", "eec584", "ffffff", on_click=start_game)

# Back Button
back_btn = Button(300, 500, 200, 60, font, "Back", "e8ab83", "eec584", "ffffff", on_click=go_back)

# Input Field
name_Field = InputField(300, 200, 200, 60, font)


# ------------------------------------------------------
# MENUS
# ------------------------------------------------------

home_menu = Menu(
    os.path.join(ASSETS, "Background/main_menu_noncut.png"),
    [new_game_btn, load_game_btn, quit_btn],
    bg_manager
)

new_game_menu = GameSetupMenu(
    os.path.join(ASSETS, "Background/main_menu_new_game.png"),
    [start_game_btn, back_btn],
    [name_Field],
    bg_manager
)

load_game_menu = GameSetupMenu(
    os.path.join(ASSETS, "Background/main_menu_new_game.png"),
    [
        Button(
            300, 100 + i * 100, 200, 60, font,
            (Persistence.load_slot(i+1)["world_name"] if Persistence.load_slot(i+1) else f"Empty Slot {i+1}"),
            "c8ab83", "eec584", "ffffff",
            on_click=(lambda slot=i: start_loaded_game(slot))
        )
        for i in range(3)
    ],
    [],
    bg_manager
)

# Start with home menu
menu_manager.push(home_menu)
home_menu.activate()


# ------------------------------------------------------
# MAIN LOOP
# ------------------------------------------------------

is_running = True

while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

        elif current_scene:
            current_scene.handle_event(event)

        else:
            menu_manager.handle_event(event)

    screen.fill((0, 0, 0))

    if current_scene:
        # If a menu is open on top of the game, freeze gameplay updates
        if menu_manager.current and menu_manager.current is not home_menu:
            current_scene.draw(screen)
            menu_manager.draw(screen)
        else:
            current_scene.update()
            current_scene.draw(screen)
    else:
        menu_manager.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
