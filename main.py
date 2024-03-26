from grid import *
from tower import *
from enemy import *


# Init pygame & Crate screen
pygame.init()
screen = pygame.display.set_mode(V_SIZE)
pygame.display.set_caption("测试")
clock = pygame.time.Clock()

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

grid.add(Grids(GRIDS_SIZE, EDGES))
tower_test.add(TestTower(pygame.Vector2(20, 20), 10))
tower_test.add(TestTower2(pygame.Vector2(60, 60), 5))
tower_test.add(TestTower3(pygame.Vector2(20, 90), 5))
tower_test.add(TestTower4(pygame.Vector2(90, 90), 5))
info_bar.add(Info())

last_enemy = 0
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
    enemy_test.update()
    player_bullets.update()
    # 不会有重叠，所以画不分先后
    grids.draw(screen)
    info_bar.draw(screen)
    grid.draw(screen)
    tower_test.draw(screen)
    texts.draw(screen)
    enemy_test.draw(screen)
    player_bullets.draw(screen)
    # 更新画布
    pygame.display.flip()
