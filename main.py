from grid import *
from tower import *
from enemy import *


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
        for i, (key, val) in enumerate(to_dict(resource).items()):
            text = f"{key.capitalize()}: {val}"
            text_surface = self.font.render(text, True, AlmostBlack, None)
            self.image.blit(text_surface, [10, 10 + i * (10 + self.text_height)])


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(V_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

grid.add(Grids(GRIDS_SIZE, EDGES))
tower_test.add(TestTower(pygame.Vector2(20, 20), 10))
tower_test.add(TestTower2(pygame.Vector2(60, 60), 5))
info_bar.add(Info())

last_enemy = 3000
interval = 1000

# 主体
while running := True:
    # 刷新率
    clock.tick(FPS)
    # 点×时退出。。
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False
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
