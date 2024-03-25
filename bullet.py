from const import *
from scipy.stats import norm


class TestBullet(pygame.sprite.Sprite):
    """
    测试子弹-minigun子弹
    pos: 初始位置
    speed: 初始速度元向量
    speed: 实际速度倍率
    """

    def __init__(
        self, pos: pygame.Vector2, direction: Direction, speed_modifier: float
    ) -> None:
        super().__init__()
        self.radius = 1.5
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.image.set_colorkey(Black)
        self.pos = pygame.Vector2(pos)
        self.speed = direction.to_vector()
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


class TestBullet2(pygame.sprite.Sprite):
    """
    测试子弹2-激光
    """

    def __init__(self, pos: pygame.Vector2, direction: Direction) -> None:
        super().__init__()
        self.pos = pos
        self.direction = direction
        if self.direction in [Direction.UP, Direction.DOWN]:
            self.width = TOWER_GRID_SIZE
            self.height = WIN_SIZE
        elif self.direction in [Direction.LEFT, Direction.RIGHT]:
            self.width = WIN_SIZE
            self.height = TOWER_GRID_SIZE
        else:
            raise ValueError()
        self.size = [self.width, self.height]
        self.image = pygame.Surface(self.size)
        self.image.set_colorkey(Black)
        if self.direction == Direction.UP:
            self.rect = self.image.get_rect(
                topleft=self.pos + pygame.Vector2(-self.width // 2, -self.height)
            )
        elif self.direction == Direction.DOWN:
            self.rect = self.image.get_rect(
                topleft=self.pos + pygame.Vector2(-self.width // 2, 0)
            )
        elif self.direction == Direction.RIGHT:
            self.rect = self.image.get_rect(
                topleft=self.pos + pygame.Vector2(0, -self.height // 2)
            )
        elif self.direction == Direction.LEFT:
            self.rect = self.image.get_rect(
                topleft=self.pos + pygame.Vector2(-self.width, -self.height // 2)
            )
        else:
            raise ValueError()
        self.mask = pygame.mask.Mask(self.size)
        self.laser_lasting = 1200

        self.init_time = pygame.time.get_ticks()
        self.dpf = 2 / FPS

    def update(self) -> None:
        self.image.fill(Black)
        current = pygame.time.get_ticks() - self.init_time
        x = current % self.laser_lasting / (self.laser_lasting // 10) - 5
        y = norm.pdf(x, 0, 1)
        size_delta = 1.5 * y
        if self.direction in [Direction.UP, Direction.DOWN]:
            rect_x, rect_y, rect_w, rect_h = (
                (self.width - self.width * size_delta) / 2 + 1,
                0,
                self.width * size_delta - 1,
                WIN_SIZE,
            )
            pygame.draw.ellipse(
                self.image, Red, pygame.rect.Rect(rect_x, rect_y, rect_w, rect_h)
            )
        elif self.direction in [Direction.LEFT, Direction.RIGHT]:
            rect_x, rect_y, rect_w, rect_h = (
                0,
                (self.height - self.height * size_delta) / 2,
                WIN_SIZE,
                self.height * size_delta + 1,
            )
            pygame.draw.ellipse(
                self.image, Red, pygame.rect.Rect(rect_x, rect_y, rect_w, rect_h)
            )
        else:
            raise ValueError()

        if 0.2 < y < 1:
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.mask = pygame.mask.Mask(self.size)
        if pygame.time.get_ticks() - self.init_time > self.laser_lasting:
            self.kill()
