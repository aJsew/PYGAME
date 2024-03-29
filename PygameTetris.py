import pygame
import pygame_menu
import random
from time import sleep
from pygame_menu import themes
import sqlite3

conn = sqlite3.connect('leaderboard.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS players(
   username TEXT PRIMARY KEY,
   points INT);
""")
conn.commit()
pygame.init()


surface = pygame.display.set_mode((800, 700))
surface.fill((255, 255, 255))


def set_difficulty(value):
    for i in range(value):
        print(value(0), "-", value(-1))


def start_the_game():
    user = username.get_value()
    print(user)
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            main(user)
    pygame.quit()


def level_menu():
    mainmenu._open(level)


mainmenu = pygame_menu.Menu('Главное меню', 800, 700, theme=themes.THEME_SOLARIZED)

#Размеры поля и блоков
s_width = 800
s_height = 700
play_width = 300
play_height = 600
block_size = 30


top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

# формы блоков

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]


# индексы от 0 до 6 обозначают форму


class Blocks(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # от 0 до 3


def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions


def valid_space(shape, grid): #Свободные клетки на поле
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(shape)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True


def check_lost(positions): #проверка на поражение
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape(shapes, shape_colors):
    shapes, shape_colors = shapes, shape_colors
    return Blocks(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (
    top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - label.get_height() / 2))


def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * 30),
                         (sx + play_width, sy + i * 30))  # горизонтальные линии
        for j in range(col):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * 30, sy),
                             (sx + j * 30, sy + play_height))  # вертикальные линии


def clear_rows(grid, locked):
#очистка линии в случае заполнения блоками
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)


def draw_next_shape(shape, surface):
    #Вывод изображения следующей фигурки
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Следующий:', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * 30, sy + i * 30, 30, 30), 0)

    surface.blit(label, (sx + 10, sy - 30))


def main(user):

    def create_grid(locked_positions={}):  # Создание сетки поля
        grid = [[(0, 0, 0) for x in range(10)] for x in range(20)]

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if (j, i) in locked_positions:
                    c = locked_positions[(j, i)]
                    grid[i][j] = c
        return grid

    def draw_window(surface):
        surface.fill((255, 200, 200))
        # Вывод названия игры
        font = pygame.font.SysFont('comicsans', 60)
        label = font.render('ТЕТРИС', 1, (255, 255, 255))

        surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

        for i in range(len(grid)):
            for j in range(len(grid[i])):
                pygame.draw.rect(surface, grid[i][j], (top_left_x + j * 30, top_left_y + i * 30, 30, 30), 0)

        draw_grid(surface, 20, 10)
        pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)
    user = user

    points = 0

    locked_positions = {}  # (x,y):(255,0,0)
    grid = create_grid(locked_positions)

    change_Blocks = False
    run = True
    current_Blocks = get_shape(shapes, shape_colors)
    next_Blocks = get_shape(shapes, shape_colors)
    clock = pygame.time.Clock()
    fall_time = 0

    while run:
        fall_speed = 0.27

        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Как падают блоки
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_Blocks.y += 1
            if not (valid_space(current_Blocks, grid)) and current_Blocks.y > 0:
                current_Blocks.y -= 1
                change_Blocks = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_Blocks.x -= 1
                    if not valid_space(current_Blocks, grid):
                        current_Blocks.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_Blocks.x += 1
                    if not valid_space(current_Blocks, grid):
                        current_Blocks.x -= 1
                elif event.key == pygame.K_UP:
                    # вращение
                    current_Blocks.rotation = current_Blocks.rotation + 1 % len(current_Blocks.shape)
                    if not valid_space(current_Blocks, grid):
                        current_Blocks.rotation = current_Blocks.rotation - 1 % len(current_Blocks.shape)

                if event.key == pygame.K_DOWN:
                    # ускорить падение
                    current_Blocks.y += 1
                    if not valid_space(current_Blocks, grid):
                        current_Blocks.y -= 1

                '''if event.key == pygame.K_SPACE:
                    while valid_space(current_Blocks, grid):
                        current_Blocks.y += 1
                    current_Blocks.y -= 1
                    print(convert_shape_format(current_Blocks))'''

        shape_pos = convert_shape_format(current_Blocks)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_Blocks.color

        # когда блоки касаются земли
        if change_Blocks:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_Blocks.color
            current_Blocks = next_Blocks
            next_Blocks = get_shape(shapes, shape_colors)
            change_Blocks = False

            clear_rows(grid, locked_positions)

        draw_window(win)
        draw_next_shape(next_Blocks, win)
        pygame.display.update()

        # проверка на проигрыш
        if check_lost(locked_positions):
            print(points)
            run = False
        else:
            points += 1
    surface.fill((0, 0, 0))
    draw_text_middle(f"Вы проиграли, Ваш счёт: {points}", 40, (255, 0, 0), win)
    player = (user, points)
    cur.execute("INSERT INTO players VALUES(?, ?);", player)
    conn.commit()
    pygame.display.update()
    pygame.time.delay(1000)
    mainmenu.mainloop(surface)


win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')
username = mainmenu.add.text_input('Никнейм: ', default='Player', maxchar=20)
mainmenu.add.button('Играть', start_the_game)
mainmenu.add.button('Таблица лидеров', level_menu)
mainmenu.add.button('Выйти', pygame_menu.events.EXIT)
level = pygame_menu.Menu('Таблица лидеров', 600, 400, theme=themes.THEME_BLUE)
cur.execute("SELECT * FROM players ORDER BY points DESC;")
all_results = cur.fetchall()
all_results = ''.join([str((i[0]) + " - " + str(i[1]) + '\n') for i in all_results])
level.add.label(all_results)
mainmenu.mainloop(surface)


