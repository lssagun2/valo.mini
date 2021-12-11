import socket
import pygame
import time
import math
from pygame.locals import *

images = {"sage": None}
for character in images.keys():
	images[character] = {"up": None, "down": None, "left": None, "right": None}
	for direction in images[character].keys():
		directory = "assets/characters/" + character + "/" + direction + "/"
		images[character][direction] = [pygame.image.load(directory + str(i) + ".png") for i in range(1, 9)]
masks = {}
for character in images.keys():
	masks[character] = {"up": None, "down": None, "left": None, "right": None, "still": None}
	for direction in images[character].keys():
		directory = "assets/characters/" + character + "/" + direction + "/"
		masks[character][direction] = [pygame.mask.from_surface(image) for image in images[character][direction]]
#connect to server
client_socket = socket.socket()
HOST = '127.0.0.1'
PORT = 1233
print('Waiting for connection')
try:
	client_socket.connect((HOST, PORT))
except socket.error as e:
	print(str(e))

#game variables
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
MAP_WIDTH = 5 * SCREEN_WIDTH
MAP_HEIGHT = 5 * SCREEN_HEIGHT
USERNAME = "asdasd"

#colors
WHITE = (255, 255, 255)
BACKGROUND = (127, 201, 159)
BLACK = (0, 0, 0)
PLAYER_COLOR = (7,135,123)

