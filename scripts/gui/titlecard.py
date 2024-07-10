import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import os
import colorsys
import math

from scripts.utils.CORE_FUNCS import vec, apply_rainbow
from scripts.config.SETTINGS import WIDTH

    ##############################################################################################

def swap_color(img: pygame.Surface, old_c, new_c):
    e_colorkey = (0, 0, 0)
    img.set_colorkey(old_c)
    surf = img.copy()
    surf.fill(new_c)
    surf.blit(img,(0,0))
    surf.set_colorkey(e_colorkey)
    return surf

def get_rainbow_color(value, max_value, offset=0):
    # Normalize the value to the range [0, 1]
    normalized_value = (value % max_value) / max_value

    # Convert the normalized value to a hue value (0 to 1)
    hue = normalized_value

    # Convert the hue to an RGB color
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    # Convert to 0-255 range for Pygame
    return max(0, int(r * 255) + offset), max(0, int(g * 255) + offset), max(0, int(b * 255) + offset)

    ##############################################################################################

class Titlecard(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.screen = self.game.screen

        self.image = pygame.image.load("assets/gui/titlecard.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, vec(self.image.get_size())*8)
        self.image.set_colorkey((0, 0, 0))

        self.shadow = pygame.image.load("assets/gui/titlecard_shadow.png").convert_alpha()
        self.shadow = pygame.transform.scale(self.shadow, vec(self.shadow.get_size())*8)
        self.shadow.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect(centerx=WIDTH/2, y=60)
        self.colour = (255, 0, 0)
        self.shadow_colour = (255, 0, 0)
        self.animation_period = 2000
        self.elapsed_time = 0
        self.t = 0

        self.exit_flag = False
        self.end_pos = vec(self.rect.x, -self.rect.height * 3)

    def exit(self):
        self.rect.topleft = vec(self.rect.topleft).lerp(self.end_pos, 0.025)

    def animate(self):
        self.t += self.game.dt * 100
        self.elapsed_time += self.game.dt * 1000
        # self.image = swap_color(self.image, self.colour, (c := get_rainbow_color(self.t, 1000)))
        # self.colour = c
        # self.shadow = swap_color(self.shadow, self.shadow_colour, (d := get_rainbow_color(self.t, 1000, offset=-100)))
        # self.shadow_colour = d

    def update(self):
        self.animate()
        self.draw()

    def draw(self):
        image = apply_rainbow(
            self.image,
            offset=(self.animation_period - self.elapsed_time) / self.animation_period,
            bands=1.2, strength=0.5
        )
        shadow = apply_rainbow(
            self.shadow,
            offset=(self.animation_period - self.elapsed_time) / self.animation_period,
            bands=1.2, strength=0.8,
            colour_offset=(-20, -20, -20)
        )
        self.screen.blit(shadow, self.rect.topleft + vec(1.2, 1.2 + 5 * math.sin(0.5 * math.radians(self.t))))
        self.screen.blit(image, self.rect.topleft + vec(0, 5 * math.sin(0.5 * math.radians(self.t))))