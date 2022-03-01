import random
import pygame
import sys
import os
import math
import pygame_gui  # библиотека графического интерфейса: кнопки поле ввода и др
import sqlite3
from pygame_gui.core import ObjectID

pygame.init()
SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60
clock = pygame.time.Clock()


# класс для загрузки изображения
class LoadImage:
    def __call__(self, name):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        found_image = pygame.image.load(fullname).convert_alpha()
        return found_image


# словарь большинства изображений программы
IMAGES = {'PACMAN': LoadImage()('pacman.png'),
          'RED': LoadImage()("red.png"),
          'GREEN': LoadImage()("green.png"),
          'YELLOW': LoadImage()("yellow.png"),
          'BLUE': LoadImage()("blue.png"),
          'EDIBLE': LoadImage()("edible.png"),
          'BACKGROUND': LoadImage()("GUI/background.png"),
          'SIMPLE_BACKGROUND': LoadImage()("GUI/simple_background.jpg"),
          'TILE': LoadImage()("square.png"),
          'DOT': LoadImage()("dot.png"),
          'HEART': LoadImage()('heart.png'),
          'CLEAR': LoadImage()('clear.png'),
          'LEVEL_2': LoadImage()('level2.png'),
          'LEVEL_3': LoadImage()('level3.png'),
          'LEVEL_4': LoadImage()('level4.png'),
          'CUP': LoadImage()('cup.png')}


