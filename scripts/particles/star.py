import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random
import os
import math
import numpy as np

from scripts.utils.CORE_FUNCS import vec, gen_rand_colour
from scripts.config.SETTINGS import Z_LAYERS, WIDTH, SCREEN_CENTER, HEIGHT

vec3 = pygame.math.Vector3

    ##############################################################################################

class Star_3D(pygame.sprite.Sprite):
    angle = 0
    Z_DISTANCE = 10

    @classmethod
    def update_angle(cls):
        if ((180 / math.pi) * cls.angle) < 45:
            angle = .25
        else:
            angle = 2

        # if pygame.key.get_pressed()[pygame.K_UP]:
        cls.angle += math.radians(angle)
        # if pygame.key.get_pressed()[pygame.K_DOWN]:
        #     cls.angle -= math.radians(angle)

    def __init__(self, game, groups, screen=None):
        super().__init__(groups)
        self.game = game
        self.screen = screen or self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.z = random.uniform(0.1, Star_3D.Z_DISTANCE)
        self.o_pos = self.get_pos_3d()
        self.o_pos.z = self.z
        self.pos_3d = self.o_pos.copy()

        self.radius = random.randint(2, 4) / 2
        self.alpha = random.uniform(0, 3)
        self.alpha_decay = random.uniform(1.5, 3) / 10
        self.vel = vec3(-1, 0, 0) / 5
        self.total_vel = vec3()

        self.colour = gen_rand_colour(vibrant=True)
        self.grey_colour = pygame.Color(c:=(int(0.299 * self.colour.r + 0.587 * self.colour.g + 0.114 * self.colour.b)),c,c)
        self.grey = False

    def grey_switch(self):
        self.grey = True
        self.colour = self.grey_colour

    def get_pos_3d(self, scale=1):
        x = random.uniform(-WIDTH, WIDTH) * 4
        y = random.uniform(-HEIGHT, HEIGHT) * 4
        p = vec3(x, y, Star_3D.Z_DISTANCE)
        return p

    def project(self) -> vec:
        return vec(self.pos_3d.x / self.pos_3d.z, self.pos_3d.y / self.pos_3d.z) + vec(SCREEN_CENTER) - self.game.offset
    

    def update(self):

        vel = self.vel.copy()
        vel.xz = vel.xy.rotate(self.angle) * 10
        self.total_vel += vel * (1 if self.angle > 0 else 2)
        self.pos_3d = self.o_pos + self.total_vel

        if self.pos_3d.z <= 0:
            self.o_pos = self.get_pos_3d()
            self.pos_3d = self.o_pos.copy()
            self.total_vel = vec3()

        if self.angle == 0:
            if self.pos_3d.x < -self.radius - (WIDTH / 2) * self.pos_3d.z:
                # self.pos_3d.x = (1.5* WIDTH * self.pos_3d.z) + self.radius
                self.total_vel = vec3()

        self.alpha += math.radians(self.alpha_decay)
        self.size = max(1, (Star_3D.Z_DISTANCE / (((self.pos_3d.z * self.radius) ** 1.3))))

        if not 641 <= self.pos_3d.x <= 642:
            if 100 > self.size > 1:
                self.draw()
            else:
                self.draw(pixel=True)
            

    def draw(self, pixel=False):
        if pixel == False:
            r = (self.size)
            surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (self.colour.r, self.colour.g, self.colour.b, 255 * math.sin(self.alpha) ** 2), (r, r), r)
            self.screen.blit(surf, surf.get_rect(center=self.project()))

        else:
            self.screen.set_at(self.project(), (
                (self.colour.r * math.sin(self.alpha) ** 2), 
                (self.colour.g * math.sin(self.alpha) ** 2), 
                (self.colour.b * math.sin(self.alpha) ** 2))
            )

        if vec(pygame.mouse.get_pos()).distance_to(vec(self.project())) < self.size:
            self.game.debugger.add_text(f"{self.vel} | {self.pos_3d}")
        # if 641 <= self.pos_3d.x <= 642:
        #     self.game.debugger.add_text(f"{self.vel} | {self.pos_3d}")



class Falling_Down_Star(pygame.sprite.Sprite):
    def __init__(self, game, groups, screen=None):
        super().__init__(groups)
        self.game = game
        self.screen = screen or self.game.screen
        self.z = Z_LAYERS["background particle"]

        self.pos = vec(random.uniform(0, WIDTH), random.uniform(0, HEIGHT))
        self.pos_z = random.uniform(1.5, 10)
        self.radius = random.randint(2, 4) / 2
        self.size = max(1.3, (10 / (((self.pos_z * self.radius) ** 1.3))))
        self.vel = vec(1, 1.75) * 8
        
        self.alpha = random.uniform(0, 3)
        self.alpha_decay = random.uniform(1.5, 3) / 10
        self.colour = gen_rand_colour(vibrant=True)
        self.colour = pygame.Color(c:=(int(0.299 * self.colour.r + 0.587 * self.colour.g + 0.114 * self.colour.b)),c,c)

    def move(self):
        self.pos -= self.vel / self.pos_z

        if self.pos.y < 0:
            self.pos = vec(random.uniform(0, WIDTH*1.5), HEIGHT+5)
        if self.pos.x < 0:
            self.pos = vec(random.uniform(0, WIDTH*1.5), HEIGHT+5)

    def update(self):
        self.move()
        
        self.alpha += math.radians(self.alpha_decay)
        self.draw(not (1 < self.size < 100))

    def draw(self, pixel=False):
        if pixel == False:
            r = (self.size)
            surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (self.colour.r, self.colour.g, self.colour.b, 255 * math.sin(self.alpha) ** 2), (r, r), r)
            self.screen.blit(surf, surf.get_rect(center=self.pos))

        else:
            self.screen.set_at(self.pos, (
                (self.colour.r * math.sin(self.alpha) ** 2), 
                (self.colour.g * math.sin(self.alpha) ** 2), 
                (self.colour.b * math.sin(self.alpha) ** 2))
            )