import pygame
import os
from datetime import datetime
from typing import Any

# local dependencies
from game_manager import Menu, Button, InputField, Text, MenuManager, GameSetupMenu, BackgroundManager
from gameplay import GameScene, FlappyBirdScene
from logger import log, clear
from persistence import Persistence
from minigames import FlappyBird

# Path and Assets
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
# asset pack from https://mandinhart.itch.io/garden-cozy-ui-kit-buttons-icons <<< to credit later

# Game INIT
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("assets/Music/HomeScene_music.mp3")
    pygame.mixer.music.play(-1)

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
creatureslist : list[str]= []

# Callbacks
def new_game():
    worlds = Persistence.taken_name()
    if len(worlds) >= 3:
        log(1, "Maximum World Count has been reached")
        return
    menu_manager.switch(new_game_menu)
    new_game_menu.activate()
    log(2, "Player Opened New Game Menu")

def load_game():
    
    global saved_games_btn, texts
    log(2, "Load Game Menu Opened")
    saved_games_btn = []
    texts = []

    saved_files = Persistence.taken_name()

    for idx, filename in enumerate(saved_files):
        btn = Button(
            300,
            120 + idx * 100,
            200,
            60,
            font,
            Persistence.load_slot(filename).get("world_name", "Unknown World"),
            "c8ab83",
            "eec584",
            "ffffff",
            on_click=(lambda slot=filename: select_loaded_game(slot))
        )
        saved_games_btn.append(btn)

    saved_games_btn.append(back_btn)

    load_game_menu.buttons = saved_games_btn
    menu_manager.switch(load_game_menu)
    load_game_menu.activate()

def quit_game():
    log(2, "Game Exited")
    pygame.quit()
    exit()


def start_game():
    worlds = Persistence.taken_name()
    if len(worlds) >= 3:
        pass
    world_name = name_Field.return_input()
    if world_name in worlds or world_name.split == "":
        print("HEY OVER HERE!")
        return # TO DO: User picks another world name
    print(f"World Name:{world_name}")
    print(f"Time of Creation: {datetime.now().strftime("%B %d, %Y %I:%M:%S %p")}")
    log(2, "World Name set to " + world_name)

    global current_scene
    go_back() # so that when the player quits the gameplay, it returns to the main menu

    pygame.mixer.music.load("assets/Music/GameScene_music.mp3")
    pygame.mixer.music.play(-1)
    print("NEW GAME CREATED")
    current_scene = GameScene(world_name)
    log(2, f"[Main] Scene switched to: {type(current_scene).__name__}")
    log(2, "Player Started New Game")

def start_loaded_game(slot: str):
    print(f"Game selected from slot {slot}")
    global current_scene, creatureslist
    creatureslist = []
    log(2, f"Stated Loaded Game: {slot}")

    loaded_data = Persistence.load_slot(slot)

    go_back()
    for c in loaded_data["creatures"]:
        creature = Persistence.unpack_creatures(c)
        creatureslist.append(creature)

    inv = loaded_data.get("inventory", {})
    foods = inv.get("foods", {})
    potions = inv.get("potions", {})
    cleanse = inv.get("cleanse", {})

    pygame.mixer.music.load("assets/Music/GameScene_music.mp3")
    pygame.mixer.music.play(-1)

    current_scene = GameScene(
        loaded_data["world_name"],
        creatureslist,
        foods=foods,
        potions=potions,
        cleanse=cleanse
    )
    log(3, f"[Main] Scene switched to: {type(current_scene).__name__}")


def delete_loaded_game(slot : str):
    global saved_games_btn
    os.remove(f"save_files/{slot}")
    saved_games_btn[:] = []

    for i, slot in enumerate(Persistence.taken_name()):
        btn = Button(
            300, 100 + i * 100, 200, 60, font,
            Persistence.load_slot(slot)["world_name"],
            "#dda658", "#eec584", "ffffff",
            on_click=lambda s=slot: select_loaded_game(s)
        )
        saved_games_btn.append(btn)

    saved_games_btn.append(back_btn)
 