# класс игрока, управление происходит с помощью стрелок на клавиатуре
class Player(pygame.sprite.Sprite):
    image = IMAGES['PACMAN']

    def __init__(self, *param):
        super().__init__(param[:-3])
        self.map = param[-1]

        # здесь и в других классах большинство изображений масштабируются в
        # соответствии с размерами окнаЮ размеров тайлов и отступов
        self.image = pygame.transform.scale(Player.image,
                                            (self.map.TILE_SIZE,
                                             self.map.TILE_SIZE))
        Player.image = self.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = self.map.INDENT + param[-3] * self.map.TILE_SIZE
        self.rect.y = self.map.INDENT + param[-2] * self.map.TILE_SIZE
        self.speed = 2
        self.direction = None
        self.command = None
        self.add(self.map.player)
        self.map.player_object = self

    def get_tile_location(self):  # получение местоположения в клетках поля
        tile_x = (self.rect.x - self.map.INDENT + self.map.TILE_SIZE
                  // 2) // self.map.TILE_SIZE

        tile_y = (self.rect.y - self.map.INDENT + self.map.TILE_SIZE
                  // 2) // self.map.TILE_SIZE

        return tile_x, tile_y

    def moving(self, args):  # основная ф-ия движения
        tile_x, tile_y = self.get_tile_location()

        # self.command и условия ниже используются для более удобного
        # поворота игрока, т.к. размеры игрока равны проходу между стенками
        # и для перемещения нужно чтобы игрок перед поворотом разместился
        # точно в проходе
        if self.command == 'LEFT_TURN':
            if (self.rect.y - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y][tile_x - 1] == 0:
                self.image = pygame.transform.flip(Player.image, True, False)
                self.direction = 'LEFT'
                self.command = None
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y][tile_x - 1] == 1:
                self.command = None

        elif self.command == 'RIGHT_TURN':
            if (self.rect.y - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y][tile_x + 1] == 0:
                self.image = Player.image
                self.direction = 'RIGHT'
                self.command = None
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y][tile_x + 1] == 1:
                self.command = None

        elif self.command == 'UP_TURN':
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y - 1][tile_x] == 0:
                self.image = pygame.transform.rotate(Player.image, 90)
                self.direction = 'UP'
                self.command = None
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y - 1][tile_x] == 1:
                self.command = None

        elif self.command == 'DOWN_TURN':
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y + 1][tile_x] == 0:
                self.image = pygame.transform.rotate(Player.image, 270)
                self.direction = 'DOWN'
                self.command = None
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    self.map.map_mask[tile_y + 1][tile_x] == 1:
                self.command = None

        elif args and args[0].key == pygame.K_DOWN:  # нажата клавиша "вниз"
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    tile_y != self.map.width - 1 and \
                    self.map.map_mask[tile_y + 1][tile_x] == 0:
                self.image = pygame.transform.rotate(Player.image, 270)
                self.direction = 'DOWN'
            elif self.map.map_mask[tile_y + 1][tile_x] == 0:
                self.command = 'DOWN_TURN'
            elif tile_y != self.map.width - 1:
                if self.direction == 'RIGHT':
                    if self.map.map_mask[tile_y + 1][tile_x + 1] == 0:
                        self.command = 'DOWN_TURN'
                elif self.direction == 'LEFT':
                    if self.map.map_mask[tile_y + 1][tile_x - 1] == 0:
                        self.command = 'DOWN_TURN'
                elif self.direction == 'UP':
                    self.direction = 'DOWN'

        elif args and args[0].key == pygame.K_UP:  # нажата клавиша "вверх"
            if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE \
                    == 0 and tile_y != 0 and \
                    self.map.map_mask[tile_y - 1][tile_x] == 0:
                self.image = pygame.transform.rotate(Player.image, 90)
                self.direction = 'UP'
            elif self.map.map_mask[tile_y - 1][tile_x] == 0:
                self.command = 'UP_TURN'
            elif tile_y != 0:
                if self.direction == 'RIGHT':
                    if self.map.map_mask[tile_y - 1][tile_x + 1] == 0:
                        self.command = 'UP_TURN'
                elif self.direction == 'LEFT':
                    if self.map.map_mask[tile_y - 1][tile_x - 1] == 0:
                        self.command = 'UP_TURN'
                elif self.direction == 'DOWN':
                    self.direction = 'UP'

        elif args and args[0].key == pygame.K_LEFT:  # нажата клавиша "влево"
            if (self.rect.y - self.map.INDENT) % self.map.TILE_SIZE \
                    == 0 and tile_x != 0 and \
                    self.map.map_mask[tile_y][tile_x - 1] == 0:
                self.image = pygame.transform.flip(Player.image, True, False)
                self.direction = 'LEFT'
            elif self.map.map_mask[tile_y][tile_x - 1] == 0:
                self.command = 'LEFT_TURN'
            elif tile_x != 0:
                if self.direction == 'UP':
                    if self.map.map_mask[tile_y - 1][tile_x - 1] == 0:
                        self.command = 'LEFT_TURN'
                elif self.direction == 'DOWN':
                    if self.map.map_mask[tile_y + 1][tile_x - 1] == 0:
                        self.command = 'LEFT_TURN'
                elif self.direction == 'RIGHT':
                    self.direction = 'LEFT'

        elif args and args[0].key == pygame.K_RIGHT:  # нажата клавиша "вправо"
            if (self.rect.y - self.map.INDENT) % self.map.TILE_SIZE == 0 and \
                    tile_x != self.map.width - 1 and \
                    self.map.map_mask[tile_y][tile_x + 1] == 0:
                self.image = Player.image
                self.direction = 'RIGHT'
            elif self.map.map_mask[tile_y][tile_x + 1] == 0:
                self.command = 'RIGHT_TURN'
            elif tile_x != self.map.width - 1:
                if self.direction == 'UP':
                    if self.map.map_mask[tile_y - 1][tile_x + 1] == 0:
                        self.command = 'RIGHT_TURN'
                elif self.direction == 'DOWN':
                    if self.map.map_mask[tile_y + 1][tile_x + 1] == 0:
                        self.command = 'RIGHT_TURN'
                elif self.direction == 'LEFT':
                    self.direction = 'RIGHT'

    def can_eat_ghosts(self):  # ф-ия делает всех не возраждающихся врагов
        # уязвивыми
        for ghost in self.map.ghosts_list:
            if not ghost.edible:
                ghost.set_edible(True)

    def update(self, *args):  # ф-ия корректировки положения  и
        # столкновения игрока
        self.moving(args)

        if self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed

        if pygame.sprite.spritecollideany(self, self.map.barriers):
            if self.direction == 'UP':
                self.rect.y += self.speed
            elif self.direction == 'DOWN':
                self.rect.y -= self.speed
            elif self.direction == 'LEFT':
                self.rect.x += self.speed
            elif self.direction == 'RIGHT':
                self.rect.x -= self.speed


