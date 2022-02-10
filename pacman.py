import random
import pygame
import sys
import os
import pygame_gui
import sqlite3
from pygame_gui.core import ObjectID

pygame.init()
SIZE = WIDTH, HEIGHT = 580, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60
clock = pygame.time.Clock()


class LoadImage:
    def __call__(self, name):
        color_key = None
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        found_image = pygame.image.load(fullname)
        if color_key is not None:
            found_image = found_image.convert()
            if color_key == -1:
                color_key = found_image.get_at((0, 0))
            found_image.set_colorkey(color_key)
        else:
            found_image = found_image.convert_alpha()
        return found_image


IMAGES = {'PACMAN': LoadImage()('pacman.png'),
          'RED': LoadImage()("red.png"),
          'GREEN': LoadImage()("green.png"),
          'YELLOW': LoadImage()("yellow.png"),
          'BLUE': LoadImage()("blue.png"),
          'EDIBLE': LoadImage()("edible.png"),
          'BACKGROUND': LoadImage()("GUI/background.png"),
          'TILE': LoadImage()("square.png"),
          'DOT': LoadImage()("dot.png"),
          'HEART': LoadImage()('heart.png')}


class Map:
    def __init__(self, filename, level):
        self.constants = {'TILE_SIZE': 30,
                          'INDENT': 20}
        self.map_mask = []
        with open(filename) as file:
            for line in file:
                self.map_mask.append(list(map(int, line.split())))
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

    def get_free_tiles(self):
        res = []
        for i in range(len(self.map_mask)):
            for j in range(len(self.map_mask[0])):
                if self.map_mask[i][j] == 0:
                    res.append((i, j))
        return res

    def fill_dots(self):
        free_tiles = sorted(self.free_tiles, key=lambda x: random.random())
        for i in free_tiles[:-3]:
            SmallDot(i[1], i[0], self)
        for i in free_tiles[-3:]:
            Dot(i[1], i[0], self)

    def render(self):
        TILE_SIZE = self.constants['TILE_SIZE']
        INDENT = self.constants['INDENT']
        b1 = Border(INDENT - 1, INDENT - 1,
                    INDENT + self.width * TILE_SIZE + 1, INDENT - 1, self)

        b2 = Border(INDENT - 1, INDENT - 1, INDENT - 1,
                    INDENT + self.height * TILE_SIZE + 1, self)

        b3 = Border(INDENT - 1,
                    INDENT + self.height * TILE_SIZE + 1,
                    INDENT + self.width * TILE_SIZE + 1,
                    INDENT + self.height * TILE_SIZE + 1, self)

        b4 = Border(INDENT + self.width * TILE_SIZE + 1,
                    INDENT - 1, INDENT + self.width * TILE_SIZE + 1,
                    INDENT + self.height * TILE_SIZE + 1, self)

        for i in range(self.height):
            for j in range(self.height):
                if self.map_mask[j][i] == 1:
                    rect = pygame.Rect(INDENT + i * TILE_SIZE,
                                       INDENT + j * TILE_SIZE,
                                       TILE_SIZE, TILE_SIZE)
                    tile = Tile(rect, self)


