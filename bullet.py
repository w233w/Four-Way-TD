import pygame
from const import *


class TestBullet(pygame.sprite.Sprite):
    """
    测试子弹
    pos: 初始位置
    speed: 初始速度元向量
    speed: 实际速度倍率
    """

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
