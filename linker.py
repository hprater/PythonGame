#!/usr/bin/env python
import json
import random
import os

import pygame as pg
from pygame import K_LEFT, K_RIGHT, K_UP, K_DOWN

if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# game constants
SCREENRECT = pg.Rect(0, 0, 800, 600)

main_dir = os.path.split(os.path.abspath(__file__))[0]
dir = {K_LEFT: (-1, 0), K_RIGHT: (1, 0), K_UP: (0, -1), K_DOWN: (0, 1)}
anti_dir = {K_LEFT: (1, 0), K_RIGHT: (-1, 0), K_UP: (0, 1), K_DOWN: (0, -1)}


def load_image(file):
    file = os.path.join(main_dir, "images", file)
    try:
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
    # print(data["rooms"][0]["bricks"])
    for brick in data["rooms"][0]["bricks"]:
        Brick(brick["x"], brick["y"])
    for pot in data["rooms"][0]["pots"]:
        Pot(pot["x"], pot["y"])


class Player(pg.sprite.Sprite):
    speed = 5
    bounce = 24
    animation_cycle = 12
    right_images = []
    left_images = []
    up_images = []
    down_images = []
    current_direction = (0, 0)

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.down_images[0]
        self.rect = self.image.get_rect(topleft=(55, 55))
        self.reloading = 0
        self.origtop = self.rect.top
        self.frame = 0
        self.facing = -1

    def update(self):
        self.rect.move_ip(self.current_direction[0] * self.speed, self.current_direction[1] * self.speed)
        self.rect = self.rect.clamp(SCREENRECT)

    def move(self, direction):
        self.current_direction = (self.current_direction[0] + direction[0], self.current_direction[1] + direction[1])


class Brick(pg.sprite.Sprite):
    speed = 0
    images = []

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frame = 0

    def update(self):
        pass


class BrokenPot(pg.sprite.Sprite):
    default_life = 20
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.default_life

    def update(self):
        self.life = self.life - 1
        if self.life <= 0:
            self.kill()


class Pot(pg.sprite.Sprite):
    speed = 7
    images = []
    direction = None

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frame = 0

    def update(self):
        if self.direction is not None:
            self.rect.move_ip(self.direction[0] * self.speed, self.direction[1] * self.speed)
            self.rect = self.rect.clamp(SCREENRECT)

    def move(self, direction):
        self.direction = direction


class Boomerang(pg.sprite.Sprite):
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)

    def update(self):
        if self.direction is not None:
            self.rect.move_ip(self.direction * self.speed, 0)
            self.rect = self.rect.clamp(SCREENRECT)


def main():
    # Initialize pygame
    pg.init()

    fullscreen = False
    # Set the display mode
    best_depth = pg.display.mode_ok(SCREENRECT.size, 32, 32)
    screen = pg.display.set_mode(SCREENRECT.size, 32, best_depth)

    Player.left_images = [load_image(im) for im in ("link-left1.png", "link-left2.png", "link-left3.png",
                                                    "link-left4.png", "link-left5.png")]
    Player.right_images = [load_image(im) for im in ("link-right1.png", "link-right2.png", "link-right3.png",
                                                     "link-right4.png", "link-right5.png")]
    Player.up_images = [load_image(im) for im in ("link-up1.png", "link-up2.png", "link-up3.png",
                                                  "link-up4.png", "link-up5.png")]
    Player.down_images = [load_image(im) for im in ("link-down1.png", "link-down2.png", "link-down3.png",
                                                    "link-down4.png", "link-down5.png")]
    Brick.images = [load_image("brick.png")]
    Boomerang.images = [load_image(im) for im in ("boomerang1.png", "boomerang2.png", "boomerang3.png",
                                                  "boomerang4.png")]
    Pot.images = [load_image("pot.png")]
    BrokenPot.images = [load_image("pot_broken.png")]

    # decorate the game window
    icon = pg.transform.scale(Player.down_images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Zelda Prater")
    pg.mouse.set_visible(False)

    # create the background, tile the bgd image
    background = pg.Surface(SCREENRECT.size)
    color = (0, 200, 100)
    background.fill(color)
    screen.blit(background, SCREENRECT)
    pg.display.flip()

    # Initialize Game Groups
    bricks = pg.sprite.Group()
    pots = pg.sprite.Group()
    broken = pg.sprite.Group()
    boomerangs = pg.sprite.Group()
    everyone = pg.sprite.RenderUpdates()

    # assign default groups to each sprite class
    Player.containers = everyone
    Brick.containers = bricks, everyone
    Pot.containers = pots, everyone
    Boomerang.containers = boomerangs, everyone
    BrokenPot.containers = everyone, broken

    # Create Some Starting Values
    # global score
    clock = pg.time.Clock()

    # initialize our starting sprites
    # global SCORE
    load_map()
    player = Player()

    # Run our main loop whilst the player is alive.
    while player.alive():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and (event.key == pg.K_ESCAPE or event.key == pg.K_q):
                return
            if event.type == pg.KEYDOWN:
                if event.key in dir:
                    v = dir[event.key]
                    player.move(v)
            if event.type == pg.KEYUP:
                if event.key in dir and player.current_direction != (0, 0):
                    v = anti_dir[event.key]
                    player.move(v)
        everyone.clear(screen, background)
        everyone.update()

        for _ in pg.sprite.spritecollide(player, bricks, False):
            player.current_direction = (0, 0)

        for _ in pg.sprite.spritecollide(player, broken, False):
            player.current_direction = (0, 0)

        for pot in pg.sprite.spritecollide(player, pots, False):
            pot.move(player.current_direction)

        for pot in pg.sprite.groupcollide(pots, bricks, True, False):
            BrokenPot(pot)

        # draw the scene
        dirty = everyone.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 60fps.
        clock.tick(40)

    pg.time.wait(2000)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
