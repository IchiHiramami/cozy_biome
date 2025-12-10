# ----------------------------------------------------------------
# Contained here are classes and methods related to MAIN GAMEPLAY
# ----------------------------------------------------------------

# Imports
import os
import pygame
from random import randint, choice
from persistence import Persistence
from classes import PetAction, Creature, Food, Potion, Cleanse, GlobalSatisfactionBar, Less_Decay, More_Satisfaction, Inventory, Money  # type: ignore
from game_manager import Button, InputField, InventorySlot, Toolbar
from logger import log
from minigames import FlappyBird
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

animated_cat = {
    "Sprite" : ["assets/Sprites/cat_animation_1.png", "assets/Sprites/cat_animation_2.png", "assets/Sprites/cat_animation_3.png", "assets/Sprites/Dead.png"],
    }

#cat = {"Sprite" : ["assets/Sprites/cat.jpg", "assets/Sprites/cat.jpg", "assets/Sprites/cat.jpg"]} # MINIMUM LAGI 3 sprites

Nocky_OC = {
        "Sprite" : ["assets/Sprites/Nocky_OC_2.png", "assets/Sprites/Nocky_OC_1.png", "assets/Sprites/Nocky_OC_2.png", "assets/Sprites/Dead.png"]
    }

spritz = [animated_cat["Sprite"], Nocky_OC["Sprite"]]#, cat["Sprite"]]

PADDING = 20
WORLD_LEFT = 0 + PADDING
WORLD_TOP = 0 + PADDING
WORLD_RIGHT = 800 - PADDING
WORLD_BOTTOM = 600 - PADDING


