#!/usr/bin/env python
""" pygame.examples.aliens

Shows a mini game where you have to defend against aliens.

What does it show you about pygame?

* pg.sprite, the difference between Sprite and Group.
* dirty rectangle optimization for processing for speed.
* music with pg.mixer.music, including fadeout
* sound effects with pg.Sound
* event processing, keyboard handling, QUIT handling.
* a main loop frame limited with a game clock from pg.time.Clock
* fullscreen switching.


Controls
--------

* Left and right arrows to move.
* Space bar to shoot
* f key to toggle between fullscreen.

"""

import random
import os

import pygame as pg

if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# game constants
SCREENRECT = pg.Rect(0, 0, 800, 600)

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file).convert()
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    surface.set_colorkey([0, 0, 0])
    return surface.convert()


# Each type of game object gets an init and an update function.
# The update function is called once per frame, and it is when each object should
# change its current position and state.
#
# The Player object actually gets a "move" function instead of update,
# since it is passed extra information about the keyboard.


class Player(pg.sprite.Sprite):
    speed = 5
    bounce = 24
    right_images = []
    left_images = []
    up_images = []
    down_images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.down_images[0]
        self.rect = self.image.get_rect(topleft=(55, 55))
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction:
            self.facing = direction
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.down_images[0]
        elif direction > 0:
            self.image = self.down_images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)


class Brick(pg.sprite.Sprite):
    speed = 0
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(topright=SCREENRECT.topright)
        self.frame = 0

    def update(self):
        self.frame = self.frame + 1


class BrokenPot(pg.sprite.Sprite):
    defaultlife = 12
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self):
        """called every time around the game loop.
        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.
        Also we animate the explosion.
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Pot(pg.sprite.Sprite):
    animcycle = 3
    images = []

    def __init__(self, actor):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)

    def update(self):
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


def main():
    # Initialize pygame
    pg.init()

    fullscreen = False
    # Set the display mode
    winstyle = 32  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    Player.left_images = [load_image(im) for im in ("link-left1.png", "link-left2.png", "link-left3.png",
                                                    "link-left4.png", "link-left5.png")]
    Player.right_images = [load_image(im) for im in ("link-right1.png", "link-right2.png", "link-right3.png",
                                                     "link-right4.png", "link-right5.png")]
    Player.up_images = [load_image(im) for im in ("link-up1.png", "link-up2.png", "link-up3.png",
                                                  "link-up4.png", "link-up5.png")]
    Player.down_images = [load_image(im) for im in ("link-down1.png", "link-down2.png", "link-down3.png",
                                                    "link-down4.png", "link-down5.png")]
    im = load_image("brick.png")
    Brick.images = [im]
    # Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    # Bomb.images = [load_image("bomb.gif")]
    # Shot.images = [load_image("shot.gif")]

    # decorate the game window
    icon = pg.transform.scale(Player.down_images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Linker")
    pg.mouse.set_visible(False)

    # create the background, tile the bgd image
    background = pg.Surface(SCREENRECT.size)
    color = (0, 200, 100)
    background.fill("darkgrey")
    screen.blit(background, SCREENRECT)
    pg.display.flip()

    # Initialize Game Groups
    bricks = pg.sprite.Group()
    pots = pg.sprite.Group()
    # boomerangs = pg.sprite.Group()
    everyone = pg.sprite.RenderUpdates()

    # assign default groups to each sprite class
    Player.containers = everyone
    Brick.containers = bricks, everyone
    Pot.containers = pots, everyone
    # Boomerang.containers = boomerangs, everyone
    # BrokenPot.containers = everyone

    # Create Some Starting Values
    # global score
    # alienreload = ALIEN_RELOAD
    clock = pg.time.Clock()

    # initialize our starting sprites
    # global SCORE
    player = Player()
    Brick()  # note, this 'lives' because it goes into a sprite group

    # Run our main loop whilst the player is alive.
    while player.alive():

        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        everyone.clear(screen, background)

        # update all the sprites
        everyone.update()

        # handle player input
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        player.move(direction)

        # Detect collisions between bricks and player.
        for _ in pg.sprite.spritecollide(player, bricks, 1):
            player.kill()

        # See if alien boms hit the player.
        # for bomb in pg.sprite.spritecollide(player, bombs, 1):
        #     Explosion(player)
        #     Explosion(bomb)
        #     player.kill()

        # draw the scene
        dirty = everyone.draw(screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        clock.tick(40)

    pg.time.wait(2000)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
