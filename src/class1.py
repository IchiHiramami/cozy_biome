import pygame
from typing import Any

class Dock: 
    def __init__(self,
                window : pygame.Surface, 
                height : int = 100, 
                color : tuple[int, int, int] = (50, 50, 70)
                ):
        
        self.window = window
        self.height = height
        self.color = color
        self.rect = pygame.Rect(0, window.get_height() - height, window.get_width(), height)
        self.buttons: list[dict[str, Any ]] = []

    def add_button(self, 
                    text : str, 
                    pos : tuple[int, int], 
                    size : tuple [int,int] = (100, 40), 
                    color : tuple[int, int, int] = (200, 80, 80)
                    ):
        rect = pygame.Rect(pos[0], self.rect.top + pos[1], size[0], size[1])
        self.buttons.append({"text": text, "rect": rect, "color": color})

    def draw(self):
        pygame.draw.rect(self.window, self.color, self.rect)
        font = pygame.font.SysFont(None, 24)
        for btn in self.buttons:
            pygame.draw.rect(self.window, btn["color"], btn["rect"])
            text_surf = font.render(btn["text"], True, (255, 255, 255))
            self.window.blit(text_surf, text_surf.get_rect(center=btn["rect"].center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn["rect"].collidepoint(event.pos):
                    print(f"Button {btn['text']} clicked!")
                    return btn["text"]
        return None