# класс врага, его движение происходит по циклу:
# 1.случайное движение
# 2.корректировка положения
# 3.преследование игрока
class Ghost(pygame.sprite.Sprite):
    edible_image = IMAGES['EDIBLE']

    def __init__(self, *param):
        super().__init__(param[:-4])
        self.color = param[-1]

        self.map = param[-2]
        # изображение связано с цветом врага (self.color)
        self.image = pygame.transform.scale(IMAGES[self.color],
                                            (self.map.TILE_SIZE,
                                             self.map.TILE_SIZE))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = self.map.INDENT + param[-4] * self.map.TILE_SIZE
        self.rect.y = self.map.INDENT + param[-3] * self.map.TILE_SIZE
        self.spawn = (param[-4], param[-3])  # запоминает спавн для вохрождения
        self.moving_loop_counter = 0
        self.edible = False  # уязвимость перед игроком
        self.time_to_respawn = 0
        self.speed = 2
        self.next_location = None
        self.edible_counter = 0
        self.direction = random.choice(['DOWN', 'UP', 'LEFT', 'RIGHT'])
        self.add(self.map.ghosts)
        self.map.ghosts_list.append(self)

    def get_tile_location(self):  # получение местоположения в клетках поля
        tile_x = (self.rect.x - self.map.INDENT + self.map.TILE_SIZE
                  // 2) // self.map.TILE_SIZE

        tile_y = (self.rect.y - self.map.INDENT + self.map.TILE_SIZE
                  // 2) // self.map.TILE_SIZE
        return tile_x, tile_y

    def set_position(self, x, y):
        self.rect.x = x * self.map.TILE_SIZE + self.map.INDENT
        self.rect.y = y * self.map.TILE_SIZE + self.map.INDENT

    def random_moving(self):  # ф-ия случайного движения
        if pygame.sprite.spritecollideany(self, self.map.barriers):
            location = self.get_tile_location()

            if self.direction == 'DOWN':
                self.rect.y -= self.speed
            elif self.direction == 'UP':
                self.rect.y += self.speed
            elif self.direction == 'RIGHT':
                self.rect.x -= self.speed
            elif self.direction == 'LEFT':
                self.rect.x += self.speed

            direction_choices = []

            if location[0] != 0:
                if self.map.map_mask[location[1]][location[0] - 1] == 0:
                    direction_choices.append('LEFT')
            if location[0] != self.map.width - 1:
                if self.map.map_mask[location[1]][location[0] + 1] == 0:
                    direction_choices.append('RIGHT')
            if location[1] != 0:
                if self.map.map_mask[location[1] - 1][location[0]] == 0:
                    direction_choices.append('UP')
            if location[1] != self.map.height - 1:
                if self.map.map_mask[location[1] + 1][location[0]] == 0:
                    direction_choices.append('DOWN')
            try:
                self.direction = random.choice(direction_choices)
            except Exception:
                self.direction = 'UP'

        if self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed

    def find_path_step(self, start, target):  # нахождение пути до игрока
        INF = 1000
        x, y = start
        distance = [[INF] * self.map.width for _ in range(
            self.map.height)]
        distance[y][x] = 0
        prev = [[None] * self.map.width for _ in range(
            self.map.height)]
        queue = [(x, y)]

        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if self.map.width > next_x >= 0 == self.map.map_mask[next_y][
                    next_x] and 0 < next_y < self.map.height \
                        and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))

        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def persecution(self):  # преследование игрока
        self_location = self.get_tile_location()
        player_location = self.map.player_object.get_tile_location()

        if self.next_location is None:
            self.next_location = self.find_path_step(self_location,
                                                     player_location)
        if self.next_location[1] * self.map. \
                TILE_SIZE - self.rect.y + self.map.INDENT > 0:
            self.rect.y += self.speed

        elif self.next_location[1] * self.map. \
                TILE_SIZE - self.rect.y + self.map.INDENT < 0:
            self.rect.y -= self.speed

        elif self.next_location[0] * self.map. \
                TILE_SIZE - self.rect.x + self.map.INDENT > 0:
            self.rect.x += self.speed

        elif self.next_location[0] * self.map. \
                TILE_SIZE - self.rect.x + self.map.INDENT < 0:
            self.rect.x -= self.speed

        else:
            self.next_location = self.find_path_step(self_location,
                                                     player_location)

    def set_edible(self, var):  # изменяет уязвимость по времени
        if not var:
            self.edible = False
            self.image = pygame.transform.scale(IMAGES[self.color],
                                                (self.map.TILE_SIZE,
                                                 self.map.TILE_SIZE))
        else:
            self.edible = True
            self.image = pygame.transform.scale(IMAGES['EDIBLE'],
                                                (self.map.TILE_SIZE,
                                                 self.map.TILE_SIZE))
            self.edible_counter = self.map.EDIBLE_TIME

    def respawn(self):  # ожидание во время возраждения
        if self.time_to_respawn >= 0:
            self.time_to_respawn -= 1
        else:
            x, y = self.rect.x, self.rect.y
            self.image = pygame.transform.scale(IMAGES[self.color],
                                                (self.map.TILE_SIZE,
                                                 self.map.TILE_SIZE))
            self.rect = self.image.get_rect()
            self.mask = pygame.mask.from_surface(self.image)
            self.rect.x = x
            self.rect.y = y

    def update(self, *args):  # аналогично с Player
        if self.edible_counter > 1:
            self.edible_counter -= 1
        elif self.edible_counter == 1:
            self.set_edible(False)
            self.edible_counter -= 1

        if pygame.sprite.spritecollideany(self, self.map.player):
            if self.edible:
                self.mask.clear()
                self.image = pygame.transform.scale(IMAGES['CLEAR'],
                                                    (self.map.TILE_SIZE,
                                                     self.map.TILE_SIZE))
                self.set_position(self.spawn[0], self.spawn[1])
                self.time_to_respawn = 350
                self.map.level.score += self.map.POINTS_FOR_GHOSTS
            else:
                self.map.player_object.mask.clear()
                self.map.player_object.kill()
                self.map.level.losing()

        if self.time_to_respawn > 0:
            self.respawn()

        elif not self.edible:
            if self.moving_loop_counter < 500:
                self.random_moving()
                self.moving_loop_counter += 1
            elif self.moving_loop_counter == 500:
                if (self.rect.x - self.map.INDENT) % self.map.TILE_SIZE != 0:
                    self.rect.x += self.speed
                elif (self.rect.y - self.map.INDENT) % self.map.TILE_SIZE != 0:
                    self.rect.y += self.speed
                else:
                    self.moving_loop_counter += 1
            elif self.moving_loop_counter < 1300:
                self.persecution()
                self.moving_loop_counter += 1
            else:
                self.next_location = None
                self.moving_loop_counter = 0
                self.random_moving()

        else:
            self.moving_loop_counter = 0
            self.random_moving()


