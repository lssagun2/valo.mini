import socket
import pygame
import time
from pygame.locals import *


#connect to server
ClientSocket = socket.socket()
HOST = '127.0.0.1'
PORT = 1233
print('Waiting for connection')
try:
	ClientSocket.connect((HOST, PORT))
except socket.error as e:
	print(str(e))

#game variables
MAP_WIDTH = 2000
MAP_HEIGHT = 2000
USERNAME = "asdasd"

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PLAYER = (7,135,123)

#classes
class Player(pygame.sprite.Sprite):
	def __init__(self, ID, username, color, radius, speed):
		pygame.sprite.Sprite.__init__(self)
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
#initialize Pygame
pygame.init()
clock = pygame.time.Clock()

#create main display
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption('Basic Pygame program')
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface = map_surface.convert()

#receive data about covers from server and create Cover objects
covers_data = ClientSocket.recv(4096)
covers_data = eval(covers_data.decode('utf-8'))
covers = pygame.sprite.Group()
for cover_data in covers_data:
	x, y, width, height = cover_data
	cover = Cover(BLACK, width, height)
	cover.rect.x = x
	cover.rect.y = y
	covers.add(cover)

#communicate with server about player information (id and initial location) of this client
username = input("Please input username: ")
ClientSocket.send(str.encode(username))
my_info = ClientSocket.recv(2048)
my_info = eval(my_info.decode('utf-8'))
my_id, initial_x, initial_y = my_info

#create Player object for this client
players = pygame.sprite.Group()
me = Player(1, username, PLAYER, 7, 3)
me.rect.x = initial_x
me.rect.y = initial_y
players.add(me)

#retrieve list of players




#main loop
done = False
while not done:
	for event in pygame.event.get():
		if event.type == QUIT:
			done = True
		# if event.type == KEYDOWN and event.key in pressed.keys():
		# 	pressed[event.key] = True
		# if event.type == KEYUP and event.key in pressed.keys():
		# 	pressed[event.key] = False
	# me.move(pressed)
	map_surface.fill(WHITE)
	players.draw(map_surface)
	covers.draw(map_surface)
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
	screen.blit(map_surface, (0, 0), (0, 0, 500, 500))
	pygame.display.flip()
	clock.tick(60)

	# Input = input('Say Something: ')
	# ClientSocket.send(str.encode(Input))
	# Response = ClientSocket.recv(1024)
	# print(Response.decode('utf-8'))

ClientSocket.close()