# Zelda Game Python
# Hayden Prater

# easier to reference to pygame
import pygame as pg
import json
import os

from pygame.locals import *
from time import sleep

# Sound effects
pg.mixer.init()
break_sound = pg.mixer.Sound("sound/glass_shatter_c.wav")
boomerang_sound = pg.mixer.Sound("sound/golf_swing.wav")

# Game constant
SCREEN_RECT = pg.Rect(0, 0, 800, 600)
# 1 = right, 2 = left, 3 = down, 4 = up
ROOM_RIGHT = 1
ROOM_LEFT = 2
ROOM_DOWN = 3
ROOM_UP = 4
R0 = {ROOM_RIGHT: "R1", ROOM_DOWN: "R2"}
R1 = {ROOM_LEFT: "R0"}
R2 = {ROOM_DOWN: "R3", ROOM_UP: "R0"}
R3 = {ROOM_RIGHT: "R4", ROOM_UP: "R2"}
R4 = {ROOM_LEFT: "R3"}

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file_name, size):
    image_file = os.path.join(main_dir, "images", file_name)
    try:
        # pygame optimized image with convert (but removes transparency)
        image = pg.image.load(image_file)
        if size is not None:
            image = pg.transform.scale(image, size)
        surface = image.convert()
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (image_file, pg.get_error()))
    surface.set_colorkey([0, 0, 0])  # sets color to skip rendering (simulates transparency)
    return surface.convert()


class View:
    def __init__(self, model):
        screen_size = (800, 600)
        self.screen = pg.display.set_mode(screen_size, 32)  # main pygame surface
        self.model = model
        # self.model.rect = self.character_image.get_rect()

    def update(self):
        self.screen.fill([0, 200, 100])
        # self.screen.blit(self.character_image, self.model.rect)
        dirty = self.model.everyone.draw(self.screen)
        pg.display.update(dirty)
        pg.display.flip()


class Controller:
    def __init__(self, model):
        self.model = model
        self.keep_going = True

    def update(self):
        keys = pg.key.get_pressed()
        move = (0, 0)
        if keys[K_LEFT]:
            move = (move[0] - 1, move[1])
        if keys[K_RIGHT]:
            move = (move[0] + 1, move[1])
        if keys[K_UP]:
            move = (move[0], move[1] - 1)
        if keys[K_DOWN]:
            move = (move[0], move[1] + 1)
        self.model.character.move(move)
        for event in pg.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                self.keep_going = False
            if event.type == KEYDOWN and (event.key == K_RCTRL or event.key == K_LCTRL):
                self.model.create_boomerang(move)
        if self.model.character.rect.top == SCREEN_RECT.top:
            self.model.change_room(ROOM_UP)
        elif self.model.character.rect.bottom == SCREEN_RECT.bottom:
            self.model.change_room(ROOM_DOWN)
        elif self.model.character.rect.right == SCREEN_RECT.right:
            self.model.change_room(ROOM_RIGHT)
        elif self.model.character.rect.left == SCREEN_RECT.left:
            self.model.change_room(ROOM_LEFT)
        for pot in pg.sprite.spritecollide(self.model.character, self.model.pots, False):
            pot.move(move)
        for _ in pg.sprite.spritecollide(self.model.character, self.model.bricks, False):
            move = (-move[0], -move[1])
            self.model.character.move(move)
            move = (0, 0)
        for pot in pg.sprite.groupcollide(self.model.pots, self.model.bricks, True, False):
            self.model.create_broken_pot(pot)
        for pot in pg.sprite.groupcollide(self.model.pots, self.model.boomerangs, True, True):
            self.model.create_broken_pot(pot)
        for _ in pg.sprite.groupcollide(self.model.boomerangs, self.model.bricks, True, False):
            pass
        for _ in pg.sprite.spritecollide(self.model.character, self.model.broken, False):
            move = (-move[0], -move[1])
            self.model.character.move(move)
            move = (0, 0)


