import socket
import pygame
import time
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
MAP_WIDTH = 2000
MAP_HEIGHT = 2000
USERNAME = "asdasd"

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER_COLOR = (7,135,123)

#classes
class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, color, radius, speed):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.health = 100
		self.speed = 1
		self.radius = radius
		self.speed = speed
		self.image = pygame.Surface([2*radius, 2*radius], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, color, (radius, radius), radius)
	def move(self, pressed):
		if pressed[pygame.K_RSHIFT] or pressed[pygame.K_LSHIFT]:
			self.speed = 2
		else:
			self.speed = 3
		if pressed[pygame.K_w] or pressed[pygame.K_UP]:
			if self.rect.y - self.speed < 0:
				self.rect.move_ip(0, -self.rect.y)
			else:
				self.rect.move_ip(0, -self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(0, hits[0].rect.bottom - self.rect.top)
		if pressed[pygame.K_s] or pressed[pygame.K_DOWN]:
			if self.rect.y + 2 * self.radius + self.speed > MAP_HEIGHT:
				self.rect.move_ip(0, MAP_HEIGHT - self.rect.y - 2 * self.radius)
			else:
				self.rect.move_ip(0, self.speed)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(0, hits[0].rect.top - self.rect.bottom)
		if pressed[pygame.K_a] or pressed[pygame.K_LEFT]:
			if self.rect.x - self.speed < 0:
				self.rect.move_ip(-self.rect.x, 0)
			else:
				self.rect.move_ip(-self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(hits[0].rect.right - self.rect.left, 0)
		if pressed[pygame.K_d] or pressed[pygame.K_RIGHT]:
			if self.rect.x + 2 * self.radius + self.speed  > MAP_WIDTH:
				self.rect.move_ip(MAP_WIDTH - self.rect.x - 2 * self.radius, 0)
			else:
				self.rect.move_ip(self.speed, 0)
			hits = pygame.sprite.spritecollide(self, covers, False)
			if len(hits) != 0:
				self.rect.move_ip(hits[0].rect.left - self.rect.right, 0)
class Cover(pygame.sprite.Sprite):
	def __init__(self, color, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.rect = self.image.get_rect()

#create main display
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Basic Pygame program')
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface = map_surface.convert()

#receive data about covers from server and create Cover objects
covers_data = client_socket.recv(4096)
covers_data = eval(covers_data.decode('utf-8'))
covers = pygame.sprite.Group()
for cover_data in covers_data:
	x, y, width, height = cover_data
	cover = Cover(BLACK, width, height)
	cover.rect.x = x
	cover.rect.y = y
	covers.add(cover)

#communicate with server about player information (id and initial location) of this client
my_username = input("Please input username: ")
client_socket.send(str.encode(my_username))
my_info = client_socket.recv(2048)
my_info = eval(my_info.decode('utf-8'))
my_id, location = my_info

#create Player object for this client
players = pygame.sprite.Group()
me = Player(my_id, my_username, PLAYER_COLOR, 7, 3)
me.rect.x = location[0]
me.rect.y = location[1]
players.add(me)

#get other information players
other_players = client_socket.recv(8192)
other_usernames, other_locations = eval(other_players.decode('utf-8'))

#create Player objects for other players
for i in range(len(other_locations)):
	if i == my_id:
		continue
	if other_usernames[i] is None:
		continue
	username = other_usernames[i]
	location = other_locations[i]
	player = Player(i, username, PLAYER_COLOR, 7, 3)
	player.rect.x = location[0]
	player.rect.y = location[1]
	players.add(player)
for player in players.sprites():
	print(player)
#initialize Pygame
pygame.init()
clock = pygame.time.Clock()



#main loop
pressed = {pygame.K_w: False, pygame.K_UP: False, pygame.K_s: False, pygame.K_DOWN: False, pygame.K_d: False, pygame.K_RIGHT: False, pygame.K_a: False, pygame.K_LEFT: False, K_RSHIFT: False, K_LSHIFT: False}
done = False
while not done:
	for event in pygame.event.get():
		if event.type == QUIT:
			done = True
		if event.type == KEYDOWN and event.key in pressed.keys():
			pressed[event.key] = True
		if event.type == KEYUP and event.key in pressed.keys():
			pressed[event.key] = False
	me.move(pressed)
	client_socket.send(str.encode(str((me.rect.x, me.rect.y))))
	other_players = client_socket.recv(8192)
	other_usernames, other_locations = eval(other_players.decode('utf-8'))
	for i in range(len(other_locations)):
		if i == my_id:
			continue
		if other_locations[i] is None:
			continue
		location = other_locations[i]
		username = other_usernames[i]
		found = False
		for player in players.sprites():
			if player.ID != i:
				continue
			found = True
			player.rect.x = location[0]
			player.rect.y = location[1]
		if not found:
			new_player = Player(i, username, PLAYER_COLOR, 7, 3)
			new_player.rect.x = location[0]
			new_player.rect.y = location[1]
			players.add(new_player)
	map_surface.fill(WHITE)
	covers.draw(map_surface)
	players.draw(map_surface)
	left = me.rect.x - 250
	if left < 0:
		left = 0
	elif left + 500 > MAP_WIDTH:
		left = MAP_WIDTH - 500
	top = me.rect.y - 250
	if top < 0:
		top = 0
	elif top + 500 > MAP_HEIGHT:
		top = MAP_HEIGHT - 500
	screen.blit(map_surface, (0, 0), (left, top, 500, 500))
	pygame.display.flip()
	clock.tick(60)

	# Input = input('Say Something: ')
	# client_socket.send(str.encode(Input))
	# Response = client_socket.recv(1024)
	# print(Response.decode('utf-8'))

client_socket.close()