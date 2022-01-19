import pygame

#global variables
map_image = pygame.image.load("assets/background/map.png")
map_image = pygame.transform.scale(map_image, (5760, 5760))
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 768
MAP_WIDTH = map_image.get_height() + DISPLAY_WIDTH
MAP_HEIGHT = map_image.get_width() + DISPLAY_HEIGHT
MAP = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
MAP.blit(map_image, (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2))
MENU_BACKGROUND = pygame.transform.scale(pygame.image.load('assets/background/titlescreen-fullscreen.png'), (1280, 720))
END_BACKGROUND = pygame.transform.scale(pygame.image.load('assets/background/endtitle-fullscreen.png'), (1280, 720))

#pygame custom events
RELOAD = pygame.USEREVENT + 0

#Pygame fonts for texts
pygame.font.init()
stats_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 30)
reloading_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 15)
username_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 15)

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ENDING_RED = (255, 51, 51)

#key presses
key_pressed = {pygame.K_w: False, pygame.K_UP: False, pygame.K_s: False, pygame.K_DOWN: False, pygame.K_d: False, pygame.K_RIGHT: False, pygame.K_a: False, pygame.K_LEFT: False, pygame.K_RSHIFT: False, pygame.K_LSHIFT: False, pygame.K_e: False}
mouse_pressed = {1: False, 2: False, 3: False, 4: False, 5: False}