# класс ограничивающий игровое поле
class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, my_map):
        super().__init__(my_map.barriers)
        if x1 == x2:
            self.image = pygame.Surface([1, abs(y2 - y1)])
            self.rect = pygame.Rect(x1, y1, 1, abs(y2 - y1))
        else:
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        self.image.fill(pygame.Color('white'))


# класс стенки игрового поля
class Tile(pygame.sprite.Sprite):
    def __init__(self, rect, parent_map):
        super().__init__(parent_map.barriers)
        self.map = parent_map
        self.image = pygame.transform.scale(IMAGES['TILE'],
                                            (self.map.TILE_SIZE,
                                             self.map.TILE_SIZE))
        self.rect = rect


# класс игрового бонуса в виде точки делает врагов уязвимыми
class Dot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.map = param[-1]

        self.image = pygame.transform.scale(IMAGES['DOT'],
                                            (self.map.TILE_SIZE // 2,
                                             self.map.TILE_SIZE // 2))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = (self.map.TILE_SIZE - self.map.TILE_SIZE // 2
                       ) // 2 + self.map.INDENT + param[
                          -3] * self.map.TILE_SIZE
        self.rect.y = (self.map.TILE_SIZE - self.map.TILE_SIZE // 2
                       ) // 2 + self.map.INDENT + param[
                          -2] * self.map.TILE_SIZE

        self.add(self.map.dots)

    def update(self):
        if pygame.sprite.spritecollideany(self, self.map.player):
            self.map.player_object.can_eat_ghosts()
            self.mask.clear()
            self.kill()
            self.map.level.score += self.map.POINTS_FOR_DOTS


# класс игрового бонуса в виде маленткой точки увеличивает счёт пользователя
class SmallDot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.map = param[-1]

        self.image = pygame.transform.scale(IMAGES['DOT'],
                                            (self.map.TILE_SIZE // 5,
                                             self.map.TILE_SIZE // 5))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = (self.map.TILE_SIZE - self.map.TILE_SIZE // 5
                       ) // 2 + self.map.INDENT + param[
                          -3] * self.map.TILE_SIZE

        self.rect.y = (self.map.TILE_SIZE - self.map.TILE_SIZE // 5
                       ) // 2 + self.map.INDENT + param[
                          -2] * self.map.TILE_SIZE

        self.add(self.map.dots)

    def update(self):
        if pygame.sprite.spritecollideany(self, self.map.player):
            self.mask.clear()
            self.kill()
            self.map.level.score += self.map.POINTS_FOR_DOTS


# класс достижения пользователя
class Achievement(pygame.sprite.Sprite):
    def __init__(self, num):
        super().__init__()
        self.image = IMAGES['LEVEL_' + str(num + 1)]
        self.rect = self.image.get_rect()

        self.rect.x = WIDTH + 185
        self.rect.y = HEIGHT + 60
        self.flag = False
        self.counter = 0

    def update(self):
        if self.counter <= 150:
            self.rect.x -= 2
        elif 5000 >= self.counter > 350:
            self.rect.x += 2
        self.counter += 1

        screen.blit(self.image, self.rect)


# ниже 3 класса для создания визуального эффекта салюта, взяты с этой страницы
# у пользователя S. Nick https://ru.stackoverflow.com/questions/1335957/
class Circles:
    def __init__(self, r, x, y):
        self.color = self.choose_random_color()
        self.radius = r
        self.x = x
        self.y = y
        angle = random.uniform(-60, 360)
        velocity_mag = random.uniform(.3, 4)
        self.vx = velocity_mag * math.cos(math.radians(angle))
        self.vy = -velocity_mag * math.sin(math.radians(angle))
        self.timer = 0
        self.ended = False

    def choose_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return r, g, b

    def area(self):
        return self.radius ** 2 * 3.14

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.timer += 1
        if self.timer >= 60:
            self.ended = True

    def draw(self):
        red = (200, 0, 0)
        circleX = 100
        circleY = 100
        radius = 10
        active = True

        while active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    active = False

            pygame.draw.circle(screen, red, (circleX, circleY), radius)


