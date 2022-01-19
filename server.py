import socket
import os
import random
import math
from _thread import *
import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location, character):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.health = 100
		self.image = pygame.Surface([38, 38], pygame.SRCALPHA)
		self.rect = self.image.get_rect(center = location)
		self.location = location
		self.character = character
		self.state = "walking"
		self.animation_count = 0
		self.angle = 0
		self.gun_name = ""
	def update(self, location, character, state, animation_count, angle, gun_name):
		self.location = location
		self.rect.center = location
		self.character = character
		self.state = state
		self.animation_count = animation_count
		self.angle = angle
		self.gun_name = gun_name
class Cover(pygame.sprite.Sprite):
	def __init__(self, x, y, width, height):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([width, height])
		self.rect = self.image.get_rect()
		self.width = width
		self.height = height
		self.rect.x = x
		self.rect.y = y
		self.location = (self.rect.x, self.rect.y)
class Bullet(pygame.sprite.Sprite):
	def __init__(self, origin, direction, magnitude):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.Surface([2*4, 2*4], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (127, 127, 127), (4, 4), 4)
		self.damage = 10
		o_x, o_y = origin
		x, y = direction
		self.location = (math.ceil(o_x + (38 + 3) * (x / math.sqrt(x**2 + y**2))), math.ceil(o_y + (38 + 3) * (y / math.sqrt(x**2 + y**2))))
		self.rect.center = self.location
		scale = magnitude / math.sqrt(x**2 + y**2)
		self.velocity = (x * scale, y * scale)
	def update(self):
		v_x, v_y = self.velocity
		self.rect.x += v_x
		self.rect.y += v_y
		self.location = self.rect.center
		players_hit = pygame.sprite.spritecollide(self, players, False)
		if len(players_hit) != 0:
			for player in players_hit:
				player.health = player.health - self.damage
			self.kill()
			return
		covers_hit = pygame.sprite.spritecollide(self, covers, False)
		if len(covers_hit) != 0:
			self.kill()
class Gun(pygame.sprite.Sprite):
	def __init__(self, name, location):
		pygame.sprite.Sprite.__init__(self)
		self.name = name
		self.location = location
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 768
MAP_WIDTH = 5760 + DISPLAY_WIDTH
MAP_HEIGHT = 5760 + DISPLAY_HEIGHT
covers_count = 100
guns_count = 200

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
player_count = 0
try:
	ServerSocket.bind((host, port))
except socket.error as e:
	print(str(e))

#initialize map
covers = pygame.sprite.Group()
covers.add(Cover(0, 0, MAP_WIDTH, DISPLAY_HEIGHT // 2))
covers.add(Cover(0, MAP_HEIGHT - DISPLAY_HEIGHT // 2, MAP_WIDTH, DISPLAY_HEIGHT // 2))
covers.add(Cover(0, 0, DISPLAY_WIDTH // 2, MAP_HEIGHT))
covers.add(Cover(MAP_WIDTH - DISPLAY_WIDTH // 2, 0, DISPLAY_WIDTH // 2, MAP_HEIGHT))
for i in range(covers_count):
	cover = Cover(random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT), random.randint(4, 8) * 32, random.randint(4, 8) * 32)
	while True:
		if not pygame.sprite.spritecollide(cover, covers, False): break
		cover.rect.x, cover.rect.y = random.randint(0, MAP_WIDTH), random.randint(0, MAP_HEIGHT)
	cover.location = (cover.rect.x, cover.rect.y)
	covers.add(cover)

gun_list = ["odin", "spectre", "vandal"]
guns = pygame.sprite.Group()
for i in range(guns_count):
	name = random.choice(gun_list)
	location = (random.randint(DISPLAY_WIDTH / 2, MAP_WIDTH - DISPLAY_WIDTH / 2), random.randint(DISPLAY_HEIGHT / 2, MAP_HEIGHT - DISPLAY_HEIGHT / 2))
	gun = Gun(name, location)
	guns.add(gun)
players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
print('Waiting for a Connection..')
ServerSocket.listen()
players_to_remove = []

def threaded_client(connection):
	global player_count
	player_id = player_count
	player_count += 1
	connection.send(str.encode(str([(cover.location, cover.width, cover.height) for cover in covers.sprites()])))
	confirmation = connection.recv(64)
	connection.send(str.encode(str([(gun.name, gun.location) for gun in guns.sprites()])))
	initial_data = connection.recv(64)
	username, character = eval(initial_data.decode('utf-8'))
	location = (random.uniform(DISPLAY_WIDTH / 2, MAP_WIDTH - DISPLAY_WIDTH / 2), random.uniform(DISPLAY_HEIGHT / 2, MAP_HEIGHT - DISPLAY_HEIGHT / 2))
	player = Player(player_id, username, location, character)
	players.add(player)
	connection.send(str.encode(str((player_id, location, 100))))
	connection.recv(64)
	data = {}
	for player in players.sprites():
		data[player.ID] = (player.username, player.location, player.health, player.character, player.state, player.animation_count, player.angle)
	connection.send(str.encode(str(data)))
	while True:
		new_info = connection.recv(2048)
		if not new_info:
			break
		location, character, state, animation_count, angle, gun_name = eval(new_info.decode('utf-8'))
		for player in players.sprites():
			if player.ID == player_id:
				player.update(location, character, state, animation_count, angle, gun_name)
			data[player.ID] = (player.username, player.location, player.health, player.character, player.state, player.animation_count, player.angle, player.gun_name)
		connection.send(str.encode(str(data)))
		bullets.update()
		bullet = connection.recv(1024)
		if bullet.decode('utf-8') != " ":
			origin, direction, magnitude = eval(bullet.decode('utf-8'))
			bullets.add(Bullet(origin, direction, magnitude))
		connection.send(str.encode(str([bullet.location for bullet in bullets])))
	connection.close()

while True:
	Client, address = ServerSocket.accept()
	print('Connected to: ' + address[0] + ':' + str(address[1]))
	start_new_thread(threaded_client, (Client, ))
	print('Number of Players: ' + str(player_count + 1))
ServerSocket.close()