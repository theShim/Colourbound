import pygame

DEBUG = False

SIZE = WIDTH, HEIGHT = (640, 400)
SCREEN_CENTER = (SIZE[0] / 2, SIZE[1] / 2)
WINDOW_TITLE = "WINDOW TITLE"
FPS = 60
CAMERA_FOLLOW_SPEED = 12
TILE_SIZE = 32

#blitting order of sprites, tilemap goes before this
Z_LAYERS = {
    "background particle" : 3,
    "pedestal" : 4,
    "enemy" : 5,
    "player" : 6,
    "projectile" : 7,
    "foreground particle" : 8,
    "gui" : 10
}

#   PHYSICS
FRIC = 0.9
GRAV = 20

CONTROLS = {
    "up"        : pygame.K_w,
    "down"      : pygame.K_s,
    "left"      : pygame.K_a,
    "right"     : pygame.K_d,
    "jump"      : pygame.K_SPACE,
}