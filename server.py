import socket
import os
import random
import math
from _thread import *
import pygame
from pygame.locals import *

class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, location):
		pygame.sprite.Sprite.__init__(self)
		self.ID = ID
		self.username = username
		self.health = 100
		self.location = location
		self.image = pygame.Surface([2*7, 2*7], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (7,135,123), (7, 7), 7)
		self.rect.center = location
	def set_location(self, location):
		self.location = location
		self.rect.center = location
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
		self.image = pygame.Surface([2*3, 2*3], pygame.SRCALPHA)
		self.rect = pygame.draw.circle(self.image, (127, 127, 127), (3, 3), 3)
		self.damage = 10
		o_x, o_y = origin
		x, y = direction
		self.location = (math.ceil(o_x + (7 + 3) * (x / math.sqrt(x**2 + y**2))), math.ceil(o_y + (7 + 3) * (y / math.sqrt(x**2 + y**2))))
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
MAP_WIDTH = 5000
MAP_HEIGHT = 3750
covers_count = 100

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
covers.add(Cover(0, 0, MAP_WIDTH, 250))
covers.add(Cover(0, MAP_HEIGHT - 250, MAP_WIDTH, 250))
covers.add(Cover(0, 0, 250, MAP_HEIGHT))
covers.add(Cover(MAP_WIDTH - 250, 0, 250, MAP_HEIGHT))
for i in range(100):
	cover = Cover(random.uniform(0, MAP_WIDTH), random.uniform(0, MAP_HEIGHT), random.uniform(40, 80), random.uniform(40, 80))
	while True:
		if not pygame.sprite.spritecollide(cover, covers, False): break
		cover.rect.x, cover.rect.y = random.uniform(0, MAP_WIDTH), random.uniform(0, MAP_HEIGHT)
	cover.location = (cover.rect.x, cover.rect.y)
	covers.add(cover)

players = pygame.sprite.Group()
bullets = pygame.sprite.Group()
print('Waiting for a Connection..')
ServerSocket.listen(5)
players_to_remove = []

def threaded_client(connection):
	global player_count
	player_id = player_count
	player_count += 1
	connection.send(str.encode(str([(cover.location, cover.width, cover.height) for cover in covers.sprites()])))
	username = connection.recv(64)
	location = (random.uniform(250, MAP_WIDTH - 250), random.uniform(250, MAP_HEIGHT - 250))
	player = Player(player_id, username, location)
	players.add(player)
	connection.send(str.encode(str((player_id, location, 100))))
	connection.recv(64)
	data = {}
	for player in players.sprites():
		data[player.ID] = (player.username, player.location, player.health)
	connection.send(str.encode(str(data)))
	while True:
		new_location = connection.recv(2048)
		if not new_location:
			break
		new_location = eval(new_location.decode('utf-8'))
		for player in players.sprites():
			if player.ID == player_id:
				player.set_location(new_location)
			data[player.ID] = (player.username, player.location, player.health)
		connection.send(str.encode(str(data)))
		bullets.update()
		bullet = connection.recv(1024)
		if bullet.decode('utf-8') != "empty":
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