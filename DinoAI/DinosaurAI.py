import pygame
import neat
import sys
from random import uniform
from math import floor
from Dino import (width, height, Cactus,
                  Dino, bg, calc_dist, skins,
                  names, DinoState, draw_text
                  )

generation = 0


def run_game(genomes, config):
    global game_speed, score, generation, speedup

    score = 0
    speedup = 100
    game_speed = 8
    enemies = [Cactus(width + 300 / uniform(0.8, 3), height - 85),
               Cactus(width * 2 + 200 / uniform(0.8, 3), height - 85),
               Cactus(width * 3 + 400 / uniform(0.8, 3), height - 85)]
    generation += 1
    screen = pygame.display.set_mode((width, height))
    dinosaurs = []
    nets = []
    skins_copy = skins[:]
    names_copy = names[:]
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)  # чтобы нейросеть следила за каждым динозавром отдельно
        nets.append(net)
        g.fitness = 0  # баланс печенек
        skin = "default"
        if len(skins_copy): skin = skins_copy.pop()
        name = "Dino"
        if len(names_copy): name = names_copy.pop()
        dinosaurs.append(Dino(30, height - 170, skin, name))
    pygame.init()
    clock = pygame.time.Clock()
    fps = 60
    road_sprites = [[pygame.image.load('road.png'), [0, height - 100]],
                    [pygame.image.load('road.png'), [2404, height - 100]]]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(bg)
        for road_sprite in road_sprites:
            if road_sprite[1][0] < -2404:
                road_sprite[1][0] = road_sprites[len(road_sprites) - 1][1][0] + 2404
                road_sprites[0], road_sprites[1] = road_sprites[1], road_sprites[0]
                break
            road_sprite[1][0] -= game_speed
            screen.blit(road_sprite[0], (road_sprite[1][0], road_sprite[1][1]))
        for dino in dinosaurs:
            dino.update(game_speed)
            dino.draw(screen)
        if not dinosaurs:
            print(generation, score)
            break
        if len(enemies) < 3:
            enemies.append(Cactus(enemies[len(enemies) - 1].hitbox.x + width / uniform(0.8, 3), height - 85))

        rem_list = []
        for i, enemy in enumerate(enemies):
            enemy.update(game_speed)
            enemy.draw(screen)

            if not enemy.is_active:
                rem_list.append(i)
                continue

            for j, dinosaur in enumerate(dinosaurs):
                if dinosaur.hitbox.colliderect(enemy.hitbox):
                    genomes[j][1].fitness -= 10
                    dinosaurs.pop(j)
                    genomes.pop(j)
                    nets.pop(j)

        for i in rem_list:
            enemies.pop(i)

            for j, dinosaur in enumerate(dinosaurs): genomes[j][1].fitness += 5  # дали печеньку всем динозаврам,
                                                                                # которые перепрыгнули кактус

        for i, dinosaur in enumerate(dinosaurs):
            output = nets[i].activate((dinosaur.hitbox.y,  # наблюдаемая точка
                                       calc_dist(dinosaur.hitbox.center, enemies[0].hitbox.center),
                                       # наблюдаемый параметр
                                       (dino.hitbox.width + enemies[0].hitbox.width) // 2,
                                       # граница наблюдаемого параметра (чтобы не было меньше этого)
                                       game_speed))  # следующий этап эволюции

            if output[0] > 0.5 and dinosaur.state is not DinoState.JUMP:
                dinosaur.jump(game_speed)
                genomes[i][1].fitness -= 1  # забираем печеньку, если прыжок был сделан просто так

            # score & game speed
        score += 0.125 * game_speed
        if score > speedup:
            speedup += 50 * game_speed
            game_speed += 1

        draw_text("Score: " + str(floor(score)), screen, (50, 50, 50), (width - 100, 50), "Roboto Condensed", 40)
        draw_text("Speed: " + str(game_speed / 8) + "x", screen, (50, 50, 50), (150, 50), "Roboto Condensed", 40)
        draw_text(f"Epoch {str(generation)}", screen, (255, 115, 214), (width // 2, 150), "Roboto Condensed", 70)
        for i, dinosaur in enumerate(dinosaurs):
            if floor(score) >= 10000:
                draw_text(f'Winner: {dinosaurs[0].name}', screen, (39, 196, 0), (width // 2, 200), "Roboto Condensed",
                          70)
            if i < len(dinosaurs) // 2:
                draw_text(dinosaur.name, screen, (39, 196, 0), (width - 100, 100 + (i * 25)), "Roboto Condensed", 30)
            else:
                draw_text(dinosaur.name, screen, (39, 196, 0), (width - 230, 100 + ((i - len(dinosaurs) // 2) * 25)),
                          "Roboto Condensed", 30)
        draw_text("FPS: " + str(round(clock.get_fps(), 1)), screen, (50, 50, 50), (100, height - 25),
                  "Roboto Condensed", 30)

        pygame.display.flip()
        clock.tick(fps)


if __name__ == '__main__':
    config_path = 'config-feedforward.txt'
    # fitness_threshold - насколько хорошо мы хотим тренировать нс
    # pop_size - размер популяции
    # num_inputs - Количество входов в нашу модель
    # num_outputs - кнопки действий
    # activation_default - используемая функция активации (activation options - тоже самое)

    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    # DefaultGenome - подвижный нейрон (может делать не только 2 действия, как в обычном нейроне)
    # DefaultReproduction - характеристика наследования
    # DefaultSpeciesSet - указывается не дефолт, если нам необходима другая конфигурация
    # (не та, что с файла на официальноми сайте neat)
    # DefaultStagnation - каждое новое покодение должно быть лучше предыдущего (есть исключения из правила)

    p = neat.Population(config)  # популяция динозавров
    p.run(run_game, 1000)  # запускаем программу обучения нейронной сети

    pygame.quit()
    sys.exit()
