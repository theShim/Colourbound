import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *

from scripts.world_loading.tilemap import Tilemap
from scripts.world_loading.backgrounds import Starry_Background
from scripts.gui.colour_fill_meter import Colour_Meter
from scripts.gui.player_icon import Player_Icon

    ##############################################################################################

#state handler / finite state machine that stores a queue of all states
# e.g. ["title_screen", "cutscene_1", "cutscene_2", "planet_1"] (beats world 1) ->
#      ["title_screen", "cutscene_1", "cutscene_2", "planet_2"] (presses exit button to main menu) ->
#      ["title_screen"] (loads world 2) ->
#      ["title_screen", "planet_2"] (loads world 2) ->

class State_Loader:
    def __init__(self, game, start="splash_screen"):
        self.game = game
        self.stack: list[State] = []

        self.start = start #what the state machine should begin on, useful for debugging to save having to run the entire game
        self.states = {}

    #storing all the states. has to be done post initialisation as the states are created after the State class below
    #is created
    def populate_states(self):
        from scripts.world_loading.states.splash_screen import Splash_Screen
        from scripts.world_loading.states.title_screen import Title_Screen
        from scripts.world_loading.states.cutscenes import Cutscene_1, Cutscene_2
        from scripts.world_loading.states.planet_1 import Planet_1

        self.states = {
            "splash_screen" : Splash_Screen(self.game),
            "title_screen" : Title_Screen(self.game),
            "cutscene_1" : Cutscene_1(self.game),
            "cutscene_2" : Cutscene_2(self.game),
            "planet_1" : Planet_1(self.game)
        }

        #adding the first state
        if self.start:
            self.add_state(self.states[self.start])

        #############################################################################
    
    @property
    def current_state(self):
        return self.stack[-1]

    #the current state's tilemap, or the last state that has a tilemap
    @property
    def tilemap(self) -> Tilemap:
        try:
            t = self.current_state.tilemap
            return t
        except AttributeError:
            for i in range(len(self.stack)-2, -1, -1):
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

    #the main method, mostly rendering it and all sprite updates
    def update(self):
        self.stack[-1].update()

    ##############################################################################################

class State:
    def __init__(self, game, name, prev=None):
        self.game = game
        self.screen = self.game.screen

        self.name = name
        self.prev = prev #the previous state
        self.tilemap = Tilemap(self.game)
        
        self.background = Starry_Background(self.game)
        self.colour_meter = Colour_Meter(self.game, [self.game.all_sprites])
        self.player_icon = Player_Icon(self.game, [self.game.all_sprites], (10, 10))

        self.bg_music = None
        self.end = False

    def update(self):
        if self.bg_music:
            if not self.game.music_player.is_playing("bg"):
                self.game.music_player.set_vol(vol=1, channel="bg")
                self.game.music_player.play(self.bg_music, "bg", loop=True, fade_in=1000)

        self.background.update()
        self.game.calculate_offset() #camera
        self.render()

    def render(self):
        self.tilemap.render()
        self.colour_meter.percent = (self.tilemap.filled / self.tilemap.to_fill) * 100

        if self.end == False:
            from scripts.world_loading.states.cutscenes import Ending
            if self.colour_meter.percent >= 97:
                self.end = True
                self.game.state_loader.add_state(Ending(self.game, self))

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