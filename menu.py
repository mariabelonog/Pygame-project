import pygame
import time
import math
import random
import csv
import os
import sys

pygame.font.init()
size = width, height = 500, 500
screen = pygame.display.set_mode(size)


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width() /
                      2, win.get_height()/2 - render.get_height()/2))




TRACK = scale_image(pygame.image.load("race3.png"), 0.9)

track_limits = scale_image(pygame.image.load("Tracklims1.png"), 1.6 * 0.9)

RED_CAR = scale_image(pygame.image.load("purple-car.png"), 0.55)



WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
fon = scale_image(pygame.image.load("back2.jpg"), 1.42)

mask1 = pygame.mask.from_surface(track_limits)
flag = scale_image(pygame.image.load("Flag2.png"), 1.6 * 0.9)
mask2 = pygame.mask.from_surface(flag)
winwin = scale_image(pygame.image.load("win1.jpg"), 1.2)
pygame.display.set_caption("Racing Game!")

FPS = 60
MAIN_FONT =  pygame.font.SysFont('andale mono', 30)

screen_rect = (0, 0, width, height)
GRAVITY = 1

class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [pygame.image.load("star.png")]
    for scale in (10, 20, 30):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()

def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-10, 9)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Game:
    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.win = False
        self.time = 0

    def start_game(self):
        self.started = True
        self.win = False
        self.level_start_time = time.time()
        self.time = 0

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)

    def next_level(self):
        self.level += 1
        self.started = False

    def over(self):
        self.win = True
        self.time = round(time.time() - self.level_start_time)



class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 270
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backword(self):
        self.vel = -max(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        return mask.overlap(car_mask, (int(self.x - x), int(self.y - y)))


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (330, 610)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


def draw(win, images, player_car, game):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render(
        f"Level {game.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 40))

    time_text = MAIN_FONT.render(
        f"Time: {game.get_level_time()}s", 6, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 10))


    player_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()


def collision(player_car, game):

    if player_car.collide(mask1) != None:
        player_car.bounce()
    if player_car.collide(mask2) != None:
        game.over()

run = True
clock = pygame.time.Clock()
images = [(TRACK, (0, 0))]
player_car = PlayerCar(4, 4)
game = Game()
all_sprites = pygame.sprite.Group()

while run:
    clock.tick(FPS)

    while not game.started:

        intro_text = [
                      "Чтобы начать, выберите уровень.",
                      "Нажмите 1, 2 или 3.",
                      "W - вперед, S - назад, ",
                      "A - направо, D - налево."]

        WIN.blit(fon, (0, 0))

        font1 = pygame.font.SysFont('copperplate', 70)

        text_coord = 500
        text = 'RACING WHEELS'
        render = font1.render(text, 1, '#F75605')
        WIN.blit(render, (WIN.get_width() / 2 - render.get_width() / 2, 100))

        font = pygame.font.SysFont('andale mono', 30)

        with open('text.csv', encoding="utf8") as csvfile1:
            reader = csv.reader(csvfile1, delimiter='-', quotechar='"')
            for index, line in enumerate(reader):
                line = line[0]

                string_rendered = font.render(line, 1, pygame.Color('white'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 10
                text_coord += intro_rect.height
                WIN.blit(string_rendered, intro_rect)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            keys1 = pygame.key.get_pressed()

            if keys1[pygame.K_1]:
                player_car = PlayerCar(4, 4)

                game.level = 1
                game.start_game()

            if keys1[pygame.K_2]:
                game.level = 2

                player_car = PlayerCar(5, 4)
                game.start_game()

            if keys1[pygame.K_3]:
                game.level = 3

                player_car = PlayerCar(7, 6)
                game.start_game()

    draw(WIN, images, player_car, game)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backword()

    if not moved:
        player_car.reduce_speed()

    collision(player_car, game)

    while game.win:
        intro_text = [f"Time: {game.time}s",
                      f"Level {game.level}",
                      'Нажмите любвую кнопку, чтобы выйти.']

        WIN.blit(winwin, (0, 0))

        font = pygame.font.SysFont('andale mono', 30)

        text_coord = 10

        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            WIN.blit(string_rendered, intro_rect)

        create_particles((WIDTH // 2, HEIGHT // 2 - 100))
        all_sprites.update()
        all_sprites.draw(screen)
        pygame.display.flip()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game.started = False
                game.win = False


pygame.quit()