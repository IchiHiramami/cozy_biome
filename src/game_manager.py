# --------------------------------------------------------------
# Contained here are classes and methods related to UI and Menus
# --------------------------------------------------------------

import pygame
from classes import Food, Cleanse, Potion
from collections.abc import Callable
from typing import Any
from non_essential import hex_to_rgb

class InfoBox:
    def __init__(self, xpos : int, ypos : int, wid : int | float, hei : int | float, 
                 font : pygame.font.Font, 
                 text : str | None,
                 base_color : tuple[int, int, int] |str ,
                 text_color : tuple[int, int, int] | str,
                 ):
        
        self.rect = pygame.Rect(xpos, ypos, wid, hei)
        self.color = base_color if isinstance(base_color, tuple) else hex_to_rgb(base_color)
        self.text_color = text_color if isinstance(text_color, tuple) else hex_to_rgb(text_color)
        self.text = text
        self.font = font

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)

        if not self.text:
            return

        lines = self.text.split("\n")
        line_height = self.font.get_height()
        total_height = line_height * len(lines)

        start_y = self.rect.centery - total_height // 2

        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, start_y + i * line_height))
            surface.blit(text_surf, text_rect)
            
    def handle_event(self, event : pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return False

class Button:
    def __init__(self, xpos : int, ypos : int, wid : int | float, hei : int | float, 
                 font : pygame.font.Font, 
                 text : str | None,
                 # dev's note: color args can either be in hex <#str> or RGB <(rr,gg,bb)>
                 base_color : tuple[int, int, int] |str ,
                 on_hover_color : tuple[int, int, int] | str,
                 text_color : tuple[int, int, int] | str,
                 # function callback
                 on_click : Callable[[], None]
                 ):
        
        self.rect = pygame.Rect(xpos, ypos, wid, hei)
        self.color = base_color if isinstance(base_color, tuple) else hex_to_rgb(base_color)
        self.hover_color = on_hover_color if isinstance(on_hover_color, tuple) else hex_to_rgb(on_hover_color)
        self.text_color = text_color if isinstance(text_color, tuple) else hex_to_rgb(text_color)
        self.text = text
        self.font = font
        self.on_click = on_click
        self.hovered = False

    def draw(self, surface : pygame.Surface):
        """
        Draws button state depending the mouse position hover
        """
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)

        button_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(surface, button_color, self.rect, border_radius = 5)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center = self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event : pygame.event.Event):
        """Button handles"""
        mx, my = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mx, my)
        self.hovered = hovered

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

class InputField:
    def __init__(self, xpos : int, ypos : int, wid : int | float, hei : int | float, font : pygame.font.Font):
        self.rect = pygame.Rect(xpos, ypos, wid, hei)
        self.font = font
        self.text = ""
        self.active = False

    def draw(self, screen : pygame.Surface):
        pygame.draw.rect(screen, (255,255,255), self.rect, 2)
        txt = self.font.render(self.text, True, (255,255,255))
        screen.blit(txt, (self.rect.x + 5, self.rect.y + 5))

    def handle_event(self, event : pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos) # true if the field in being interacted


        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    
    def return_input(self) -> str:
        return self.text
        
class Text:
    def __init__(self, xpos: int, ypos: int, wid: int | float, hei: int | float, font: pygame.font.Font,
                 text: str,
                 bg_color: tuple[int, int, int] | str,
                 text_color: tuple[int, int, int] | str,
                 should_draw: bool = True):
        self.rect = pygame.Rect(xpos, ypos, wid, hei)
        self.text = text
        self.font = font
        self.bg_color = bg_color if isinstance(bg_color, tuple) else hex_to_rgb(bg_color)
        self.text_color = text_color if isinstance(text_color, tuple) else hex_to_rgb(text_color)
        self.should_draw = should_draw

    def draw(self, screen : pygame.Surface):
        if self.should_draw:
            pygame.draw.rect(screen, self.bg_color, self.rect)
            text_surf = self.font.render(self.text, True, self.text_color)
            text_rect = text_surf.get_rect(center=self.rect.center)  # center in the rectangle
            screen.blit(text_surf, text_rect)
        else: return

class BackgroundManager:
    def __init__(self, wid : int = 800, hei : int = 600):
        self.width = wid
        self.height = hei
        self.current : pygame.Surface | None = None

    def load(self, filename : str):
        bg = pygame.image.load(filename).convert()
        self.current = pygame.transform.scale(bg, (self.width, self.height))

    def draw(self, screen: pygame.Surface):
        if self.current:
            screen.blit(self.current, (0,0))

