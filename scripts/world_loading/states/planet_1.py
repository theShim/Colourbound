import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

import random

from scripts.world_loading.state_machine import State
from scripts.entities.liztard import Liztard
from scripts.entities.spaceship import Fallen_Ship

    ##############################################################################################

class Planet_1(State):
    def __init__(self, game, prev=None):
        super().__init__(game, "planet_1", prev)
        self.tilemap.load("data/stage_data/test2.json")
        self.game.player.rect.center = (pos := pygame.math.Vector2(self.tilemap.map.get_size()) / 2)
        Fallen_Ship(self.game, [self.game.all_sprites], pos - (50, 10))
        self.bg_music = "into_space"

        map_size = self.tilemap.map.get_size()
        [Liztard(self.game, [self.game.all_sprites, self.game.entities], (random.uniform(50, map_size[0]-50), random.uniform(50, map_size[1]-50)))for i in range(5)]