def select_loaded_game(slot : str):
    texts = []
    saved_games_btn[:] = [btn for btn in saved_games_btn 
                        if btn.text not in ("Delete", "Continue")]

    p = Persistence.load_slot(slot)["last_saved"].split()
    text = Text(550, 100, 200, 60, pygame.font.Font(None, 30), f"{p[0]} {p[1]} {p[2]}", "#e8ab83", "#ffffff")
    text2 = Text(550, 150, 200, 60, pygame.font.Font(None, 30), f"{p[3]} {p[4]}", "#e8ab83", "#ffffff")

    delete_game_btn =  Button(550, 350, 200, 60, font, "Delete", "#dda658", "#eec584", "#ffffff", on_click = lambda : delete_loaded_game(slot))


    play_game_btn = Button(550, 250, 200, 60, font, "Continue", "#dda658", "#eec584", "#ffffff", on_click = lambda : start_loaded_game(slot))

    saved_games_btn.append(delete_game_btn)
    saved_games_btn.append(play_game_btn)
    texts.append(text)
    texts.append(text2)
    load_game_menu.texts = texts

def go_back():
    saved_games_btn[:] = [btn for btn in saved_games_btn 
                        if btn.text not in ("Delete", "Continue")]
    menu_manager.back()
    if menu_manager.current:
        menu_manager.current.activate()

def start_flappy():
    global current_scene, flappystate
    flappystate = True
    current_scene = FlappyBirdScene(screen)
    log(3, f"[Main] Scene switched to: {type(current_scene).__name__}")


# Global Variables
return_to : Menu | None = None
flappystate = False
flappyscore = 0

# Button Lists

# Home Buttons
new_game_btn = Button(300, 200, 200, 60, font, "New Game", "#dda658", "eec584", "ffffff", on_click = new_game)
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "#dda658", "eec584", "ffffff", on_click = load_game)  
quit_btn = Button(300, 400, 200, 60, font, "Quit Game", "#dda658", "eec584", "ffffff", on_click = quit_game)

# New Game Buttons
start_game_btn = Button(300, 300, 200, 60, font, "Start", "#dda658", "eec584", "ffffff", on_click = start_game)

# All purpose Buttons:
back_btn = Button(300, 500, 200, 60, font, "Back", "#dda658", "eec584", "ffffff", on_click = go_back)
flappy_btn = Button(
    300, 500, 200, 60, font, 
    "Flappy Bird", "c8ab83", "eec584", "ffffff", 
    on_click=start_flappy
)

# Load Game Buttons
saved_files = Persistence.taken_name()



saved_games_btn  : list [Button]= []
saved_games_btn.append(back_btn) # note this

texts : list[Any]= []


# Input Fields
name_Field = InputField(300, 200, 200, 60, font)

# ---------------------------------------------
# Note: Menu Creation Syntax:
# Menu (<filepath to bg>, <button list>, <field list> [for gamesetup only], bg_manager [<<< ALWAYS INCLUDE])

# Splash Screen Menu
home_menu = Menu(os.path.join(ASSETS, "Background/main_menu_noncut.png"), [new_game_btn, load_game_btn, quit_btn], bg_manager)

# New Game Setup Menu
new_game_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"), [start_game_btn, back_btn], [name_Field], bg_manager)
where_to_save_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"), saved_games_btn, [], bg_manager)
load_game_menu = GameSetupMenu(os.path.join(ASSETS, "Background/main_menu_new_game.png"),  saved_games_btn,
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

flappy = FlappyBird(screen, width=800, height=600)
home_menu.buttons.append(flappy_btn)

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

        for btn in current_scene.get_all_active_buttons():
            if btn.hovered:
                cursor_to_draw = cursor_point
                break
        else:
            if current_scene.selected:
                cursor_to_draw = cursor_hand

            else:
                if current_scene.cursor_mode == "Petting":
                    
                    for creature in current_scene.creatures:
                        if creature.hovered:
                            cursor_to_draw = cursor_hover
                            break
                    else:
                        cursor_to_draw = cursor_default

                else:
                    cursor_to_draw = cursor_default

    screen.blit(cursor_to_draw, (mx, my))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()