class Streak:
    def __init__(self, x, y):
        self.color = self.choose_random_color()
        self.x = x
        self.y = y
        angle = random.uniform(-60, 360)
        velocity_mag = random.uniform(.3, 4)
        self.vx = velocity_mag * math.cos(math.radians(angle))
        self.vy = -velocity_mag * math.sin(math.radians(angle))
        self.timer = 0
        self.ended = False

    def choose_random_color(self):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return r, g, b

    def get_angle(self):
        return math.atan2(-self.vy, self.vx)

    def move(self):
        self.x += self.vx
        self.y += self.vy
        self.timer += 1
        if self.timer >= 60:
            self.ended = True

    def draw(self):
        angle = self.get_angle()
        length = 1
        dx = length * math.cos(angle)
        dy = length * math.sin(angle)
        a = [int(self.x + dy), int(self.y - dx)]
        b = [int(self.x - dy), int(self.y + dx)]
        pygame.draw.line(screen, self.color, a, b, 1)


class Firework:
    def __init__(self):
        self.x = random.randint(0, 1000)
        self.y = 600
        self.velocity = random.uniform(3.5, 7)
        self.end_y = random.uniform(10, 300)
        self.ended = False

    def move(self):
        self.y -= self.velocity
        if self.y <= self.end_y:
            self.ended = True

    def draw(self):
        a = [self.x, int(self.y + 15)]

        color = [random.randint(0, 255) for _ in range(3)]
        pygame.draw.ellipse(screen, color, [a[0], a[1], 15, 15], 2)


# класс игровой карты, при иницилизации получает путь к файлу игры и уровень
# к которому эта карта относится
class Map:
    def __init__(self, filename, level):
        self.TILE_SIZE = 24
        self.INDENT = 10
        self.POINTS_FOR_DOTS = 20
        self.POINTS_FOR_GHOSTS = 200
        self.EDIBLE_TIME = 400
        self.map_mask = []
        with open(filename) as file:
            for line in file:
                if line == '\n':
                    break
                else:
                    self.map_mask.append(
                        list(map(int, list(line.rstrip('\n')))))
        self.level = level
        self.barriers = pygame.sprite.Group()
        self.ghosts = pygame.sprite.Group()
        self.player = pygame.sprite.Group()
        self.player_object = None
        self.ghosts_list = []
        self.dots = pygame.sprite.Group()
        self.free_tiles = self.get_free_tiles()
        self.height = len(self.map_mask)
        self.width = len(self.map_mask[0])
        self.render()
        self.fill_dots()

    def get_free_tiles(self):  # получение свободных клеток поля
        res = []
        for i in range(len(self.map_mask)):
            for j in range(len(self.map_mask[0])):
                if self.map_mask[i][j] == 0:
                    res.append((i, j))
        return res

    def fill_dots(self):  # размещение игровых бонусов
        free_tiles = sorted(self.free_tiles, key=lambda x: random.random())
        for i in free_tiles[:-3]:
            SmallDot(i[1], i[0], self)
        for i in free_tiles[-3:]:
            Dot(i[1], i[0], self)

    def render(self):  # создание классов для границ и стенок игры
        pygame.display.set_mode((
            self.width * self.TILE_SIZE + 2 * self.INDENT,
            self.height * self.TILE_SIZE + 4 * self.INDENT))

        Border(self.INDENT - 1, self.INDENT - 1,
               self.INDENT + self.width * self.TILE_SIZE + 1,
               self.INDENT - 1, self)

        Border(self.INDENT - 1, self.INDENT - 1, self.INDENT - 1,
               self.INDENT + self.height * self.TILE_SIZE + 1, self)

        Border(self.INDENT - 1,
               self.INDENT + self.height * self.TILE_SIZE + 1,
               self.INDENT + self.width * self.TILE_SIZE + 1,
               self.INDENT + self.height * self.TILE_SIZE + 1, self)

        Border(self.INDENT + self.width * self.TILE_SIZE + 1,
               self.INDENT - 1,
               self.INDENT + self.width * self.TILE_SIZE + 1,
               self.INDENT + self.height * self.TILE_SIZE + 1, self)

        for i in range(self.width):
            for j in range(self.height):
                if self.map_mask[j][i] == 1:
                    tile_rect = pygame.Rect(self.INDENT + i * self.TILE_SIZE,
                                            self.INDENT + j * self.TILE_SIZE,
                                            self.TILE_SIZE, self.TILE_SIZE)
                    Tile(tile_rect, self)


