import socket
import pygame
import time
import math
from pygame.locals import *
from entities import *
from menu import *

def draw_group(group, center, surface):
	c_x, c_y = center
	for sprite in group:
		if abs(c_x - sprite.rect.left) > DISPLAY_WIDTH and abs(c_x - sprite.rect.right) > DISPLAY_WIDTH:
			continue
		if abs(c_y - sprite.rect.top) > DISPLAY_HEIGHT and abs(c_y - sprite.rect.bottom) > DISPLAY_HEIGHT:
			continue
		left, top =  (sprite.rect.x - c_x) + DISPLAY_WIDTH / 2, (sprite.rect.y - c_y) + DISPLAY_HEIGHT / 2
		surface.blit(sprite.image, (left, top))
		if hasattr(sprite, 'username'):
			username_display = username_font.render(sprite.username, 1, BLACK)
			x, y = sprite.rect.center
			left, top =  (x - c_x) + DISPLAY_WIDTH / 2 - username_display.get_width() / 2, (y - c_y) + DISPLAY_HEIGHT / 2 - username_display.get_height() / 2 - 35
			surface.blit(username_display, (left, top))

def game(username):
	client_socket = socket.socket()
	HOST = '127.0.0.1'
	PORT = 1233
	print('Waiting for connection')
	try:
		client_socket.connect((HOST, PORT))
	except socket.error as e:
		print(str(e))

	#receive data about covers from server and create Cover objects
	covers_data = client_socket.recv(8192)
	covers_data = eval(covers_data.decode('utf-8'))
	covers = pygame.sprite.Group()
	for cover_data in covers_data:
		location, width, height = cover_data
		cover = Cover(location, width, height)
		covers.add(cover)

	#communicate with server about player information (id and initial location) of this client
	my_username = username
	client_socket.send(str.encode(my_username))
	my_info = client_socket.recv(2048)
	my_info = eval(my_info.decode('utf-8'))
	my_id, my_location, my_health = my_info
	client_socket.send(str.encode("received"))

	#create Player object for this client
	players = pygame.sprite.Group()
	alive_players = pygame.sprite.Group()
	dead_players = pygame.sprite.Group()
	me = Player(my_id, my_username, my_location, my_health, 5)
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
		players.add(Player(ID, username, location, health, 5))
		alive_players.add(Player(ID, username, location, health, 5))
	done = False
	while not done:
		if me.health <= 0:
			done = True
			continue

		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
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

		#send this player's location to the server
		client_socket.send(str.encode(str(me.location)))

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
				players.add(Player(ID, username, location, health, 5))
				alive_players.add(Player(ID, username, location, health, 5))

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


		left, top = me.rect.center
		left -= DISPLAY_WIDTH / 2
		top -= DISPLAY_HEIGHT / 2
		display_surface.blit(MAP, (0, 0), (left, top, DISPLAY_WIDTH, DISPLAY_HEIGHT))
		draw_group(covers, me.rect.center, display_surface)
		draw_group(alive_players, me.rect.center, display_surface)
		draw_group(bullets, me.rect.center, display_surface)
		screen.blit(display_surface, (0, 0))

		ammo_display = stats_font.render(str(me.gun.ammo) + "|" + str(me.ammo), 1, BLACK)
		screen.blit(ammo_display, (DISPLAY_WIDTH - ammo_display.get_width() - 25, DISPLAY_HEIGHT - ammo_display.get_height() - 25))
		health_display = stats_font.render(str(me.health), 1, BLACK)
		screen.blit(health_display, (25, DISPLAY_HEIGHT - ammo_display.get_height() - 25))
		if me.reloading:
			reloading_display = reloading_font.render("Reloading", 1, BLACK)
			screen.blit(reloading_display, (DISPLAY_WIDTH / 2 - reloading_display.get_width() / 2, DISPLAY_HEIGHT / 2 + reloading_display.get_height() / 2 + 30))
		pygame.display.flip()
		clock.tick(60)
		players.remove(players_to_remove)
	end_display(screen)