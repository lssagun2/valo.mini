from variables import *
import pygame, cv2, sys
from pygame.locals import *
from pygame import mixer
from game import *

def draw_text(surface, font, text, location, color):
	# font = pygame.font.Font(font_name, size)
	text_surface = font.render(text, True, color)
	text_rect = text_surface.get_rect()
	text_rect.center = location
	surface.blit(text_surface, text_rect)

def main_menu(surface):
	mixer.music.load("assets/background/music/game_bg.mp3")
	mixer.music.play(0)
	options = [('Start Game', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 30), request_username), ('Credits', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 80), credits), ('Quit', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 200))]
	selected = 0
	exit = False
	while not exit:
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
			if event.type == KEYDOWN:
				if event.key == pygame.K_RETURN:
					options[selected][2](surface)
				if event.key == pygame.K_w or event.key == pygame.K_UP:
					selected = (selected - 1) % 4
				if event.key == pygame.K_s or event.key == pygame.K_DOWN:
					selected = (selected + 1) % 4
		surface.blit(MENU_BACKGROUND, (0, 0))
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 60)
		draw_text(surface, font, 'VALORANT MINI', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 - 100), WHITE)
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 40)
		for option in options:
			draw_text(surface, font, option[0], option[1], WHITE)
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 30)
		draw_text(surface, font, '*', (options[selected][1][0] - 230, options[selected][1][1]), WHITE)
		pygame.display.flip()
	mixer.music.stop()

def request_username(surface):
	submitted = False
	username = ""
	while not submitted:
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
			if event.type == KEYDOWN:
				if event.key == pygame.K_RETURN:
					game(username)
				elif event.key == pygame.K_BACKSPACE:
					username = username[0:-1]
				elif event.key == K_MINUS:
					username = username + "_"
				elif event.key <= 127:
					username = username + chr(event.key)
		surface.blit(MENU_BACKGROUND, (0, 0))
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 60)
		draw_text(surface, font, 'Input Username', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 - 100), WHITE)
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 40)
		draw_text(surface, font, username, (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 30), WHITE)
		pygame.display.flip()
# def character_style(surface):
# 	char_style1 = pygame.image.load('assets/characters/character1/walking1.png')
# 	char_style1 = pygame.transform.scale(char_style1, (648, 648))
# 	char_style2 = pygame.image.load('assets/characters/character2/walking1.png')
# 	char_style2 = pygame.transform.scale(char_style2, (648, 648))
# 	char_style3 = pygame.image.load('assets/characters/character3/walking1.png')
# 	char_style3 = pygame.transform.scale(char_style3, (648, 648))
# 	surface.blit(char_style1, (-150, 30))
# 	surface.blit(char_style2, (300, 10))
# 	surface.blit(char_style3, (700, -10))
#
# 	character1 = char_style1.get_rect()
# 	character2 = char_style2.get_rect()
# 	character3 = char_style3.get_rect()
#
# 	pos = pygame.mouse.get_pos()
#
# 	clicked = False
#
# 	if character1.collidepoint(pos):
# 		if pygame.mouse.get_pressed()[0] == 1 and clicked == False:
# 			self.clicked = True
# 			print('Character 1')
# 	if pygame.mouse.get_pressed()[0] == 0:
#             self.clicked == False
#
# 	# if self.rect.collidepoint(pos):
# 	# 	if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
# 	# 		self.clicked = True
# 	# 		action = True
# 	# if pygame.mouse.get_pressed()[0] == 0:
# 	# 	self.clicked == False
#
# 	run = True
# 	while run:
# 		if char_style1 == True:
# 			print('You chose Character 1')
# 		elif char_style2 == True:
# 			print('You chose Character 2')
# 		elif char_style3 == True:
# 			print('You chose Character 3')
# 		for event in pygame.event.get():
# 			if event.type == pygame.QUIT():
# 				pygame.quit()
# 			pygame.display.update()
def credits(surface):
	options = [('Gisselle Derije', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 40)), ('Leandrei Sagun', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 100))]
	selected = 0
	exit = False
	while not exit:
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
			if event.type == KEYDOWN:
				if event.key == pygame.K_RETURN:
					main_menu(surface)
				if event.key == pygame.K_BACKSPACE:
					main_menu(surface)
				# if event.key == pygame.K_w or event.key == pygame.K_UP:
				# 	selected = (selected - 1) % 4
				# if event.key == pygame.K_s or event.key == pygame.K_DOWN:
				# 	selected = (selected + 1) % 4
		surface.blit(MENU_BACKGROUND, (0, 0))
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 60)
		draw_text(surface, font, 'Settings', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 - 100), WHITE)
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 40)
		for option in options:
			draw_text(surface, font, option[0], option[1], WHITE)
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 30)
		draw_text(surface, font, '*', (options[selected][1][0] - 230, options[selected][1][1]), WHITE)
		pygame.display.flip()

def end_display(surface):
	options = [('Gisselle Derije', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 40)), ('Leandrei Sagun', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2 + 100))]
	selected = 0
	exit = False
	while not exit:
		for event in pygame.event.get():
			if event.type == QUIT:
				exit()
		surface.blit(END_BACKGROUND, (0, 0))
		font = pygame.font.Font("assets/font/8-BIT WONDER.TTF", 40)
		draw_text(surface, font, 'Thanks For Playing', (DISPLAY_WIDTH / 2, DISPLAY_HEIGHT / 2), ENDING_RED)
		pygame.display.flip()

def start_video(surface):
	pygame.display.set_caption('Valo.mini')
	pygame.display.set_icon(pygame.image.load('assets/logo/valo.png'))
	mixer.pre_init(44100, -16, 1, 24000)
	mixer.quit()
	mixer.init()
	video = cv2.VideoCapture("assets/intro/introduction.wmv")
	success, video_image = video.read()
	fps = video.get(cv2.CAP_PROP_FPS)
	sound = mixer.Sound("assets/intro/intro.wav")
	mixer.Sound.play(sound)
	clock = pygame.time.Clock()

	run = success
	while run:
		clock.tick(fps)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

		success, video_image = video.read()
		if success:
			video_surf = pygame.image.frombuffer(
				video_image.tobytes(), video_image.shape[1::-1], "BGR")
			video_surf = pygame.transform.scale(video_surf, (1280, 720))

		else:
			run = False
		surface.blit(video_surf, (0, 0))
		pygame.display.flip()
	main_menu(surface)
