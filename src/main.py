import pygame
import os
from datetime import datetime

# local dependencies
from game_manager import Menu, Button, InputField, MenuManager, GameSetupMenu, BackgroundManager
from gameplay import GameScene
from logger import log, clear
from persistence import Persistence

# Path and Assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
# asset pack from https://mandinhart.itch.io/garden-cozy-ui-kit-buttons-icons <<< to credit later

# Game INIT
if __name__ == "__main__":
    pygame.init()

clock = pygame.time.Clock()
clear()

# Managers
menu_manager = MenuManager()
bg_manager = BackgroundManager()

font = pygame.font.Font(None, 40)
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("Cozy Cove the App")

# Gameplay Stuff
current_scene = None
creatureslist = []

# Callbacks
def new_game():
    menu_manager.switch(new_game_menu)
    new_game_menu.activate()
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "New Game Set")

def load_game():
    pass #TODO: put the log here (or maybe in the log.py file)
    menu_manager.switch(load_game_menu)
    load_game_menu.activate()

def quit_game():
    #TODO: log here quit before quitting
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "Game Exited")
    pygame.quit()
    exit()

def start_game():
    world_name = name_Field.return_input()
    if world_name in Persistence.taken_name():
        return # TO DO: User picks another world name
    print(f"World Name:{world_name}")
    print(f"Time of Creation: {datetime.now().strftime("%B %d, %Y %I:%M:%S %p")}")
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "World Name set to " + world_name)

    global current_scene # Transfer over to main gameplay
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "New Game Started")
    go_back() # so that when the player quits the gameplay, it returns to the main menu

    current_scene = GameScene(world_name)

def start_loaded_game(slot : str):
    print(f"Game selected from slot {slot}")
    global current_scene, creatureslist
    creatureslist = []
    log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, f"Stated Loaded Game: {slot}")
    loaded_data = Persistence.load_slot(slot)
    go_back() # so that when the player quits the gameplay, it returns to the main menu
    for c in loaded_data["creatures"]:
        creature = Persistence.unpack_creatures(c)
        print(creature.x)
        creatureslist.append(creature)
    if loaded_data:
        current_scene = GameScene(loaded_data["world_name"], creatureslist)

def go_back():
    menu_manager.back()
    if menu_manager.current:
        menu_manager.current.activate()

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
# Menu (<filepath to bg>, <button list>, <field list> [for gamesetup only], bg_manager [<<< ALWAYS INCLUDE])

# Splash Screen Menu
home_menu = Menu(os.path.join(ASSETS, "Background/main_menu_noncut.png"), [new_game_btn, load_game_btn, quit_btn], bg_manager)

# New Game Setup Menu
new_game_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"), [start_game_btn, back_btn], [name_Field], bg_manager)
load_game_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"), [
    Button(
        300, 100 + Persistence.taken_name().index(i) * 100, 200, 60, font,
        (Persistence.load_slot(i)["world_name"]),
        "c8ab83", "eec584", "ffffff",
        on_click = (lambda slot=i: start_loaded_game(slot))
    )
    for i in Persistence.taken_name()
],
[],
bg_manager) # TO DO: Scrollbar if load slots are more than 3

menu_manager.push(home_menu)
home_menu.activate()

is_running = True

cursor_default = pygame.image.load("assets/Cursors/dark/pointer.png").convert_alpha()
cursor_point = pygame.image.load("assets/Cursors/dark/link.png").convert_alpha()
cursor_hand = pygame.image.load("assets/Cursors/dark/grab.png").convert_alpha()
cursor_hover = pygame.image.load("assets/Cursors/dark/grab_hover.png").convert_alpha()

pygame.mouse.set_visible(False)

while is_running:

    mx, my = pygame.mouse.get_pos()

    # -------------------------
    # EVENT HANDLING
    # -------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
        else:
            if current_scene:
                current_scene.handle_event(event)
            else:
                menu_manager.handle_event(event)

    # -------------------------
    # UPDATE
    # -------------------------
    if current_scene:
        current_scene.update()

    # -------------------------
    # DRAW SCENE OR MENU
    # -------------------------
    screen.fill((0, 0, 0))

    if current_scene:
        current_scene.draw(screen)
    else:
        menu_manager.draw(screen)

    # -------------------------
    # CURSOR LOGIC (PRIORITY STACK)
    # -------------------------
    cursor_to_draw = cursor_default

    if current_scene:

        # 1. BUTTON HOVER (highest priority)
        for btn in current_scene.get_all_active_buttons():
            if btn.hovered:
                cursor_to_draw = cursor_hand
                break
        else:
            # 2. DRAGGING A CREATURE
            if current_scene.selected:
                cursor_to_draw = cursor_hand

            else:
                # 3. PETTING MODE
                if current_scene.cursor_mode == "Petting":

                    # 3a. Hovering a creature
                    for creature in current_scene.creatures:
                        if creature.hovered:
                            cursor_to_draw = cursor_hover
                            break
                    else:
                        # 3b. Petting mode but not hovering a creature
                        cursor_to_draw = cursor_default

                # 4. NORMAL MODE (no special cursor)
                else:
                    cursor_to_draw = cursor_default

    # Draw cursor last so it stays on top
    screen.blit(cursor_to_draw, (mx, my))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()