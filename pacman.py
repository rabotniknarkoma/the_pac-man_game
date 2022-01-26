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
arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 20)
INDENT = 20
FPS = 60
SCORE = 0
TILE_SIZE = 30
clock = pygame.time.Clock()


def load_image(name, color_key=None):
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


IMAGES = {'RED': load_image("red.png"),
          'GREEN': load_image("green.png"),
          'YELLOW': load_image("yellow.png"),
          'BLUE': load_image("blue.png"),
          'EDIBLE': load_image("edible.png"),
          'BACKGROUND': load_image("GUI/background.png"),
          'TILE': load_image("square.png"),
          'DOT': load_image("dot.png"),
          'HEART': load_image('heart.png')}


class Map:
    def __init__(self, filename):
        self.map_mask = []
        self.barriers = pygame.sprite.Group()
        self.entities = pygame.sprite.Group()
        self.dots = pygame.sprite.Group()
        with open(filename) as file:
            for line in file:
                self.map_mask.append(list(map(int, line.split())))
        self.height = len(self.map_mask)
        self.width = len(self.map_mask[0])
        self.render()

    def render(self):
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
    image = load_image("pacman.png")

    def __init__(self, *param):
        super().__init__(param[:-3])
        self.image = Player.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.parent_map = param[-1]
        self.rect.x = INDENT + param[-3] * TILE_SIZE
        self.rect.y = INDENT + param[-2] * TILE_SIZE
        self.speed = 2
        self.direction = None
        self.add(self.parent_map.entities)

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, self.parent_map.barriers):
            if self.direction == 'DOWN':
                self.rect.y -= self.speed
            elif self.direction == 'UP':
                self.rect.y += self.speed
            elif self.direction == 'RIGHT':
                self.rect.x -= self.speed
            elif self.direction == 'LEFT':
                self.rect.x += self.speed
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
    new_image = load_image("edible.png")

    def __init__(self, *param):
        super().__init__(param[:-4])
        self.color = param[-1]
        self.image = IMAGES[self.color]
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.parent_map = param[-2]
        self.rect.x = INDENT + param[-4] * TILE_SIZE
        self.rect.y = INDENT + param[-3] * TILE_SIZE
        self.counter = 0
        self.edible = False
        self.speed = 2
        self.direction = 'DOWN'
        self.add(self.parent_map.entities)

    def update(self, *args):
        if self.edible:
            self.image = IMAGES['EDIBLE']
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.image = IMAGES[self.color]
            self.image.set_colorkey(pygame.Color('white'))
        if pygame.sprite.spritecollideany(self, self.parent_map.barriers):
            if self.direction == 'DOWN':
                self.direction = 'UP'
            elif self.direction == 'UP':
                self.direction = 'DOWN'
            elif self.direction == 'RIGHT':
                self.direction = 'LEFT'
            elif self.direction == 'LEFT':
                self.direction = 'RIGHT'
        elif self.counter >= 40:
            self.direction = random.choice(['DOWN', 'UP', 'LEFT', 'RIGHT'])
            self.counter = 0
        if self.direction == 'DOWN':
            self.rect.y += self.speed
        elif self.direction == 'UP':
            self.rect.y -= self.speed
        elif self.direction == 'RIGHT':
            self.rect.x += self.speed
        elif self.direction == 'LEFT':
            self.rect.x -= self.speed
        self.counter += 1


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2, parent_map):
        super().__init__(parent_map.barriers)
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
        self.parent_map = parent_map
        self.image = IMAGES['TILE']
        self.rect = rect


class Dot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.image = IMAGES['DOT']
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.parent_map = param[-1]
        self.rect.x = INDENT + param[-3] * TILE_SIZE
        self.rect.y = INDENT + param[-2] * TILE_SIZE
        self.add(self.parent_map.dots)


class SmallDot(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(param[:-3])
        self.image = pygame.transform.scale(IMAGES['DOT'], (10, 10))
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.parent_map = param[-1]
        self.rect.x = INDENT + param[-3] * TILE_SIZE
        self.rect.y = INDENT + param[-2] * TILE_SIZE
        self.add(self.parent_map.dots)


class Heart(pygame.sprite.Sprite):
    def __init__(self, *param):
        super().__init__(*param[:-2])
        self.image = IMAGES['HEART']
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]


