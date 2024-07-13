import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os
import math
import numpy as np

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour, lerp
from scripts.config.SETTINGS import Z_LAYERS

    ##############################################################################################

class Death_Spark(pygame.sprite.Sprite):
    def __init__(self, game, groups, pos, scale, angle, speed=None, colour=(255, 255, 255), spin=False, grav=False):
        super().__init__(groups)
        self.game = game
        self.screen = self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.o_pos = vec(pos)
        self.pos = vec(pos)
        self.scale = scale * 1.1
        self.angle = angle
        self.speed = random.uniform(3, 6) if speed == None else speed
        self.colour = colour

        self.spin = spin
        self.grav = grav
        self.dh = 0

        for i in range(int(self.scale*2)+1):
            self.move()


    def move(self):
        self.pos += vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        self.dh = math.sin(self.angle) * (self.o_pos.y - self.pos.y)

    def apply_gravity(self, friction, force, terminal_velocity):
        movement = vec(math.cos(self.angle), math.sin(self.angle)) * self.speed
        movement[1] = min(terminal_velocity, movement[1] + force)
        movement[0] *= friction
        self.angle = math.atan2(movement[1], movement[0])


    def update(self):
        self.speed -= 0.1
        if self.speed < 0:
            self.kill()
        
        if self.spin:
            self.angle += 0.1
        if self.grav:
            self.apply_gravity(0.975, 0.2, 8)
        self.move()
        
        self.draw()

    def draw(self):
        points = np.array([
            vec(math.cos(self.angle), math.sin(self.angle)) * self.scale * self.speed,
            vec(math.cos(self.angle - math.pi/2), math.sin(self.angle - math.pi/2)) * 0.3 * self.scale * self.speed,
            vec(math.cos(self.angle - math.pi), math.sin(self.angle - math.pi)) * 3 * self.scale * self.speed + vec(random.random(), random.random())*self.speed,
            vec(math.cos(self.angle + math.pi/2), math.sin(self.angle + math.pi/2))  * 0.3 * self.scale * self.speed,
        ])
        points += (self.pos - self.game.offset)
        pygame.draw.polygon(self.screen, self.colour, points)
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

        # points -= (self.pos - self.game.offset)
        # min_x = np.min(points[:, 0])
        # min_y = np.min(points[:, 1])
        # points += [min_x, min_y]

        # min_x = np.min(points[:, 0])
        # max_x = np.max(points[:, 0])
        # min_y = np.min(points[:, 1])
        # max_y = np.max(points[:, 1])
        # print(max_x - min_x, max_y, min_y)
        # width, height = max_x - min_x, max_y, min_y
        # print(width, height)
        # pygame.draw.polygon(self.screen, (0, 0, 0, 128), points - [0, self.dh])