# класс уровня
class Level:
    def __init__(self, num, map_name):
        self.main_map = Map(map_name, self)
        self.map_number = num
        self.user_id = int()
        self.map_name = map_name
        self.running = True
        self.score = 0
        self.lives = 3

        self.render()

    def render(self):  # создание сущностей, также нужно для сброса уровня при
        # проигрыше
        self.main_map.ghosts = pygame.sprite.Group()
        self.main_map.player = pygame.sprite.Group()
        data = list(
            map(lambda x: x.split('-'), open(self.map_name).readlines()[
                -1].strip().split(';')))

        if len(data) >= 2:
            Ghost(int(data[0][1]), int(data[0][2]),
                  self.main_map, data[0][3])

        if len(data) >= 3:
            Ghost(int(data[1][1]), int(data[1][2]),
                  self.main_map, data[1][3])

        if len(data) >= 4:
            Ghost(int(data[2][1]), int(data[2][2]),
                  self.main_map, data[2][3])

        if len(data) == 5:
            Ghost(int(data[3][1]), int(data[3][2]),
                  self.main_map, data[3][3])

        Player(int(data[-1][1]), int(data[-1][2]),
               self.main_map)

    def draw_score(self):
        font = pygame.font.Font(None, 30)
        text = 'SCORE:' + str(self.score)
        string_rendered = font.render(text, True, pygame.Color('white'))
        score_rect = string_rendered.get_rect()
        score_rect.x = self.main_map.INDENT
        score_rect.y = self.main_map.INDENT + self.main_map. \
            height * self.main_map.TILE_SIZE + 10

        screen.blit(string_rendered, score_rect)

    def draw_hearts(self):
        heart_surf = pygame.transform.scale(IMAGES['HEART'],
                                            (2 * self.main_map.INDENT,
                                             2 * self.main_map.INDENT))
        heart_rect = heart_surf.get_rect()

        heart_rect.y = self.main_map.height * self.main_map. \
            TILE_SIZE + self.main_map.INDENT * 2

        if self.lives == 3:
            heart_rect.x = self.main_map.INDENT * 21
            screen.blit(heart_surf, heart_rect)

        if self.lives >= 2:
            heart_rect.x = self.main_map.INDENT * 18
            screen.blit(heart_surf, heart_rect)

        if self.lives >= 1:
            heart_rect.x = self.main_map.INDENT * 15
            screen.blit(heart_surf, heart_rect)

    def losing(self):
        self.lives -= 1

        if self.lives != 0:
            pygame.time.set_timer(pygame.USEREVENT,
                                  150000)  # перезапуск таймера
            pygame.time.wait(1000)

            self.render()
        else:
            self.running = False
            screen.fill(pygame.Color(0))

            # сообщение "YOU LOSE" на экране
            font = pygame.font.Font('data/fonts/arcade-n.ttf', 40)
            text = 'YOU LOSE'
            string_rendered = font.render(text, True, pygame.Color('red'))
            lose_rect = string_rendered.get_rect()
            lose_rect.x = SIZE[0] // 2.5
            lose_rect.y = SIZE[1] // 2
            screen.blit(string_rendered, lose_rect)

            # сообщение "PRESS ANY KEY" на экране
            small_font = pygame.font.Font('data/fonts/arcade-n.ttf', 10)
            text = 'PRESS ANY KEY'
            string_rendered = small_font.render(text, True, pygame.Color(
                'white'))
            lose_rect = string_rendered.get_rect()
            lose_rect.x = SIZE[0] // 2
            lose_rect.y = SIZE[1] * 0.8
            screen.blit(string_rendered, lose_rect)

            key_count = 0

            pygame.display.flip()

            lose_running = True
            while lose_running:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if key_count >= 5:
                            lose_running = False
                        else:
                            key_count += 1
            StartScreen().run()

    def winning(self):
        # обращение к БД для открытия следущих уровней и записи счёта
        if self.map_number == 1:
            DatabaseQuery().call(f'UPDATE Scoring SET level_two_status = 1'
                                 f' WHERE player_id = {self.user_id}')
        elif self.map_number == 2:
            DatabaseQuery().call(f'UPDATE Scoring SET level_three_status '
                                 f'= 1 WHERE player_id = {self.user_id}')

        DatabaseQuery().call(f'UPDATE Scoring SET score = score + '
                             f'{self.score} WHERE player_id = {self.user_id}')

        # сообщение "YOU WIN" на экране
        font = pygame.font.Font('data/fonts/arcade-n.ttf', 40)
        text = 'YOU WIN'
        string_rendered = font.render(text, True, pygame.Color('yellow'))
        win_rect = string_rendered.get_rect()
        win_rect.x = SIZE[0] // 2.4
        win_rect.y = SIZE[1] // 2

        # сообщение "PRESS ANY KEY TO CONTINUE" на экране
        font = pygame.font.Font('data/fonts/arcade-n.ttf', 10)
        info_text = 'PRESS ANY KEY TO CONTINUE'
        info_string_rendered = font.render(info_text, True, pygame.Color(
            'white'))
        info_rect = info_string_rendered.get_rect()
        info_rect.x = SIZE[0] // 2.3
        info_rect.y = SIZE[1] * 0.7

        game_achievement = Achievement(self.map_number)

        fireworks = [Firework()]
        streaks = []

        key_count = 0

        win_running = True
        while win_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if key_count >= 5:
                        win_running = False
                    else:
                        key_count += 1

            if random.uniform(0, 1) <= 1 / 60:
                fireworks.append(Firework())
            screen.fill((0, 0, 0))
            screen.blit(string_rendered, win_rect)
            screen.blit(info_string_rendered, info_rect)

            # "запуск фейерверков"
            for firework in fireworks:
                firework.move()
                firework.draw()
                if firework.ended:
                    streaks += [Streak(firework.x, firework.y) for _ in range(
                        random.randint(20, 700))]
                    fireworks.remove(firework)
            for streak in streaks:
                streak.move()
                streak.draw()
                if streak.ended:
                    streaks.remove(streak)

            game_achievement.update()

            pygame.display.flip()
            clock.tick(FPS)

        if self.map_number == 3:
            FinalScreen().run()
        else:
            StartScreen().run()

    def draw_level(self):
        screen.fill(pygame.Color(0))
        self.main_map.barriers.draw(screen)
        self.main_map.ghosts.draw(screen)
        self.main_map.player.draw(screen)
        self.main_map.dots.draw(screen)
        self.draw_score()
        self.draw_hearts()

    def run(self, user_id):
        self.main_map.render()
        self.user_id = user_id
        pygame.time.set_timer(pygame.NOEVENT, 150000)

        while self.running:
            self.draw_level()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    self.main_map.player.update(event)
                if event.type == pygame.NOEVENT:
                    self.running = False
                    self.winning()

            self.main_map.ghosts.update()
            self.main_map.player.update()
            self.main_map.dots.update()

            clock.tick(FPS)
            pygame.display.flip()


