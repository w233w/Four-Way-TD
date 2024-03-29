from const import *
from scipy.stats import norm
from groups import *
from enemy import *


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
            return
        hit: list[BaseEnemy] = pygame.sprite.spritecollide(
            self, enemy_test, False, pygame.sprite.collide_mask
        )
        for enemy in hit:
            enemy.hp -= 1
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
        self.laser_lasting = 1200

        self.init_time = pygame.time.get_ticks()
        self.dpf = 10 / FPS

    def update(self) -> None:
        current_time = pygame.time.get_ticks() - self.init_time
        if current_time > self.laser_lasting:
            self.kill()
            return
        self.image.fill(Black)
        x = current_time % self.laser_lasting / (self.laser_lasting // 10) - 5
        y = norm.pdf(x, 0, 1)
        size_delta = 1.2 * y
        if self.direction in [Direction.UP, Direction.DOWN]:
            rect_x, rect_y, rect_w, rect_h = (
                (self.width - self.width * size_delta) / 2 + 1,
                0,
                self.width * size_delta - 1,
                WIN_SIZE,
            )
            pygame.draw.ellipse(
                self.image, Lightcyan, pygame.rect.Rect(rect_x, rect_y, rect_w, rect_h)
            )
        elif self.direction in [Direction.LEFT, Direction.RIGHT]:
            rect_x, rect_y, rect_w, rect_h = (
                0,
                (self.height - self.height * size_delta) / 2,
                WIN_SIZE,
                self.height * size_delta + 1,
            )
            pygame.draw.ellipse(
                self.image, Lightcyan, pygame.rect.Rect(rect_x, rect_y, rect_w, rect_h)
            )
        else:
            raise ValueError()

        if 0.2 < y < 1:
            self.mask = pygame.mask.from_surface(self.image)
            hit: list[BaseEnemy] = pygame.sprite.spritecollide(
                self, enemy_test, False, pygame.sprite.collide_mask
            )
            for enemy in hit:
                enemy.hp -= self.dpf


class TestBullet3(pygame.sprite.Sprite):
    """
    测试子弹三-震波
    """

    def __init__(self, pos: pygame.Vector2, radius: float) -> None:
        super().__init__()
        self.pos = pos
        self.radius = radius
        self.image = pygame.Surface([2 * self.radius, 2 * self.radius])
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=self.pos)
        self.init_time = pygame.time.get_ticks()
        self.hitted = []

    def update(self) -> None:
        current_time = pygame.time.get_ticks() - self.init_time
        if current_time > 800:
            self.kill()
            return
        self.image.fill(Black)
        r = self.radius * current_time / 800
        pygame.draw.circle(
            self.image,
            Blue,
            [self.radius, self.radius],
            r,
            max(1, 12 - round(12 * current_time / 800)),
        )
        self.mask = pygame.mask.from_surface(self.image)
        hit: list[BaseEnemy] = pygame.sprite.spritecollide(
            self, enemy_test, False, pygame.sprite.collide_mask
        )
        for enemy in hit:
            if enemy not in self.hitted:
                enemy.hp -= 0.5
                enemy.buff["cold"] = pygame.time.get_ticks()
        self.hitted.extend(hit)


class TestBullet4(pygame.sprite.Sprite):
    """
    测试子弹4-闪电链
    """

    def __init__(
        self,
        pos: pygame.Vector2,
        target: BaseEnemy,
        radius: float,
        rest_bounce: int,
        hit_hist: list[BaseEnemy],
        start_shift: pygame.Vector2,
    ) -> None:
        super().__init__()
        self.rest_bounce = rest_bounce
        self.hit_hist = hit_hist
        self.pos = pos
        self.target = target
        self.start_shift = start_shift
        self.end_shift = Direction.random().to_vector() * 3
        self.target.hp -= 1
        self.init_time = pygame.time.get_ticks()
        self.next_target: BaseEnemy = None
        self.image = pygame.Surface([WIN_SIZE, WIN_SIZE])
        self.image.set_colorkey(Black)
        self.rect = self.image.get_rect(center=V_SIZE // 2)
        min_distance = radius
        for enemy in enemy_test.sprites():
            if enemy in self.hit_hist:
                continue
            distance = pygame.Vector2.distance_to(self.target.pos, enemy.pos)
            if distance < min_distance:
                min_distance = distance
                self.next_target = enemy
        if self.next_target is not None and self.rest_bounce > 1:
            self.hit_hist.append(self.next_target)
            player_bullets.add(
                self.__class__(
                    self.target.pos,
                    self.next_target,
                    radius,
                    rest_bounce - 1,
                    self.hit_hist,
                    self.end_shift,
                )
            )

    def update(self):
        current_time = pygame.time.get_ticks() - self.init_time
        if current_time > 150:
            self.kill()
            return
        self.image.fill(Black)
        start = self.pos + self.start_shift
        end = self.target.pos + self.end_shift
        pygame.draw.line(self.image, Lightblue, start, end, 3)
