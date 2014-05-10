#!/usr/bin/python2
# Copyright (C) 2014  Roman Zimbelmann <hut@lavabit.com>
# This software is distributed under the terms of the GNU GPL version 3.

import getpass
import os.path
import pygame
import sys
import time
from collections import deque
from math import sin, cos, atan2, pi, sqrt
from pygame.locals import *
from random import random, randint, choice, shuffle, setstate, getstate, seed
tau = 2 * pi

class Game(object):
    def __init__(self):
        self.fillcolor = (0, 0, 0)
        self.fullscreen = '--fullscreen' in sys.argv
        self.w = 800
        self.h = 600
        self.font_name = None
        self.font_size = 16, 24
        self.maxfps = 30

        # initialized in init_pygame()
        self.clock = None
        self.font = None
        self.font_small = None
        self.screen = None
        self.pause = False

    def reset_game(self):
        self.logged = deque(maxlen=30)
        self.game_time = 0

    def log(self, *things):
        self.logged.extend([str(obj) for obj in things])

    def start(self):
        self.init_pygame()
        self.loop()

    def init_pygame(self):
        pygame.init()
        pygame.font.init()
        pygame.key.set_repeat(180, 80)
        flags = DOUBLEBUF | (self.fullscreen and FULLSCREEN)
        self.screen = pygame.display.set_mode((self.w, self.h), flags, 32)
        self.font_small = pygame.font.Font(self.font_name, self.font_size[0])
        self.font = pygame.font.Font(self.font_name, self.font_size[1])
        self.clock = pygame.time.Clock()

    def keypress(self, key):
        if key == K_ESCAPE:
            raise SystemExit()
        if key == K_F11:
            pygame.display.toggle_fullscreen()

    def keyhold(self, key):
        pass

    def loop(self):
        next_log_refresh = 0
        while True:
            time_before = time.time()
            self.clock.tick(self.maxfps)
            if next_log_refresh <= time.time():
                next_log_refresh = time.time() + 1
                self.log("")

            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN:
                    self.keypress(event.key)
#                elif event.type in (MOUSEBUTTONDOWN, MOUSEBUTTONUP):
#                    self.click(event.type, event.pos, event.button)
            self.keyhold(pygame.key.get_pressed())

            if not self.pause:
                pass

            self.draw_game()

            if not self.pause:
                self.dt = time.time() - time_before
                self.game_time += self.dt

    def draw_game(self):
        self.screen.fill(self.fillcolor)

        self.draw_hud()
        pygame.display.flip()

    def draw_hud(self):
        s = 30
        nx = 10
        ny = 16
        x = (s+2)*(nx/2)
        y = (s+2)*(ny/2)
        w = game.w/2
        h = game.h/2
        pygame.draw.rect(self.screen, (0, 255, 0), Rect(w-x-1, h-y-1, x*2, y*2), 2)
        for i in range(nx):
            for j in range(ny):
                pygame.draw.rect(self.screen, (64, 64, 64), Rect(w-x + i*(s+2), h-y + j*(s+2), s, s), 1)



if __name__ == '__main__':
    game = Game()
    game.reset_game()

    if '--help' in sys.argv or '-h' in sys.argv:
        print(__doc__)
    elif '--version' in sys.argv:
        print(game.version)
    else:
        game.start()
