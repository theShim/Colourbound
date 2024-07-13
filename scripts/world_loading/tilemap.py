import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import json
from tkinter.filedialog import asksaveasfile, askopenfilename
import os
import math
import numpy as np
import random

from scripts.objects.pedestal import Pedestal

from scripts.utils.CORE_FUNCS import vec, crop, lerp
from scripts.config.SETTINGS import TILE_SIZE, WIDTH, HEIGHT

    ##############################################################################################

class Tilemap:
    def __init__(self, game, editor_flag=False):
        self.game = game

        self.tilemap = {}
        self.tile_size = TILE_SIZE
        self.map = None
        self.grey_map = None

        self.true_filled = 0
        self.filled = 0
        self.to_fill = -math.inf
        self.changed = False #if the grey map has been affected, only calculte how much left if something has happened

        self.editor_flag = editor_flag

    def add_tile(self, layer: int, type: str, variant: str, tile_loc: str, pos: list[int, int]):
        if layer not in self.tilemap.keys():
            self.tilemap[layer] = {}

        self.tilemap[layer][tile_loc] = Tile(self.game, type, variant, pos)

    def generate_map(self, size: list[int, int], lowest_buffer: list[int, int]):
        map_width = size[0] * TILE_SIZE
        map_height = size[1] * TILE_SIZE
        lowest_x, lowest_y = lowest_buffer
        self.map = pygame.Surface((map_width, map_height), pygame.SRCALPHA)

        for layer in self.tilemap:
            for tile_loc in self.tilemap[layer]:
                tile = self.tilemap[layer][tile_loc]

                tile.pos.x -= lowest_x
                tile.pos.y -= lowest_y

                image = Tile.SPRITES[tile.type][tile.variant].copy()
                self.map.blit(image, tile.pos * TILE_SIZE)

        self.grey_map = pygame.transform.grayscale(self.map)
        self.to_fill = self.grey_map.width * self.grey_map.height

    def add_pedestals(self):

        def generate_points(n, size, buffer, min_dist=200):
            points = [vec(random.uniform(buffer, size[0] - buffer), random.uniform(buffer, size[1] - buffer)) for i in range(n)]
            # flag = True
            # while flag:
            #     flag = False
            #     for p1 in points:
            #         for p2 in points:
            #             if p1 != p2:
            #                 if p1.distance_to(p2) < min_dist:
            #                     dy = p2.y - p1.y
            #                     dx = p2.x - p1.x
            #                     angle = math.atan2(dy, dx)
            #                     p1 += vec(math.cos(angle), math.sin(angle)) * 10
            #                     p2 -= vec(math.cos(angle), math.sin(angle)) * 10
            #                     flag = True

            #                     old_p1 = p1.copy
            #                     p1.x = sorted([buffer, WIDTH - buffer, p1.x])[1]
            #                     p1.y = sorted([buffer, HEIGHT - buffer, p1.y])[1]
            #                     if old_p1 != p1: flag = False
                                
            #                     old_p2 = p2.copy
            #                     p2.x = sorted([buffer, WIDTH - buffer, p2.x])[1]
            #                     p2.y = sorted([buffer, HEIGHT - buffer, p2.y])[1]
            #                     if old_p2 != p2: flag = False
                                
            return points

        def get_radius(point, points):
            nearest_radius = math.inf
            for p in points:
                if 0 < (dist := p.distance_to(point)) < nearest_radius:
                    nearest_radius = dist
            return nearest_radius
        
        for pos in (points := sorted(generate_points(8, self.map.get_size(), 50, min_dist=200), key=lambda p: p.y)):
            Pedestal(self.game, [self.game.all_sprites], pos, radius = get_radius(pos, points) * 1)

            ##############################################################################

    #save the tilemap as a json file
    def save(self):
        f = asksaveasfile(
            filetypes=[('JSON File', ".json")], 
            defaultextension=".json",
            initialdir="level_data"
        )
        if f:
            tilemap = {}
            for layer in self.tilemap:
                tilemap[layer] = {key:item.dict for key,item in self.tilemap[layer].items()}

            json.dump(
                {
                    'tilemap' : tilemap, 
                    'tile_size' : self.tile_size
                }, 
                f,
                indent=4
            )
            print("Saved to", f.name)

    def load(self, path: str=None):
        if path == None:
            f = askopenfilename(
                title="Open existing level data...",
                initialdir="level_data",
                filetypes=[('JSON File', ".json")]
            )
        else:
            f = path

        try:
            with open(f, 'r') as file:
                data = json.load(file)
        except FileNotFoundError as err:
            raise FileNotFoundError(err)
        except:
            return
        
        
        if not self.editor_flag: 
            tile_x = set()
            tile_y = set()
            lowest_x = math.inf
            lowest_y = math.inf
        self.tilemap = {}

        for layer in data["tilemap"]:
            self.tilemap[int(layer)] = {}

            for dic in data["tilemap"][layer]:
                tile_data = data["tilemap"][layer][dic]

                pos = tile_data["pos"]
                self.add_tile(
                    int(layer), 
                    tile_data["type"], 
                    tile_data["variant"], 
                    f"{int(pos[0])};{int(pos[1])}", 
                    tile_data["pos"]
                )

                if not self.editor_flag: 
                    if int(pos[0]) not in tile_x:
                        tile_x.add(int(pos[0]))
                    if int(pos[1]) not in tile_y:
                        tile_y.add(int(pos[1]))

                    if int(pos[0]) < lowest_x:
                        lowest_x = int(pos[0])
                    if int(pos[1]) < lowest_y:
                        lowest_y = int(pos[1])

        if not self.editor_flag: 
            self.max_tile_x = len(tile_x)
            self.max_tile_y = len(tile_y)
            self.generate_map([self.max_tile_x, self.max_tile_y], [lowest_x, lowest_y])
            self.add_pedestals()

    def auto_tile(self):
        pass

            ##############################################################################

    def render(self):
        section_map = crop(self.map, self.game.offset.x, self.game.offset.y, WIDTH, HEIGHT)
        self.game.screen.blit(section_map, (0, 0))
        section_grey_map = crop(self.grey_map, self.game.offset.x, self.game.offset.y, WIDTH, HEIGHT)
        self.game.screen.blit(section_grey_map, (0, 0))

    async def colour_calculator(self):
        if self.changed:
            arr = pygame.surfarray.array3d(self.grey_map)
            clear = np.logical_and.reduce(arr == 0, axis=-1)
            self.true_filled = np.count_nonzero(clear)
            self.changed = False

        if self.filled != self.true_filled:
            self.filled = lerp(self.true_filled, self.filled, 0.1)
            if abs(self.filled - self.true_filled) < 0.5:
                self.filled = self.true_filled

    ##############################################################################################

