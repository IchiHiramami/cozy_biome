# --------------------------------------------------------------
# Contained here are classes and methods related to UI and Menus
# --------------------------------------------------------------

import pygame
from collections.abc import Callable

def hex_to_rgb(hex_color : str) -> tuple[int, int, int]:
    """
    Allows for all the functions to be able to take HEX values instead of just RGB
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Hex color must be 6 characters long.")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

class Button:
    def __init__(self, xpos : int, ypos : int, wid : int | float, hei : int | float, 
                 font : pygame.font.Font, 
                 text : str,
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
        """Return a bool value if mouse is clicked"""
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
            self.history.append(menu) #store to history
        self.menus = [menu]

    def back(self):
        """Return to previously removed Menu"""
        if self.history:
            restored = self.history.pop()
            self.menus.append(restored)

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
    def __init__(self, background: str, buttons: list[Button], input_fields: list[InputField], bg_manager: BackgroundManager):
        super().__init__(background, buttons, bg_manager)
        self.input_fields = input_fields
        self.labels = ["World Name"] 

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
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
    
