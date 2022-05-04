import pygame
import pygame_gui
from pygame_gui.core import ObjectID

pygame.init()
SIZE = WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode(SIZE)
FPS = 60
clock = pygame.time.Clock()


class MapCreator:
    def __init__(self):
        self.arcade_font = pygame.font.Font('data/fonts/arcade-n.ttf', 10)
        self.arcade_font_small = pygame.font.Font('data/fonts/arcade-n.ttf',
                                                  8)
        self.map_edit_manager = pygame_gui.UIManager((600, 600),
                                                     'data/theme.json')

        self.text = self.arcade_font.render('Here you can create your own '
                                            'map', 1,
                                            (0, 0, 0))
        self.small_text = self.arcade_font_small.render('map name', 1,
                                                        (60, 60, 60))

        self.action = 'SET_CLEAR'

        self.create_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((460, 55), (120, 25)),
            text='Create map',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#create_button'))

        self.eraser_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((320, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#eraser_button'))

        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((360, 55), (90, 30)),
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#map_name_text_box'))

        self.text_input.set_text_length_limit(10)

        self.player_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((20, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#player_button'))

        self.tile_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((70, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#tile_button'))

        self.blue_ghost_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((120, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#blue_ghost_button'))

        self.red_ghost_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((170, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#red_ghost_button'))

        self.yellow_ghost_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((220, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#yellow_ghost_button'))

        self.green_ghost_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((270, 50), (35, 35)),
            text='',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#green_ghost_button'))

    def run(self):
        board = Board(30, 30, 50, 100)
        running = True
        while running:
            screen.fill(pygame.Color(175, 238, 238))
            screen.blit(self.text, (145, 10))
            screen.blit(self.small_text, (370, 46))

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    running = False
                if pygame.mouse.get_pressed()[0] and board.pos_on_board(
                        pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]):
                    board.on_click(board.get_cell(event.pos), self.action)
                    board.render(screen)
                    pygame.display.flip()
                elif event.type == pygame_gui.UI_BUTTON_PRESSED:

                    if event.ui_element == self.tile_button:
                        self.action = 'SET_TILE'
                    elif event.ui_element == self.eraser_button:
                        self.action = 'SET_CLEAR'
                    elif event.ui_element == self.player_button:
                        self.action = 'SET_PLAYER'
                    elif event.ui_element == self.red_ghost_button:
                        self.action = 'SET_RED'
                    elif event.ui_element == self.green_ghost_button:
                        self.action = 'SET_GREEN'
                    elif event.ui_element == self.blue_ghost_button:
                        self.action = 'SET_BLUE'
                    elif event.ui_element == self.yellow_ghost_button:
                        self.action = 'SET_YELLOW'
                    elif event.ui_element == self.create_button:
                        if self.text_input.get_text() != '' \
                                and board.enemy_list != []:
                            file_map = open(
                                'data/maps/' + self.text_input.get_text() +
                                '.txt', 'w+')
                            for line in board.board:
                                file_map.write(''.join(list(map(
                                    str, line))) + '\n')
                            file_map.write('\n')
                            file_map.write(';'.join(list(
                                map(lambda x: '-'.join(list(map(str, x))),
                                    board.enemy_list))))
                            file_map.close()

                self.map_edit_manager.process_events(event)

            board.render(screen)
            self.map_edit_manager.update(FPS)
            self.map_edit_manager.draw_ui(screen)
            pygame.display.flip()


class Board:
    def __init__(self, width, height, left, top):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.enemy_list = []
        self.left = left
        self.top = top
        self.cell_size = 16

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen_to_render):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.board[y][x] == 0:
                    pygame.draw.rect(screen_to_render,
                                     pygame.Color(255, 255, 255), (
                                         x * self.cell_size + self.left,
                                         y * self.cell_size + self.top,
                                         self.cell_size, self.cell_size), 1)
                elif self.board[y][x] == 1:
                    pygame.draw.rect(screen_to_render,
                                     pygame.Color(106, 13, 173), (
                                         x * self.cell_size + self.left,
                                         y * self.cell_size + self.top,
                                         self.cell_size, self.cell_size))
        for i in self.enemy_list:
            if i[0] == 'G' and i[-1] == 'RED':
                IMAGE = pygame.transform.scale(
                    pygame.image.load('data/red.png').convert(),
                    (self.cell_size, self.cell_size))
                rect = IMAGE.get_rect()
                rect.x, rect.y = i[1] * self.cell_size + self.left, i[
                    2] * self.cell_size + self.top
                screen_to_render.blit(IMAGE, rect)

            elif i[0] == 'G' and i[-1] == 'GREEN':
                IMAGE = pygame.transform.scale(
                    pygame.image.load('data/green.png').convert(),
                    (self.cell_size, self.cell_size))
                rect = IMAGE.get_rect()
                rect.x, rect.y = i[1] * self.cell_size + self.left, i[
                    2] * self.cell_size + self.top
                screen_to_render.blit(IMAGE, rect)

            elif i[0] == 'G' and i[-1] == 'BLUE':
                IMAGE = pygame.transform.scale(
                    pygame.image.load('data/blue.png').convert(),
                    (self.cell_size, self.cell_size))
                rect = IMAGE.get_rect()
                rect.x, rect.y = i[1] * self.cell_size + self.left, i[
                    2] * self.cell_size + self.top
                screen_to_render.blit(IMAGE, rect)

            elif i[0] == 'G' and i[-1] == 'YELLOW':
                IMAGE = pygame.transform.scale(
                    pygame.image.load('data/yellow.png').convert(),
                    (self.cell_size, self.cell_size))
                rect = IMAGE.get_rect()
                rect.x, rect.y = i[1] * self.cell_size + self.left, i[
                    2] * self.cell_size + self.top
                screen_to_render.blit(IMAGE, rect)

            elif i[0] == 'P':
                IMAGE = pygame.transform.scale(
                    pygame.image.load('data/pacman.png').convert(),
                    (self.cell_size, self.cell_size))
                rect = IMAGE.get_rect()
                rect.x, rect.y = i[1] * self.cell_size + self.left, i[
                    2] * self.cell_size + self.top
                screen_to_render.blit(IMAGE, rect)

    def get_cell(self, mouse_pos):
        x = 0
        while not (x * self.cell_size <= mouse_pos[0] - self.left <= (
                x + 1) * self.cell_size):
            x += 1
        y = 0
        while not (y * self.cell_size <= mouse_pos[1] - self.top <= (
                y + 1) * self.cell_size):
            y += 1
        return x, y

    def on_click(self, cell_coords, action):
        for i in range(len(self.enemy_list) - 1):
            if self.enemy_list[i][1] == cell_coords[0] and \
                    self.enemy_list[i][2] == cell_coords[1]:
                del self.enemy_list[i]
        if action == 'SET_TILE':
            self.board[cell_coords[1]][cell_coords[0]] = 1
        elif action == 'SET_CLEAR':
            self.board[cell_coords[1]][cell_coords[0]] = 0
        elif action == 'SET_RED':
            self.enemy_list.append(
                ['G', cell_coords[0], cell_coords[1], 'RED'])
        elif action == 'SET_GREEN':
            self.enemy_list.append(
                ['G', cell_coords[0], cell_coords[1], 'GREEN'])
        elif action == 'SET_BLUE':
            self.enemy_list.append(
                ['G', cell_coords[0], cell_coords[1], 'BLUE'])
        elif action == 'SET_YELLOW':
            self.enemy_list.append(
                ['G', cell_coords[0], cell_coords[1], 'YELLOW'])
        elif action == 'SET_PLAYER':
            flag = False
            for i in self.enemy_list:
                if i[0] == 'P':
                    flag = True
            if not flag:
                self.enemy_list.append(
                    ['P', cell_coords[0], cell_coords[1]])

    def pos_on_board(self, x, y):
        if self.left <= x <= self.width * self.cell_size + self.left and \
                self.top <= y <= self.height * self.cell_size + self.top:
            return True
        return False


MapCreator().run()
