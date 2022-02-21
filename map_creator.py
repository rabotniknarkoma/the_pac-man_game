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
        self.map_edit_manager = pygame_gui.UIManager((600, 600),
                                                     'data/theme.json')

        self.text = self.arcade_font.render('Here you can create your own '
                                            'map', 1,
                                            (0, 0, 0))

        self.create_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((450, 55), (120, 25)),
            text='Create map',
            manager=self.map_edit_manager,
            object_id=ObjectID(class_id='@map_creator_screen',
                               object_id='#create_button'))

        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((320, 55), (100, 30)),
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

            events = pygame.event.get()
            for event in events:

                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    board.get_click(event.pos)
                    board.render(screen)
                    pygame.display.flip()

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
        self.left = left
        self.top = top
        self.cell_size = 16

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for y in range(0, self.height):
            for x in range(0, self.width):
                if self.board[y][x] == 0:
                    pygame.draw.rect(screen, pygame.Color(255, 255, 255), (
                        x * self.cell_size + self.left,
                        y * self.cell_size + self.top,
                        self.cell_size, self.cell_size), 1)
                else:
                    pygame.draw.rect(screen, pygame.Color(255, 255, 255), (
                        x * self.cell_size + self.left,
                        y * self.cell_size + self.top,
                        self.cell_size, self.cell_size))

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

    def on_click(self, cell_coords):
        if self.board[cell_coords[1]][cell_coords[0]] == 0:
            self.board[cell_coords[1]][cell_coords[0]] = 1
        else:
            self.board[cell_coords[1]][cell_coords[0]] = 0

    def get_click(self, mouse_pos):
        if self.left < mouse_pos[
            0] < self.left + self.width * self.cell_size and self.top < \
                mouse_pos[1] < self.top + self.height * self.cell_size:
            self.on_click(self.get_cell(mouse_pos))


MapCreator().run()
