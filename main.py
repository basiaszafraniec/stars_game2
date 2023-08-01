import numpy as np
import random
import pygame as pg
import sys
from pygame.locals import *

pg.init()
game_on = True
fps = 60
fpsClock = pg.time.Clock()
Black = (0, 0, 0)
width, height = 700, 700
HW, HH = width / 2, height / 2
run_time = 0
timer_rock = 1000
last_time_rock = pg.time.get_ticks()
timer_energy = 5000
last_time_energy = pg.time.get_ticks()
timer_star = 100
last_time_star = pg.time.get_ticks()
last_angle = 0
screen = pg.display.set_mode((width, height), pg.SRCALPHA)
pg.display.set_caption("stars")
# Images
ROCK_IMG = pg.image.load("meteorite.png").convert_alpha()
SPACESHIP_IMG = pg.image.load("spaceship.png").convert_alpha()
ENERGY_IMG = pg.image.load("energy.png").convert_alpha()
BATTERY_IMG = pg.image.load("battery.png").convert_alpha()
BATTERY_IMG = pg.transform.scale(BATTERY_IMG, (int(width / 20), int(height / 5)))
RESTART_IMG = pg.image.load("restart1.png").convert_alpha()
# Sound
pg.mixer.pre_init(44100, -16, 2, 512)
pg.mixer.set_num_channels(64)
collision_sound = pg.mixer.Sound("collision.flac")
energy_sound = pg.mixer.Sound("energy_charge.wav")
pg.mixer.music.load("arpegiator.mp3")
spaceship_sound = pg.mixer.Sound("spaceship_engine_louder.wav")

pg.mixer.music.play(-1)
pg.mixer.music.set_volume(0.5)
pg.mixer.Sound.play(spaceship_sound, -1)

font = pg.font.SysFont("SFCompact", 20)


def new_game():
    global run_time, game_on
    game_on = True
    run_time = 0
    pg.init()
    print(pg.time.get_ticks())


def draw_rect_alpha(surface, color, rect):
    kwadrat = pg.Surface(pg.Rect(rect).size, pg.SRCALPHA)
    print(pg.Rect(rect).size)
    pg.draw.rect(kwadrat, color, kwadrat.get_rect())
    surface.blit(kwadrat, rect)


def radius_angle_to_xy(radius, angle):
    x = (np.cos(np.deg2rad(angle)) * radius) + (width / 2)
    y = (np.sin(np.deg2rad(angle)) * radius) + (height / 2)
    return x, y


def text(txt, x, y):
    text_print = font.render(txt, True, (255, 255, 255))
    screen.blit(text_print, (x, y))


