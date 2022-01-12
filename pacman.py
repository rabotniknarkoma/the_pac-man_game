import random
import pygame
import sys
import os


pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
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

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Player.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 50
        self.rect.y = 50
        self.const = (0, '')

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.const = (0, '')
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 354:
                self.rect.y = 353
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.const = (0, '')
            if self.rect.x <= 5:
                self.rect.x = 6
            elif self.rect.x >= 555:
                self.rect.x = 553
        if args and args[0].key == pygame.K_DOWN:
            self.image = pygame.transform.rotate(Player.image, 270)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (3, 'y')
        elif args and args[0].key == pygame.K_UP:
            self.image = pygame.transform.rotate(Player.image, 90)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (-3, 'y')
        elif args and args[0].key == pygame.K_LEFT:
            self.image = pygame.transform.flip(Player.image, True, False)
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (-3, 'x')
        elif args and args[0].key == pygame.K_RIGHT:
            self.image = Player.image
            self.image.set_colorkey(pygame.Color('white'))
            self.const = (3, 'x')
        a, b = self.const
        if b == 'x':
            self.rect.x += a
        elif b == 'y':
            self.rect.y += a


class Red(pygame.sprite.Sprite):
    image = load_image("red.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Red.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 10
        self.rect.y = 10
        self.turn = random.randint(1, 4)
        self.counter = 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 352:
                self.rect.y = 351
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

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Green.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 70
        self.rect.y = 10
        self.turn = random.randint(1, 4)
        self.counter = 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 352:
                self.rect.y = 351
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

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Yellow.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 130
        self.rect.y = 10
        self.turn = random.randint(1, 4)
        self.counter = 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 352:
                self.rect.y = 351
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

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Blue.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 190
        self.rect.y = 10
        self.turn = random.randint(1, 4)
        self.counter = 0

    def update(self, *args):
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.turn = random.choice([2, 4])
            if self.rect.y <= 5:
                self.rect.y = 6
            elif self.rect.y >= 352:
                self.rect.y = 351
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


class Dot(pygame.sprite.Sprite):
    image = load_image("dot.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Dot.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 80
        self.rect.y = 80
        self.const = (0, '')


class SmallDot(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image("dot.png"), (10, 10))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = SmallDot.image
        self.image.set_colorkey(pygame.Color('white'))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = 100
        self.rect.y = 100
        self.const = (0, '')


def the_game():
    pygame.display.flip()
    dot = Dot(all_sprites)
    small_dot = SmallDot(all_sprites)
    red = Red(all_sprites)
    yellow = Yellow(all_sprites)
    green = Green(all_sprites)
    blue = Blue(all_sprites)
    player = Player(all_sprites)
    Border(5, 5, width - 5, 5)
    Border(5, 400 - 5, width - 5, 400 - 5)
    Border(5, 5, 5, 400 - 5)
    Border(width - 5, 5, width - 5, 400 - 5)
    running = True
    font = pygame.font.Font(None, 30)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                all_sprites.update(event)

        heart1_image = load_image('heart.png')
        heart1_image.set_colorkey(pygame.Color('white'))
        heart1_rect = heart1_image.get_rect()
        heart1_rect.x = 10
        heart1_rect.y = 500

        heart2_image = load_image('heart.png')
        heart2_image.set_colorkey(pygame.Color('white'))
        heart2_rect = heart1_image.get_rect()
        heart2_rect.x = 50
        heart2_rect.y = 500

        heart3_image = load_image('heart.png')
        heart3_image.set_colorkey(pygame.Color('white'))
        heart3_rect = heart1_image.get_rect()
        heart3_rect.x = 90
        heart3_rect.y = 500

        text = 'SCORE:' + str(SCORE)
        string_rendered = font.render(text, True, pygame.Color('white'))
        score_rect = string_rendered.get_rect()
        score_rect.x = 400
        score_rect.y = 500

        all_sprites.update()
        screen.fill(pygame.Color('black'))
        screen.blit(heart1_image, heart1_rect)
        screen.blit(heart2_image, heart2_rect)
        screen.blit(heart3_image, heart3_rect)
        screen.blit(string_rendered, score_rect)
        all_sprites.draw(screen)

        clock.tick(FPS)
        pygame.display.flip()
    terminate()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    screen.fill(pygame.color.Color('black'))
    font = pygame.font.Font(None, 30)
    text_coord = 150
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                the_game()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                the_game()
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
