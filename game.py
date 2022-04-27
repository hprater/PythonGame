import pygame
import time

from pygame.locals import *
from time import sleep


class Model:
    def __init__(self):
        self.dest_x = 0
        self.dest_y = 0
        self.character = Character(0, 0)
        self.sprites = []
        # self.lettuce = Lettuce(500, 500)
        # self.sprites.append(self.lettuce)
        self.sprites.append(self.character)

    def update(self):
        if self.rect.left < self.dest_x:
            self.rect.left += 2
        if self.rect.left > self.dest_x:
            self.rect.left -= 2
        if self.rect.top < self.dest_y:
            self.rect.top += 2
        if self.rect.top > self.dest_y:
            self.rect.top -= 2

    def set_dest(self, pos):
        self.dest_x = pos[0]
        self.dest_y = pos[1]


class View:
    def __init__(self, model):
        screen_size = (800, 600)
        self.screen = pygame.display.set_mode(screen_size, 32)  # main pygame surface
        # pygame optimized image with convert (but removes transparency)
        self.character_image = pygame.image.load("images/link-down1.png").convert()
        pygame.Surface.set_colorkey(self.character_image, [0, 0, 0])  # makes the black from convert transparent again
        self.model = model
        self.model.rect = self.character_image.get_rect()

    def update(self):
        self.screen.fill([0, 200, 100])
        self.screen.blit(self.character_image, self.model.rect)
        pygame.display.flip()


class Controller:
    def __init__(self, model):
        self.model = model
        self.keep_going = True

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False
            elif event.type == pygame.MOUSEBUTTONUP:
                self.model.set_dest(pygame.mouse.get_pos())
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.model.dest_x -= 1
        if keys[K_RIGHT]:
            self.model.dest_x += 1
        if keys[K_UP]:
            self.model.dest_y -= 1
        if keys[K_DOWN]:
            self.model.dest_y += 1


class Sprite:
    def __init__(self, xPos, yPos, width, height, im):
        self.x = xPos
        self.y = yPos
        self.w = width
        self.h = height
        self.image = pygame.image.load(im)


class Character(Sprite):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, 80, 59, "images/link-down1.png")  # xPos, yPos, 80, 59, "turtle.png"
        # self.x = xPos
        # self.y = yPos
        # self.w = 80
        # self.h = 59
        # self.image = pygame.image.load("turtle.png")


class Brick(Sprite):
    def __init__(self, xPos, yPos):
        super(Brick, self).__init__(xPos, yPos, 100, 100, "images/brick.png")


print("Use the arrow keys to move. Press Esc to quit.")
pygame.init()
m = Model()
v = View(m)
c = Controller(m)
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.04)
print("Goodbye")