class Player(pygame.sprite.Sprite):
    image = IMAGES['PACMAN']

    def __init__(self, *param):
        super().__init__(param[:-3])
        self.image = Player.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.map = param[-1]

        INDENT = self.map.constants['INDENT']
        TILE_SIZE = self.map.constants['TILE_SIZE']

        self.rect.x = INDENT + param[-3] * TILE_SIZE
        self.rect.y = INDENT + param[-2] * TILE_SIZE
        self.speed = 2
        self.direction = None
        self.add(self.map.player)
        self.map.player_object = self

    def get_tile_location(self):
        TILE_SIZE = self.map.constants['TILE_SIZE']
        INDENT = self.map.constants['INDENT']

        tile_x = (self.rect.x - INDENT) // TILE_SIZE
        if TILE_SIZE - (self.rect.x - INDENT) % TILE_SIZE < (
                self.rect.x - INDENT) % TILE_SIZE:
            tile_x = ((self.rect.x - INDENT) + TILE_SIZE
                      - (self.rect.x - INDENT) % TILE_SIZE) // TILE_SIZE

        tile_y = (self.rect.y - INDENT) // TILE_SIZE
        if TILE_SIZE - (self.rect.y - INDENT) % TILE_SIZE < (
                self.rect.y - INDENT) % TILE_SIZE:
            tile_y = ((self.rect.y - INDENT) + TILE_SIZE
                      - (self.rect.y - INDENT) % TILE_SIZE) // TILE_SIZE
        return tile_x, tile_y

    def can_eat_ghosts(self):
        if self.map.ghosts_list[0].edible == False:
            for i in self.map.ghosts_list:
                i.change_edibility()

    def update(self, *args):
        TILE_SIZE = self.map.constants['TILE_SIZE']
        INDENT = self.map.constants['INDENT']

        if pygame.sprite.spritecollideany(self, self.map.barriers):
            x_calibration = (self.rect.x - INDENT) % TILE_SIZE
            if TILE_SIZE - x_calibration < x_calibration:
                x_calibration = x_calibration - TILE_SIZE
            y_calibration = (self.rect.y - INDENT) % TILE_SIZE
            if TILE_SIZE - y_calibration < y_calibration:
                y_calibration = y_calibration - TILE_SIZE

            next_free = False if self.map.map_mask[
                (self.rect.x - INDENT + x_calibration) // TILE_SIZE][
                (self.rect.y - INDENT + y_calibration) // TILE_SIZE] else True
            if self.direction == 'DOWN':
                if x_calibration > 8 or x_calibration == 0 or not next_free:
                    self.rect.y -= self.speed
                else:
                    self.rect.x -= x_calibration
            elif self.direction == 'UP':
                if x_calibration > 8 or x_calibration == 0 or not next_free:
                    self.rect.y += self.speed
                else:
                    self.rect.x -= x_calibration
            elif self.direction == 'RIGHT':
                if y_calibration > 8 or y_calibration == 0 or not next_free:
                    self.rect.x -= self.speed
                else:
                    self.rect.y -= y_calibration
            elif self.direction == 'LEFT':
                if y_calibration > 8 or y_calibration == 0 or not next_free:
                    self.rect.x += self.speed
                else:
                    self.rect.y -= y_calibration
        if args and args[0].key == pygame.K_DOWN:
            self.image = pygame.transform.rotate(Player.image, 270)
            self.direction = 'DOWN'
        elif args and args[0].key == pygame.K_UP:
            self.image = pygame.transform.rotate(Player.image, 90)
            self.direction = 'UP'
        elif args and args[0].key == pygame.K_LEFT:
            self.image = pygame.transform.flip(Player.image, True, False)
            self.direction = 'LEFT'
        elif args and args[0].key == pygame.K_RIGHT:
            self.image = Player.image
            self.direction = 'RIGHT'

        self.image.set_colorkey(pygame.Color('white'))
        if self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed


class Ghost(pygame.sprite.Sprite):
    edible_image = IMAGES['EDIBLE']

    def __init__(self, *param):
        super().__init__(param[:-4])
        self.color = param[-1]
        self.image = IMAGES[self.color]
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.map = param[-2]

        INDENT = self.map.constants['INDENT']
        TILE_SIZE = self.map.constants['TILE_SIZE']

        self.rect.x = INDENT + param[-4] * TILE_SIZE
        self.rect.y = INDENT + param[-3] * TILE_SIZE
        self.moving_loop_counter = 0
        self.edible = False
        self.speed = 2
        self.next_location = None
        self.edible_counter = 0
        self.direction = random.choice(['DOWN', 'UP', 'LEFT', 'RIGHT'])
        self.add(self.map.ghosts)
        self.map.ghosts_list.append(self)

    def get_tile_location(self):
        TILE_SIZE = self.map.constants['TILE_SIZE']
        INDENT = self.map.constants['INDENT']

        tile_x = (self.rect.x - INDENT) // TILE_SIZE
        if TILE_SIZE - (self.rect.x - INDENT) % TILE_SIZE < (
                self.rect.x - INDENT) % TILE_SIZE:
            tile_x = ((self.rect.x - INDENT) + TILE_SIZE
                      - (self.rect.x - INDENT) % TILE_SIZE) // TILE_SIZE

        tile_y = (self.rect.y - INDENT) // TILE_SIZE
        if TILE_SIZE - (self.rect.y - INDENT) % TILE_SIZE < (
                self.rect.y - INDENT) % TILE_SIZE:
            tile_y = ((self.rect.y - INDENT) + TILE_SIZE
                      - (self.rect.y - INDENT) % TILE_SIZE) // TILE_SIZE
        return tile_x, tile_y

    def random_moving(self):
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
            self.direction = random.choice(direction_choices)

        if self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed

    def find_path_step(self, start, target):
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
                if 0 <= next_x < self.map.width \
                        and 0 <= next_y < self.map.height \
                        and self.map.map_mask[next_y][next_x] == 0 \
                        and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y

    def persecution(self):
        TILE_SIZE = self.map.constants['TILE_SIZE']
        INDENT = self.map.constants['INDENT']

        self_location = self.get_tile_location()
        player_location = self.map.player_object.get_tile_location()

        if self.next_location is None:
            self.next_location = self.find_path_step(self_location,
                                                     player_location)
        if self.next_location[1] * TILE_SIZE - self.rect.y + INDENT > 0:
            self.rect.y += self.speed
        elif self.next_location[1] * TILE_SIZE - self.rect.y + INDENT < 0:
            self.rect.y -= self.speed
        elif self.next_location[0] * TILE_SIZE - self.rect.x + INDENT > 0:
            self.rect.x += self.speed
        elif self.next_location[0] * TILE_SIZE - self.rect.x + INDENT < 0:
            self.rect.x -= self.speed
        else:
            self.next_location = self.find_path_step(self_location,
                                                     player_location)

    def change_edibility(self):
        if self.edible:
            self.edible = False
            self.image = IMAGES[self.color]
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.edible = True
            self.image = IMAGES['EDIBLE']
            self.image.set_colorkey(pygame.Color('white'))
            self.edible_counter = self.map.level.constants['EDIBLE_TIME']

    def update(self, *args):
        TILE_SIZE = self.map.constants['TILE_SIZE']
        INDENT = self.map.constants['INDENT']

        if self.edible_counter > 1:
            self.edible_counter -= 1
        elif self.edible_counter == 1:
            self.change_edibility()
            self.edible_counter -= 1

        if pygame.sprite.spritecollideany(self, self.map.player):
            if self.edible:
                self.mask.clear()
                self.kill()
                self.map.level.score += self.map.level.constants[
                    'POINTS_FOR_GHOSTS']
            else:
                self.map.player_object.mask.clear()
                self.map.player_object.kill()
                pygame.time.wait(1000)
                self.map.level.render()

        if not self.edible:
            if self.moving_loop_counter < 500:  # сделать константой уровня
                self.random_moving()
                self.moving_loop_counter += 1
            elif self.moving_loop_counter == 500:
                if (self.rect.x - INDENT) % TILE_SIZE != 0:
                    self.rect.x += self.speed
                elif (self.rect.y - INDENT) % TILE_SIZE != 0:
                    self.rect.y += self.speed
                else:
                    self.moving_loop_counter += 1
            elif self.moving_loop_counter < 1300:  # сделать константой уровня
                self.persecution()
                self.moving_loop_counter += 1
            else:
                self.moving_loop_counter = 0
                self.random_moving()
        else:
            self.moving_loop_counter = 0
            self.random_moving()


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, map):
        super().__init__(map.barriers)
        if x1 == x2:
            self.image = pygame.Surface([1, abs(y2 - y1)])
            self.rect = pygame.Rect(x1, y1, 1, abs(y2 - y1))
        else:
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)
        self.image.fill(pygame.Color('white'))


