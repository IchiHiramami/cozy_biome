import pygame #type: ignore
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
                 on_click : Callable[[], None] | None = None
                 ):
        
        self.rect = pygame.Rect(xpos, ypos, wid, hei)
        self.color = base_color if isinstance(base_color, tuple) else hex_to_rgb(base_color)
        self.hover_color = on_hover_color if isinstance(on_hover_color, tuple) else hex_to_rgb(on_hover_color)
        self.text_color = text_color if isinstance(text_color, tuple) else hex_to_rgb(text_color)
        self.text = text
        self.font = font
        if on_click:
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

class Menu:
    def __init__(self, background : pygame.Surface, buttons : list[Button]):
        self.background = background
        self.buttons = buttons

    def draw(self, screen : pygame.Surface):
        screen.blit(self.background, (0, 0))

        for button in self.buttons:
            button.draw(screen)

    def handle_event(self, event : pygame.event.Event):
        for button in self.buttons:
            button.handle_event(event)