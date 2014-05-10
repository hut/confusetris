#!/usr/bin/python2
# Copyright (C) 2014  Roman Zimbelmann <hut@lavabit.com>
# This software is distributed under the terms of the GNU GPL version 3.

import getpass
import os.path
import pygame
import random
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
        self.grid_y = 16
        self.grid_x = 8

        # initialized in init_pygame()
        self.clock = None
        self.font = None
        self.font_small = None
        self.screen = None
        self.pause = False
        self.brickwid = 4
        self.colors = [[0, 0, 0], [0x7f, 0x30, 0x30], [0x30, 0x7f, 0x30], [0x30, 0x30, 0x7f], [0x7f, 0x7f, 0x30]]
        self.all_bricks = [
                [[0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0],
                 [0, 1, 0, 0]],
                [[0, 2, 0, 0],
                 [0, 2, 2, 0],
                 [0, 2, 0, 0],
                 [0, 0, 0, 0]],
                [[0, 3, 0, 0],
                 [0, 3, 3, 0],
                 [0, 0, 3, 0],
                 [0, 0, 0, 0]],
                [[0, 0, 0, 0],
                 [0, 4, 4, 0],
                 [0, 4, 4, 0],
                 [0, 0, 0, 0]],
            ]

    def reset_game(self):
        self.logged = deque(maxlen=30)
        self.game_time = 0
        self.grid = []
        for i in range(self.grid_x):
            self.grid.append([0] * self.grid_y)
        self.shit_brick()

    def shit_brick(self):
        self.brick1_type = randint(0, len(self.all_bricks) - 1)
        self.brick2_type = choice(list(set(range(len(self.all_bricks))) - set([self.brick1_type])))
        self.brick = []
        self.brick.append(self.all_bricks[self.brick1_type])
        self.brick.append(self.all_bricks[self.brick2_type])
        self.brick_x = int(self.grid_x / 2 - self.brickwid/2)
        self.brick_y = -3
        self.true_brick = choice(range(len(self.brick)))

    def log(self, *things):
        self.logged.extend([str(obj) for obj in things])

    def start(self):
        self.init_pygame()
        self.loop()

    def init_pygame(self):
        pygame.init()
        pygame.font.init()
        pygame.key.set_repeat(180, 80)
        pygame.mouse.set_visible(False)
        flags = DOUBLEBUF | (self.fullscreen and FULLSCREEN)
        self.screen = pygame.display.set_mode((self.w, self.h), flags, 32)
        self.font_small = pygame.font.Font(self.font_name, self.font_size[0])
        self.font = pygame.font.Font(self.font_name, self.font_size[1])
        self.clock = pygame.time.Clock()

    def keypress(self, key):
        if key == K_ESCAPE:
            raise SystemExit()
        elif key == K_F11:
            pygame.display.toggle_fullscreen()
        elif key == K_h:
            if not self.would_a_move_collide(-1, 0):
                self.brick_x -= 1
        elif key == K_l:
            if not self.would_a_move_collide(1, 0):
                self.brick_x += 1
        elif key == K_k:
            pass
#            self.brick_rotate()

    def keyhold(self, pressed):
        if (pressed[K_j] or pressed[K_s] or pressed[K_DOWN] or pressed[K_SPACE]):
            self.speed = 10
        else:
            self.speed = 1
#            acceleration[1] += 50.0
#        if (pressed[K_k] or pressed[K_w] or pressed[K_UP]) and g.active:
#            acceleration[1] -= 50.0
#        if (pressed[K_h] or pressed[K_a] or pressed[K_LEFT]) and g.active:
#            acceleration[0] -= 50.0
#        if (pressed[K_l] or pressed[K_d] or pressed[K_RIGHT]) and g.active:
#            acceleration[0] += 50.0

    def loop(self):
        next_log_refresh = 0
        previous_tick = 0
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
            self.keyhold(pygame.key.get_pressed())

            if not self.pause:
                pass

            self.draw_game()

            if not self.pause:
                self.dt = time.time() - time_before
                self.game_time += self.dt
                if self.game_time > previous_tick + (0.5 / self.speed):
                    previous_tick = self.game_time
                    self.brick_move_down()

    def brick_move_down(self):
        if self.would_a_move_collide(0, 1):
            print("Collision!")
            for x in range(self.brickwid):
                for y in range(self.brickwid):
                    newx = self.brick_x + x
                    newy = self.brick_y + y
                    if newx >= 0 or newy >= 0 or newx < self.grid_x - 1 or newy < self.grid_y - 1:
                        newcolor = self.brick[self.true_brick][x][y]
                        if newcolor:
                            self.grid[newx][newy] = newcolor
            self.shit_brick()
        else:
            self.brick_y += 1

    def would_a_move_collide(self, dx, dy):
        for x in range(self.brickwid):
            for y in range(self.brickwid):
                if any(brick[x][y] for brick in self.brick):
                    newx = self.brick_x + x + dx
                    newy = self.brick_y + y + dy
                    if newx < 0 or newx > self.grid_x - 1 or newy > self.grid_y - 1:
                        return True
                    if newy > 0 and self.grid[newx][newy]:
                        return True
        return False

    def draw_game(self):
        self.screen.fill(self.fillcolor)

        self.draw_hud()
        self.draw_brick()
        self.draw_field()
        pygame.display.flip()

    def draw_brick(self):
        s = 30
        w = game.w/2
        h = game.h/2
        x = (s+2)*(self.grid_x/2)
        y = (s+2)*(self.grid_y/2)
        for i in range(4):
            for j in range(4):
                clr1 = self.colors[self.brick[0][i][j]]
                clr2 = self.colors[self.brick[1][i][j]]
                color = [clr1[0] + clr2[0], clr1[1] + clr2[1], clr1[2] + clr2[2]]
                if any(color):
                    self.screen.fill((color[0], color[1], color[2]), \
                            Rect(w-x + (i+self.brick_x)*(s+2), \
                            h-y + (j+self.brick_y)*(s+2), s, s))

    def draw_field(self):
        s = 30
        w = game.w/2
        h = game.h/2
        x = (s+2)*(self.grid_x/2)
        y = (s+2)*(self.grid_y/2)
        for i in range(self.grid_x):
            for j in range(self.grid_y):
                clr = self.grid[i][j]
                color = self.colors[clr]
                if clr:
                    self.screen.fill((color[0], color[1], color[2]), \
                            Rect(w-x + (i)*(s+2), \
                            h-y + (j)*(s+2), s, s))

    def draw_hud(self):
        s = 30
        nx = self.grid_x
        ny = self.grid_y
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