class Tile(pygame.sprite.Sprite):
    def __init__(self, rect, parent_map):
        super().__init__(parent_map.barriers)
        self.map = parent_map
        self.image = IMAGES['TILE']
        self.rect = rect


class Dot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.map = param[-1]

        INDENT = self.map.constants['INDENT']
        TILE_SIZE = self.map.constants['TILE_SIZE']

        self.image = pygame.transform.scale(IMAGES['DOT'], (TILE_SIZE // 2,
                                                            TILE_SIZE // 2))
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = (TILE_SIZE - TILE_SIZE // 2) // 2 + INDENT + param[
            -3] * TILE_SIZE
        self.rect.y = (TILE_SIZE - TILE_SIZE // 2) // 2 + INDENT + param[
            -2] * TILE_SIZE

        self.add(self.map.dots)

    def update(self):
        if pygame.sprite.spritecollideany(self, self.map.player):
            self.map.player_object.can_eat_ghosts()
            self.mask.clear()
            self.kill()
            self.map.level.score += self.map.level.constants['POINTS_FOR_DOTS']


class SmallDot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.map = param[-1]

        INDENT = self.map.constants['INDENT']
        TILE_SIZE = self.map.constants['TILE_SIZE']

        self.image = pygame.transform.scale(IMAGES['DOT'], (TILE_SIZE // 5,
                                                            TILE_SIZE // 5))
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = (TILE_SIZE - TILE_SIZE // 5) // 2 + INDENT + param[
            -3] * TILE_SIZE
        self.rect.y = (TILE_SIZE - TILE_SIZE // 5) // 2 + INDENT + param[
            -2] * TILE_SIZE

        self.add(self.map.dots)

    def update(self):
        if pygame.sprite.spritecollideany(self, self.map.player):
            self.mask.clear()
            self.kill()
            self.map.level.score += self.map.level.constants['POINTS_FOR_DOTS']


class Heart(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(*param[:-2])
        self.image = IMAGES['HEART']
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]


class Level:
    def __init__(self, ghsts, plyer, map_name):
        self.ghosts_list = ghsts  # сменить названия
        self.player_list = plyer  # сменить названия
        self.map_name = map_name
        self.score = 0
        self.lifes = 3
        self.render()
        self.constants = {'POINTS_FOR_DOTS': 20,
                          'POINTS_FOR_GHOSTS': 200,
                          'EDIBLE_TIME': 400}

    def render(self):
        self.main_map = Map(self.map_name, self)
        self.red = Ghost(self.ghosts_list[0][0], self.ghosts_list[0][1],
                         self.main_map, 'RED')
        self.yellow = Ghost(self.ghosts_list[1][0], self.ghosts_list[1][1],
                            self.main_map, 'YELLOW')
        self.blue = Ghost(self.ghosts_list[2][0], self.ghosts_list[2][1],
                          self.main_map, 'BLUE')
        self.green = Ghost(self.ghosts_list[3][0], self.ghosts_list[3][1],
                           self.main_map, 'GREEN')
        self.player = Player(self.player_list[0], self.player_list[1],
                             self.main_map)

    def change_constants(self, change_dict):
        for key, val in change_dict:
            if key in self.constants:
                self.constants[key] = val

    def draw_score(self):
        font = pygame.font.Font(None, 30)
        INDENT = self.main_map.constants['INDENT']
        TILE_SIZE = self.main_map.constants['TILE_SIZE']

        text = 'SCORE:' + str(self.score)
        string_rendered = font.render(text, True, pygame.Color('white'))
        score_rect = string_rendered.get_rect()
        score_rect.x = INDENT
        score_rect.y = INDENT + self.main_map.height * TILE_SIZE + 10
        screen.blit(string_rendered, score_rect)

    def draw_level(self):
        screen.fill(pygame.Color(0))
        self.main_map.barriers.draw(screen)
        self.main_map.ghosts.draw(screen)
        self.main_map.player.draw(screen)
        self.main_map.dots.draw(screen)

    def run(self, user_id):
        self.user_id = user_id
        running = True
        flag = True

        while running:
            self.draw_level()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    self.main_map.player.update(event)

            self.draw_score()
            self.main_map.ghosts.update()
            self.main_map.player.update()
            self.main_map.dots.update()

            clock.tick(FPS)
            pygame.display.flip()


class DatabaseQuery:
    def __init__(self):
        pass

    def call(self, query):
        con = sqlite3.connect('data/database.db')
        cur = con.cursor()
        res = list(map(list, cur.execute(query).fetchall()))
        con.commit()
        return res


class TransitionScreen:
    def __init__(self):
        pass

    def run(self, reverse=False):
        if reverse:
            rang = range(26, 1, -1)
        else:
            rang = range(1, 26)

        for i in rang:
            self.background = pygame.image.load(
                "data/GUI/bck/" + str(i) + ".jpg")
            screen.blit(self.background, (0, 0))

            clock.tick(FPS)
            pygame.display.flip()


class RecordsScreen:
    def __init__(self):
        self.arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 20)
        self.records_screen_manager = pygame_gui.UIManager((600, 600),
                                                           'data/theme.json')
        self.exit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((226, 545), (131, 42)),
            text='',
            manager=self.records_screen_manager,
            object_id=ObjectID(class_id='@records_screen',
                               object_id='#exit_button'))

        scoring_list = sorted(DatabaseQuery().call("SELECT * FROM Scoring"),
                              key=lambda x: x[2], reverse=True)
        if scoring_list:
            if len(scoring_list) < 10:
                count = len(scoring_list)
            else:
                count = 10
            for i in range(count):
                text = arcade_font.render(
                    str(i + 1) + ' ' + scoring_list[i][1] + '  ' + str(
                        scoring_list[i][2]) + ' pts', 1, (180, 0, 0))
                screen.blit(text, (100, 80 + i * 46))
        else:
            text = arcade_font.render('there is no any players!', 1,
                                      (180, 0, 0))
            screen.blit(text, (100, 250))

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


class InitScreen:
    def __init__(self):
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
        running = True
        while running:
            screen.blit(IMAGES['BACKGROUND'], (0, 0))
            screen.blit(self.text, (145, 150))

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN \
                            and self.text_input.get_text() != '':
                        player_name = self.text_input.get_text().lower()
                        player_info = DatabaseQuery().call(
                            f"SELECT * FROM Scoring WHERE PLAYER_NAME"
                            f" ='{player_name}'")[0]

                        if not player_info:
                            DatabaseQuery().call(
                                f"INSERT INTO Scoring(PLAYER_NAME)"
                                f" VALUES('{player_name}')")
                            player_info = DatabaseQuery().call(
                                f"SELECT * FROM Scoring WHERE PLAYER_NAME"
                                f" ='{player_name}'")[0]

                        if player_info[4] == 1:
                            TransitionScreen().run()
                            pass
                            # Lvl3.run(player_info[0])
                        elif player_info[3] == 1:
                            TransitionScreen().run()
                            pass
                            # Lvl2.run(player_info[0])
                        else:
                            TransitionScreen().run()
                            Lvl1.run(player_info[0])

                        running = False

                self.init_screen_manager.process_events(event)

            self.init_screen_manager.update(FPS)
            self.init_screen_manager.draw_ui(screen)
            pygame.display.flip()


class StartScreen:
    def __init__(self):
        self.start_screen_manager = pygame_gui.UIManager((600, 600),
                                                         'data/theme.json')
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
                    running = False
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


if __name__ == '__main__':
    G = [(14, 6), (15, 6), (13, 6), (16, 6)]
    Lvl1 = Level(G, (1, 1), 'data/maps/map0.txt')
    StartScreen().run()
