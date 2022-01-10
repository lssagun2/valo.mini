import pygame


class Menu():

    def __init__(self, game):
        self.game = game
        self.mid_w, self.mid_h = self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = - 230

    def draw_cursor(self):
        self.game.draw_text_white('*', 30, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        self.game.window.blit(self.game.display, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = "Start"
        self.startx, self.starty = self.mid_w, self.mid_h + 30
        self.optionsx, self.optionsy = self.mid_w, self.mid_h + 80
        self.creditsx, self.creditsy = self.mid_w, self.mid_h + 130
        self.quitx, self.quity = self.mid_w, self.mid_h + 220
        self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
        self.background = pygame.image.load('assets/background/titlescreen-fullscreen.png')
        self.game.introductory_video()

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.display.blit(self.background, (0, 0))
            self.game.draw_text_white('VALORANT MINI', 60, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 100)
            self.game.draw_text_white('Start Game', 40, self.startx, self.starty)
            self.game.draw_text_white('Options', 40, self.optionsx, self.optionsy)
            self.game.draw_text_white('Credits', 40, self.creditsx, self.creditsy)
            self.game.draw_text_white('Quit', 40, self.quitx, self.quity)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        if self.game.DOWN_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                self.state = 'Quit'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
        if self.game.UP_KEY:
            if self.state == 'Start':
                self.cursor_rect.midtop = (self.quitx + self.offset, self.quity)
                self.state = 'Quit'
            elif self.state == 'Options':
                self.cursor_rect.midtop = (self.startx + self.offset, self.starty)
                self.state = 'Start'
            elif self.state == 'Credits':
                self.cursor_rect.midtop = (self.optionsx + self.offset, self.optionsy)
                self.state = 'Options'
            elif self.state == 'Quit':
                self.cursor_rect.midtop = (self.creditsx + self.offset, self.creditsy)
                self.state = 'Credits'

    def check_input(self):
        self.move_cursor()
        if self.game.START_KEY:
            if self.state == 'Start':
                self.game.playing = True
            elif self.state == 'Options':
                self.game.curr_menu = self.game.options
            elif self.state == 'Credits':
                self.game.curr_menu = self.game.credits
            elif self.state == 'Quit':
                pygame.quit()
                exit()
            self.run_display = False


class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.state = 'Volume'
        self.volx, self.voly = self.mid_w, self.mid_h + 60
        self.controlsx, self.controlsy = self.mid_w, self.mid_h + 120
        self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        self.background = pygame.image.load('assets/background/titlescreen-fullscreen.png')

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            # self.game.display.fill((0, 0, 0))
            self.game.display.blit(self.background, (0, 0))
            self.game.draw_text_white('Options', 60, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 100)
            self.game.draw_text_white('Volume', 40, self.volx, self.voly)
            self.game.draw_text_white('Controls', 40, self.controlsx, self.controlsy)
            self.draw_cursor()
            self.blit_screen()

    def check_input(self):
        if self.game.BACK_KEY:
            self.game.curr_menu = self.game.main_menu
            self.run_display = False
        elif self.game.UP_KEY or self.game.DOWN_KEY:
            if self.state  == 'Volume':
                self.state = 'Controls'
                self.cursor_rect.midtop = (self.controlsx + self.offset, self.controlsy)
            elif self.state == 'Controls':
                self.state = 'Volume'
                self.cursor_rect.midtop = (self.volx + self.offset, self.voly)
        elif self.game.START_KEY:
            pass

class CreditsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.background = pygame.image.load('assets/background/titlescreen-fullscreen.png')

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            if self.game.START_KEY or self.game.BACK_KEY:
                self.game.curr_menu = self.game.main_menu
                self.run_display = False
            # self.game.display.fill(self.game.BLACK)
            self.game.display.blit(self.background, (0, 0))
            self.game.draw_text_white('Credits', 60, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 - 100)
            self.game.draw_text_white('Gisselle Derije', 40, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 40)
            self.game.draw_text_white('Leandrei Sagun', 40, self.game.DISPLAY_W / 2, self.game.DISPLAY_H / 2 + 100)
            self.blit_screen()