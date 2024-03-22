import pygame

from const import *
from groups import grids
from tower import *


class Grids(pygame.sprite.Sprite):
    def __init__(self, size: int, edges: int) -> None:
        super().__init__()
        self.image = pygame.Surface(VSIZE)
        self.image.set_colorkey(Black)
        self.size = pygame.Vector2(size)
        self.interval = pygame.Vector2(GRIDS_INTERVAL)
        self.top_left_pos = (VSIZE - pygame.Vector2(size)) / 2
        self.rect = self.image.get_rect(center=pygame.Vector2(VSIZE) / 2)
        for e in range(0, edges + 1):
            pygame.draw.line(
                self.image,
                Line,
                pygame.Vector2(0, self.top_left_pos.y + e * self.interval.y),
                pygame.Vector2(WIN_SIZE, self.top_left_pos.y + e * self.interval.y),
                1,
            )
            pygame.draw.line(
                self.image,
                Line,
                pygame.Vector2(self.top_left_pos.x + e * self.interval.x, 0),
                pygame.Vector2(self.top_left_pos.x + e * self.interval.x, WIN_SIZE),
                1,
            )
        for i in range(edges**2):
            x, y = i // edges, i % edges
            if not HAVE_CORNOR:
                if (x, y) in [
                    (0, 0),
                    (0, edges - 1),
                    (edges - 1, 0),
                    (edges - 1, edges - 1),
                ]:
                    continue
            coordinate = (x, y)
            pos = self.top_left_pos + pygame.Vector2(
                GRIDS_INTERVAL * (0.5 + y), GRIDS_INTERVAL * (0.5 + x)
            )
            grids.add(Grid(pos=pos, coordinate=coordinate))


class Grid(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, coordinate: tuple) -> None:
        super().__init__()
        self.image = pygame.Surface([GRIDS_INTERVAL, GRIDS_INTERVAL])
        self.image.set_colorkey(Black)
        self.image.fill(BaseColor)
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.cord = coordinate
        self.tower: BaseTower = None

    def available(self, tower: BaseTower):
        if self.tower:
            return self.tower.mergeable(tower)
        else:
            return True

    def place(self, tower: BaseTower):
        if self.tower:
            self.tower.tier += 1
            tower.kill()
        else:
            self.tower = tower
            tower.pos = self.pos
            tower.rect.center = self.pos
            tower.placed = True