class Menu:
    def __init__(self, background_file: str, buttons: list[Button], bg_manager: BackgroundManager):
        self.buttons = buttons
        self.bg_file = background_file
        self.bg_manager = bg_manager

    def activate(self):
        self.bg_manager.load(self.bg_file)

    def draw(self, screen: pygame.Surface):
        self.bg_manager.draw(screen)
        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event : pygame.event.Event):
        for button in self.buttons:
            button.handle_event(event)

class MenuManager:
    def __init__(self):
        self.menus : list[Menu] = []
        self.history : list[Menu] = []

    def push(self, menu : Menu):
        """Overlay menu on top of another menu"""
        self.menus.append(menu)

    def pop_menu(self):
        """Remove menu from list of menus, stores to history"""
        if self.menus:
            removed = self.menus.pop()
            self.history.append(removed)
    
    def switch(self, menu: Menu):
        """Replace Menu with a new Menu"""
        if self.menus:
            self.history.append(self.menus[-1]) #store to history
        self.menus = [menu]

    def back(self):
        """Return to previously removed Menu"""
        if self.history:
            restored = self.history.pop()
            self.menus = [restored]

    @property
    def current(self):
        return self.menus[-1] if self.menus else None

    def handle_event(self, event : pygame.event.Event):
        if self.current:
            self.current.handle_event(event)

    def draw(self, screen : pygame.Surface):
        for menu in self.menus:
            menu.draw(screen)

class GameSetupMenu(Menu):
    def __init__(self, background: str, buttons: list[Button], input_fields: list[InputField], bg_manager: BackgroundManager, texts :list[Text] = []):
        super().__init__(background, buttons, bg_manager)
        self.input_fields = input_fields
        self.labels = ["World Name"]
        self.texts = texts

    def draw(self, screen: pygame.Surface):
        super().draw(screen)

        for t in self.texts:
            t.draw(screen)


        if self.input_fields:
            for i, field in enumerate(self.input_fields):
                label_surf = field.font.render(self.labels[i], True, hex_to_rgb('ffffff'))
                screen.blit(label_surf, (field.rect.x, field.rect.y - 30))
                field.draw(screen)

    def handle_event(self, event: pygame.event.Event):
        super().handle_event(event)
        if self.input_fields:
            for field in self.input_fields:
                field.handle_event(event)

    def get_values(self):
        """Return dict of all input field values"""
        return {f"field_{i}": field.text for i, field in enumerate(self.input_fields)}
    
class InventorySlot:
    def __init__(
        self,
        x: int,
        y: int,
        size: int,
        item_name: str | None = None,
        icon: pygame.Surface | None = None,
        bg_color: str = "#c8ab83",
        border_color: str = "#ffffff",
        on_click: Callable[[str], None] | None = None
    ) -> None:
        
        self.rect: pygame.Rect = pygame.Rect(x, y, size, size)

        # Item identity (string only)
        self.item_name = item_name
        self.icon = icon

        # Callback when clicked
        self.on_use = on_click

        # UI state
        self.hovered: bool = False
        self.bg_color: tuple[int, int, int] = hex_to_rgb(bg_color)
        self.border_color: tuple[int, int, int] = hex_to_rgb(border_color)

        # Displayed quantity (synced from Inventory)
        self.quantity: int = 0

        # Font
        self.font: pygame.font.Font = pygame.font.Font(None, 18)
        self.item: Food | Potion | Cleanse | None = None

    def clear(self):
        """Clear item image from slot"""
        self.icon = None

    def handle_event(self, event : pygame.event.Event):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.on_use:
                    self.on_use(self.item_name)
                return True
        return False

    def draw(self, screen : pygame.Surface, inventory: Any):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=6)
        pygame.draw.rect(screen, self.border_color, self.rect, width=2, border_radius=6)

        if self.hovered:
            pygame.draw.rect(screen, hex_to_rgb("#f2ff00"), self.rect, width=2, border_radius=6)
        # Draw icon
        if self.icon:
            if self.quantity > 0:
                icon = pygame.transform.scale(self.icon, (self.rect.width - 8, self.rect.height - 8))
                screen.blit(icon, (self.rect.x + 4, self.rect.y + 4))

        # Get quantity from inventory
        if self.item_name in inventory.foods:
            self.quantity = inventory.foods[self.item_name]
        elif self.item_name in inventory.potions:
            self.quantity = inventory.potions[self.item_name]
        elif self.item_name in inventory.cleanse:
            self.quantity = inventory.cleanse[self.item_name]

        # Draw quantity
        if self.quantity > 0:
            text = self.font.render(str(self.quantity), True, (255, 255, 255))
            screen.blit(text, (self.rect.right - text.get_width() - 4,
                            self.rect.bottom - text.get_height() - 2))

