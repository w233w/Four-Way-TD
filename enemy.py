from const import *
from groups import *


class BaseEnemy(pygame.sprite.Sprite):
    """
    敌人基类
    road: 出现在第几路
    side: 出现在哪一侧
    """

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
        if self.hp <= 0:
            texts.add(
                FloatText(
                    self.pos,
                    pygame.font.SysFont("timesnewroman", 12),
                    Golden,
                    "+10 gold",
                )
            )
            RESOURCE.gold += 10
            self.kill()