class Tile(pygame.sprite.Sprite):
    SPRITES = {}

    @classmethod
    def cache_sprites(cls):
        Tile.SPRITES = {}
        BASE_TILE_PATH = 'assets/tiles/'

        for img_name in os.listdir(BASE_TILE_PATH):
            images = []
            for name in sorted(os.listdir(BASE_TILE_PATH + img_name), key=lambda x: int(x.split(".")[0])):
                img = pygame.transform.scale(
                    pygame.image.load(BASE_TILE_PATH + img_name + '/' + name).convert_alpha(),
                    (TILE_SIZE, TILE_SIZE)
                )
                img.set_colorkey((0, 0, 0))
                images.append(img)

            Tile.SPRITES[img_name] = images

    def __init__(self, game, type: str, variant: int, pos: list[int, int]):
        super().__init__()
        self.game = game

        self.type = type
        self.variant = variant
        self.pos = vec(pos)

    @property
    def dict(self):
        return {'type':self.type, "pos":[self.pos[0], self.pos[1]], "variant":self.variant}

    def update(self, dim=False):
        image = Tile.SPRITES[self.type][self.variant].copy()
        if dim:
            image.set_alpha(128)
        self.game.screen.blit(image, [(self.pos.x * TILE_SIZE) - self.game.offset.x, (self.pos.y * TILE_SIZE) - self.game.offset.y])