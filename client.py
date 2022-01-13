import socket
import pygame
import time
import math
from pygame.locals import *
from entities import *

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

client_socket = socket.socket()
HOST = '127.0.0.1'
PORT = 1233
print('Waiting for connection')
try:
	client_socket.connect((HOST, PORT))
except socket.error as e:
	print(str(e))

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

#create main display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Valo.mini')
map_surface = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
map_surface = map_surface.convert()
display_surface = pygame.Surface((SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
display_surface = display_surface.convert()

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
me = Player(my_id, my_username, my_location, my_health, 2.5)
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
	players.add(Player(ID, username, location, health, 2.5))
	alive_players.add(Player(ID, username, location, health, 2.5))

#initialize Pygame
pygame.init()
clock = pygame.time.Clock()

#Pygame fonts for texts
stats_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 20)
reloading_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 10)
username_font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 10)

#main loop
key_pressed = {pygame.K_w: False, pygame.K_UP: False, pygame.K_s: False, pygame.K_DOWN: False, pygame.K_d: False, pygame.K_RIGHT: False, pygame.K_a: False, pygame.K_LEFT: False, K_RSHIFT: False, K_LSHIFT: False}
mouse_pressed = {1: False, 2: False, 3: False, 4: False, 5: False}
done = False
while not done:
	map_surface.blit(BACKGROUND, (250, 250))
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

	#move player
	me.still = True
	x, y = 0, 0
	speed = me.speed
	if (key_pressed[pygame.K_w] or key_pressed[pygame.K_UP] or key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]) and (key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]):
		speed = math.ceil(speed / math.sqrt(2))
	if key_pressed[pygame.K_RSHIFT] or key_pressed[pygame.K_LSHIFT]:
		speed = math.ceil(speed / 2)
	if key_pressed[pygame.K_w] or key_pressed[pygame.K_UP]:
		me.still = False
		y = -speed
	if key_pressed[pygame.K_s] or key_pressed[pygame.K_DOWN]:
		me.still = False
		y = speed
	if key_pressed[pygame.K_a] or key_pressed[pygame.K_LEFT]:
		me.still = False
		x = -speed
	if key_pressed[pygame.K_d] or key_pressed[pygame.K_RIGHT]:
		me.still = False
		x = speed
	me.rect.move_ip(x, y)

	#handle collisions
	hits = pygame.sprite.spritecollide(me, covers, False, pygame.sprite.collide_mask)
	if len(hits) != 0:
		me.rect.move_ip(-x, -y)
	me.location = me.rect.center
	me.animate(pygame.mouse.get_pos())
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
			map_surface.blit(username_display, (x - username_display.get_width() / 2, y - username_display.get_height() / 2 - 20))

	#create Player objects for players who just joined
	if len(players.sprites()) != len(players_info):
		new_players = [ID for ID in IDs if ID not in [player.ID for player in players.sprites()]]
		for ID in new_players:
			username, location, health = players_info[ID]
			players.add(Player(ID, username, location, health, 2.5))
			alive_players.add(Player(ID, username, location, health, 2.5))

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
	left -= SCREEN_WIDTH / 4
	top -= SCREEN_HEIGHT / 4
	display_surface.blit(map_surface, (0, 0), (left, top, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
	screen.blit(pygame.transform.scale2x(display_surface), (0, 0))

	ammo_display = stats_font.render(str(me.gun.ammo) + "|" + str(me.ammo), 1, BLACK)
	screen.blit(ammo_display, (SCREEN_WIDTH - ammo_display.get_width() - 25, SCREEN_HEIGHT - ammo_display.get_height() - 25))
	health_display = stats_font.render(str(me.health), 1, BLACK)
	screen.blit(health_display, (25, SCREEN_HEIGHT - ammo_display.get_height() - 25))
	if me.reloading:
		reloading_display = reloading_font.render("Reloading", 1, BLACK)
		screen.blit(reloading_display, (SCREEN_WIDTH / 2 - reloading_display.get_width() / 2, SCREEN_HEIGHT / 2 + reloading_display.get_height() / 2 + 30))
	pygame.display.flip()
	clock.tick(60)
	players.remove(players_to_remove)
print("Thanks for playing!")
client_socket.close()
pygame.quit()