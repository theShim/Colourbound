import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ['SDL_VIDEO_CENTERED'] = '1'

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import sys
import time
import asyncio

from scripts.entities.player import Player
from scripts.entities.spaceship import Spaceship, Spaceship_Side, Spaceship_Fidget_Spinner
from scripts.gui.custom_fonts import Custom_Font
from scripts.gui.dialogue_box import Press_Spacebar
from scripts.music.music_player import Music_Player
from scripts.objects.pedestal import Pedestal
from scripts.particles.colour_void_shockwave import Shockwave_Particle
from scripts.particles.paint_splatter import Paint_Splat
from scripts.particles.star import Star_3D
from scripts.screen_effects.effect_manager import Effect_Manager
from scripts.world_loading.backgrounds import Background_Star
from scripts.world_loading.state_machine import State_Loader
from scripts.world_loading.tilemap import Tile

from scripts.config.SETTINGS import *
from scripts.utils.CORE_FUNCS import *
from scripts.utils.debugger import Debugger

if DEBUG:
    #code profiling for performance optimisations
    import pstats
    import cProfile
    import io

pygame.Rect = pygame.FRect

# from scripts.utils.CORE_FUNCS import countLinesIn
# countLinesIn(os.getcwd()) #counts number of lines of code in directory (just for progress counting)

    ##############################################################################################

class Game:
    def __init__(self):
        #intiaising pygame stuff
        self.initialise()

        #initalising pygame window
        flags = pygame.RESIZABLE | pygame.SCALED
        self.screen = pygame.display.set_mode(SIZE, flags)
        pygame.display.toggle_fullscreen()
        self.clock = pygame.time.Clock()
        self.offset = vec()
        self.offset_boundary_buffer = vec(50, 50)
        self.debugger = Debugger()

        #cache sprites
        self.cache_sprites()

        #various sprite groups, just to collect everything together
        self.all_sprites = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        #the player object stored here just so its "universally" accessibly
        self.player = Player(self, groups=[self.all_sprites, self.entities])

        #the finite state machine responsible for the current scene in game.
        self.state_loader = State_Loader(self, "splash_screen")
        self.state_loader.populate_states() #initialising all the states

        #vfx and sfx stuff
        self.effect_manager = Effect_Manager(self)
        self.music_player = Music_Player()
        
    #caching all the sprites at the beginning of the game to avoid repetitive image loading which takes time
    def cache_sprites(self):
        Player.cache_sprites()
        Spaceship.cache_sprites()
        Spaceship_Side.cache_sprites()
        Spaceship_Fidget_Spinner.cache_sprites()
        Paint_Splat.cache_sprites()
        Tile.cache_sprites()
        Custom_Font.init()
        Shockwave_Particle.cache_sprites()
        Press_Spacebar.cache_sprites()
        Star_3D.cache_sprites()
        Background_Star.cache_sprites()
        Pedestal.cache_sprites()

    def initialise(self):
        pygame.init()  #general pygame
        pygame.font.init() #font stuff
        pygame.display.set_caption(WINDOW_TITLE) #Window Title 

        pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
        pygame.mixer.init()

        pygame.event.set_blocked(None) #setting allowed events to reduce lag
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])

    #essentially the camera system
    def calculate_offset(self):
        #have the screen offset kinda lerp to the player location, making it seem more alive
        self.offset.x += (self.player.rect.centerx - WIDTH/2 - self.offset.x) / CAMERA_FOLLOW_SPEED
        self.offset.y += (self.player.rect.centery - HEIGHT/2 - self.offset.y) / CAMERA_FOLLOW_SPEED
        #the alternative to this so the camera is always above the player is simply
        # self.offset = self.player.rect.center - (vec(SIZE) / 2)

        #camera boundaries
        if self.offset.x < -self.offset_boundary_buffer.x:
            self.offset.x = -self.offset_boundary_buffer.x
        if self.offset.y < -self.offset_boundary_buffer.y:
            self.offset.y = -self.offset_boundary_buffer.y

        map_ = self.state_loader.current_state.tilemap.map
        if self.offset.x > map_.get_width() - WIDTH + self.offset_boundary_buffer.x:
            self.offset.x = map_.get_width() - WIDTH + self.offset_boundary_buffer.x
        if self.offset.y > map_.get_height() - HEIGHT + self.offset_boundary_buffer.y:
            self.offset.y = map_.get_height() - HEIGHT + self.offset_boundary_buffer.y


    async def run(self):
        if DEBUG:
            PROFILER = cProfile.Profile()
            PROFILER.enable()

        last_time = pygame.time.get_ticks()
        running = True
        while running:
            #deltatime for framerate independence
            self.dt = (current_time := pygame.time.get_ticks()) - last_time
            self.dt /= 1000
            last_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    
            # self.screen.fill((0, 0, 0))
            
            #updating everything
            self.state_loader.update()
            self.effect_manager.update()

            #this is my game specific
            try:
                await self.state_loader.tilemap.colour_calculator()
            except AttributeError:
                pass

            #blitting everything to screen such as FPS, player velocity and positions etc. useful when u cant print to terminal
            if DEBUG:
                self.debugger.update()
                self.debugger.add_text(f"FPS: {round(self.clock.get_fps(), 1)}")

            pygame.display.update()
            self.clock.tick(FPS)

        if DEBUG:
            PROFILER.disable()
            PROFILER.dump_stats("test.stats")
            pstats.Stats("test.stats", stream=(s:=io.StringIO())).sort_stats((sortby:=pstats.SortKey.CUMULATIVE)).print_stats()
            print(s.getvalue())

        pygame.quit()
        sys.exit()
    

    ##############################################################################################

if __name__ == "__main__":
    game = Game()
    asyncio.run(game.run())