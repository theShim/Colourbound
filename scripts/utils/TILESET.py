import pygame
pygame.init()

import os
import numpy as np

pygame.display.set_mode((0, 0), pygame.HIDDEN)

    ##############################################################################################

def extract_tiles(spritesheet_path, tile_size=[16, 16], scale_size=[32, 32]):
    spritesheet = pygame.image.load(spritesheet_path).convert_alpha()
    sheet_width, sheet_height = spritesheet.get_size()

    path = "assets/tilesets/" + spritesheet_path.split("/")[-1].split(".")[0]
    if not os.path.exists(path):
        os.makedirs(path)

    x = 0
    y = 0
    i = 0
    while y < sheet_height:
        while x < sheet_width:
            spr = pygame.transform.scale(spritesheet.subsurface([x, y, *tile_size]), scale_size)

            alpha = pygame.surfarray.pixels_alpha(spr)
            pixels = pygame.surfarray.pixels3d(spr)
            if not np.all(pixels == 255):
                pygame.image.save(spr, f"{path}/{i}.png")
                i += 1

            x += tile_size[0]

        x = 0
        y += tile_size[1]
    

extract_tiles("assets/tilesets/grass_6.png")

pygame.quit()