# класс для взаимодействия с БД
class DatabaseQuery:
    def __init__(self):
        pass

    def call(self, query):
        con = sqlite3.connect('data/database.db')
        cur = con.cursor()
        res = list(map(list, cur.execute(query).fetchall()))
        con.commit()
        return res


# класс экрана перехода между другими экранами
class TransitionScreen:
    def __init__(self):
        self.width = 600
        self.height = 600
        pygame.display.set_mode((self.width, self.height))

    def run(self, reverse=False):  # меняет изображения для движения
        if reverse:
            rang = range(26, 1, -1)
        else:
            rang = range(1, 26)

        for i in rang:
            background = pygame.image.load(
                "data/GUI/bck/" + str(i) + ".jpg")
            screen.blit(background, (0, 0))

            clock.tick(FPS)
            pygame.display.flip()


# класс экрана рекордов игроков
class RecordsScreen:
    def __init__(self):
        self.width = 600
        self.height = 600
        pygame.display.set_mode((self.width, self.height))

        self.arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 20)
        self.records_screen_manager = pygame_gui.UIManager((600, 600),
                                                           'data/theme.json')
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((226, 545), (131, 42)),
            text='',
            manager=self.records_screen_manager,
            object_id=ObjectID(class_id='@records_screen',
                               object_id='#exit_button'))

        screen.blit(IMAGES['SIMPLE_BACKGROUND'], (0, 0))

        scoring_list = sorted(DatabaseQuery().call("SELECT * FROM Scoring"),
                              key=lambda x: x[2], reverse=True)
        if scoring_list:
            if len(scoring_list) < 10:
                count = len(scoring_list)
            else:
                count = 10
            for i in range(count):
                text = self.arcade_font.render(
                    str(i + 1) + ' ' + scoring_list[i][1] + '  ' + str(
                        scoring_list[i][2]) + ' pts', 1, (180, 0, 0))
                screen.blit(text, (100, 80 + i * 46))
        else:
            text = self.arcade_font.render('there is no any players!', 1,
                                           (180, 0, 0))
            screen.blit(text, (70, 250))

    def run(self):
        running = True
        while running:

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == self.exit_button:
                        TransitionScreen().run()
                        TransitionScreen().run(reverse=True)
                        StartScreen().run()
                        running = False

                self.records_screen_manager.process_events(event)

            self.records_screen_manager.update(FPS)
            self.records_screen_manager.draw_ui(screen)
            pygame.display.flip()


