from classes import Button
import pygame

def new_game():
    pass #TODO: put the log here

def load_game():
    pass #TODO: put the log here (or maybe in the log.py file)

def quit_game():
    #TODO: log here quit before quitting
    pygame.quit()
    exit()

pygame.font.init()
font = pygame.font.Font(None, 40)

new_game_btn = Button(300, 200, 200, 60, font, "New Game", "c8ab83", "eec584", "ffffff")
load_game_btn = Button(300, 300, 200, 60, font, "Load Game", "c8ab83", "eec584", "ffffff")  
quit_btn     = Button(300, 400, 200, 60, font, "Quit Game", "c8ab83", "eec584", "ffffff", on_click = quit_game)

home_screen_buttons = [new_game_btn, load_game_btn, quit_btn]