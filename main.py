import pygame
import random
from enum import Enum
from dataclasses import dataclass
from typing import Self, ClassVar

from pygame.event import Event
from pygame.sprite import Group

# 三方向塔防，左上角是建造菜单，右上角游戏内信息，左下角塔信息，右下角游戏菜单。
# 塔该不该有方向还有待研究，地图四角要不要去除也有待研究（防止四角上的塔压力过大）。
# 下一步计划先把左下角塔数据做出来

from const import *


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

    def __add__(self, other: int):
        return Direction((self.value + other) % 4)

    def __sub__(self, other: int):
        return Direction((self.value - other) % 4)

    def to_vector(self):
        if self == Direction.UP:
            return pygame.Vector2(0, -1)
        elif self == Direction.RIGHT:
            return pygame.Vector2(1, 0)
        elif self == Direction.DOWN:
            return pygame.Vector2(0, 1)
        elif self == Direction.LEFT:
            return pygame.Vector2(-1, 0)
        else:
            raise ValueError(f"Unknown direction: {self}")

    @classmethod
    def random(cls) -> Self:
        return Direction(random.randint(0, 3))

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
    def __init__(self, font: pygame.font.Font) -> None:
        super().__init__()
        self.font = pygame.font.SysFont("timesnewroman", 16)
        self.size = (WIN_SIZE - GRIDS_SIZE) / 2, (WIN_SIZE - GRIDS_SIZE) / 2
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(0, WIN_SIZE - ROAD_LENGTH)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.image.fill([192, 192, 192])

    def update(self) -> None:
        self.image.fill([192, 192, 192])
        text = f"Gold: {resource.gold}"
        text_surface = self.font.render(text, True, AlmostBlack, None)
        self.image.blit(text_surface, [10, 10])
        text = f"Crystal: {resource.crystal}"
        text_surface = self.font.render(text, True, AlmostBlack, None)
        self.image.blit(text_surface, [10, 60])


class TestBullet(pygame.sprite.Sprite):
    def __init__(
        self, pos: pygame.Vector2, speed: pygame.Vector2, speed_modifier: float
    ) -> None:
        super().__init__()
        self.radius = 1.5
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(pos)
        self.speed = speed
        self.speed_modifier = speed_modifier
        self.shift = self.speed.rotate(90).normalize() * random.uniform(
            -2 * self.radius, 2 * self.radius
        )
        self.pos += self.shift
        self.rect = self.image.get_rect(center=self.pos)
        pygame.draw.circle(
            self.image, AlmostBlack, [self.radius, self.radius], self.radius
        )
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.pos += self.speed * self.speed_modifier
        self.rect.center = self.pos
        if (
            self.pos.x >= WIN_SIZE + self.radius
            or self.pos.x <= 0 - self.radius
            or self.pos.y >= WIN_SIZE + self.radius
            or self.pos.y <= 0 - self.radius
        ):
            self.kill()


class BaseTower(pygame.sprite.Sprite):
    def __init__(self, pos: pygame.Vector2, *group: pygame.sprite.Group) -> None:
        super().__init__()
        self.init_pos = pygame.Vector2(pos)
        self.pos = self.init_pos
        self.shape = pygame.Vector2(TOWER_GRID_SIZE)
        self.image = pygame.Surface(self.shape)
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.placed = False
        self.draging = False
        self.init_time = pygame.time.get_ticks()
        self.last_shot = self.init_time
        self.add(*group)

    def update(self, event_list: list[pygame.event.Event], cls) -> None:
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        if not self.placed and self.affordable:
            for event in event_list:
                if event.type == pygame.MOUSEBUTTONDOWN and self.hoving:
                    self.draging = True
                elif event.type == pygame.MOUSEBUTTONUP and self.hoving:
                    self.draging = False
                    for grid in grids.sprites():
                        if grid.rect.collidepoint(mouse_pos) and grid.available:
                            resource.gold -= TestTower.sale_price
                            TestTower.sale_price += 5
                            self.pos = grid.pos
                            self.rect.center = self.pos
                            self.placed = True
                            self.grid_pos = grid.cord
                            grid.tower = self
                            cls(self.init_pos, self.groups())
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
    sale_price: int = 10

    def __init__(self, pos: pygame.Vector2, *group: pygame.sprite.Group) -> None:
        super().__init__(pos, *group)
        pygame.draw.circle(
            self.image, Yellow, self.shape / 2, TOWER_GRID_SIZE * 0.8 // 2
        )
        self.shot_interval = 800  # ms

    @property
    def affordable(self) -> bool:
        return resource.gold >= TestTower.sale_price

    def update(self, event_list: list[pygame.event.Event]):
        super().update(event_list)
        if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
            if self.placed:
                player_bullets.add(TestBullet(self.pos, Direction.UP.to_vector(), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(0, 1), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(-1, 0), 8))
                player_bullets.add(TestBullet(self.pos, pygame.Vector2(1, 0), 8))
            self.last_shot = pygame.time.get_ticks()