def the_game():
    global SCORE

    pygame.display.flip()

    main_map = Map('data/maps/map0.txt')
    player = Player(0, 0, main_map)
    dot = Dot(7, 12, main_map)
    small_dot = SmallDot(1, 6, main_map)
    red = Ghost(14, 6, main_map, 'RED')
    yellow = Ghost(15, 6, main_map, 'YELLOW')
    green = Ghost(16, 6, main_map, 'GREEN')
    blue = Ghost(17, 6, main_map, 'BLUE')
    # heart1 = Heart(10, 500)
    # heart2 = Heart(40, 500)
    # heart3 = Heart(70, 500)

    ticks = 0
    running = True
    flag = True
    font = pygame.font.Font(None, 30)
    while running:
        screen.fill(pygame.Color(0))
        main_map.barriers.draw(screen)
        main_map.entities.draw(screen)
        main_map.dots.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                main_map.entities.update(event)

        if pygame.sprite.collide_mask(player, red):
            if red.edible:
                red.mask.clear()
                red.kill()
                SCORE += 200
            else:
                player.mask.clear()
                player.kill()
                flag = False

        if pygame.sprite.collide_mask(player, yellow):
            if yellow.edible:
                yellow.mask.clear()
                yellow.kill()
                SCORE += 200
            else:
                player.mask.clear()
                player.kill()
                flag = False

        if pygame.sprite.collide_mask(player, green):
            if green.edible:
                green.mask.clear()
                green.kill()
                SCORE += 200
            else:
                player.mask.clear()
                player.kill()
                flag = False

        if pygame.sprite.collide_mask(player, blue):
            if red.edible:
                blue.mask.clear()
                blue.kill()
                SCORE += 200
            else:
                player.mask.clear()
                player.kill()
                flag = False

        if pygame.sprite.collide_mask(player, small_dot):
            small_dot.mask.clear()
            small_dot.kill()
            SCORE += 10

        if pygame.sprite.collide_mask(player, dot):
            dot.mask.clear()
            dot.kill()
            red.edible = True
            yellow.edible = True
            green.edible = True
            blue.edible = True
            ticks = 200

        if ticks == 0:
            red.edible = False
            yellow.edible = False
            green.edible = False
            blue.edible = False
        else:
            ticks -= 1
        text = 'SCORE:' + str(SCORE)
        string_rendered = font.render(text, True, pygame.Color('white'))
        score_rect = string_rendered.get_rect()
        score_rect.x = INDENT
        score_rect.y = INDENT + main_map.height * TILE_SIZE + 10

        screen.blit(string_rendered, score_rect)

        main_map.entities.update()
        clock.tick(FPS)
        pygame.display.flip()


def database_query(query):
    con = sqlite3.connect('data/database.db')
    cur = con.cursor()
    res = list(map(list, cur.execute(query).fetchall()))
    con.commit()
    return res


def transition_screen(reverse=False):
    if reverse:
        rang = range(26, 1, -1)
    else:
        rang = range(1, 26)

    for i in rang:
        background = pygame.image.load("data/GUI/bck/" + str(i) + ".jpg")
        screen.blit(background, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def records_screen():
    records_screen_manager = pygame_gui.UIManager((600, 600), 'data/theme.json')
    scoring_list = sorted(database_query("SELECT * FROM Scoring"),
                          key=lambda x: x[2], reverse=True)

    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((226, 545), (131, 42)),
        text='',
        manager=records_screen_manager,
        object_id=ObjectID(class_id='@records_screen',
                           object_id='#exit_button'))

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
        text = arcade_font.render('there is no any players!', 1, (180, 0, 0))
        screen.blit(text, (100, 250))

    running = True
    while running:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == exit_button:
                    transition_screen()
                    transition_screen(reverse=True)
                    start_screen()
                    running = False

            records_screen_manager.process_events(event)

        records_screen_manager.update(FPS)
        records_screen_manager.draw_ui(screen)

        pygame.display.flip()


def init_screen():
    init_screen_manager = pygame_gui.UIManager((600, 600), 'data/theme.json')

    text = arcade_font.render('Enter your name', 1, (180, 0, 0))

    text_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((140, 240), (300, 60)),
        manager=init_screen_manager,
        object_id=ObjectID(class_id='@init_screen',
                           object_id='#text_box'))

    text_input.set_text_length_limit(10)

    running = True
    while running:
        screen.blit(IMAGES['BACKGROUND'], (0, 0))
        screen.blit(text, (145, 150))

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_RETURN and text_input.get_text() != '':
                    player_name = text_input.get_text().lower()
                    player_info = database_query("SELECT * FROM Scoring "
                                                 "WHERE PLAYER_NAME = "
                                                 f"'{player_name}'")

                    if not player_info:
                        database_query("INSERT INTO Scoring(PLAYER_NAME) "
                                       f"VALUES('{player_name}')")
                    running = False
                    transition_screen()
                    the_game()

            init_screen_manager.process_events(event)

        init_screen_manager.update(FPS)
        init_screen_manager.draw_ui(screen)
        pygame.display.flip()


def start_screen():
    start_screen_manager = pygame_gui.UIManager((600, 600), 'data/theme.json')

    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((175, 120), (232, 76)),
        text='',
        manager=start_screen_manager,
        object_id=ObjectID(class_id='@start_screen',
                           object_id='#start_button'))

    records_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((175, 220), (232, 76)),
        text='',
        manager=start_screen_manager,
        object_id=ObjectID(class_id='@start_screen',
                           object_id='#records_button'))

    screen.blit(IMAGES['BACKGROUND'], (0, 0))

    running = True
    while running:

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == start_button:
                    running = False
                    transition_screen()
                    transition_screen(reverse=True)
                    init_screen()
                elif event.ui_element == records_button:
                    running = False
                    transition_screen()
                    transition_screen(reverse=True)
                    records_screen()

            start_screen_manager.process_events(event)

        start_screen_manager.update(FPS)
        start_screen_manager.draw_ui(screen)
        pygame.display.flip()


start_screen()
