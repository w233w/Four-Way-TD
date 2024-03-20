from const import *
import pygame
from typing import Type
from groups import *
from bullet import *


class BaseTower(pygame.sprite.Sprite):
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
        self.draging = False
        self.init_time = pygame.time.get_ticks()
        self.last_shot = self.init_time
        self.add(*group)

    @property
    def affordable(self) -> bool:
        return resource.gold >= self.sale_price

    def update(self, event_list: list[pygame.event.Event], cls: Type[Self]) -> None:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        if not self.placed and self.affordable:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hoving:
                    self.draging = True
                elif event.type == pygame.MOUSEBUTTONUP and self.hoving:
                    self.draging = False
                    for grid in grids.sprites():
                        if grid.rect.collidepoint(mouse_pos) and grid.available(self):
                            resource.gold -= self.sale_price
                            if cls == TestTower:
                                self.pos = grid.pos
                                self.rect.center = self.pos
                                self.placed = True
                                grid.tower = self
                                cls(self.init_pos, self.sale_price + 5, self.groups())
                            elif cls == TestTower2:
                                if grid.tower:
                                    grid.tower.level += 1
                                    self.pos = self.init_pos
                                    self.rect.center = self.pos
                                else:
                                    self.pos = grid.pos
                                    self.rect.center = self.pos
                                    self.placed = True
                                    grid.tower = self
                                    cls(
                                        self.init_pos,
                                        self.sale_price + 5,
                                        self.groups(),
                                    )
                            break
                    else:
                        self.pos = self.init_pos
                        self.rect.center = self.pos
        if self.draging:
            self.pos = mouse_pos
            self.rect.center = self.pos

    @property
    def hoving(self) -> bool:
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

    def update(self, event_list: list[pygame.event.Event]):
        super().update(event_list, self.__class__)
        if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
            if self.placed:
                player_bullets.add(TestBullet(self.pos, Direction.UP.to_vector(), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(0, 1), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(-1, 0), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(1, 0), 8))
            self.last_shot = pygame.time.get_ticks()


class TestTower2(BaseTower):
    tri = {1: [0], 2: [0, 2], 3: [-1, 0, 1], 4: [-1, 0, 1, 2]}

    def __init__(
        self, pos: pygame.Vector2, price: int, *group: pygame.sprite.Group
    ) -> None:
        super().__init__(pos, price, *group)
        self.side = Direction.UP
        self.level = 1
        self.shape_modifier = 0.8
        self.draw_triangle()
        self.shot_interval = 200

    def draw_triangle(self) -> None:
        self.image.fill(Black)
        self.triangles = TestTower2.tri[self.level]
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
        super().update(event_list, self.__class__)
        if self.placed:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hoving:
                    self.side += 1
            if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
                for triangle in self.triangles:
                    player_bullets.add(
                        TestBullet(self.pos, (self.side + triangle).to_vector(), 8)
                    )
                self.last_shot = pygame.time.get_ticks()
            self.draw_triangle()