class TestTower2(BaseTower):
    tri = {1: [0], 2: [0, 2], 3: [-1, 0, 1], 4: [-1, 0, 1, 2]}
    sale_price = 5

    def __init__(self, pos: pygame.Vector2, *group: Group) -> None:
        super().__init__(pos, *group)
        self.side = Direction.UP
        self.sides = 1
        self.shape_modifier = 0.8
        self.triangles = TestTower2.tri[self.sides]
        self.center = pygame.Vector2(self.rect.center)
        self.radius = TOWER_GRID_SIZE // 2
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
        self.shot_interval = 200

    @property
    def affordable(self) -> bool:
        return resource.gold >= TestTower2.sale_price

    def update(self, event_list: list[Event]) -> None:
        super().update(event_list, self.__class__)
        if pygame.time.get_ticks() - self.last_shot > self.shot_interval:
            if self.placed:
                for triangle in self.triangles:
                    player_bullets.add(
                        TestBullet(self.pos, (self.side + triangle).to_vector(), 8)
                    )
            self.last_shot = pygame.time.get_ticks()


class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, road: int, side: Direction) -> None:
        super().__init__()
        if road not in range(EDGES):
            raise ValueError()
        self.road = road
        self.side = side
        x, y = 0, 0
        self.x_limit, self.y_limit = 0, 0
        match self.side:
            case Direction.UP:
                x = ROAD_LENGTH + ENEMY_SIZE // 2 + self.road * GRIDS_INTERVAL
                y = 0 - ENEMY_SIZE // 2
                self.y_limit = ROAD_LENGTH - ENEMY_SIZE // 2
                self.base_speed = Direction.DOWN.to_vector()
            case Direction.DOWN:
                x = ROAD_LENGTH + ENEMY_SIZE // 2 + self.road * GRIDS_INTERVAL
                y = WIN_SIZE + ENEMY_SIZE // 2
                self.y_limit = WIN_SIZE - ROAD_LENGTH + ENEMY_SIZE // 2
                self.base_speed = Direction.UP.to_vector()
            case Direction.LEFT:
                x = 0 - ENEMY_SIZE // 2
                y = ROAD_LENGTH + ENEMY_SIZE // 2 + self.road * GRIDS_INTERVAL
                self.x_limit = ROAD_LENGTH - ENEMY_SIZE // 2
                self.base_speed = Direction.RIGHT.to_vector()
            case Direction.RIGHT:
                x = WIN_SIZE + ENEMY_SIZE // 2
                y = ROAD_LENGTH + ENEMY_SIZE // 2 + self.road * GRIDS_INTERVAL
                self.x_limit = WIN_SIZE - ROAD_LENGTH + ENEMY_SIZE // 2
                self.base_speed = Direction.LEFT.to_vector()

        self.pos = pygame.Vector2(x, y)
        self.speed_modifier = 1
        self.image = pygame.Surface([ENEMY_SIZE, ENEMY_SIZE])
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

    def update(self) -> None:
        match self.side:
            case Direction.UP:
                if self.pos.y > self.y_limit:
                    return
            case Direction.DOWN:
                if self.pos.y < self.y_limit:
                    return
            case Direction.LEFT:
                if self.pos.x > self.x_limit:
                    return
            case Direction.RIGHT:
                if self.pos.x < self.x_limit:
                    return
        self.pos += self.base_speed * self.speed_modifier
        self.rect.center = self.pos


class TestEnemy(BaseEnemy):
    def __init__(self, road: int, side: Direction) -> None:
        super().__init__(road, side)
        pygame.draw.circle(
            self.image, Red, (ENEMY_SIZE // 2, ENEMY_SIZE // 2), ENEMY_SIZE * 0.8 // 2
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_modifier = 0.2
        self.hp = 10

    def update(self) -> None:
        super().update()
        hitted = pygame.sprite.spritecollide(
            self, player_bullets, True, pygame.sprite.collide_mask
        )
        if len(hitted) >= 1:
            self.hp -= 1
        if self.hp <= 0:
            texts.add(FloatText(self.pos, Font, Golden, "+10 gold"))
            resource.gold += 10
            self.kill()


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
        self.available = True
        self.tower: BaseTower = None

    def update(self) -> None:
        if self.tower:
            self.available = False


@dataclass
class Resource:
    gold: int = 20
    crystal: int = 0


resource = Resource()


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(VSIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()
# 状态栏
# setting the pygame font style(1st parameter)
# and size of font(2nd parameter)
Font = pygame.font.SysFont("timesnewroman", 12)

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

grids = pygame.sprite.Group()
grid = pygame.sprite.GroupSingle(Grids(GRIDS_SIZE, EDGES))
texts = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
info_bar = pygame.sprite.GroupSingle(Info(Font))

tower_test = pygame.sprite.Group()
tower_test.add(TestTower2(pygame.Vector2(20, 20)))
enemy_test = pygame.sprite.Group()

last_enemy = 3000
interval = 1000

# 主体
while running := True:
    # 决定游戏刷新率
    clock.tick(FPS)
    # 点×时退出。。
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    # 生成敌人
    if pygame.time.get_ticks() - last_enemy >= interval:
        enemy_test.add(
            TestEnemy(
                random.randint(0, EDGES - 1),
                Direction.random(),
            )
        )
        last_enemy = pygame.time.get_ticks()
    # 先铺背景再画sprites
    screen.fill(pygame.Color(BackgroundColor))
    # 更新sprites
    # 永远先更新玩家
    grids.update()
    info_bar.update()
    grid.update()
    tower_test.update(event_list)
    texts.update()
    player_bullets.update()
    enemy_test.update()
    # 不会有重叠，所以画不分先后
    grids.draw(screen)
    info_bar.draw(screen)
    grid.draw(screen)
    tower_test.draw(screen)
    texts.draw(screen)
    player_bullets.draw(screen)
    enemy_test.draw(screen)
    # 更新画布
    pygame.display.flip()
