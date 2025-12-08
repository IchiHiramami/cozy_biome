# ----------------------------------------------------------------
# Contained here are classes and methods related to MAIN GAMEPLAY
# ----------------------------------------------------------------

# Imports
import os
import pygame
from random import randint, choice
from classes import Creature, Food, Potion, Cleanse, GlobalSatisfactionBar  # type: ignore
from game_manager import Button, InputField
from game_manager import Menu, MenuManager, BackgroundManager
from logger import log
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

animated_cat = [
    "assets/Sprites/cat_animation_1.png",
    "assets/Sprites/cat_animation_2.png",
    "assets/Sprites/cat_animation_3.png",
    "assets/Sprites/cat_animation_4.png"
]

Nocky_OC = [
    "assets/Sprites/Nocky_OC_1.png",
    "assets/Sprites/Nocky_OC_2.png",
    "assets/Sprites/Nocky_OC_2.png"
]

spritz = [animated_cat, Nocky_OC]

class GameScene:
    def __init__(self, world_name: str):
        self.world_name = world_name
        self.global_bar = GlobalSatisfactionBar(800, 20)

        self.background = pygame.image.load(os.path.join(ASSETS, "Background/main_world.png"))
        self.background = pygame.transform.scale(self.background, (800, 600))

        self.creatures: list[Creature] = [
            Creature(
                f"creature{i}",
                randint(50, 750),
                randint(50, 550),
                choice(spritz),
            )
            for i in range(randint(2, 4))
        ]

        self.selected: Creature | None = None

        self.master_buttons: list[Button] = []
        self.master_visible = False      

        self.inputs: list[InputField] = []
        self.admin_field = InputField(300, 200, 200, 60, pygame.font.Font(None, 20))
        self.inputs.append(self.admin_field)

        self.admin_mode = False

        # Disregard attribute mismatch here (only visible in stricttype)
        self.menu_manager : MenuManager = None
        self.bg_manager : BackgroundManager = None
        self.home_menu : Menu  = None
        self.pause_menu : Menu = None

        # FIX: Increase font size so the hamburger icon is readable
        self.hamburger_btn = Button(
            10, 10, 40, 40,
            pygame.font.Font(None, 30),   # FIX: was 10, too small
            '≡',
            "c8ab83", "eec584", "ffffff",
            on_click=self.open_pause_menu   # FIX: removed lambda wrapper
        )
        # Master Panel Buttons
        spawn_btn_m = Button(
            20, 80, 120, 40,
            pygame.font.Font(None, 20),
            "Master Spawn",
            "c8ab83", "eec584", "ffffff",
            on_click=lambda: self.run_admin_command("spawn")
        )

        reset_btn_m = Button(
            20, 130, 120, 40,
            pygame.font.Font(None, 20),
            "Reset All",
            "c8ab83", "eec584", "ffffff",
            on_click=lambda: self.run_admin_command("reset")
        )

        refill_btn_m = Button(
            20, 180, 120, 40,
            pygame.font.Font(None, 20),
            "Refill All",
            "c8ab83", "eec584", "ffffff",
            on_click=lambda: self.run_admin_command("refill")
        )

        hide_btn_m = Button(
            20, 230, 120, 40,
            pygame.font.Font(None, 20),
            "Hide Panel",
            "c8ab83", "eec584", "ffffff",
            on_click=lambda: self.toggle_master(False)
        )

        self.master_buttons.extend([spawn_btn_m, reset_btn_m, refill_btn_m, hide_btn_m])

    # -------------------------
    # PAUSE MENU FUNCTIONS
    # -------------------------

    def build_pause_menu(self):
        pause_font = pygame.font.Font(None, 40)

        resume_btn = Button(300, 200, 200, 60, pause_font, "Resume", "c8ab83", "eec584", "ffffff", on_click=self.resume_game)
        save_btn   = Button(300, 280, 200, 60, pause_font, "Save Game", "c8ab83", "eec584", "ffffff", on_click=self.save_game_state)
        load_btn   = Button(300, 360, 200, 60, pause_font, "Load Game", "c8ab83", "eec584", "ffffff", on_click=self.load_game_state)
        quit_btn   = Button(300, 440, 200, 60, pause_font, "Quit to Menu", "c8ab83", "eec584", "ffffff", on_click=self.quit_to_main_menu)

        self.pause_menu = Menu(
            os.path.join(ASSETS, "Background/main_menu_new_game.png"),
            [resume_btn, save_btn, load_btn, quit_btn],
            self.bg_manager
        )

    def open_pause_menu(self):
        self.menu_manager.push(self.pause_menu)
        self.pause_menu.activate()

    def resume_game(self):
        self.menu_manager.pop_menu()

    def save_game_state(self):
        print("TODO: Save game here")

    def load_game_state(self):
        print("TODO: Load game here")

    def quit_to_main_menu(self):
        import main
        main.current_scene = None
        self.menu_manager.switch(self.home_menu)
        self.home_menu.activate()

    # -------------------------
    # ADMIN PANEL
    # -------------------------

    def toggle_master(self, state: bool):
        self.master_visible = state
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Admin toggle set to {state}")

    def debug_spawn(self):
        new = Creature(
            f"creature{len(self.creatures)}",
            randint(50, 750),  
            randint(50, 550),  
            choice(spritz)
        )
        self.creatures.append(new)
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Spawned creature")

    def run_admin_command(self, cmd: str):
        cmd = cmd.strip().lower()

        if cmd == "spawn":
            self.debug_spawn()
            return

        if cmd == "reset":
            self.creatures.clear()
            return

        if cmd == "refill":
            for c in self.creatures:
                c.satisfaction_level = 100
            return

        if cmd == "master":
            self.master_visible = True
            return

        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Unknown command '{cmd}'")

    # -------------------------
    # EVENT HANDLING
    # -------------------------

    def handle_event(self, event: pygame.event.Event):

        # FIX: Only allow hamburger button when pause menu is NOT active
        if self.menu_manager.current is not self.pause_menu:
            self.hamburger_btn.handle_event(event)

        # FIX: Only allow master buttons when visible
        if self.master_visible:
            for button in self.master_buttons:
                button.handle_event(event)

        if self.admin_mode:
            for fields in self.inputs:
                fields.handle_event(event)

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SLASH:
                self.admin_mode = not self.admin_mode
                log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Admin access set to {self.admin_mode}")

            if self.admin_mode and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                cmd = self.admin_field.text 
                self.run_admin_command(cmd) 
                self.admin_field.text = ""   

        # Creature dragging
        if event.type == pygame.MOUSEBUTTONDOWN:
            for creature in self.creatures:
                if creature.rect.collidepoint(event.pos):
                    self.selected = creature
                    self.drag_offset = (
                        creature.rect.x - event.pos[0],
                        creature.rect.y - event.pos[1]
                    )
                    break

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected = None

        elif event.type == pygame.MOUSEMOTION and self.selected:
            self.selected.rect.x = event.pos[0] + self.drag_offset[0]
            self.selected.rect.y = event.pos[1] + self.drag_offset[1]
            self.selected.x, self.selected.y = self.selected.rect.center  

    # -------------------------
    # UPDATE + DRAW
    # -------------------------

    def update(self):
        # FIXED: Pause menu should freeze gameplay
        if self.menu_manager.current is self.pause_menu:
            return

        for creature in self.creatures:
            creature.update_effects()
            creature.satisfaction_level = max(
                0,
                creature.satisfaction_level - creature.satisfaction_decay
            )

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))

        self.global_bar.draw(screen, self.creatures)

        # FIXED: Draw hamburger only when pause menu is NOT active
        if self.menu_manager.current is not self.pause_menu:
            self.hamburger_btn.draw(screen)

        for creature in self.creatures:
            if creature.satisfaction_level > 70:
                creature.update_sprite(1)
            elif creature.satisfaction_level < 30:
                creature.update_sprite(2)
            else:
                creature.update_sprite(0)

            creature.draw(screen)

        if self.master_visible:
            for buttons in self.master_buttons:
                buttons.draw(screen)

        if self.admin_mode:
            for input_field in self.inputs:
                input_field.draw(screen)
