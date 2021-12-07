import pygame
import sys
import math

pygame.init()

display = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

player_walk_images = [pygame.image.load("assets/characters/sage-right/sage-right1.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right2.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right3.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right4.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right5.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right6.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right7.png"),
                      pygame.image.load("assets/characters/sage-right/sage-right8.png")]

player_walkup_images = [pygame.image.load("assets/characters/sage-back/sage-back1.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back2.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back3.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back4.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back5.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back6.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back7.png"),
                          pygame.image.load("assets/characters/sage-back/sage-back8.png")]

player_walkdown_images = [pygame.image.load("assets/characters/sage-front/sage-front1.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front2.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front3.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front4.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front5.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front6.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front7.png"),
                          pygame.image.load("assets/characters/sage-front/sage-front8.png")]

player_stationary_image = [pygame.image.load("assets/characters/sage-front/sage-front1.png")]

player_weapon = pygame.transform.scale(pygame.image.load("assets/gun/smg.png"), (128, 64)).convert()
player_weapon.set_colorkey((0, 0, 0)) # convert to transparent background

# player_background = pygame.image.load("assets/background/background.png")


class Player:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.animation_count = 0
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

    def handle_weapons(self, display):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        rel_x, rel_y = mouse_x - player.x, mouse_y - player.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)

        player_weapon_copy = pygame.transform.rotate(player_weapon, angle)

        display.blit(player_weapon_copy, (self.x + 30 - int(player_weapon_copy.get_width() / 2), self.y + 35 - int(player_weapon_copy.get_height() / 2)))

    def main(self, display):
        if self.animation_count + 1 >= 16:
            self.animation_count = 0

        self.animation_count += 1

        if self.moving_right:
            display.blit(player_walk_images[self.animation_count // 8], (self.x, self.y))
        elif self.moving_left:
            display.blit(pygame.transform.flip(player_walk_images[self.animation_count // 8], True, False), (self.x, self.y))
        elif self.moving_up:
            display.blit(player_walkup_images[self.animation_count // 8], (self.x, self.y))
        elif self.moving_down:
            display.blit(player_walkdown_images[self.animation_count // 8], (self.x, self.y))
        else:
            display.blit(player_stationary_image[0], (self.x, self.y))

        self.handle_weapons(display)

        # display.blit(pygame.transform.scale(player_walk_images[self.animation_count // 8], (32, 32)), (self.x, self.y))
        # pygame.draw.rect(display, (255, 0, 0), (self.x, self.y, self.width, self.height))

        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False


class PlayerBullet:
    def __init__(self, x, y, mouse_x, mouse_y):
        self.x = x
        self.y = y
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y
        self.speed = 15
        self.angle = math.atan2(y - mouse_y, x - mouse_x)
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed

    def main(self, display):
        self.x -= int(self.x_vel)
        self.y -= int(self.y_vel)

        pygame.draw.circle(display, (0, 0, 0), (self.x + 30, self.y + 30), 3)


player = Player(400, 300, 32, 32)

display_scroll = [0, 0]

player_bullets = []

while True:
    display.fill((127, 201, 159))
    # display.blit(player_background, (0, 0))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
            pygame.quit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                player_bullets.append(PlayerBullet(player.x, player.y, mouse_x, mouse_y))

    keys = pygame.key.get_pressed()

    pygame.draw.rect(display, (255, 255, 255), (100-display_scroll[0], 100-display_scroll[1], 16, 16))

    if keys[pygame.K_a]:
        display_scroll[0] -= 5

        player.moving_left = True

        for bullet in player_bullets:
            bullet.x += 5

    if keys[pygame.K_d]:
        display_scroll[0] += 5

        player.moving_right = True

        for bullet in player_bullets:
            bullet.x -= 5

    if keys[pygame.K_w]:
        display_scroll[1] -= 5

        player.moving_up = True

        for bullet in player_bullets:
            bullet.y += 5

    if keys[pygame.K_s]:
        display_scroll[1] += 5

        player.moving_down = True

        for bullet in player_bullets:
            bullet.y -= 5

    player.main(display)

    for bullet in player_bullets:
        bullet.main(display)

    clock.tick(60)
    pygame.display.update()