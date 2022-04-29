# Zelda Game Python
# Hayden Prater

# easier to reference to pygame
import pygame as pg
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN
import time
import json
import os

from pygame.locals import *
from time import sleep

# Game constant
# SCREENRECT = pg.Rect(0, 0, 800, 600)

main_dir = os.path.split(os.path.abspath(__file__))[0]
dir = {K_LEFT: (-1, 0), K_RIGHT: (1, 0), K_UP: (0, -1), K_DOWN: (0, 1)}
anti_dir = {K_LEFT: (1, 0), K_RIGHT: (-1, 0), K_UP: (0, 1), K_DOWN: (0, -1)}


def load_image(file):
    file = os.path.join(main_dir, "images", file)
    try:
        # pygame optimized image with convert (but removes transparency)
        surface = pg.image.load(file).convert()
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    surface.set_colorkey([0, 0, 0])
    return surface.convert()


def load_map():
    file = open(os.path.join(main_dir, 'map.json'))
    try:
        data = json.load(file)
    except pg.error:
        raise SystemExit('Could not load data "%s" %s' % (file, pg.get_error()))
    print(data["rooms"][0]["bricks"])  # For viewing what is in a room.
    for brick in data["rooms"][0]["bricks"]:
        Brick(brick["x"], brick["y"])
    for pot in data["rooms"][0]["pots"]:
        Pot(pot["x"], pot["y"])


class Model:
    def __init__(self):
        self.dest_x = 0
        self.dest_y = 0
        self.character = Character(0, 0)
        self.sprites = []
        # self.rooms = []
        # self.activeRoomName = "R0"
        self.sprites.append(self.character)
        # self.roomJson = json["rooms"]
        # for i in range(len(self.roomJson)):
        #     self.rooms.append(self.roomJson[i])

        # self.wireRooms()
        # self.activeRoom = self.rooms.get(self.activeRoomName)
        # self.zelda = Character.json["character"]
        # self.activeRoom.sprites.push(self.zelda)

        # def wireRooms():
        #     self.theRooms = self.rooms
        #     self.rooms.forEach(function(value, key)
        #     switch(key)
        #     case"R0":
        #         value.connectingRooms.set("right", theRooms.get("R1"));
        #         value.connectingRooms.set("down", theRooms.get("R2"));
        #         break;
        #     case"R1":
        #         value.connectingRooms.set("left", theRooms.get("R0"));
        #         break;
        #     case "R2":
        #         value.connectingRooms.set("up", theRooms.get("R0"));
        #         value.connectingRooms.set("down", theRooms.get("R3"));
        #         break;
        #     case"R3":
        #         value.connectingRooms.set("up", theRooms.get("R2"));
        #         value.connectingRooms.set("right", theRooms.get("R4"));
        #         break;
        #     case"R4":
        #         value.connectingRooms.set("left", theRooms.get("R3"));
        #         break;

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
        self.screen = pg.display.set_mode(screen_size, 32)  # main pygame surface
        self.character_image = load_image("link-down1.png")
        pg.Surface.set_colorkey(self.character_image, [0, 0, 0])  # makes the black from convert transparent again
        self.model = model
        self.model.rect = self.character_image.get_rect()

    def update(self):
        self.screen.fill([0, 200, 100])
        self.screen.blit(self.character_image, self.model.rect)
        pg.display.flip()


class Controller:
    def __init__(self, model):
        self.model = model
        self.keep_going = True

    def update(self):
        for event in pg.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False
            elif event.type == pg.MOUSEBUTTONUP:
                self.model.set_dest(pg.mouse.get_pos())
        keys = pg.key.get_pressed()
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
        self.image = pg.image.load(im)


class Character(Sprite):
    def __init__(self, xPos, yPos):
        super().__init__(xPos, yPos, 80, 59, "images/link-down1.png")


class Brick(Sprite):
    def __init__(self, xPos, yPos):
        super(Brick, self).__init__(xPos, yPos, 100, 100, "images/brick.png")


class Pot(Sprite):
    def __init__(self, xPos, yPos):
        super(Pot, self).__init__(xPos, yPos, 100, 100, "images/boomerang1.png")


print("Use the arrow keys to move. Press Esc to quit.")
pg.init()
m = Model()
v = View(m)
c = Controller(m)
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.04)
print("Goodbye")