#classes
class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location, health, color, radius, speed, character = "sage", direction = "left" ):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.radius = radius
		self.health = health
		self.speed = speed
		self.gun = Gun(30, 10, 10, 2000)
		self.time_last_fired = 0
		self.ammo = 1000
		self.reloading = False
		self.animation_count = 0
		self.still = True
		self.last_moved_left = True
		self.last_moved_right = False
		self.character = character
		self.direction = direction
		self.image = images[character][direction][0]
		self.mask = masks[character][direction][0]
		self.rect = self.image.get_rect(center = location)
		self.location = location

	def update(self, location, health):
		self.location = location
		self.rect.center = location
		self.health = health

	def animate(self):
		if self.still:
			if self.last_moved_right and self.direction != "right":
				self.image = pygame.transform.flip(images[self.character][self.direction][0], True, False)
				self.mask = pygame.mask.from_surface(self.image)
			else:
				self.image = images[self.character][self.direction][0]
				self.mask = masks[self.character][self.direction][0]
		else:
			if self.direction == "left" or self.direction == "right":
				self.image = images[self.character][self.direction][self.animation_count // 8]
				self.mask = masks[self.character][self.direction][self.animation_count // 8]
			else:
				if self.last_moved_left:
					self.image = images[self.character][self.direction][self.animation_count // 8]
					self.mask = masks[self.character][self.direction][self.animation_count // 8]
				elif self.last_moved_right:
					self.image = pygame.transform.flip(images[self.character][self.direction][self.animation_count // 8], True, False)
					self.mask = pygame.mask.from_surface(self.image)
		
		self.animation_count = (self.animation_count + 1) % 16

	def move(self, key_pressed):
		if key_pressed[pygame.K_RSHIFT] or key_pressed[pygame.K_LSHIFT]:
			self.speed = 2
		else:
			self.speed = 3
		self.still = True
		if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
			self.still = False
			self.direction = "up"
			self.rect.move_ip(0, -self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False, pygame.sprite.collide_mask)
			if len(hits) != 0:
				self.rect.move_ip(0, self.speed)
				# self.rect.move_ip(0, hits[0].rect.bottom - self.rect.top)
		if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
			self.still = False
			self.direction = "down"
			self.rect.move_ip(0, self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False, pygame.sprite.collide_mask)
			if len(hits) != 0:
				self.rect.move_ip(0, -self.speed)
				# self.rect.move_ip(0, hits[0].rect.top - self.rect.bottom)
		if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
			self.still = False
			self.last_moved_left = True
			self.last_moved_right = False
			self.direction = "left"
			self.rect.move_ip(-self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False, pygame.sprite.collide_mask)
			if len(hits) != 0:
				self.rect.move_ip(self.speed, 0)
				# self.rect.move_ip(hits[0].rect.right - self.rect.left, 0)
		if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
			self.still = False
			self.last_moved_right = True
			self.last_moved_left = False
			self.direction = "right"
			self.rect.move_ip(self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False, pygame.sprite.collide_mask)
			if len(hits) != 0:
				self.rect.move_ip(-self.speed, 0)
				# self.rect.move_ip(hits[0].rect.left - self.rect.right, 0)
		self.location = self.rect.center
		self.animate()

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
					direction = (x - SCREEN_WIDTH / 2, y - SCREEN_HEIGHT / 2)
					return (origin, direction, self.gun.bullet_speed)
			else:
				if self.ammo > 0:
					self.reloading = True
					pygame.time.set_timer(RELOAD, self.gun.reload_time, loops = 1)
		return " "

class Cover(pygame.sprite.Sprite):
	def __init__(self, color, location, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = location
class Bullet(pygame.sprite.Sprite):
	def __init__(self, location, radius = 4):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([2*radius, 2*radius], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (127, 127, 127), (radius, radius), radius)
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

#create main display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Basic Pygame program')
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface = map_surface.convert()

#receive data about covers from server and create Cover objects
covers_data = client_socket.recv(8192)
covers_data = eval(covers_data.decode('utf-8'))
covers = pygame.sprite.Group()
for cover_data in covers_data:
	location, width, height = cover_data
	cover = Cover(BLACK, location, width, height)
	covers.add(cover)

#communicate with server about player information (id and initial location) of this client
my_username = input("Please input username: ")
client_socket.send(str.encode(my_username))
my_info = client_socket.recv(2048)
my_info = eval(my_info.decode('utf-8'))
my_id, my_location, my_health = my_info
client_socket.send(str.encode("received"))

#create Player object for this client
players = pygame.sprite.Group()
alive_players = pygame.sprite.Group()
dead_players = pygame.sprite.Group()
me = Player(my_id, my_username, my_location, my_health, PLAYER_COLOR, 7, 3)
players.add(me)
alive_players.add(me)

#get other information players
other_players = client_socket.recv(8192)
other_players = eval(other_players.decode('utf-8'))

#create Player objects for other players
for ID, values in other_players.items():
	if ID == me.ID:
		continue
	username, location, health = values
	players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))
	alive_players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))

#initialize Pygame
pygame.init()
clock = pygame.time.Clock()

#Pygame events
RELOAD = pygame.USEREVENT + 0

#Pygame fonts for texts
stats_font = pygame.font.SysFont("monospace", 30, bold = True)
reloading_font = pygame.font.SysFont("monospace", 15)
username_font = pygame.font.SysFont("monospace", 15)

#main loop
key_pressed = {pygame.K_w: False, pygame.K_UP: False, pygame.K_s: False, pygame.K_DOWN: False, pygame.K_d: False, pygame.K_RIGHT: False, pygame.K_a: False, pygame.K_LEFT: False, K_RSHIFT: False, K_LSHIFT: False}
mouse_pressed = {1: False, 2: False, 3: False, 4: False, 5: False}
done = False
while not done:
	map_surface.fill(BACKGROUND)
	if me.health <= 0:
		done = True
		continue
	for event in pygame.event.get():
		if event.type == QUIT:
			done = True
		if event.type == KEYDOWN:
			if event.key in key_pressed.keys():
				key_pressed[event.key] = True
			if event.key == pygame.K_r and not me.reloading:
				me.reloading = True
				pygame.time.set_timer(RELOAD, me.gun.reload_time, loops = 1)
		if event.type == KEYUP and event.key in key_pressed.keys():
			key_pressed[event.key] = False
		if event.type == MOUSEBUTTONDOWN:
			mouse_pressed[event.button] = True
		if event.type == MOUSEBUTTONUP:
			mouse_pressed[event.button] = False
		if event.type == RELOAD:
			me.reload()
	me.move(key_pressed)
	client_socket.send(str.encode(str(me.rect.center)))

	#update other players' location
	players_info = client_socket.recv(8192)
	players_info = eval(players_info.decode('utf-8'))
	IDs = list(players_info.keys())
	values = list(players_info.values())
	usernames, locations, healths = list(zip(*values))
	locations = dict(zip(IDs, locations))
	players_to_remove = []
	for player in alive_players.sprites():
		player.update(locations[player.ID], healths[player.ID])
		if player.health <= 0:
			alive_players.remove(player)
			dead_players.add(player)
		else:
			username_display = username_font.render(player.username, 1, BLACK)
			x, y = player.location
			map_surface.blit(username_display, (x - username_display.get_width() / 2, y - player.image.get_height() / 2 - username_display.get_height() / 2 - 5))

	#create Player objects for players who just joined
	if len(players.sprites()) != len(players_info):
		new_players = [ID for ID in IDs if ID not in [player.ID for player in players.sprites()]]
		for ID in new_players:
			username, location, health = players_info[ID]
			players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))
			alive_players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))

	#send bullet information to server
	if mouse_pressed[1] == True:
		client_socket.send(str.encode(str(me.fire())))
	else:
		client_socket.send(str.encode(" "))

	#receive bullet locations
	bullets = pygame.sprite.Group()
	bullets_location = client_socket.recv(16384)
	bullets_location = eval(bullets_location.decode('utf-8'))
	for location in bullets_location:
		bullets.add(Bullet(location))

	covers.draw(map_surface)
	alive_players.draw(map_surface)
	bullets.draw(map_surface)
	left, top = me.rect.center
	left -= SCREEN_WIDTH / 2
	top -= SCREEN_HEIGHT / 2
	screen.blit(map_surface, (0, 0), (left, top, SCREEN_WIDTH, SCREEN_HEIGHT))

	ammo_display = stats_font.render(str(me.gun.ammo) + "\\" + str(me.ammo), 1, BLACK)
	screen.blit(ammo_display, (SCREEN_WIDTH - ammo_display.get_width() - 25, SCREEN_HEIGHT - ammo_display.get_height() - 25))
	health_display = stats_font.render(str(me.health), 1, BLACK)
	screen.blit(health_display, (25, SCREEN_HEIGHT - ammo_display.get_height() - 25))
	if me.reloading:
		reloading_display = reloading_font.render("Reloading", 1, BLACK)
		screen.blit(reloading_display, (SCREEN_WIDTH / 2 - reloading_display.get_width() / 2, SCREEN_HEIGHT / 2 + me.rect.height / 2))
	pygame.display.flip()
	clock.tick(60)
	players.remove(players_to_remove)
print("Thanks for playing!")
client_socket.close()
pygame.quit()