class Model:
    rooms = {}
    activeRoom = None

    def __init__(self, map_json):
        # Preload the images, so we aren't doing it for every instance of the class.
        Character.left_images = [load_image(im, (49, 49)) for im in
                                 ("link-left1.png", "link-left2.png", "link-left3.png",
                                  "link-left4.png", "link-left5.png")]
        Character.right_images = [load_image(im, (49, 49)) for im in
                                  ("link-right1.png", "link-right2.png", "link-right3.png",
                                   "link-right4.png", "link-right5.png")]
        Character.up_images = [load_image(im, (49, 49)) for im in ("link-up1.png", "link-up2.png", "link-up3.png",
                                                                   "link-up4.png", "link-up5.png")]
        Character.down_images = [load_image(im, (49, 49)) for im in
                                 ("link-down1.png", "link-down2.png", "link-down3.png",
                                  "link-down4.png", "link-down5.png")]
        Character.images.append(Character.down_images[0])
        Brick.images = [load_image("brick.png", (50, 50))]
        Boomerang.images = [load_image(im, None) for im in ("boomerang1.png", "boomerang2.png", "boomerang3.png",
                                                            "boomerang4.png")]
        Pot.images = [load_image("pot.png", (50, 50))]
        BrokenPot.images = [load_image("pot_broken.png", (50, 50))]
        # Initialize Game Groups
        self.bricks = pg.sprite.Group()
        self.pots = pg.sprite.Group()
        self.broken = pg.sprite.Group()
        self.boomerangs = pg.sprite.Group()
        self.everyone = pg.sprite.RenderUpdates()

        # assign default groups to each sprite class
        Character.containers = self.everyone
        Brick.containers = self.bricks, self.everyone
        Pot.containers = self.pots, self.everyone
        Boomerang.containers = self.boomerangs, self.everyone
        BrokenPot.containers = self.everyone, self.broken

        for room in map_json["rooms"]:
            self.rooms[room["name"]] = room
        self.activeRoom = Room(self.rooms[map_json["activeRoom"]])
        self.character = Character(75, 75)
        self.activeRoom.sprites.append(self.character)

    def update(self):
        for sprite in self.activeRoom.sprites:
            sprite.update()

    def create_broken_pot(self, actor):
        self.activeRoom.sprites.append(BrokenPot(actor))

    def create_boomerang(self, direction):
        self.activeRoom.sprites.append(Boomerang(self.character, self.character.last_move))

    def change_room(self, direction):
        if self.activeRoom.name == "R0":
            if direction in R0:
                new_room_name = R0[direction]
        elif self.activeRoom.name == "R1":
            if direction in R1:
                new_room_name = R1[direction]
        elif self.activeRoom.name == "R2":
            if direction in R2:
                new_room_name = R2[direction]
        elif self.activeRoom.name == "R3":
            if direction in R3:
                new_room_name = R3[direction]
        elif self.activeRoom.name == "R4":
            if direction in R4:
                new_room_name = R4[direction]
        else:
            return
        for sprite in self.activeRoom.sprites:
            if sprite != self.character:
                sprite.kill()
        print('New Room : %s' % self.rooms[new_room_name]["name"])
        self.activeRoom = Room(self.rooms[new_room_name])
        if direction == ROOM_RIGHT:
            self.character.rect.left = SCREEN_RECT.left
        elif direction == ROOM_LEFT:
            self.character.rect.right = SCREEN_RECT.right
        elif direction == ROOM_DOWN:
            self.character.rect.top = SCREEN_RECT.top
        elif direction == ROOM_UP:
            self.character.rect.bottom = SCREEN_RECT.bottom


class Room:
    name = None
    sprites = []

    def __init__(self, room_json):
        self.name = room_json["name"]
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
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(x_pos, y_pos))


class Character(Sprite):
    left_images = None
    up_images = None
    right_images = None
    down_images = None
    speed = 5
    last_move = (1, 0)
    current_direction = (0, 0)
    animation_frames = 0
    ANIMATION_MAX = 12
    ANIMATION_DIVISOR = 3

    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        if self.animation_frames < self.ANIMATION_MAX:
            self.animation_frames += 1
        else:
            self.animation_frames = 0
        if self.current_direction[0] > 0:
            self.image = Character.right_images[self.animation_frames // self.ANIMATION_DIVISOR]
        elif self.current_direction[0] < 0:
            self.image = Character.left_images[self.animation_frames // self.ANIMATION_DIVISOR]
        elif self.current_direction[1] > 0:
            self.image = Character.down_images[self.animation_frames // self.ANIMATION_DIVISOR]
        elif self.current_direction[1] < 0:
            self.image = Character.up_images[self.animation_frames // self.ANIMATION_DIVISOR]

    def move(self, direction):
        if direction != (0, 0):
            self.last_move = direction
        self.current_direction = direction
        self.rect.move_ip(direction[0] * self.speed, direction[1] * self.speed)
        self.rect = self.rect.clamp(SCREEN_RECT)


class Brick(Sprite):
    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        pass


class Pot(Sprite):
    speed = 7
    direction = None

    def __init__(self, x_pos, y_pos):
        super().__init__(x_pos, y_pos)

    def update(self):
        if self.direction is not None:
            self.rect.move_ip(self.direction[0] * self.speed, self.direction[1] * self.speed)
            self.rect = self.rect.clamp(SCREEN_RECT)

    def move(self, direction):
        self.direction = direction


class BrokenPot(Sprite):
    containers = []

    def __init__(self, actor):
        super().__init__(actor.rect.x, actor.rect.y)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = 20
        pg.mixer.Sound.play(break_sound)

    def update(self):
        self.life = self.life - 1
        if self.life <= 0:
            self.kill()


class Boomerang(Sprite):
    speed = 9
    direction = (0, 0)
    animation_frames_b = 0
    ANIMATION_MAX_B = 6
    ANIMATION_DIVISOR_B = 2

    def __init__(self, actor, movement):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[1]  #
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.direction = movement
        pg.mixer.Sound.play(boomerang_sound)

    def update(self):
        if self.rect.top == SCREEN_RECT.top or self.rect.bottom == SCREEN_RECT.bottom \
                or self.rect.right == SCREEN_RECT.right or self.rect.left == SCREEN_RECT.left:
            self.kill()
        else:
            self.rect.move_ip(self.direction[0] * self.speed, self.direction[1] * self.speed)
        if self.animation_frames_b < self.ANIMATION_MAX_B:
            self.animation_frames_b += 1
        else:
            self.animation_frames_b = 0
        self.image = Boomerang.images[self.animation_frames_b // self.ANIMATION_DIVISOR_B]


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
