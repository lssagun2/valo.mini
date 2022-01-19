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

#load images into dictionaries
images = {"character1": None, "character2": None, "character3": None}
for character in images.keys():
	images[character] = {"walking": None, "ranged": None};
	for state in images[character].keys():
		directory = "assets/characters/" + character + "/" + state + "/"
		images[character][state] = [pygame.image.load(directory + str(i) + ".png") for i in range(1, 5)]
stone_texture = pygame.image.load('assets/textures/stones/1.png').convert_alpha()

gun_images =   {"classic": 	{"side": pygame.image.load("assets/guns/classic/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/classic/top.png").convert_alpha()}, 
				"odin": 	{"side": pygame.image.load("assets/guns/odin/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/odin/top.png").convert_alpha()}, 
				"operator": {"side": pygame.image.load("assets/guns/operator/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/operator/top.png").convert_alpha()}, 
				"sheriff": 	{"side": pygame.image.load("assets/guns/sheriff/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/sheriff/top.png").convert_alpha()}, 
				"spectre": 	{"side": pygame.image.load("assets/guns/spectre/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/spectre/top.png").convert_alpha()}, 
				"vandal": 	{"side": pygame.image.load("assets/guns/vandal/side.png").convert_alpha(), "top": pygame.image.load("assets/guns/vandal/top.png").convert_alpha()}}
gun_stats =    {"classic": 	{"clip_size": 12, "fire_rate": 5, "bullet_speed": 6, "reload_time": 1000, "full_auto": False}, 
				"odin": 	{"clip_size": 100, "fire_rate": 11, "bullet_speed": 10, "reload_time": 4000, "full_auto": True}, 
				"operator": {"clip_size": 5, "fire_rate": 3, "bullet_speed": 12, "reload_time": 3000, "full_auto": False}, 
				"sheriff": 	{"clip_size": 7, "fire_rate": 4, "bullet_speed": 7, "reload_time": 1500, "full_auto": True}, 
				"spectre": 	{"clip_size": 30, "fire_rate": 10, "bullet_speed": 8, "reload_time": 2000, "full_auto": True}, 
				"vandal": 	{"clip_size": 30, "fire_rate": 8, "bullet_speed": 10, "reload_time": 2500, "full_auto": True}}
gun_sounds =   {"classic": 	"assets/background/music/", 
				"odin": 	"assets/background/music/machinegun.wav", 
				"operator": "assets/background/music/", 
				"sheriff": 	"assets/background/music/", 
				"spectre": 	"assets/background/music/submachine-gun.wav", 
				"vandal": 	"assets/background/music/machinegun.wav"}
class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location, health, speed, character = "character1", state = "walking", angle = 0, gun_name = ""):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.health = health
		self.speed = speed
		self.gun = None
		self.gun_name = gun_name
		self.time_last_fired = 0
		self.fired = False
		self.ammo = 1000
		self.reloading = False
		self.animation_count = 0
		self.still = True
		self.character = character
		self.state = state
		self.image = images[character][state][0]
		self.mask = pygame.mask.from_surface(self.image)
		self.angle = 0
		self.rect = self.image.get_rect(center = location)
		self.location = location

	def update(self, location, health, character, state, animation_count, angle, gun_name):
		self.image = pygame.transform.rotate(images[character][state][animation_count // 8], angle)
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.rect.center = location
		self.location = location
		self.health = health
		self.gun_name = gun_name

	def animate(self, mouse_position):
		x, y = mouse_position
		self.angle = (180 / math.pi) * (-math.atan2(y - DISPLAY_HEIGHT/2, x - DISPLAY_WIDTH/2))
		if self.still:
			self.animation_count = 0
		else:
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
			if not self.fired or self.gun.full_auto:
				if self.gun.ammo > 0:
					if current_time - self.time_last_fired > 1 / self.gun.fire_rate:
						fire_sound = mixer.Sound(gun_sounds[self.gun_name])
						fire_sound.play()
						self.time_last_fired = current_time
						self.gun.ammo -= 1
						self.fired = True
						origin = self.location
						x, y = pygame.mouse.get_pos()
						direction = (x - DISPLAY_WIDTH / 2, y - DISPLAY_HEIGHT / 2)
						return (origin, direction, self.gun.bullet_speed)
				else:
					if self.ammo > 0:
						bullet_reload = mixer.Sound('assets/background/music/reload.wav')
						bullet_reload.play()
						self.reloading = True
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
	def __init__(self, name, location, clip_size, fire_rate, bullet_speed, reload_time, full_auto = True):
		pygame.sprite.Sprite.__init__(self)
		self.name = name
		self.ammo = clip_size
		self.clip_size = clip_size
		self.fire_rate = fire_rate
		self.reload_time = reload_time
		self.bullet_speed = bullet_speed
		self.full_auto = full_auto
		self.image = gun_images[name]["side"]
		self.mask = pygame.mask.from_surface(self.image)
		self.location = location
		self.rect = self.image.get_rect()
		self.rect.center = location
		self.equipped = False
	# def animate():
