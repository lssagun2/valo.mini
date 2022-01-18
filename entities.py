import pygame
import time
import math
import random
from variables import *
from pygame.locals import *
from pygame import mixer

#initialize Pygame
pygame.init()
clock = pygame.time.Clock()

#create main display
screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
logo = pygame.image.load('assets/logo/valo.png')
pygame.display.set_caption('Valo.mini')
pygame.display.set_icon(logo)
display_surface = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
display_surface = display_surface.convert()
MAP.convert()

char_style1 = pygame.image.load('assets/characters/character1/walking/1.png').convert_alpha()
char_style2 = pygame.image.load('assets/characters/character2/walking/1.png').convert_alpha()
char_style3 = pygame.image.load('assets/characters/character3/walking/1.png').convert_alpha()
char_style1 = pygame.transform.scale(char_style1, (648, 648))
char_style2 = pygame.transform.scale(char_style2, (648, 648))
char_style3 = pygame.transform.scale(char_style3, (648, 648))

#load images into dictionaries
images = {"character1": None, "character2": None, "character3": None}
for character in images.keys():
	images[character] = {"walking": None, "ranged": None};
	for state in images[character].keys():
		directory = "assets/characters/" + character + "/" + state + "/"
		images[character][state] = [pygame.image.load(directory + str(i) + ".png") for i in range(1, 5)]

class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location, health, speed, character = "character1", state = "walking"):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.health = health
		self.speed = speed
		self.gun = Gun(30, 10, 10, 2000)
		self.time_last_fired = 0
		self.ammo = 1000
		self.reloading = False
		self.animation_count = 0
		self.still = True
		self.character = character
		self.state = state
		self.image = images[character][state][0]
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect(center = location)
		self.location = location

	def update(self, location, health):
		self.location = location
		self.rect.center = location
		self.health = health

	def animate(self, mouse_position):
		x, y = mouse_position
		angle = (180 / math.pi) * (-math.atan2(y - DISPLAY_HEIGHT/2, x - DISPLAY_WIDTH/2))
		if self.still:
			self.image = pygame.transform.rotate(images[self.character][self.state][0], angle)
		else:
			self.image = pygame.transform.rotate(images[self.character][self.state][self.animation_count // 8], angle)
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.rect.center = self.location
		self.animation_count = (self.animation_count + 1) % 32

	def reload(self):
		if self.ammo > self.gun.clip_size - self.gun.ammo:
			self.ammo -= self.gun.clip_size- self.gun.ammo
			self.gun.ammo += self.gun.clip_size - self.gun.ammo
		else:
			self.gun.ammo += self.ammo
			self.ammo = 0
		self.reloading = False

	def fire(self):
		current_time = time.time()
		if not self.reloading:
			if self.gun.ammo > 0:
				if current_time - self.time_last_fired > 1 / self.gun.fire_rate:
					self.time_last_fired = current_time
					self.gun.ammo -= 1
					origin = self.location
					x, y = pygame.mouse.get_pos()
					direction = (x - DISPLAY_WIDTH / 2, y - DISPLAY_HEIGHT / 2)
					return (origin, direction, self.gun.bullet_speed)
			else:
				if self.ammo > 0:
					self.reloading = True
					bullet_reload = mixer.Sound('assets/background/music/reload.mp3')
					bullet_reload.play()
					pygame.time.set_timer(RELOAD, self.gun.reload_time, loops = 1)
		return " "
class Cover(pygame.sprite.Sprite):
	def __init__(self, location, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = location
class Bullet(pygame.sprite.Sprite):
	def __init__(self, location, radius = 3):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([2*radius, 2*radius], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (0, 0, 0), (radius, radius), radius)
		self.rect.center = location
class Gun(pygame.sprite.Sprite):
	def __init__(self, clip_size, fire_rate, bullet_speed, reload_time, full_auto = True):
		pygame.sprite.Sprite.__init__(self)
		self.ammo = clip_size
		self.clip_size = clip_size
		self.fire_rate = fire_rate
		self.reload_time = reload_time
		self.bullet_speed = bullet_speed
		self.full_auto = full_auto
	# def animate():