class Rock(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        global last_angle
        self.x = HW
        self.y = HH
        self.angle = random.randrange(0, 360)
        self.angle += (0 if 30 < abs(self.angle - last_angle) < 330 else 100) % 360
        last_angle = self.angle
        self.radius = 0.00
        self.speed_factor = 1.03
        self.speed = 0.01
        self.image_org = ROCK_IMG
        self.image = pg.transform.scale(self.image_org, (0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        # pg.sprite.LayeredUpdates.move_to_back(self)

    def update(self):
        self.radius += self.speed
        if self.radius > width:
            self.kill()

        self.x, self.y = radius_angle_to_xy(self.radius, self.angle)
        self.speed = self.speed * self.speed_factor

        width_scaled = (self.radius * 100 / HW) * (self.image_org.get_width() / 100)
        height_scaled = (self.radius * 100 / HH) * (self.image_org.get_height() / 100)
        self.image = pg.transform.scale(self.image_org, (int(width_scaled), int(height_scaled)))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)


class Energy(Rock):
    def __init__(self):
        super().__init__()
        self.image_org = ENERGY_IMG


class Spaceship(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.speed_factor = 1.01
        self.speed = 0
        self.radius = width * 4 / 10
        self.angle = 90
        self.x, self.y = radius_angle_to_xy(self.radius, self.angle)
        self.image_org = pg.transform.scale(SPACESHIP_IMG, (int(width / 8), int(height / 8)))
        self.image = self.image_org
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def update(self):
        pg.mixer.Sound.set_volume(spaceship_sound, max(0.3, abs(self.speed / 4)))
        keys = pg.key.get_pressed()
        if fuel.how_full > 0 and game_on:
            if keys[pg.K_RIGHT] and self.speed > -4:
                self.speed -= 0.2
            elif keys[pg.K_LEFT] and self.speed < 4:
                self.speed += 0.2
            else:
                self.brake()

        self.angle += self.speed
        self.x, self.y = radius_angle_to_xy(self.radius, self.angle)

        self.image = pg.transform.rotate(self.image_org, -(self.angle - 90))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def brake(self):
        self.speed += 0.1 if self.speed < -0.05 else -0.1 if self.speed > 0.05 else 0


class Fuel:
    def __init__(self):
        self.how_full = 100
        self.color = (216, 155, 236)
        self.width = int(width / 22)
        self.height = int(height / 5.8)
        self.x = int(width * 0.9043)
        self.y = int(height * 0.05)

    def draw(self):
        pg.draw.rect(screen, self.color,
                     (self.x, self.y + self.height - (self.how_full * self.height / 100), self.width,
                      (self.how_full * self.height / 100)), 0)

    def update(self):
        self.how_full -= 0.03
        # print(self.how_full)


class Stars(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.angle = random.randrange(0, 360)
        self.radius = 0.00
        self.color = 0
        self.speed = 1
        self.speed_factor = 1.02

    def draw(self):
        pg.draw.line(screen, (self.color, self.color, self.color),
                     (radius_angle_to_xy(self.radius, self.angle)),
                     (radius_angle_to_xy(self.radius + 10, self.angle)))
        self.speed = self.speed * self.speed_factor
        self.radius += self.speed
        self.color = (min(self.radius / 2, 150))


fuel = Fuel()
stars = []
spaceship = pg.sprite.GroupSingle(Spaceship())
rocks = pg.sprite.Group()
energy_balls = pg.sprite.Group()

# game loop
while 1:
    for event in pg.event.get():
        if event.type == QUIT:
            pg.quit()
            sys.exit()

    # Update
    spaceship.update()
    rocks.update()
    energy_balls.update()
    fuel.update()

    if game_on:
        run_time = pg.time.get_ticks() / 1000

    # Spawn stars
    if pg.time.get_ticks() > last_time_star + timer_star:
        last_time_star = pg.time.get_ticks()
        stars.append(Stars())

    # Spawn rock
    if pg.time.get_ticks() > last_time_rock + timer_rock:
        last_time_rock = pg.time.get_ticks()
        timer_rock = random.triangular(0, 1000, max(300, 6000 - int(last_time_rock / 10)))
        # print(last_time_rock, timer_rock)
        rocks.add(Rock())
    # Spawn energy
    if pg.time.get_ticks() > last_time_energy + timer_energy:
        last_time_energy = pg.time.get_ticks()
        timer_energy = random.randrange(5000, 10000)
        energy_balls.add(Energy())

    screen.fill(Black)
    # Draw
    for star in stars:
        if star.radius > width:
            stars.pop(stars.index(star))
        star.draw()

    rocks.draw(screen)
    energy_balls.draw(screen)
    spaceship.draw(screen)
    fuel.draw()
    screen.blit(BATTERY_IMG, (int(width * 0.9), int(height * 0.03)))
    # draw_rect_alpha(screen, (255, 0, 0, 100), (100, 100, 100, 100))
    # # pg.draw.rect(screen, pg.Color(255, 0, 0, 100), pg.Rect(100, 100, 100, 100))
    if game_on is not True:
        draw_rect_alpha(screen, (0, 0, 0, 150), (0, 0, width, height))
        screen.blit(RESTART_IMG, ((HW - (RESTART_IMG.get_width() / 2)), (HH - (RESTART_IMG.get_height() / 2))))

    text("time: " + str(run_time), width * 0.05, height * 0.05)

    if pg.sprite.spritecollide(spaceship.sprite, rocks, False, pg.sprite.collide_mask):
        pg.mixer.Sound.play(collision_sound)
        game_on = False
        spaceship.sprite.speed = 0
        # new_game()

    if pg.sprite.spritecollide(spaceship.sprite, energy_balls, False, pg.sprite.collide_mask):
        pg.mixer.Sound.play(energy_sound)
        fuel.how_full += 1 if fuel.how_full <= 99 else 0

    pg.display.flip()
    fpsClock.tick(fps)
