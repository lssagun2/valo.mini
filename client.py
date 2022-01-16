import socket
import pygame
import time
import math
from pygame.locals import *
from entities import *
from menu import *

# images = {"character1": None}
# for character in images.keys():
# 	images[character] = {"up": None, "down": None, "left": None, "right": None}
# 	for direction in images[character].keys():
# 		directory = "assets/characters/" + character + "/" + direction + "/"
# 		images[character][direction] = [pygame.image.load(directory + "walking_" + direction + str(i) + ".png") for i in range(1, 5)]
# images = {"character1": None, "character2": None}
# for character in images.keys():
# 	images[character] = {"walking": None, "ranged": None};
# 	for state in images[character].keys():
# 		directory = "assets/characters/" + character + "/" + state + "/"
# 		images[character][state] = [pygame.image.load(directory + str(i) + ".png") for i in range(1, 5)]
# masks = {}
# for character in images.keys():
# 	masks[character] = {"up": None, "down": None, "left": None, "right": None, "still": None}
# 	for direction in images[character].keys():
# 		directory = "assets/characters/" + character + "/" + direction + "/"
# 		masks[character][direction] = [pygame.mask.from_surface(image) for image in images[character][direction]]
#connect to server

start_video(screen)
#main loop
client_socket.close()
pygame.quit()