# класс экрана иницилизации
class InitScreen:
    def __init__(self):
        self.width = 600
        self.height = 600
        pygame.display.set_mode((self.width, self.height))

        self.arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 20)
        self.init_screen_manager = pygame_gui.UIManager((600, 600),
                                                        'data/theme.json')

        self.text = self.arcade_font.render('Enter your name', 1, (180, 0, 0))

        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((140, 240), (300, 60)),
            manager=self.init_screen_manager,
            object_id=ObjectID(class_id='@init_screen',
                               object_id='#text_box'))

        self.text_input.set_text_length_limit(10)

    def run(self):
        player_info = list()
        running = True
        while running:
            screen.blit(IMAGES['BACKGROUND'], (0, 0))
            screen.blit(self.text, (145, 150))

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN \
                            and self.text_input.get_text() != '':
                        player_name = self.text_input.get_text().lower()
                        player_info = DatabaseQuery().call(
                            f"SELECT * FROM Scoring WHERE PLAYER_NAME"
                            f" ='{player_name}'")

                        if not player_info:
                            DatabaseQuery().call(
                                f"INSERT INTO Scoring(PLAYER_NAME)"
                                f" VALUES('{player_name}')")
                            player_info = DatabaseQuery().call(
                                f"SELECT * FROM Scoring WHERE PLAYER_NAME"
                                f" ='{player_name}'")[0]
                        else:
                            player_info = player_info[0]

                        running = False

                self.init_screen_manager.process_events(event)

            self.init_screen_manager.update(FPS)
            self.init_screen_manager.draw_ui(screen)
            pygame.display.flip()

        if player_info[4] == 1:
            TransitionScreen().run()
            Level(3, 'data/maps/map3.txt').run(player_info[0])
        elif player_info[3] == 1:
            TransitionScreen().run()
            Level(2, 'data/maps/map2.txt').run(player_info[0])
        else:
            TransitionScreen().run()
            Level(1, 'data/maps/map1.txt').run(player_info[0])


# класс стартого экрана
class StartScreen:
    def __init__(self):
        self.width = 600
        self.height = 600
        pygame.display.set_mode((self.width, self.height))

        self.start_screen_manager = pygame_gui.UIManager(
            (self.width, self.height), 'data/theme.json')

        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((175, 120), (232, 76)),
            text='',
            manager=self.start_screen_manager,
            object_id=ObjectID(class_id='@start_screen',
                               object_id='#start_button'))

        self.records_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((175, 220), (232, 76)),
            text='',
            manager=self.start_screen_manager,
            object_id=ObjectID(class_id='@start_screen',
                               object_id='#records_button'))

    def run(self):
        screen.blit(IMAGES['BACKGROUND'], (0, 0))
        running = True
        while running:

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == self.start_button:
                        running = False
                        TransitionScreen().run()
                        TransitionScreen().run(reverse=True)
                        InitScreen().run()
                    elif event.ui_element == self.records_button:
                        running = False
                        TransitionScreen().run()
                        TransitionScreen().run(reverse=True)
                        RecordsScreen().run()

                self.start_screen_manager.process_events(event)

            self.start_screen_manager.update(FPS)
            self.start_screen_manager.draw_ui(screen)
            pygame.display.flip()


# класс финального экрана
class FinalScreen:
    def __init__(self):
        self.width = 600
        self.height = 600
        pygame.display.set_mode((self.width, self.height))

    def run(self):
        font = pygame.font.Font('data/fonts/arcade-n.ttf', 30)
        text = "Congratulations!"
        string_rendered = font.render(text, True, pygame.Color('yellow'))
        final_rect = string_rendered.get_rect()
        final_rect.x = SIZE[0] // 7
        final_rect.y = SIZE[1] // 4

        text2 = "You've pass the game"
        string_rendered2 = font.render(text2, True, pygame.Color('yellow'))
        final_rect2 = string_rendered.get_rect()
        final_rect2.x = 10
        final_rect2.y = SIZE[1] // 2

        cup_image = IMAGES['CUP']
        cup_rect = cup_image.get_rect()
        cup_rect.x = SIZE[0] // 3.8
        cup_rect.y = SIZE[1] // 1.8

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    running = False

            screen.fill((0, 0, 0))
            screen.blit(string_rendered, final_rect)
            screen.blit(string_rendered2, final_rect2)
            screen.blit(cup_image, cup_rect)

            clock.tick(FPS)
            pygame.display.flip()
        StartScreen().run()


if __name__ == '__main__':
    Level(1, 'data/maps/map1.txt').run(1)
