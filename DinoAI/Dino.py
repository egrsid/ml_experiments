import pygame
from random import uniform, choice
import sys
import os
from math import floor, sqrt
from enum import Enum

width, height = 1280, 720
bg = (255, 255, 255, 255)

skins = ["default", "aqua", "black", "bloody", "cobalt", "gold", "insta",
         "lime", "magenta", "magma", "navy", "neon", "orange", "pinky",
         "purple", "rgb", "silver", "subaru", "sunny", "toxic"]
names = ["Флафи", "Фалафель", "Ведьмак", "Лютик", "Пучеглазик", "Слайм", "Шустрый", "Следопыт",
         "Малыш", "Субарик", "Т-Рекс", "Птенец", "Рядовой", "Опытный", "Ветеран", "Геймер",
         "Самурай", "Странник", "Ученый", "Пуля", "Киви", "Абрикос"]

score = 0
score_speedup = 100
game_speed = 8


class DinoState(Enum):
    RUN = 1
    JUMP = 2


class Dino:
    name = "Dino"
    color = "default"
    jump_power = 10
    cur_jump_power = jump_power
    sprites = dict()
    for skin in skins:
        sprites[skin] = {'run': [pygame.image.load(f"dino/{skin}_run1.png"),
                                 pygame.image.load(f"dino/{skin}_run2.png")],
                         'jump': pygame.image.load(f"dino/{skin}_jump.png")}
    image = None
    run_animation_index = [0, 5]
    hitbox = None
    state = DinoState.RUN

    def __init__(self, x, y, color="default", name=''):
        self.color = color
        self.hitbox = pygame.Rect(x, y, self.sprites[self.color]["run"][0].get_width(),
                                  self.sprites[self.color]["run"][0].get_height())
        self.image = self.sprites[self.color]["run"][0]
        if name: self.name = name

    def update(self, game_speed):
        if self.state == DinoState.RUN:
            self.run()
        elif self.state == DinoState.JUMP:
            self.jump(game_speed)

    def run(self):
        self.image = self.sprites[self.color]["run"][self.run_animation_index[0] // self.run_animation_index[1]]

        self.run_animation_index[0] += 1
        if self.run_animation_index[0] >= self.run_animation_index[1] * 2: self.run_animation_index[0] = 0

    def jump(self, game_speed):
        if self.state == DinoState.JUMP:
            self.hitbox.y -= int(self.cur_jump_power * (2 * (game_speed / 8)))
            self.cur_jump_power -= 0.5 * (game_speed / 8)

            if self.hitbox.y >= height - 170:
                self.hitbox.y = height - 170
                self.state = DinoState.RUN
                self.cur_jump_power = self.jump_power
        else:
            self.state = DinoState.JUMP
            self.image = self.sprites[self.color]["jump"]

    def draw(self, scr):
        scr.blit(self.image, (self.hitbox.x, self.hitbox.y))
        draw_text(self.name.capitalize(), scr, (100, 100, 100), (self.hitbox.x + 45, self.hitbox.y - 30),
                  "Roboto Condensed", 30)


class Cactus:
    cactus_types = [str(i) for i in range(1, 6 + 1)]
    sprites = [pygame.image.load(f"cactus/{skin}.png") for skin in cactus_types]
    image = None
    hitbox = None
    is_active = True

    def __init__(self, x, y):
        self.image = choice(self.sprites)
        self.hitbox = self.image.get_rect()
        self.hitbox.x = int(x)
        self.hitbox.y = y - self.hitbox.height  # origin from bottom

    def update(self, game_speed):
        self.hitbox.x -= int(game_speed)
        if self.hitbox.x < -self.hitbox.width: self.is_active = False  # remove this cactus

    def draw(self, scr):
        scr.blit(self.image, self.hitbox)


def calc_dist(a, b) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return sqrt(dx ** 2 + dy ** 2)


def draw_text(text: str, scr, color, place, fnt, fnt_size) -> None:
    font = pygame.font.SysFont(fnt, fnt_size)
    label = font.render(text, True, color)
    label_rect = label.get_rect()
    label_rect.center = place
    scr.blit(label, label_rect)


def run_game():
    global game_speed, score, enemies, dinosaurs, generation, score_speedup

    dino = Dino(30, height - 170)
    enemies = [Cactus(width + 300 / uniform(0.8, 3), height - 85),
               Cactus(width * 2 + 200 / uniform(0.8, 3), height - 85),
               Cactus(width * 3 + 400 / uniform(0.8, 3), height - 85)]

    # init
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(os.path.basename(__file__))
    clock = pygame.time.Clock()
    road_chunks = [[pygame.image.load('road.png'), [0, height - 100]],
                   [pygame.image.load('road.png'), [2404, height - 100]]]

    # the loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()

        # display bg & road
        screen.fill(bg)
        for road_chunk in road_chunks:
            if road_chunk[1][0] <= -2400:
                road_chunk[1][0] = road_chunks[len(road_chunks) - 1][1][0] + 2400
                road_chunks[0], road_chunks[1] = road_chunks[1], road_chunks[0]
                break

            road_chunk[1][0] -= game_speed
            screen.blit(road_chunk[0], (road_chunk[1][0], road_chunk[1][1]))

        # draw dino
        dino.update(game_speed)
        dino.draw(screen)

        # generate enemies
        if len(enemies) < 3:
            enemies.append(Cactus(enemies[len(enemies) - 1].hitbox.x + width / uniform(0.8, 3), height - 85))

        # quit if there is no dinos left
        # dino.hitbox.colliderect(enemies[0].hitbox):
        if calc_dist(dino.hitbox.center, enemies[0].hitbox.center) < (dino.hitbox.width + enemies[0].hitbox.width) // 2:
            pygame.time.wait(1000)
            pygame.quit();
            sys.exit()

        # draw enemies
        rem_list = []
        for i, enemy in enumerate(enemies):
            enemy.update(game_speed)
            enemy.draw(screen)

            if not enemy.is_active:
                rem_list.append(i)
                continue

        for i in rem_list: enemies.pop(i)

        # read user input (jump test)
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            if not dino.state == DinoState.JUMP: dino.jump(game_speed)

        # score & game speed
        score += 0.125 * game_speed
        if score > score_speedup:
            score_speedup += 50 * game_speed
            game_speed += 1

        draw_text("Score: " + str(floor(score)), screen, (50, 50, 50), (width - 100, 50), "Roboto Condensed", 40)
        draw_text("Speed: " + str(game_speed / 8) + "x", screen, (50, 50, 50), (150, 50), "Roboto Condensed", 40)
        draw_text("FPS: " + str(round(clock.get_fps(), 1)), screen, (50, 50, 50), (100, height - 25),
                  "Roboto Condensed", 30)

        pygame.display.flip()  # flip & tick
        clock.tick(60)  # fixed 60 fps


if __name__ == "__main__":
    run_game()
