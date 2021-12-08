import socket
import pygame
import time
import math
from pygame.locals import *


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
MAP_WIDTH = 2500
MAP_HEIGHT = 2500
USERNAME = "asdasd"

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (7,135,123)

#classes
class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location, health, color, radius, speed):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.radius = radius
		self.health = health
		self.speed = speed
		self.time_last_fired = 0
		self.fire_rate = 5 		#bullets per second
		self.auto_firing = True	#True if automatic, False if manual
		self.image = pygame.Surface([2*radius, 2*radius], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, color, (radius, radius), radius)
		self.rect.center = location
	def update(self, location, health):
		self.rect.center = location
		self.health = health
	def move(self, key_pressed):
		if key_pressed[pygame.K_RSHIFT] or key_pressed[pygame.K_LSHIFT]:
			self.speed = 2
		else:
			self.speed = 3
		if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
			self.rect.move_ip(0, -self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(0, hits[0].rect.bottom - self.rect.top)
		if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
			self.rect.move_ip(0, self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(0, hits[0].rect.top - self.rect.bottom)
		if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
			self.rect.move_ip(-self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(hits[0].rect.right - self.rect.left, 0)
		if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
			self.rect.move_ip(self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(hits[0].rect.left - self.rect.right, 0)
class Cover(pygame.sprite.Sprite):
	def __init__(self, color, location, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.rect = self.image.get_rect()
		self.rect.x, self.rect.y = location
class Bullet(pygame.sprite.Sprite):
	def __init__(self, location, radius = 3):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([2*radius, 2*radius], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (127, 127, 127), (radius, radius), radius)
		self.rect.center = location

#create main display
screen = pygame.display.set_mode((500, 500))
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

#main loop
key_pressed = {pygame.K_w: False, pygame.K_UP: False, pygame.K_s: False, pygame.K_DOWN: False, pygame.K_d: False, pygame.K_RIGHT: False, pygame.K_a: False, pygame.K_LEFT: False, K_RSHIFT: False, K_LSHIFT: False}
mouse_pressed = {1: False, 2: False, 3: False, 4: False, 5: False}
done = False
while not done:
	for event in pygame.event.get():
		if event.type == QUIT:
			done = True
		if event.type == KEYDOWN and event.key in key_pressed.keys():
			key_pressed[event.key] = True
		if event.type == KEYUP and event.key in key_pressed.keys():
			key_pressed[event.key] = False
		if event.type == MOUSEBUTTONDOWN:
			mouse_pressed[event.button] = True
		if event.type == MOUSEBUTTONUP:
			mouse_pressed[event.button] = False
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
	#create Player objects for players who just joined
	if len(players.sprites()) != len(players_info):
		new_players = [ID for ID in IDs if ID not in [player.ID for player in players.sprites()]]
		for ID in new_players:
			username, location, health = players_info[ID]
			players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))
			alive_players.add(Player(ID, username, location, health, PLAYER_COLOR, 7, 3))

	#send bullet information to server
	if mouse_pressed[1] == True:
		current_time = time.time()
		if current_time - me.time_last_fired > 1 / me.fire_rate:
			origin = me.rect.center
			x, y = pygame.mouse.get_pos()
			direction = (x - 250, y - 250)
			client_socket.send(str.encode(str((origin, direction, 10))))
			me.time_last_fired = current_time
		else:
			client_socket.send(str.encode("empty"))
	else:
		client_socket.send(str.encode("empty"))

	#receive bullet locations
	bullets = pygame.sprite.Group()
	bullets_location = client_socket.recv(16384)
	bullets_location = eval(bullets_location.decode('utf-8'))
	for location in bullets_location:
		bullets.add(Bullet(location))


	map_surface.fill(WHITE)
	covers.draw(map_surface)
	alive_players.draw(map_surface)
	bullets.draw(map_surface)
	left, top = me.rect.center
	left -= 250
	top -= 250
	screen.blit(map_surface, (0, 0), (left, top, 500, 500))
	pygame.display.flip()
	clock.tick(60)
	players.remove(players_to_remove)
	if me.health <= 0:
		done = True
		continue
	# Input = input('Say Something: ')
	# client_socket.send(str.encode(Input))
	# Response = client_socket.recv(1024)
	# print(Response.decode('utf-8'))
print("Thanks for playing!")
client_socket.close()
pygame.quit()