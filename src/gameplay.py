# ----------------------------------------------------------------
# Contained here are classes and methods related to MAIN GAMEPLAY
# ----------------------------------------------------------------

# Imports
import os
import pygame
from random import randint, choice
from persistence import Persistence # type: ignore
from classes import Creature, Food, Potion, Cleanse, GlobalSatisfactionBar, Less_Decay, More_Satisfaction  # type: ignore
from game_manager import Button, InputField, InventorySlot, Toolbar
from logger import log
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

animated_cat = {
    "Sprite" : ["assets/Sprites/cat_animation_1.png", "assets/Sprites/cat_animation_2.png", "assets/Sprites/cat_animation_3.png",],
    }

cat = {"Sprite" : ["assets/Sprites/cat.jpg"]}

Nocky_OC = {
        "Sprite" : ["assets/Sprites/Nocky_OC_1.png", "assets/Sprites/Nocky_OC_2.png", "assets/Sprites/Nocky_OC_2.png"]
    }

spritz = [animated_cat["Sprite"], Nocky_OC["Sprite"], cat["Sprite"]]

class GameScene:
    def __init__(self, world_name: str, creatures : list[Creature] = [], foods : list[Food] = [], potions : list[Potion] = []):
        self.world_name = world_name
        self.global_bar = GlobalSatisfactionBar(800, 20)

        #state
        self.is_paused = False
        self.allow_dragging = True

        self.background = pygame.image.load(os.path.join(ASSETS, "Background/main_world.png"))
        self.background = pygame.transform.scale(self.background, (800, 600))

        if creatures:
            self.creatures = creatures
        else:
            self.creatures = []
            for i in range(randint(2,4)):
                self_sprite = choice(spritz)

                c = Creature(
                    f"Creature{i}",
                    "quaker" if self_sprite == spritz[1] else "mimi-carrier",
                    randint(10, 500), randint(10, 500),
                    self_sprite
                    )
                
                self.creatures.append(c)

        ##################################
        self.foods = []
        self.potions = []
        ##################################

        self.selected: Creature | None = None
        self.inputs: list[InputField] = []
        

        # UI elements
        self.pause_menu_buttons : list[Button] = []

        # Build a tabbed toolbar with tabs
        toolbar_font = pygame.font.Font(None, 30)

        # Place tab content slightly below the header area so headers don't overlap
        tab_content_y = 540

        main_tab_buttons = [
            Button(20, tab_content_y, 100, 40, toolbar_font, "Toggle", "c8ab83", "eec584", "ffffff", on_click = self.toggle_toolbar),
            Button(140, tab_content_y, 100, 40, toolbar_font, "Pet", "c8ab83", "eec584", "ffffff", on_click = self.petting),
        ]

        Inventory_buttons = [
            Button(20, tab_content_y, 120, 40, pygame.font.Font(None, 20), "Master Spawn", "c8ab83", "eec584", "ffffff", on_click=lambda: self.run_admin_command("spawn")),
            Button(150, tab_content_y, 120, 40, pygame.font.Font(None, 20), "Refill All", "c8ab83", "eec584", "ffffff", on_click=lambda: self.run_admin_command("refill")),
        ]

        slot1 = InventorySlot(300, 560, 50)
        slot2 = InventorySlot(360, 560, 50)
        slot3 = InventorySlot(420, 560, 50)

        Inventory_buttons = [slot1, slot2, slot3]

        self.toolbar = Toolbar(
            x=0,
            y=520,
            width=800,
            height=80,
            bg_color=(200, 171, 131),
            tabs=[
                {'name': 'Main', 'buttons': main_tab_buttons, 'elements': []},
                {'name': 'Admin', 'buttons': Inventory_buttons, 'elements': []}
            ],

        )

        pause_font = pygame.font.Font(None, 32)

        self.hamburger_btn = Button(
            10, 10, 40, 40,
            pygame.font.Font(None, 30),
            "≡",
            "c8ab83", "eec584", "ffffff",
            on_click=self.toggle_pause            
        )

        self.toggle_toolbar_btn = Button(
            10, 480 if self.toolbar.visible else 600, 40, 40,
            pygame.font.Font(None, 30),
            "^",
            "c8ab83", "eec584", "ffffff",
            on_click=self.toggle_toolbar
        )

        resume_btn = Button(
            300, 200, 200, 50, pause_font,
            "Resume", "c8ab83", "eec584", "ffffff",
            on_click=self.toggle_pause
        )

        save_btn = Button(
            300, 260, 200, 50, pause_font,
            "Save Game", "c8ab83", "eec584", "ffffff",
            on_click=self.save_game_state
        )

        load_btn = Button(
            300, 320, 200, 50, pause_font,
            "Load Game", "c8ab83", "eec584", "ffffff",
            on_click=self.load_game_state
        )

        quit_btn = Button(
            300, 380, 200, 50, pause_font,
            "Quit to Menu", "c8ab83", "eec584", "ffffff",
            on_click=self.quit_to_main_menu
)

        self.pause_menu_buttons.extend([resume_btn, save_btn, load_btn, quit_btn])






        # Admin input field -> to be shipped in the final game but NOT documented (cheat code kumbaga)
        self.master_buttons: list[Button] = []
        self.master_visible = False      
        self.admin_field = InputField(300, 200, 200, 60, pygame.font.Font(None, 20))
        self.inputs.append(self.admin_field)

        self.admin_mode = False

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

    def petting(self):
        self.allow_dragging = not self.allow_dragging
        if not self.allow_dragging:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, f"World Dragging to {self.is_paused}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, f"Paused set to {self.is_paused}")

    def toggle_toolbar(self):
        self.toolbar.visible = not self.toolbar.visible

    def save_game_state(self):
        Persistence.save_to_slot(self.world_name,
                                  sum(c.satisfaction_level for c in self.creatures),
                                    self.creatures,
                                    self.foods,
                                    self.potions)
        print("TODO: Save game here")  #TODO: will wire to Persistence later

    def load_game_state(self):
        print("TODO: Load game here")

    def quit_to_main_menu(self):
        import main
        main.current_scene = None
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 2, "Returned to main menu from pause")

    def toggle_master(self, state: bool):
        """Show/hide master buttons"""
        self.master_visible = state
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Admin toggle set to {state}")

    def debug_spawn(self):
        new = Creature(
            f"creature{len(self.creatures)}",
            "super",
            randint(50, 750),  
            randint(50, 550),  
            choice(spritz)
        )
        self.creatures.append(new)
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Spawned creature")

    def run_admin_command(self, cmd: str):
        cmd = cmd.strip().lower()

        # SPAWN — spawn one creature
        if cmd == "spawn":
            self.debug_spawn()
            log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Spawned creature")
            return

        # RESET — remove all creatures
        if cmd == "reset":
            self.creatures.clear()
            log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Reset creature list")
            return

        # REFILL — refill all satisfaction to 100
        if cmd == "refill":
            for c in self.creatures:
                c.satisfaction_level = 100
            log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Refilled all creatures")
            return

        # MASTER — show all debug buttons
        if cmd == "master":
            self.master_visible = True
            log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, "Master panel activated")
            return

        # Unknown command
        log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Unknown command '{cmd}'")

    def handle_event(self, event: pygame.event.Event):
        # Always let hamburger receive events
        self.hamburger_btn.handle_event(event)

        self.toolbar.handle_event(event)
        self.toggle_toolbar_btn.handle_event(event)

        # If paused, direct events only to pause buttons and return early
        if self.is_paused:
            for b in self.pause_menu_buttons:
                b.handle_event(event)
            return

        for button in self.master_buttons:
            button.handle_event(event)

        if self.admin_mode:
            for fields in self.inputs:
                fields.handle_event(event)

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()

            if event.key == pygame.K_SLASH:
                self.admin_mode = not self.admin_mode 

                log(datetime.now().strftime("[%Y-%m-%d %H:%M:%S]"), 3, f"Admin access set to {self.admin_mode}")

            if self.admin_mode:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    cmd = self.admin_field.text 
                    self.run_admin_command(cmd) 
                    self.admin_field.text = ""   

        if event.type == pygame.MOUSEBUTTONDOWN:
            for creature in self.creatures:
                if creature.rect.collidepoint(event.pos):
                    if self.allow_dragging == True:
                        self.selected = creature
                        self.drag_offset = (
                            creature.rect.x - event.pos[0],
                            creature.rect.y - event.pos[1]
                        )
                        break

                    else:
                        creature.satisfaction_level += 0.5 * creature.satisfaction_multiplier

        elif event.type == pygame.MOUSEBUTTONUP:
            self.selected = None

        elif event.type == pygame.MOUSEMOTION and self.selected:
            if self.allow_dragging:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                self.selected.rect.x = event.pos[0] + self.drag_offset[0]
                self.selected.rect.y = event.pos[1] + self.drag_offset[1]
                self.selected.x, self.selected.y = self.selected.rect.center  

    def update(self):
        if self.is_paused:
            return #temporarily disables updates when game state is paused
        
        for creature in self.creatures:
            creature.update_effects()
            creature.satisfaction_level = max(
                0,
                creature.satisfaction_level - creature.satisfaction_decay
            )

    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.global_bar.draw(screen, self.creatures)

        # Always draw hamburger
        self.hamburger_btn.draw(screen)

        self.toolbar.draw(screen)
        self.toggle_toolbar_btn.draw(screen)
        
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

        if self.is_paused:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            for b in self.pause_menu_buttons:
                b.draw(screen)
