import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.world_loading.tilemap import Tilemap
from scripts.gui.colour_fill_meter import Colour_Meter

    ##############################################################################################

class State_Loader:
    def __init__(self, game, start="title_screen"):
        self.game = game
        self.stack: list[State] = []

        self.start = start
        self.states = {}

    def populate_states(self):
        from scripts.world_loading.states.title_screen import Title_Screen
        from scripts.world_loading.states.cutscenes import Cutscene_1, Cutscene_2
        from scripts.world_loading.states.planet_1 import Planet_1

        self.states = {
            "title_screen" : Title_Screen(self.game),
            "cutscene_1" : Cutscene_1(self.game),
            "cutscene_2" : Cutscene_2(self.game),
            "planet_1" : Planet_1(self.game)
        }

        if self.start:
            self.add_state(self.states[self.start])

        #############################################################################
    
    @property
    def current_state(self):
        return self.stack[-1]

    @property
    def tilemap(self) -> Tilemap:
        if (t := self.current_state.tilemap): return t
        else:
            for i in range(len(self.states)-2, -1, -1):
                if (t := self.stack[i].tilemap): 
                    break
            else:
                t = "No Tilemap".lower()
            return t

        #############################################################################

    def add_state(self, state):
        self.stack.append(state)

    def pop_state(self):
        self.last_state = self.stack.pop(-1)

    def get_state(self, name):
        return self.states.get(name, default=None)

        #############################################################################

    def update(self):
        self.stack[-1].update()

    ##############################################################################################

class State:
    def __init__(self, game, name, prev=None):
        self.game = game
        self.screen = self.game.screen

        self.name = name
        self.prev = prev
        self.tilemap = Tilemap(self.game)
        
        self.colour_meter = Colour_Meter(self.game, [self.game.all_sprites])

    def update(self):
        self.screen.fill((0, 0, 0))
        self.game.calculate_offset()
        self.render()

    def render(self):
        self.tilemap.render()
        self.colour_meter.percent = (self.tilemap.filled / self.tilemap.to_fill) * 100

        for spr in sorted(self.game.all_sprites.sprites(), key=lambda s: s.z):
            spr.update()

class Cutscene(State):
    def __init__(self, game, name, prev=None):
        super().__init__(game, name, prev)
        del self.tilemap

    def update(self):
        pass

    def render(self):
        pass