import pygame
import random
import math

pygame.init()

# =========================
# 基本设置
# =========================
WIDTH = 1000
HEIGHT = 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Trace Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

BG = (245, 245, 245)
WALL_COLOR = (30, 30, 30)
GREEN = (40, 200, 80)
RED = (220, 60, 60)
PATH_COLOR = (50, 120, 230)
FAIL_COLOR = (220, 50, 50)

# =========================
# 迷宫设置
# =========================
CELL_SIZE = 60
COLS = 14
ROWS = 9

MAZE_WIDTH = COLS * CELL_SIZE
MAZE_HEIGHT = ROWS * CELL_SIZE

OFFSET_X = (WIDTH - MAZE_WIDTH) // 2
OFFSET_Y = 100

WALL_THICKNESS = 8

START_RADIUS = 18
END_RADIUS = 18


# =========================
# Maze Cell
# =========================
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        # 上 右 下 左
        self.walls = [True, True, True, True]

        self.visited = False


cells = []


def index(x, y):
    if x < 0 or y < 0 or x >= COLS or y >= ROWS:
        return None

    return y * COLS + x


# =========================
# 生成迷宫
# Randomized DFS
# =========================
def generate_maze():
    global cells

    cells = []

    for y in range(ROWS):
        for x in range(COLS):
            cells.append(Cell(x, y))

    current = cells[0]
    current.visited = True

    stack = []

    while True:

        x = current.x
        y = current.y

        neighbors = []

        directions = [
            (0, -1, 0),  # up
            (1, 0, 1),   # right
            (0, 1, 2),   # down
            (-1, 0, 3)   # left
        ]

        for dx, dy, direction in directions:

            i = index(x + dx, y + dy)

            if i is not None:
                neighbor = cells[i]

                if not neighbor.visited:
                    neighbors.append((neighbor, direction))

        if neighbors:

            next_cell, direction = random.choice(neighbors)

            # 删除两个 cell 中间的墙
            if direction == 0:
                current.walls[0] = False
                next_cell.walls[2] = False

            elif direction == 1:
                current.walls[1] = False
                next_cell.walls[3] = False

            elif direction == 2:
                current.walls[2] = False
                next_cell.walls[0] = False

            elif direction == 3:
                current.walls[3] = False
                next_cell.walls[1] = False

            stack.append(current)

            current = next_cell
            current.visited = True

        elif stack:
            current = stack.pop()

        else:
            break


# =========================
# 把墙变成 Rect
# 方便进行碰撞检测
# =========================
def create_wall_rects():

    walls = []

    for cell in cells:

        x = OFFSET_X + cell.x * CELL_SIZE
        y = OFFSET_Y + cell.y * CELL_SIZE

        # 上墙
        if cell.walls[0]:
            walls.append(
                pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    WALL_THICKNESS
                )
            )

        # 右墙
        if cell.walls[1]:
            walls.append(
                pygame.Rect(
                    x + CELL_SIZE - WALL_THICKNESS,
                    y,
                    WALL_THICKNESS,
                    CELL_SIZE
                )
            )

        # 下墙
        if cell.walls[2]:
            walls.append(
                pygame.Rect(
                    x,
                    y + CELL_SIZE - WALL_THICKNESS,
                    CELL_SIZE,
                    WALL_THICKNESS
                )
            )

        # 左墙
        if cell.walls[3]:
            walls.append(
                pygame.Rect(
                    x,
                    y,
                    WALL_THICKNESS,
                    CELL_SIZE
                )
            )

    return walls


# =========================
# 起点 / 终点
# =========================
def cell_center(col, row):

    x = (
        OFFSET_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
    )

    y = (
        OFFSET_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
    )

    return x, y


start_pos = cell_center(0, 0)
end_pos = cell_center(COLS - 1, ROWS - 1)


# =========================
# 是否点击圆
# =========================
def inside_circle(pos, center, radius):

    dx = pos[0] - center[0]
    dy = pos[1] - center[1]

    return dx * dx + dy * dy <= radius * radius


