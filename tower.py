from typing import Type

from pygame import Vector2
from pygame.event import Event
from pygame.sprite import Group
from groups import *
from bullet import *

from abc import abstractmethod
import math


class BaseTower(pygame.sprite.Sprite):
    """
    塔的基类
    pos: 初始位置
    price: 初始售价
    """

    def __init__(
        self, pos: pygame.Vector2, price: int, *group: pygame.sprite.Group
    ) -> None:
        super().__init__()
        self.init_pos = pygame.Vector2(pos)
        self.pos = self.init_pos
        self.sale_price = price
        self.shape = pygame.Vector2(TOWER_GRID_SIZE)
        self.image = pygame.Surface(self.shape)
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.placed = False
        self.dragging = False
        self.tier = 1
        self.init_time = pygame.time.get_ticks()
        self.last_shot = self.init_time
        self.add(*group)

    @property
    def affordable(self) -> bool:
        return RESOURCE.gold >= self.sale_price

    @abstractmethod
    def can_merge(self, tower: Self) -> bool: ...

    @abstractmethod
    def merge(self, tower: Self) -> None: ...

    def update(self, event_list: list[pygame.event.Event]) -> None:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        if not self.placed and self.affordable:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hovering:
                    self.dragging = True
                elif event.type == pygame.MOUSEBUTTONUP and self.hovering:
                    self.dragging = False
                    for g in grids.sprites():
                        if g.rect.collidepoint(mouse_pos) and g.available(self):
                            self.__class__(
                                self.init_pos, self.sale_price + 5, self.groups()
                            )
                            RESOURCE.gold -= self.sale_price
                            g.place(self)
                            break
                    else:
                        self.pos = self.init_pos
                        self.rect.center = self.pos
        if self.dragging:
            self.pos = mouse_pos
            self.rect.center = self.pos

    @property
    def hovering(self) -> bool:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        return self.rect.collidepoint(mouse_pos)


class TestTower(BaseTower):
    def __init__(
        self, pos: pygame.Vector2, price: int, *group: pygame.sprite.Group
    ) -> None:
        super().__init__(pos, price, *group)
        pygame.draw.circle(
            self.image, Yellow, self.shape / 2, TOWER_GRID_SIZE * 0.8 // 2
        )
        self.shot_interval = 800  # ms

    def can_merge(self, tower: BaseTower) -> bool:
        return False

    def merge(self, tower: BaseTower) -> None:
        raise RuntimeError("Can't be called here")

    def update(self, event_list: list[pygame.event.Event]):
        super().update(event_list)
        if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
            if self.placed:
                player_bullets.add(TestBullet(self.pos, Direction.UP, 8))
                player_bullets.add(TestBullet(self.pos, Direction.DOWN, 8))
                player_bullets.add(TestBullet(self.pos, Direction.LEFT, 8))
                player_bullets.add(TestBullet(self.pos, Direction.RIGHT, 8))
            self.last_shot = pygame.time.get_ticks()


class TestTower2(BaseTower):
    tri = {1: [0], 2: [0, 2], 3: [-1, 0, 1], 4: [-1, 0, 1, 2]}

    def __init__(
        self, pos: pygame.Vector2, price: int, *group: pygame.sprite.Group
    ) -> None:
        super().__init__(pos, price, *group)
        self.side = Direction.UP
        self.shape_modifier = 0.8
        self.draw_triangle()
        self.shot_interval = 1500

    def can_merge(self, tower: BaseTower) -> bool:
        return self.__class__ == tower.__class__ and self.tier < 4

    def merge(self, tower: BaseTower) -> None:
        self.tier += 1
        self.draw_triangle()
        tower.kill()

    def draw_triangle(self) -> None:
        self.image.fill(Black)
        self.triangles = TestTower2.tri[self.tier]
        self.radius = TOWER_GRID_SIZE // 2
        self.center = pygame.Vector2(self.radius)
        for triangle in self.triangles:
            top = (
                self.center
                + (self.side + triangle).to_vector() * self.radius * self.shape_modifier
            )
            left_down = (
                self.center
                + (self.side + triangle - 1).to_vector()
                * self.radius
                * self.shape_modifier
                / 2
            )
            right_down = (
                self.center
                + (self.side + triangle + 1).to_vector()
                * self.radius
                * self.shape_modifier
                / 2
            )
            pygame.draw.polygon(
                self.image,
                Golden,
                [top, left_down, right_down],
            )

    def update(self, event_list: list[pygame.event.Event]) -> None:
        super().update(event_list)
        if self.placed:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hovering:
                    self.side += 1
                    self.draw_triangle()
            if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
                for triangle in self.triangles:
                    player_bullets.add(TestBullet2(self.pos, self.side + triangle))
                self.last_shot = pygame.time.get_ticks()


class TestTower3(BaseTower):
    def __init__(self, pos: Vector2, price: int, *group: Group) -> None:
        super().__init__(pos, price, *group)
        r = 0.8 * TOWER_GRID_SIZE // 2
        center = self.shape // 2
        points = []
        for i in range(6):
            point = center + pygame.Vector2(
                r * math.sin(i * math.pi / 3), r * math.cos(i * math.pi / 3)
            )
            points.append(point)
        pygame.draw.polygon(self.image, Blue, points)
        self.shot_interval = 1900

    def update(self, event_list: list[Event]) -> None:
        super().update(event_list)
        if self.placed:
            if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
                player_bullets.add(TestBullet3(self.pos, self.shape[0] * 4))
                self.last_shot = pygame.time.get_ticks()
