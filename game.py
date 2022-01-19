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
		if hasattr(sprite, 'username'):
			username_display = username_font.render(sprite.username, 1, BLACK)
			x, y = sprite.rect.center
			left, top =  (x - c_x) + DISPLAY_WIDTH / 2 - username_display.get_width() / 2, (y - c_y) + DISPLAY_HEIGHT / 2 - username_display.get_height() / 2 - 35
			surface.blit(username_display, (left, top))
			# if sprite.gun_name != "":
			# 	gun_display = pygame.transform.rotate(gun_images[sprite.gun_name]["top"], sprite.angle - 180)
			# 	gun_display_rect = gun_display.get_rect(center = (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2))
			# 	surface.blit(gun_display, gun_display_rect)
		if abs(c_x - sprite.rect.left) > DISPLAY_WIDTH and abs(c_x - sprite.rect.right) > DISPLAY_WIDTH:
			continue
		if abs(c_y - sprite.rect.top) > DISPLAY_HEIGHT and abs(c_y - sprite.rect.bottom) > DISPLAY_HEIGHT:
			continue
		left, top =  (sprite.rect.x - c_x) + DISPLAY_WIDTH / 2, (sprite.rect.y - c_y) + DISPLAY_HEIGHT / 2
		surface.blit(sprite.image, (left, top))

def game(username, character):
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
	client_socket.send(str.encode("received covers"))
	covers_data = eval(covers_data.decode('utf-8'))
	covers = pygame.sprite.Group()
	for cover_data in covers_data:
		location, width, height = cover_data
		cover = Cover(location, width, height)
		covers.add(cover)
		x, y = location
		for i in range(0, width, 32):
			for j in range(0, height, 32):
				MAP.blit(stone_texture, (x + i, y + j))

	guns_data = client_socket.recv(8192)
	guns_data = eval(guns_data.decode('utf-8'))
	guns = pygame.sprite.Group()
	for gun_data in guns_data:
		name, location = gun_data
		stats = gun_stats[name]
		gun = Gun(name, location, stats["clip_size"], stats["fire_rate"], stats["bullet_speed"], stats["reload_time"], stats["full_auto"])
		guns.add(gun)
	#communicate with server about player information (id and initial location) of this client
	my_username = username
	my_character = character
	client_socket.send(str.encode(str((my_username, my_character))))
	my_info = client_socket.recv(2048)
	my_info = eval(my_info.decode('utf-8'))
	my_id, my_location, my_health = my_info
	client_socket.send(str.encode("received"))

	#sound effects
	mixer.music.load("assets/background/music/game_bg.wav")
	mixer.music.play(-1)

	#create Player object for this client
	players = pygame.sprite.Group()
	alive_players = pygame.sprite.Group()
	dead_players = pygame.sprite.Group()
	me = Player(my_id, my_username, my_location, my_health, 5, my_character)
	players.add(me)
	alive_players.add(me)

	#get other information players
	other_players = client_socket.recv(8192)
	other_players = eval(other_players.decode('utf-8'))

	#create Player objects for other players
	for ID, values in other_players.items():
		if ID == me.ID:
			continue
		username, location, health, character, state, animation_count, angle = values
		players.add(Player(ID, username, location, health, 5, character, state))
		alive_players.add(Player(ID, username, location, health, 5, character, state))
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
		client_socket.send(str.encode(str((me.location, me.character, me.state, me.animation_count, me.angle, me.gun_name))))

		#update other players' location
		players_info = client_socket.recv(8192)
		players_info = eval(players_info.decode('utf-8'))
		IDs = list(players_info.keys())
		values = list(players_info.values())
		usernames, locations, healths, characters, states, animation_counts, angles, gun_names = list(zip(*values))
		locations = dict(zip(IDs, locations))
		players_to_remove = []
		for player in alive_players.sprites():
			player.update(locations[player.ID], healths[player.ID], characters[player.ID], states[player.ID], animation_counts[player.ID], angles[player.ID], gun_names[player.ID])
			if player.health <= 0:
				alive_players.remove(player)
				dead_players.add(player)

		#create Player objects for players who just joined
		if len(players.sprites()) != len(players_info):
			new_players = [ID for ID in IDs if ID not in [player.ID for player in players.sprites()]]
			for ID in new_players:
				username, location, health, character, state, animation_count, angle, gun_name = players_info[ID]
				players.add(Player(ID, username, location, health, 5, character, state, angle, gun_name))
				alive_players.add(Player(ID, username, location, health, 5, character, state, angle, gun_name))

		#send bullet information to server
		if mouse_pressed[1] == True and me.gun is not None:
			client_socket.send(str.encode(str(me.fire())))
		else:
			client_socket.send(str.encode(" "))
			me.fired = False

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
		# draw_group(covers, me.rect.center, display_surface)
		draw_group(guns, me.rect.center, display_surface)
		draw_group(bullets, me.rect.center, display_surface)
		draw_group(alive_players, me.rect.center, display_surface)
		screen.blit(display_surface, (0, 0))

		if me.gun is not None:
			ammo_display = stats_font.render(str(me.gun.ammo) + "|" + str(me.ammo), 1, BLACK)
		else:
			ammo_display = stats_font.render(str(0) + "|" + str(me.ammo), 1, BLACK)
		screen.blit(ammo_display, (DISPLAY_WIDTH - ammo_display.get_width() - 25, DISPLAY_HEIGHT - ammo_display.get_height() - 25))
		health_display = stats_font.render(str(me.health), 1, BLACK)
		screen.blit(health_display, (25, DISPLAY_HEIGHT - ammo_display.get_height() - 25))
		if me.reloading:
			reloading_display = reloading_font.render("Reloading", 1, BLACK)
			screen.blit(reloading_display, (DISPLAY_WIDTH / 2 - reloading_display.get_width() / 2, DISPLAY_HEIGHT / 2 + reloading_display.get_height() / 2 + 30))
		guns_hit = pygame.sprite.spritecollide(me, guns, False, pygame.sprite.collide_mask)
		if len(guns_hit) != 0:
			gun_info_display = reloading_font.render("Press E to pick up " + guns_hit[0].name, 1, BLACK)
			screen.blit(gun_info_display, (DISPLAY_WIDTH / 2 - gun_info_display.get_width() / 2, DISPLAY_HEIGHT / 2 + gun_info_display.get_height() / 2 + 50))
			if key_pressed[pygame.K_e]:
				me.gun = guns_hit[0]
				me.gun_name = guns_hit[0].name
				me.state = "ranged"
				guns.remove(guns_hit[0])
		pygame.display.flip()
		clock.tick(60)
		players.remove(players_to_remove)
	end_display(screen)