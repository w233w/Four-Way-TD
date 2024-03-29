from const import *
from const import Direction
from groups import *


class BaseEnemy(pygame.sprite.Sprite):
    """
    敌人基类
    road: 出现在第几路
    side: 出现在哪一侧
    """

    def __init__(
        self,
        road: int,
        side: Direction,
        speed_factor: float = 1,
        power_factor: float = 1,
    ) -> None:
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
        self.speed_modifier = speed_factor
        self.power_factor = power_factor
        self.image = pygame.Surface([ENEMY_SIZE, ENEMY_SIZE])
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()

        self.buff = {}

    def blink(
        self, *, x: float = 0, y: float = 0, by_x: bool = False, by_y: bool = False
    ):
        if by_x:
            self.pos.x = x
        if by_y:
            self.pos.y = y
        self.rect.center = self.pos

    def on_death(self, worth):
        texts.add(
            FloatText(
                self.pos,
                pygame.font.SysFont("timesnewroman", 12),
                Golden,
                f"+{worth} gold",
            )
        )
        RESOURCE.gold += worth

    def update(self) -> None:
        match self.side:
            case Direction.UP:
                if self.pos.y > self.y_limit:
                    RESOURCE.hp -= 1
                    return
            case Direction.DOWN:
                if self.pos.y < self.y_limit:
                    RESOURCE.hp -= 1
                    return
            case Direction.LEFT:
                if self.pos.x > self.x_limit:
                    RESOURCE.hp -= 1
                    return
            case Direction.RIGHT:
                if self.pos.x < self.x_limit:
                    RESOURCE.hp -= 1
                    return
        if "cold" in self.buff:
            if pygame.time.get_ticks() - self.buff["cold"] < 500:
                cold_modifier = 0.5
            else:
                self.buff.pop("cold", 1)
                cold_modifier = 1
        else:
            cold_modifier = 1
        self.pos += self.base_speed * self.speed_modifier * cold_modifier
        self.rect.center = self.pos


class TestEnemy1(BaseEnemy):
    """基础敌人，无特殊能力"""

    def __init__(
        self,
        road: int,
        side: Direction,
        speed_factor: float = 1,
        power_factor: float = 1,
    ) -> None:
        super().__init__(road, side, speed_factor, power_factor)
        pygame.draw.circle(
            self.image, Red, (ENEMY_SIZE // 2, ENEMY_SIZE // 2), ENEMY_SIZE * 0.8 // 2
        )
        pygame.draw.circle(
            self.image,
            AlmostBlack,
            (ENEMY_SIZE // 2, ENEMY_SIZE // 2),
            ENEMY_SIZE * 0.8 // 2,
            1,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10 * self.power_factor
        self.worth = 10

    def update(self) -> None:
        super().update()
        if self.hp <= 0:
            super().on_death(self.worth)
            self.kill()


class TestEnemy2(BaseEnemy):
    """分裂型敌人，死后在附近两路生成1/4血的不可分裂的自身"""

    def __init__(
        self,
        road: int,
        side: Direction,
        speed_factor: float = 1,
        power_factor: float = 1,
        /,
        major: bool = True,
    ) -> None:
        super().__init__(road, side, speed_factor, power_factor)
        self.is_major = major
        shape_factor = 0.4 + major * 0.4
        pygame.draw.circle(
            self.image,
            Cyan,
            (ENEMY_SIZE // 2, ENEMY_SIZE // 2),
            ENEMY_SIZE * shape_factor // 2,
        )
        pygame.draw.circle(
            self.image,
            AlmostBlack,
            (ENEMY_SIZE // 2, ENEMY_SIZE // 2),
            ENEMY_SIZE * shape_factor // 2,
            1,
        )
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10 * self.power_factor * (1 if major else 0.25)
        self.worth = 10 if major else 3

    def update(self) -> None:
        super().update()
        if self.hp <= 0:
            super().on_death(self.worth)
            if self.is_major:
                left, right = self.road + 1, self.road - 1
                for road in [left, right]:
                    if road in range(EDGES):
                        splits = self.__class__(
                            road,
                            self.side,
                            self.speed_modifier,
                            self.power_factor,
                            major=False,
                        )
                        if self.side in [Direction.UP, Direction.DOWN]:
                            splits.blink(by_y=True, y=self.pos.y)
                        else:
                            splits.blink(by_x=True, x=self.pos.x)
                        enemy_test.add(splits)
            self.kill()