class Toolbar:
    """
    IFYKYK
    """
    def __init__(self, x: int, y : int , width : int, height : int, bg_color : tuple[int, int,int] | str, buttons : list[Button] | None = None, Text : list[Text] | None = None, tabs: list[dict] | None = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.parent_scene = None

        # Background color (hex or RGB)
        self.bg_color = bg_color if isinstance(bg_color, tuple) else hex_to_rgb(bg_color)

        self.buttons = buttons if buttons else []
        self.text = Text if Text else []

        # Tabs support: each tab is a dict with keys: 'name', 'buttons', 'elements'
        # Accepts a list of such dicts. If provided, toolbar becomes tabbed.
        self.tabs: list[dict[str, Any]] = tabs if tabs else []
        self.active_tab = 0

        # Create header buttons for tabs (lazily built)
        self._tab_header_buttons: list[Button] = []

        # Default font for tab headers
        self._tab_font = pygame.font.Font(None, 22)

        self.visible = True

        # If tabs provided, prepare header buttons
        if self.tabs:
            self._build_tab_headers()

    def _build_tab_headers(self):
        """Create small header Buttons for each tab to switch views."""
        self._tab_header_buttons =  []

        padding = 8
        width = 110
        height = 26

        header_y = 480
        header_x = self.rect.x + 10 + 40 + padding

        for i, tab in enumerate(self.tabs):
            name = tab.get('name', f'Tab {i}')

            def switch_onclick(idx : int):
                return lambda idx = idx: self.switch_tab(idx)
            
            btn = Button(
                header_x, header_y,
                width, height,
                self._tab_font,
                name,
                'c8ab83', 'eec584', 'ffffff',
                on_click = switch_onclick(i)
            )

            btn.active_bg = hex_to_rgb("bfa476")   # darker beige
            btn.inactive_bg = hex_to_rgb("c8ab83") # normal beige

            self._tab_header_buttons.append(btn)
            header_x += width + padding
            

    def add_tab(self, name: str, buttons: list[Button] | None = None, elements: list[object] | None = None):
        """Add a new tab to the toolbar."""
        self.tabs.append({'name': name, 'buttons': buttons if buttons else [], 'elements': elements if elements else []})
        self._build_tab_headers()

    def switch_tab(self, index: int):
        if 0 <= index < len(self.tabs):
            self.active_tab = index

    def add_button(self, button : Button):
        """Add a button to the legacy single-view toolbar (or current tab if tabbed)."""
        if self.tabs:
            self.tabs[self.active_tab]['buttons'].append(button)
        else:
            self.buttons.append(button)

    def add_element(self, element : object):
        """Add any drawable UI element (inventory slot, icon, etc.)."""
        if self.tabs:
            self.tabs[self.active_tab]['elements'].append(element)
        else:
            self.elements.append(element)

    def handle_event(self, event : pygame.event.Event):
        """Send events to toolbar components only if visible."""
        if not self.visible:
            return

        # If tabbed, send events to header buttons and active tab's components
        if self.tabs:
            for btn in self._tab_header_buttons:
                btn.handle_event(event)

            active = self.tabs[self.active_tab]
            for button in active.get('buttons', []):
                button.handle_event(event)
            for element in active.get('elements', []):
                if hasattr(element, "handle_event"):
                    element.handle_event(event)
            return

        # Legacy behavior
        for button in self.buttons:
            button.handle_event(event)

        for text in self.t:
            if hasattr(element, "handle_event"):
                element.handle_event(event)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the toolbar and all its components."""
        if not self.visible:
            return

        # Draw background rectangle
        pygame.draw.rect(screen, self.bg_color, self.rect)

        # If tabbed, draw headers and active tab contents
        if self.tabs:
            # Draw header buttons
            for i, btn in enumerate(self._tab_header_buttons):
                # highlight active
                if i == self.active_tab:
                    pygame.draw.rect(screen, btn.active_bg, btn.rect, border_radius=5)  # type: ignore
                else:
                    pygame.draw.rect(screen, btn.inactive_bg, btn.rect, border_radius=5)  # type: ignore

                btn.draw(screen)

            # Draw active tab contents
            active = self.tabs[self.active_tab]

            # ✅ Buttons (may include InventorySlot)
            for button in active.get('buttons', []):
                if isinstance(button, InventorySlot):
                    # Pass inventory from parent scene
                    button.draw(screen, self.parent_scene.inventory)
                else:
                    button.draw(screen)

            # ✅ Elements (may include InventorySlot)
            for element in active.get('elements', []):
                if hasattr(element, "draw"):
                    if isinstance(element, InventorySlot):
                        element.draw(screen, self.parent_scene.inventory)
                    else:
                        element.draw(screen)

            return

        # Draw inventory slots or other UI elements
        for element in self.Text:
            if hasattr(element, "draw"):
                if isinstance(element, InventorySlot):
                    element.draw(screen, self.parent_scene.inventory)
                else:
                    element.draw(screen)
            else:
                print("Element has no draw method:", element)
