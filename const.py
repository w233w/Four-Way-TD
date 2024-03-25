import pygame
import random
from enum import Enum
from typing import Self
from dataclasses import dataclass, fields
from util import *

# 各类参数
# 窗口大小
WIN_SIZE = 600
V_SIZE = pygame.Vector2(WIN_SIZE)
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
HAVE_CORNER = False
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
Gray = 192, 192, 192


@dataclass
class Resource:
    gold: int = 200
    crystal: int = 0


def to_dict(res: Resource):
    return {field.name: getattr(res, field.name) for field in fields(res)}


RESOURCE = Resource()


class Direction(Enum):
    LEFT = -1
    UP = 0
    RIGHT = 1
    DOWN = 2

    def __add__(self, other: int) -> Self:
        return Direction((self.value + other + 1) % 4 - 1)

    def __sub__(self, other: int) -> Self:
        return Direction((self.value - other + 1) % 4 - 1)

    def to_vector(self) -> pygame.Vector2:
        if self == Direction.UP:
            return pygame.Vector2(0, -1)
        elif self == Direction.RIGHT:
            return pygame.Vector2(1, 0)
        elif self == Direction.DOWN:
            return pygame.Vector2(0, 1)
        elif self == Direction.LEFT:
            return pygame.Vector2(-1, 0)
        else:
            raise ValueError("Impossible direction")

    @classmethod
    def random(cls) -> Self:
        return Direction(random.randint(-1, 2))

    @classmethod
    def all(cls) -> list[Self]:
        return [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]


class FloatText(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: pygame.Vector2,
        font: pygame.font.Font,
        color: pygame.Color,
        text: str,
    ) -> None:
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.text = text
        text_size = font.size(text)
        self.image = pygame.Surface(text_size)
        self.image.set_colorkey(Black)
        text_surface = font.render(self.text, False, color, None)
        self.image.blit(text_surface, [0, 0])
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

    def update(self) -> None:
        if pygame.time.get_ticks() - self.init_time >= 700:
            self.kill()
        self.pos -= pygame.Vector2(0, 1)
        self.rect.center = self.pos
