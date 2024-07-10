import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random, math

from scripts.entities.spaceship import Spaceship
from scripts.gui.titlecard import Titlecard
from scripts.particles.star import Star_3D
from scripts.world_loading.state_machine import State

from scripts.config.SETTINGS import WIDTH, HEIGHT

    ##############################################################################################

class Title_Screen(State):
    def __init__(self, game):
        super().__init__(game, "title_screen")

        self.bg = pygame.Surface((WIDTH, HEIGHT))
        self.bg.set_alpha(60)

        self.stars = pygame.sprite.Group()
        for i in range(300):
            Star_3D(game, [self.stars])

        self.spaceship = Spaceship(self.game, [])

        self.titlecard = Titlecard(self.game)

        self.black = pygame.Surface((WIDTH, HEIGHT))
        self.black.fill((0, 0, 0))
        self.black_alpha = 0
        self.black.set_alpha(self.black_alpha)

    def update(self):
        self.screen.blit(self.bg, (0, 0))
        
        self.stars.update()
        self.game.debugger.add_text(f"{(180 / math.pi) * (Star_3D.angle)}")

        self.spaceship.update()

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.titlecard.exit_flag = True
            self.spaceship.stage = 1
        if self.titlecard.exit_flag:
            self.titlecard.exit()
            self.spaceship.mouse_control = False
        if self.spaceship.stage == 2:      
            Star_3D.update_angle()
        self.titlecard.update()

        if (180/math.pi) * Star_3D.angle > 800:
            self.black_alpha += 5
            self.black.set_alpha(self.black_alpha)
            self.screen.blit(self.black, (0, 0))

        if (180/math.pi) * Star_3D.angle > 1100:
            self.game.state_loader.add_state(self.game.state_loader.states["cutscene_1"])
            self.stars.empty()
            Star_3D.angle = 0