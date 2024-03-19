import pygame
from util import *

# 各类参数
# 窗口大小
WIN_SIZE = 600
VSIZE = pygame.Vector2(WIN_SIZE)
GRIDS_SIZE = 200
EDGES = 5
if GRIDS_SIZE % EDGES != 0:
    raise ValueError()
GRIDS_INTERVAL = GRIDS_SIZE / EDGES
if not is_integer_value(GRIDS_INTERVAL):
    raise ValueError()
ROAD_LENGTH = (WIN_SIZE - GRIDS_SIZE) / 2
if not is_integer_value(ROAD_LENGTH):
    raise ValueError()
HAVE_CORNOR = False
TOWER_GRID_SIZE = GRIDS_INTERVAL
ENEMY_SIZE = GRIDS_INTERVAL

# 刷新率
FPS = 60

# 颜色
BackgroundColor = 248, 248, 255
BaseColor = 173, 213, 162
Black = 0, 0, 0
Line = 20, 35, 52
AlmostBlack = 1, 1, 1
White = 255, 255, 255
Red = 255, 0, 0
Blue = 0, 0, 255
Green = 0, 255, 0
Yellow = 255, 255, 0
Golden = 255, 215, 0
