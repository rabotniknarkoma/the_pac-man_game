import random
import pygame
import sys
import os
import pygame_gui
import sqlite3
from pygame_gui.core import ObjectID

pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 20)
background = pygame.image.load("data/GUI/background.png")
SCORE = 0
FPS = 60
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


def terminate():
    pygame.quit()
    sys.exit()


class Player(pygame.sprite.Sprite):
    image = load_image("pacman.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Player.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]
        self.speed = 3
        self.const = (0, '')

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.const = (0, '')
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 454:
                self.rect.y = 453
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.const = (0, '')
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 553
        if args and args[0].key == pygame.K_DOWN:
            self.image = pygame.transform.rotate(Player.image, 270)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (self.speed, 'y')
        elif args and args[0].key == pygame.K_UP:
            self.image = pygame.transform.rotate(Player.image, 90)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (self.speed * -1, 'y')
        elif args and args[0].key == pygame.K_LEFT:
            self.image = pygame.transform.flip(Player.image, True, False)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (self.speed * -1, 'x')
        elif args and args[0].key == pygame.K_RIGHT:
            self.image = Player.image
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (self.speed, 'x')
        a, b = self.const
        if b == 'x':
            self.rect.x += a
        elif b == 'y':
            self.rect.y += a


class Red(pygame.sprite.Sprite):
    image = load_image("red.png")
    new_image = load_image("edible_ghost.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Red.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]
        self.turn = random.randint(1, 4)
        self.counter = 0
        self.edible = False

    def update(self, *args):
        if self.edible:
            self.image = Red.new_image
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.image = Red.image
            self.image.set_colorkey(pygame.Color('white'))
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 452:
                self.rect.y = 451
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.turn = random.choice([1, 3])
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 553
        elif self.counter >= 40:
            self.turn = random.randint(1, 4)
            self.counter = 0
        if self.turn == 1:
            self.rect.y -= 2
        elif self.turn == 2:
            self.rect.x += 2
        elif self.turn == 3:
            self.rect.y += 2
        elif self.turn == 4:
            self.rect.x -= 2
        self.counter += 1


class Green(pygame.sprite.Sprite):
    image = load_image("green.png")
    new_image = load_image("edible_ghost.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Green.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]
        self.turn = random.randint(1, 4)
        self.counter = 0
        self.edible = False

    def update(self, *args):
        if self.edible:
            self.image = Green.new_image
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.image = Green.image
            self.image.set_colorkey(pygame.Color('white'))
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 452:
                self.rect.y = 451
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.turn = random.choice([1, 3])
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 553
        elif self.counter >= 40:
            self.turn = random.randint(1, 4)
            self.counter = 0
        if self.turn == 1:
            self.rect.y -= 2
        elif self.turn == 2:
            self.rect.x += 2
        elif self.turn == 3:
            self.rect.y += 2
        elif self.turn == 4:
            self.rect.x -= 2
        self.counter += 1


class Yellow(pygame.sprite.Sprite):
    image = load_image("yellow.png")
    new_image = load_image("edible_ghost.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Yellow.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]
        self.turn = random.randint(1, 4)
        self.counter = 0
        self.edible = False

    def update(self, *args):
        if self.edible:
            self.image = Yellow.new_image
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.image = Yellow.image
            self.image.set_colorkey(pygame.Color('white'))
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 452:
                self.rect.y = 451
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.turn = random.choice([1, 3])
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 553
        elif self.counter >= 40:
            self.turn = random.randint(1, 4)
            self.counter = 0
        if self.turn == 1:
            self.rect.y -= 2
        elif self.turn == 2:
            self.rect.x += 2
        elif self.turn == 3:
            self.rect.y += 2
        elif self.turn == 4:
            self.rect.x -= 2
        self.counter += 1


class Blue(pygame.sprite.Sprite):
    image = load_image("blue.png")
    new_image = load_image("edible_ghost.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Blue.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]
        self.turn = random.randint(1, 4)
        self.counter = 0
        self.edible = False

    def update(self, *args):
        if self.edible:
            self.image = Blue.new_image
            self.image.set_colorkey(pygame.Color('white'))
        else:
            self.image = Blue.image
            self.image.set_colorkey(pygame.Color('white'))
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 452:
                self.rect.y = 451
        elif pygame.sprite.spritecollideany(self, vertical_borders):
            self.turn = random.choice([1, 3])
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 554
        elif self.counter >= 40:
            self.turn = random.randint(1, 4)
            self.counter = 0
        if self.turn == 1:
            self.rect.y -= 2
        elif self.turn == 2:
            self.rect.x += 2
        elif self.turn == 3:
            self.rect.y += 2
        elif self.turn == 4:
            self.rect.x -= 2
        self.counter += 1


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

        self.image.fill(pygame.Color('white'))


class Dot(pygame.sprite.Sprite):
    image = load_image("dot.png")

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = Dot.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]


class SmallDot(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("dot.png"), (10, 10))

    def __init__(self, *param):
        super().__init__(param[:-2])
        self.image = SmallDot.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]


class Heart(pygame.sprite.Sprite):
    image = load_image('heart.png')

    def __init__(self, *param):
        super().__init__(*param[:-2])
        self.image = Heart.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = param[-2]
        self.rect.y = param[-1]


def the_game():
    global SCORE

    pygame.display.flip()
    dot = Dot(43, 58)
    small_dot = SmallDot(228, 229)
    red = Red(10, 10)
    yellow = Yellow(50, 10)
    green = Green(90, 10)
    blue = Blue(130, 10)
    player = Player(200, 300)
    heart1 = Heart(10, 500)
    heart2 = Heart(40, 500)
    heart3 = Heart(70, 500)

    all_sprites.add(dot)
    all_sprites.add(small_dot)
    all_sprites.add(red)
    all_sprites.add(yellow)
    all_sprites.add(green)
    all_sprites.add(blue)
    all_sprites.add(player)
    all_sprites.add(heart1)
    all_sprites.add(heart2)
    all_sprites.add(heart3)

    b1 = Border(5, 5, width - 5, 5)
    b2 = Border(5, 500 - 5, width - 5, 500 - 5)
    b3 = Border(5, 5, 5, 500 - 5)
    b4 = Border(width - 5, 5, width - 5, 500 - 5)

    ticks = 0

    running = True
    flag = True
    font = pygame.font.Font(None, 30)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                all_sprites.update(event)

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
        score_rect.x = 400
        score_rect.y = 500

        if flag:
            all_sprites.update()
        screen.fill(pygame.Color('black'))
        screen.blit(string_rendered, score_rect)
        all_sprites.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    terminate()


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
        screen.blit(background, (0, 0))
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
                    print(player_info)

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

    screen.blit(background, (0, 0))

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
