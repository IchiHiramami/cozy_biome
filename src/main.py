import pygame
from class1 import Dock

pygame.init()
screen = pygame.display.set_mode((800, 600))
dock = Dock(screen)
dock.add_button("Start", (20, 20))
dock.add_button("Exit", (140, 20))

clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        dock.handle_event(event)

    screen.fill((30, 30, 30))
    dock.draw()
    pygame.display.flip()
    clock.tick(60)