class GameScene:
    def __init__(self, world_name: str, creatures : list[str] = [], foods : defaultdict[str, int] | None = None, potions : defaultdict[str, int] | None = None, cleanse : defaultdict[str, int] | None = None, money : int  = 0):
        pygame.mixer.music.load("assets/Music/Gamescene_music.mp3")
        pygame.mixer.music.set_volume(0.5)  # 0.0 to 1.0
        pygame.mixer.music.play(-1)  

        # Initial Game Constants
        self.world_name = world_name
        self.global_bar = GlobalSatisfactionBar(800, 20)

        self.money = Money(money)
        self.money.add_money(40) 

        #state
        self.is_paused = False
        self.is_market_open = False
        self.allow_dragging = True # -> allows whether creatures can be dragged during petting mode
        self.cursor_mode = "Default"
        self.game_continue = True
        self.is_dragging = False # -> IFKYK
        self.drag_starts_pos = None

        self.inventory = Inventory()
        if foods: self.inventory.foods = foods
        if potions: self.inventory.potions = potions
        if cleanse: self.inventory.cleanse = cleanse

        self.background = pygame.image.load(os.path.join(ASSETS, "Background/main_world.png"))
        self.background = pygame.transform.scale(self.background, (800, 600))

        self.icon_grapes = pygame.image.load("assets/Items/grapes.png").convert_alpha()
        self.icon_cola = pygame.image.load("assets/Items/cola.png").convert_alpha()
        self.icon_cassis = pygame.image.load("assets/Items/cassis.png").convert_alpha()
        self.icon_cherry = pygame.image.load("assets/Items/cherry.png").convert_alpha()
        self.icon_aisu = pygame.image.load("assets/Items/aisu.png").convert_alpha()
        self.icon_makku = pygame.image.load("assets/Items/makku.png").convert_alpha()
        self.icon_spam = pygame.image.load("assets/Items/spamcan.png").convert_alpha()
        self.icon_diamond = pygame.image.load("assets/Collectibles/Diamond-green.png").convert_alpha()
        self.icon_cleanse = pygame.image.load("assets/Items/Cleanse.png").convert_alpha()
        self.icon_less_decay = pygame.image.load("assets/Items/Lessdecay.png").convert_alpha()
        self.icon_more_satsifaction = pygame.image.load("assets/Items/MoreSatisfaction.png").convert_alpha()

        # Creatures
        if creatures:
            self.creatures = creatures
        else:
            self.creatures : list[Creature] = []
            for i in range(randint(2,4)):
                self_sprite = choice(spritz)

                c = Creature(
                    f"Creature{i}",
                    "quacker" if self_sprite == spritz[1] or self_sprite[2] else "mimi-carrier",
                    randint(10, 500), randint(10, 500),
                    self_sprite
                    )
                
                self.creatures.append(c)

        self.selected: Creature | None = None
        
        self.inputs: list[InputField] = []
        

        # UI elements
        self.pause_menu_buttons : list[Button] = []

        # Build a tabbed toolbar with tabs
        toolbar_font = pygame.font.Font(None, 30)

        # Place tab content slightly below the header area so headers don't overlap
        tab_content_y = 540

        main_tab_buttons = [
            Button(20, tab_content_y, 100, 40, toolbar_font, "Toggle", "#dda658", "#eec584", "##ffffff", on_click = self.toggle_toolbar),
            Button(680, tab_content_y, 100, 40, toolbar_font, "Pet", "#dda658", "#eec584", "#ffffff", on_click = self.petting),
        ]

        Inv_Action_Buttons = [
            Button(670, tab_content_y, 120, 40, toolbar_font, "Shop", "#dda658", "#eec584", "#ffffff", on_click=self.toggle_marketplace),
            Button(20, tab_content_y, 120, 40, pygame.font.Font(None, 20), "Refill All", "#dda658", "#eec584", "#ffffff", on_click=lambda: self.run_admin_command("refill")),
        ]


        import main
        mini_game_Buttons = [
            Button(20, tab_content_y, 100, 40, pygame.font.Font(None, 25), "Plappy Birb", "#dda658", "#eec584", "##ffffff", on_click = lambda : (main.start_flappy(self.world_name), self.save_game_state())),
        ]

        self.market_items : list[dict[str, str | int | pygame.Surface]] = [
            {"name": "Grapes", "price": 5, "icon": self.icon_grapes, "for-type" : "Quaker", "Satisfaction" : 6, "Item Type" : "Food"},
            {"name": "Makku", "price": 7, "icon": self.icon_makku, "for-type" : "Quaker", "Satisfaction" : 15, "Item Type" : "Food"},
            {"name": "Spam", "price": 60, "icon": self.icon_spam, "for-type" : "Quaker", "Satisfaction" : 45, "Item Type" : "Food"},

            {"name": "Cassis", "price": 10, "icon": self.icon_cassis, "for-type" : "mimi-carrier", "Satisfaction" : 12, "Item Type" : "Food"},
            {"name": "Cherry", "price": 3, "icon": self.icon_cherry, "for-type" : "mimi-carrier", "Satisfaction" : 2, "Item Type" : "Food"},
            {"name": "Aisu", "price": 60, "icon": self.icon_aisu, "for-type" : "mimi-carrier", "Satisfaction" : 50, "Item Type" : "Food"},

            {"name": "Less Decay", "price": 5, "icon": self.icon_less_decay, "for-type" : "Any", "Duration" : 10, "Item Type" : "Potion"},
            {"name": "More Satisfaction", "price": 7, "icon": self.icon_more_satsifaction, "for-type" : "Any", "Duration" : 8, "Item Type" : "Potion"},
            {"name": "Cleanse", "price": 10, "icon": self.icon_cleanse, "for-type" : "Any", "Duration" : 10, "Item Type" : "Cleanse"},
        ]
        self.market_buttons : list[Button]= []

        sloti = InventorySlot(140, 540, 50, "Grapes",icon = self.icon_grapes, on_click = self.use_item)
        slot0 = InventorySlot(200, 540, 50, "Makku",icon = self.icon_makku, on_click = self.use_item)
        slot1 = InventorySlot(260, 540, 50, "Spam",icon = self.icon_spam, on_click = self.use_item)

        slot2 = InventorySlot(320, 540, 50, "Cassis",icon = self.icon_cassis, on_click = self.use_item)
        slot3 = InventorySlot(380, 540, 50, "Cherry",icon = self.icon_cherry, on_click = self.use_item)
        slot4 = InventorySlot(440, 540, 50, "Aisu",icon = self.icon_aisu, on_click = self.use_item)

        slot5 = InventorySlot(500,540, 50, "Less Decay",icon = self.icon_less_decay, on_click = self.use_item)
        slot6 = InventorySlot(560,540, 50, "More Satisfaction", icon = self.icon_more_satsifaction, on_click = self.use_item)
        slot7 = InventorySlot(620, 540, 50, "Cleanse",icon = self.icon_cleanse, on_click = self.use_item)

        Inventory_slots = [sloti ,slot0 ,slot1, slot2, slot3, slot4, slot5, slot6, slot7]

        self.toolbar = Toolbar(
            x=0,
            y=520,
            width=800,
            height=80,
            bg_color=(200, 171, 131),
            tabs=[
                {'name': 'Actions', 'buttons': main_tab_buttons, 'elements': []},
                {'name': 'Inventory', 'buttons': Inventory_slots + Inv_Action_Buttons, 'elements': []},
                {'name': 'Mini Game', 'buttons': mini_game_Buttons, 'elements': []}
            ],

        )
        self.toolbar.parent_scene = self #type: ignore

        pause_font = pygame.font.Font(None, 32)

        self.hamburger_btn = Button(
            10, 10, 40, 40,
            pygame.font.Font(None, 30),
            "≡",
            "#dda658", "#eec584", "#ffffff",
            on_click=self.toggle_pause            
        )

        self.toggle_toolbar_btn = Button(
            10, 480 if self.toolbar.visible else 600, 40, 40,
            pygame.font.Font(None, 30),
            "^",
            "#dda658", "#eec584", "#ffffff",
            on_click=self.toggle_toolbar
        )

        resume_btn = Button(
            300, 200, 200, 50, pause_font,
            "Resume", "#dda658", "#eec584", "#ffffff",
            on_click=self.toggle_pause
        )

        save_btn = Button(
            300, 260, 200, 50, pause_font,
            "Save Game", "#dda658", "#eec584", "#ffffff",
            on_click=self.save_game_state
        )

        load_btn = Button(
            300, 320, 200, 50, pause_font,
            "Load Game", "#dda658", "#eec584", "#ffffff",
            on_click=self.load_game_state
        )

        quit_btn = Button(
            300, 380, 200, 50, pause_font,
            "Quit to Menu", "#dda658", "#eec584", "#ffffff",
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
            "#dda658", "#eec584", "#ffffff",
            on_click=lambda: self.run_admin_command("spawn")
        )

        reset_btn_m = Button(
            20, 130, 120, 40,
            pygame.font.Font(None, 20),
            "Reset All",
            "#dda658", "#eec584", "#ffffff",
            on_click=lambda: self.run_admin_command("reset")
        )

        refill_btn_m = Button(
            20, 180, 120, 40,
            pygame.font.Font(None, 20),
            "Refill All",
            "#dda658", "#eec584", "#ffffff",
            on_click=lambda: self.run_admin_command("refill")
        )

        hide_btn_m = Button(
            20, 230, 120, 40,
            pygame.font.Font(None, 20),
            "Hide Panel",
            "#dda658", "#eec584", "#ffffff",
            on_click=lambda: self.toggle_master(False)
        )

        self.master_buttons.extend([spawn_btn_m, reset_btn_m, refill_btn_m, hide_btn_m])

    def use_item(self, item_name: str):
        target = self.selected
        if target is None:
            return

        food_effects : dict[str, tuple[str, float, float]] = {
            "Grapes":        ("quacker", 6,   -3),
            "Makku":         ("quacker", 7,   -3.5),
            "Spam":          ("quacker", 45,  -22.5),
            "Cassis":        ("mimi-carrier", 12, -6),
            "Cherry":        ("mimi-carrier", 2,  -1),
            "Aisu":          ("mimi-carrier", 50, -25),
        }

        def effect_handler(used_item_name: str):
            if used_item_name in food_effects:
                preferred_type, good, bad = food_effects[used_item_name]
                delta = good if target.type == preferred_type else bad
                target.satisfaction_level = min(100, target.satisfaction_level + delta)
                return
            
            if used_item_name == "Less Decay":
                eff = Less_Decay()
                eff.consume(target, target.satisfaction_multiplier, eff.duration)
                return

            if used_item_name == "More Satisfaction":
                eff = More_Satisfaction()
                eff.consume(target, target.satisfaction_multiplier, eff.duration)
                return

            # Cleanse
            if used_item_name == "Cleanse":
                target.effects.clear()

        self.inventory.remove_inventory(item_name, on_consumed=effect_handler)

    def toggle_marketplace(self):
        self.is_market_open = not self.is_market_open
        self.market_buttons.clear()

        base_x = 100
        base_y = 140
        col_spacing = 200   # distance between columns
        row_spacing = 120   # distance between rows



        for idx, item in enumerate(self.market_items):
            col = idx % 3
            row = idx // 3


            btn_x = base_x + col * col_spacing
            btn_y = base_y + row * row_spacing + 30
            buy_btn = Button(btn_x, btn_y, 120, 40, 
                        pygame.font.Font(None, 20),
                        f"Buy ({item["price"]})", 
                        "#dda658", "#eec584", "#ffffff",
                        on_click=lambda i = item: self.buy_item(i)
                        )
            self.market_buttons.append(buy_btn)
        
        close_btn = Button(
            350, 500, 120, 40,
            pygame.font.Font(None, 20),
            "Close",
            "#dda658", "#eec584", "#ffffff",
            on_click=self.close_market
        )
        self.market_buttons.append(close_btn)

    def close_market(self):
        self.is_market_open = False
        self.market_buttons

    def buy_item(self, item: dict[str, str | int | pygame.Surface]):
        print(self.money.money)
        if self.money.money - item["price"] <= 0: #type: ignore
            return
        self.money.remove_money(item) # type: ignore
        
        if item["Item Type"] == "Food":
            to_add = Food(item["name"], item["for-type"], item["Satisfaction"]) #type: ignore
        elif item["Item Type"] == "Potion":
            to_add = Potion(item["name"], item["for-type"]) #type: ignore
        else:
            to_add = Cleanse()
        self.inventory.add_inventory(to_add)
        log(2, "Bought item")

    def get_all_active_buttons(self) -> list[Button]:
        """
        Put all the buttons into one giant list
        """
        buttons: list[Button] = []

        # Toolbar tab buttons
        if self.toolbar.visible:
            buttons.extend(self.toolbar._tab_header_buttons) # type: ignore

            active_tab: dict[str, list[Button]] = self.toolbar.tabs[self.toolbar.active_tab]
            buttons.extend(active_tab['buttons']) # type: ignore

        # Pause menu buttons
        if self.is_paused:
            buttons.extend(self.pause_menu_buttons)

        # Master admin panel
        if self.master_visible:
            buttons.extend(self.master_buttons)

        # Hamburger + toggle toolbar button
        buttons.append(self.hamburger_btn)
        buttons.append(self.toggle_toolbar_btn)

        if self.is_market_open:
            buttons.extend(self.market_buttons)

        return buttons

    def petting(self):
        self.allow_dragging = not self.allow_dragging
        self.cursor_mode = "Petting" if not self.allow_dragging else "Default"
        log(2, f"World Dragging to {self.allow_dragging}")

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        log(2, f"Paused set to {self.is_paused}")

    def toggle_toolbar(self):
        self.toolbar.visible = not self.toolbar.visible

    def save_game_state(self):
        Persistence.save_to_slot(self.world_name,
                                sum(c.satisfaction_level for c in self.creatures),
                                    self.creatures,
                                    self.inventory.foods,
                                    self.inventory.potions,
                                    self.inventory.cleanse,
                                    self.money.money)

    def load_game_state(self):
        pygame.mixer.music.load("assets/Music/HomeScene_music.mp3")
        pygame.mixer.music.play(-1)
        import main
        main.creatureslist = None
        main.current_scene = None
        
        print("TODO: Load game here")

    def quit_to_main_menu(self):
        pygame.mixer.music.load("assets/Music/HomeScene_music.mp3")
        pygame.mixer.music.play(-1)
        import main
        main.current_scene = None
        log(2, "Returned to main menu from pause")

    def toggle_master(self, state: bool):
        """Show/hide master buttons"""
        self.master_visible = state
        log(3, f"Admin toggle set to {state}")

    def debug_spawn(self):
        new = Creature(
            f"creature{len(self.creatures)}",
            "super",
            randint(50, 750),  
            randint(50, 550),  
            choice(spritz)
        )
        self.creatures.append(new)
        log(3, "Spawned creature")

    def run_admin_command(self, cmd: str):
        cmd = cmd.strip().lower()

        # SPAWN — spawn one creature
        if cmd == "spawn":
            self.debug_spawn()
            log(3, "Spawned creature")
            return

        # RESET — remove all creatures
        if cmd == "reset":
            self.creatures.clear()
            log(3, "Reset creature list")
            return

        # REFILL — refill all satisfaction to 100
        if cmd == "refill":
            for c in self.creatures:
                c.satisfaction_level = 100
            log(3, "Refilled all creatures")
            return

        # MASTER — show all debug buttons
        if cmd == "master":
            self.master_visible = True
            log(3, "Master panel activated")
            return

        # Unknown command
        log(3, f"Unknown command '{cmd}'")

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

        if self.is_market_open:
            for btn in self.market_buttons:
                btn.handle_event(event)
            return

        if self.master_visible:
            for button in self.master_buttons:
                button.handle_event(event)

        if self.admin_mode:
            for fields in self.inputs:
                fields.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()

            if event.key == pygame.K_SLASH:
                self.admin_mode = not self.admin_mode 

                log(3, f"Admin access set to {self.admin_mode}")

            if self.admin_mode:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    cmd = self.admin_field.text 
                    self.run_admin_command(cmd) 
                    self.admin_field.text = ""   

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for creature in self.creatures:
                if creature.rect.collidepoint(event.pos):
                    creature.update_hover(pygame.mouse.get_pos())

                    # Always select the creature on click
                    self.selected = creature
                    log(2, f"Player selected {creature.name}")

                    if self.allow_dragging:
                        # start dragging
                        self.is_dragging = True
                        self.drag_start_pos = event.pos
                        self.drag_offset = (
                            creature.rect.x - event.pos[0],
                            creature.rect.y - event.pos[1]
                        )
                        log(2, f"Started dragging creature '{creature.name}' at {creature.rect.center}")
                    else:
                        # not dragging, treat as a pet action
                        creature.pet(PetAction.PET)
                        log(2, f"Player pet {creature.name}: Creature Satisfaction Level: {creature.satisfaction_level}")

                    break  # stop checking other creatures

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # stop dragging but keep the creature selected until another is clicked
            self.is_dragging = False
            self.drag_start_pos = None

        elif event.type == pygame.MOUSEMOTION and self.is_dragging and self.selected:
            if self.allow_dragging:
                # move the selected creature while dragging
                self.selected.rect.x = event.pos[0] + self.drag_offset[0]
                self.selected.rect.y = event.pos[1] + self.drag_offset[1]
                self.selected.x, self.selected.y = self.selected.rect.center

    def update(self):
        mx, my = pygame.mouse.get_pos()
        if self.is_paused:
            return #temporarily disables updates when game state is paused

        for i, creature in enumerate(self.creatures):
            for j in range(i +1, len(self.creatures)):
                creature.resolve_soft_collisions(self.creatures[j])

        for creature in self.creatures:
            creature.rect.x = max(WORLD_LEFT, min(creature.rect.x, WORLD_RIGHT - creature.rect.width))
            creature.rect.y = max(WORLD_TOP, min(creature.rect.y, WORLD_BOTTOM - creature.rect.height))
            creature.update_effects()
            creature.update_hover((mx, my))
            creature.satisfaction_level = max(
                0,
                creature.satisfaction_level - creature.satisfaction_decay
            )
            creature.x, creature.y = creature.rect.center

        if self.creatures and all(c.satisfaction_level <= 0 for c in self.creatures):
            if self.game_continue:
                self.game_continue = False
                log(1, "All creatures reached 0 satisfaction. Game over.")
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass


    def draw(self, screen: pygame.Surface):
        screen.blit(self.background, (0, 0))
        self.global_bar.draw(screen, self.creatures)

        # Always draw hamburger
        self.hamburger_btn.draw(screen)

        self.toolbar.draw(screen)
        self.toggle_toolbar_btn.draw(screen)

        for creature in self.creatures:
            if 100 >= creature.satisfaction_level > 70:
                creature.update_sprite(0)
            elif 70 >= creature.satisfaction_level > 30:
                creature.update_sprite(1)
            elif 30 >= creature.satisfaction_level > 0:
                creature.update_sprite(2)
            else:
                creature.update_sprite(3)
            creature.draw(screen)

        if self.master_visible:
            for buttons in self.master_buttons:
                buttons.draw(screen)

        if self.admin_mode:
            for input_field in self.inputs:
                input_field.draw(screen)

        if self.is_market_open:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            pygame.draw.rect(screen, (200, 171, 131), (50, 50, 700, 400), border_radius=12)
            pygame.draw.rect(screen, (255, 255, 255), (50, 50, 700, 400), width=3, border_radius=12)

            font = pygame.font.Font(None, 28)
            title = font.render("Marketplace", True, (0, 0, 0))
            screen.blit(title, (310, 80))

            base_x = 100
            base_y = 100
            col_spacing = 200
            row_spacing = 120

            for idx, item in enumerate(self.market_items):
                col = idx % 3
                row = idx // 3

                x = base_x + col * col_spacing
                y = base_y + row * row_spacing

                # Draw icon
                if item["icon"]:
                    icon = pygame.transform.scale(item["icon"], (64, 64)) # type: ignore
                    screen.blit(icon, (x, y + 5))

                # Draw name
                name_text = font.render(item["name"], True, (0, 0, 0)) # type: ignore
                screen.blit(name_text, (x + 80, y + 20))

                for btn in self.market_buttons:
                    btn.draw(screen)

        if self.is_paused:
            overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            for b in self.pause_menu_buttons:
                b.draw(screen)

