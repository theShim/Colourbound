import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random, math
from scripts.gui.custom_fonts import Custom_Font
from scripts.world_loading.state_machine import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Splash_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")
        self.black = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.black.fill((0, 0, 0))
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)

        self.text = "Powered by PyGame"
        self.timer = 200

        self.bg_music = "title_screen"
        self.stage = 0
        self.start = True

    def update(self):
        self.screen.fill((0, 0, 0))

        size = Custom_Font.FluffyBig.calc_surf_width(self.text), Custom_Font.FluffyBig.space_height
        pos = (WIDTH - size[0]) / 2, (HEIGHT - size[1]) / 2
        Custom_Font.FluffyBig.render(self.screen, self.text, (255, 255, 255), pos)

        self.screen.blit(self.black, (0, 0))

        if self.stage == 0:
            self.timer -= 1
            if self.timer == 100:
                self.game.music_player.play(self.bg_music, "bg", loop=True)
            if self.timer == 0:
                self.stage = 1

        elif self.stage == 1:
            if self.black_alpha > 0:
                self.black_alpha -= 1
                self.black.set_alpha(self.black_alpha)
            else:
                self.stage = 2
                self.timer = 50

        elif self.stage == 2:
            self.timer -= 1
            if self.timer == 0:
                self.stage = 3

        elif self.stage == 3:
            if self.black_alpha < 255:
                self.black_alpha += 1.5
                self.black.set_alpha(self.black_alpha)
            else:
                self.game.state_loader.add_state(self.game.state_loader.states["title_screen"])