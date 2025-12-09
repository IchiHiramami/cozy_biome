import pygame, random, time
from pygame.locals import *

# reference: minigames/flappybird.py

SPEED = 5
GRAVITY = 0.4
GAME_SPEED = 2
GROUND_WIDHT = 2 * 800
GROUND_HEIGHT = 100
PIPE_WIDHT = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.image.load('assets/flappybird/assets/sprites/bluebird-midflap.png').convert_alpha()

        self.speed = SPEED
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = 800 / 6
        self.rect.y = 600 / 2

    def update(self):
        self.speed += GRAVITY
        self.rect.y += self.speed

    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        super().__init__()

        img = pygame.image.load('assets/flappybird/assets/sprites/pipe-green.png').convert_alpha()
        img = pygame.transform.scale(img, (PIPE_WIDHT, PIPE_HEIGHT))

        if inverted:
            img = pygame.transform.flip(img, False, True)

        self.image = img
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = xpos

        if inverted:
            self.rect.y = -(self.rect.height - ysize)
        else:
            self.rect.y = 600 - ysize


    def update(self, game_speed):
        self.rect.x -= game_speed

class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        super().__init__()

        img = pygame.image.load('assets/flappybird/assets/sprites/base.png').convert_alpha()
        img = pygame.transform.scale(img, (GROUND_WIDHT, GROUND_HEIGHT))

        self.image = img
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = 600 - GROUND_HEIGHT

    def update(self):
        self.rect.x -= GAME_SPEED

# HELPER FUNCTIONS

def is_off_screen(sprite):
    return sprite.rect.x < -(sprite.rect.width)

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe_bottom = Pipe(False, xpos, size)
    pipe_top = Pipe(True, xpos, 600 - size - PIPE_GAP)
    pipe_top.scored = False
    pipe_bottom.scored = False
    return pipe_bottom, pipe_top

# MAIN WRAPPER CLASS FOR GAME LOOP

class FlappyBird:
    """
    Wraps the minigame into update()/draw() methods so your main loop can call:
        flappy.update()
        flappy.draw(screen)
    """

    def __init__(self, screen, width=800, height=600):
        self.screen = screen
        self.surface = pygame.Surface((800, 600))  # internal game screen


        # background
        self.background = pygame.image.load('assets/flappybird/assets/sprites/background-day.png')
        self.background = pygame.transform.scale(self.background, (800, 600))


        # create sprite groups
        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_group.add(self.bird)

        self.ground_group = pygame.sprite.Group()
        for i in range(2):
            self.ground_group.add(Ground(GROUND_WIDHT * i))

        self.pipe_group = pygame.sprite.Group()
        for i in range(2):
            p1, p2 = get_random_pipes(800 * i + 800)
            self.pipe_group.add(p1, p2)

        self.clock = pygame.time.Clock()
        self.state = "menu"   # menu → running → dead
        self.game_speed = GAME_SPEED   # starting scroll speed
        self.speed_increase = 0.01
        self.score = 0
        self.finished = False

    # UPDATE
    def update(self):
        self.game_speed += self.speed_increase


        if self.state == "menu":
            self.menu_update()
        elif self.state == "running":
            self.game_update()
        elif self.state == "dead":
            self.finished = True

    # DRAW
    def draw(self, screen : pygame.Surface):
        screen.blit(self.surface, (0, 0))

    # MENU STATE
    def menu_update(self):
        self.surface.blit(self.background, (0, 0))

        self.bird_group.draw(self.surface)

        self.ground_group.update()
        self.ground_group.draw(self.surface)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            self.state = "running"

    # GAME RUNNING STATE
    def game_update(self):
        self.surface.blit(self.background, (0, 0))

        # ground looping
        if is_off_screen(self.ground_group.sprites()[0]):
            g = Ground(GROUND_WIDHT - 20)
            self.ground_group.remove(self.ground_group.sprites()[0])
            self.ground_group.add(g)

        # pipes looping
        if is_off_screen(self.pipe_group.sprites()[0]):
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])

            p1, p2 = get_random_pipes(800 * 2)
            self.pipe_group.add(p1, p2)

        for pipe in self.pipe_group:
            if not pipe.scored and pipe.rect.right < self.bird.rect.left:
                pipe.scored = True
                self.score += 0.5

        # updates
        self.bird_group.update()
        self.pipe_group.update(self.game_speed)
        self.ground_group.update()

        # draw
        self.bird_group.draw(self.surface)
        self.pipe_group.draw(self.surface)
        self.ground_group.draw(self.surface)

        # collision
        if (pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask)
            or pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask)):
            pygame.mixer.music.load("assets/Music/HomeScene_music.mp3")
            pygame.mixer.music.play(-1)
            self.state = "dead"

    def handle_event(self, event: pygame.event.Event):
        """Handle user input for the bird"""
        if event.type == pygame.KEYDOWN: 
            if event.key in (pygame.K_SPACE, pygame.K_UP):
                self.bird.bump()  # This makes the bird flap
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self.bird.bump()  # This makes the bird flap