# =========================
# 重置游戏
# =========================
def reset_game():

    global wall_rects
    global points
    global state
    global last_record_time

    generate_maze()

    wall_rects = create_wall_rects()

    points = []

    state = "waiting"

    last_record_time = 0


# =========================
# 初始游戏
# =========================
generate_maze()

wall_rects = create_wall_rects()

points = []

# waiting
# playing
# failed
# won
state = "waiting"

last_record_time = 0

# 鼠标轨迹记录间隔
# 20 毫秒 ≈ 每秒记录 50 个点
RECORD_INTERVAL = 20


# =========================
# 主循环
# =========================
running = True

while running:

    dt = clock.tick(120)

    # -------------------------
    # Events
    # -------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            # R 生成新迷宫
            if event.key == pygame.K_r:
                reset_game()

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                mouse_pos = pygame.mouse.get_pos()

                # waiting / failed / won 状态
                # 点击绿点重新开始
                if state != "playing":

                    if inside_circle(
                        mouse_pos,
                        start_pos,
                        START_RADIUS + 10
                    ):

                        points = [start_pos]

                        state = "playing"

                        last_record_time = pygame.time.get_ticks()

                        # 把鼠标移动到绿点
                        pygame.mouse.set_pos(start_pos)

    # =========================
    # Playing
    # =========================
    if state == "playing":

        mouse_pos = pygame.mouse.get_pos()

        # -------------------------
        # 碰墙检测
        # -------------------------
        for wall in wall_rects:

            if wall.collidepoint(mouse_pos):

                state = "failed"

                break

        # -------------------------
        # 到达终点检测
        # -------------------------
        if state == "playing":

            if inside_circle(
                mouse_pos,
                end_pos,
                END_RADIUS
            ):

                points.append(mouse_pos)

                state = "won"

        # -------------------------
        # 记录轨迹
        # -------------------------
        current_time = pygame.time.get_ticks()

        if (
            state == "playing"
            and current_time - last_record_time
            >= RECORD_INTERVAL
        ):

            points.append(mouse_pos)

            last_record_time = current_time

    # =========================
    # DRAW
    # =========================
    screen.fill(BG)

    # -------------------------
    # 画墙
    # -------------------------
    for wall in wall_rects:
        pygame.draw.rect(
            screen,
            WALL_COLOR,
            wall
        )

    # -------------------------
    # 画轨迹
    # -------------------------
    if len(points) >= 2:

        if state == "failed":
            color = FAIL_COLOR
        else:
            color = PATH_COLOR

        pygame.draw.lines(
            screen,
            color,
            False,
            points,
            4
        )

    # -------------------------
    # 起点
    # -------------------------
    pygame.draw.circle(
        screen,
        GREEN,
        start_pos,
        START_RADIUS
    )

    # -------------------------
    # 终点
    # -------------------------
    pygame.draw.circle(
        screen,
        RED,
        end_pos,
        END_RADIUS
    )

    # =========================
    # 提示文字
    # =========================
    if state == "waiting":

        text = font.render(
            "Click the GREEN circle to start",
            True,
            (30, 30, 30)
        )

    elif state == "playing":

        text = font.render(
            "Reach the RED circle - don't touch the walls!",
            True,
            (30, 30, 30)
        )

    elif state == "failed":

        text = font.render(
            "You hit a wall! Click GREEN to try again",
            True,
            RED
        )

    else:

        text = font.render(
            "YOU WIN! Click GREEN to play again",
            True,
            GREEN
        )

    screen.blit(
        text,
        (
            WIDTH // 2 - text.get_width() // 2,
            35
        )
    )

    # R 提示
    small_font = pygame.font.SysFont(None, 24)

    info = small_font.render(
        "R = generate a new maze     ESC = quit",
        True,
        (80, 80, 80)
    )

    screen.blit(
        info,
        (
            WIDTH // 2 - info.get_width() // 2,
            HEIGHT - 35
        )
    )

    pygame.display.flip()


pygame.quit()