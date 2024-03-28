import pygame
import random
from enum import Enum
from typing import Self
from dataclasses import dataclass, fields


def is_integer_value(var):
    if isinstance(var, (int, float)):
        if isinstance(var, float):
            return var.is_integer()
        else:
            return True
    else:
        raise ValueError("Input must be of type int or float.")


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
HAVE_CORNER = True
TOWER_GRID_SIZE = GRIDS_INTERVAL
ENEMY_SIZE = GRIDS_INTERVAL


# 刷新率
FPS = 60

# 颜色
BackgroundColor = 222, 222, 222
BaseColor = 173, 213, 162
Black = 0, 0, 0
Line = 20, 35, 52
AlmostBlack = 1, 1, 1
White = 255, 255, 255
Red = 255, 0, 0
Blue = 0, 0, 255
Lightblue = 135, 206, 235
Lightcyan = 204, 255, 255
Green = 0, 255, 0
Yellow = 255, 255, 0
Golden = 255, 215, 0
Gray = 192, 192, 192


@dataclass
class Resource:
    hp: int = 1000
    gold: int = 20
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


class Info(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.font = pygame.font.SysFont("timesnewroman", 16)
        _, self.text_height = self.font.size("test")
        self.size = (WIN_SIZE - GRIDS_SIZE) / 2, (WIN_SIZE - GRIDS_SIZE) / 2
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(0, WIN_SIZE - ROAD_LENGTH)
        self.rect = self.image.get_rect(topleft=self.pos)

    def update(self) -> None:
        self.image.fill(Gray)
        for i, (key, val) in enumerate(to_dict(RESOURCE).items()):
            text = f"{key.capitalize()}: {val}"
            text_surface = self.font.render(text, True, AlmostBlack, None)
            self.image.blit(text_surface, [10, 10 + i * (10 + self.text_height)])