class FlappyBirdScene(GameScene):
    def __init__(self, screen : pygame.Surface, slot):
        super().__init__("Flappy Bird MiniGame")
        self.screen = screen
        self.flappy = FlappyBird(screen, width=screen.get_width(), height=screen.get_height())
        self.running = True
        self.slot = slot

    def handle_event(self, event : pygame.event.Event):
        self.flappy.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.running = False

    def update(self):
        self.flappy.update()

        if self.flappy.finished:
            self.money.add_money(self.flappy.score)
            print(self.money.money)
            import main
            main.current_scene = None
            print(self.slot)
            main.start_loaded_game(f"{self.slot}.json")
            return self.money

    def draw(self, screen: pygame.Surface):
        if self.running:
            # Draw the flappy game first
            self.flappy.draw(screen)

            font = pygame.font.Font(None, 28)

            # Build the text showing current score; FlappyBird exposes `score`
            score_text = f"Score: {int(getattr(self.flappy, 'score', 0))}"

            # Create a Text widget and draw it (x, y, w, h, font, text, bg_color, text_color)
            score_label = None
            try:
                # use the project's Text class from game_manager
                from game_manager import Text
                score_label = Text(10, 10, 140, 36, font, score_text, "#000000", "#ffffff")
            except Exception:
                # Fallback: render directly with pygame if Text import or construction fails
                txt_surf = font.render(score_text, True, (255, 255, 255))
                screen.blit(txt_surf, (10, 10))

            if score_label:
                score_label.draw(screen)
