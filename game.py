# Zelda Game Python
# Hayden Prater

# easier to reference to pygame
import pygame as pg
import json
import os

from pygame.locals import *
from time import sleep

# Game constant
SCREEN_RECT = pg.Rect(0, 0, 800, 600)

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    file = os.path.join(main_dir, "images", file)
    try:
        # pygame optimized image with convert (but removes transparency)
        surface = pg.image.load(file).convert()
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    surface.set_colorkey([0, 0, 0])
    return surface.convert()


class View:
    def __init__(self, model):
        screen_size = (800, 600)
        self.screen = pg.display.set_mode(screen_size, 32)  # main pygame surface
        self.character_image = load_image("link-down1.png")
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


class Model:
    rooms = {}
    activeRoom = None

    def __init__(self, map_json):
        # Preload the images, so we aren't doing it for every instance of the class.
        Character.left_images = [load_image(im) for im in ("link-left1.png", "link-left2.png", "link-left3.png",
                                                           "link-left4.png", "link-left5.png")]
        Character.right_images = [load_image(im) for im in ("link-right1.png", "link-right2.png", "link-right3.png",
                                                            "link-right4.png", "link-right5.png")]
        Character.up_images = [load_image(im) for im in ("link-up1.png", "link-up2.png", "link-up3.png",
                                                         "link-up4.png", "link-up5.png")]
        Character.down_images = [load_image(im) for im in ("link-down1.png", "link-down2.png", "link-down3.png",
                                                           "link-down4.png", "link-down5.png")]
        Brick.images = [load_image("brick.png")]
        Boomerang.images = [load_image(im) for im in ("boomerang1.png", "boomerang2.png", "boomerang3.png",
                                                      "boomerang4.png")]
        Pot.images = [load_image("pot.png")]
        BrokenPot.images = [load_image("pot_broken.png")]
        # Initialize Game Groups
        bricks = pg.sprite.Group()
        pots = pg.sprite.Group()
        broken = pg.sprite.Group()
        boomerangs = pg.sprite.Group()
        everyone = pg.sprite.RenderUpdates()

        # assign default groups to each sprite class
        Character.containers = everyone
        Brick.containers = bricks, everyone
        Pot.containers = pots, everyone
        Boomerang.containers = boomerangs, everyone
        BrokenPot.containers = everyone, broken

        for room in map_json["rooms"]:
            self.rooms[room["name"]] = Room(room)
        self.activeRoom = self.rooms[map_json["activeRoom"]]
        self.dest_x = 0
        self.dest_y = 0
        self.character = Character(0, 0)

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
        for sprite in self.activeRoom.sprites:
            sprite.update()

    def set_dest(self, pos):
        self.dest_x = pos[0]
        self.dest_y = pos[1]


class Room:
    sprites = []

    def __init__(self, room_json):
        for brick in room_json["bricks"]:
            self.sprites.append(Brick(brick["x"], brick["y"]))
        for pot in room_json["pots"]:
            self.sprites.append(Pot(pot["x"], pot["y"]))


class Sprite(pg.sprite.Sprite):
    images = []

    def __init__(self, x_pos, y_pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.x = x_pos
        self.y = y_pos


class Character(Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        pass


class Brick(Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        pass


class Pot(Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        pass


class BrokenPot(Sprite):
    def __init__(self, actor):
        super.__init__(actor.rect.x, actor.rect.y)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = 20

    def update(self):
        self.life = self.life - 1
        if self.life <= 0:
            self.kill()


class Boomerang(Sprite):
    speed = 15

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.direction = actor.direction

    def update(self):
        if self.direction is not None:
            self.rect.move_ip(self.direction * self.speed, 0)
            self.rect = self.rect.clamp(SCREEN_RECT)


print("Use the arrow keys to move. Press Esc to quit.")
pg.init()
file = open(os.path.join(main_dir, 'map.json'))
map_js = json.load(file)
best_depth = pg.display.mode_ok(SCREEN_RECT.size, 32, 32)
screen = pg.display.set_mode(SCREEN_RECT.size, 32, best_depth)

m = Model(map_js)
v = View(m)
c = Controller(m)
while c.keep_going:
    c.update()
    m.update()
    v.update()
    sleep(0.04)
print("Goodbye")
