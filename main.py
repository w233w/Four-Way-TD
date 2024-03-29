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
tower_test.add(TestTower(pygame.Vector2(TOWER_GRID_SIZE // 2, TOWER_GRID_SIZE // 2), 10))
tower_test.add(TestTower2(pygame.Vector2(40 + TOWER_GRID_SIZE // 2, TOWER_GRID_SIZE // 2), 5))
tower_test.add(TestTower3(pygame.Vector2(TOWER_GRID_SIZE // 2, 40 + TOWER_GRID_SIZE // 2), 10))
tower_test.add(TestTower4(pygame.Vector2(80 + TOWER_GRID_SIZE // 2, TOWER_GRID_SIZE // 2), 10))
info_bar.add(Info())

last_enemy1, last_enemy2 = 5000, 5000
interval = 3000
enemy_count = 0
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
    if pygame.time.get_ticks() - last_enemy1 >= 1000:
        enemy_count += 1
        enemy_test.add(
            TestEnemy1(
                random.randint(0, EDGES - 1),
                Direction.random(),
                0.2,
                1 + min(5, enemy_count / 20),
            )
        )
        last_enemy1 = pygame.time.get_ticks()
    if pygame.time.get_ticks() - last_enemy2 >= 3000:
        enemy_count += 1
        enemy_test.add(
            TestEnemy2(
                random.randint(0, EDGES - 1),
                Direction.random(),
                0.2,
                1,
            )
        )
        last_enemy2 = pygame.time.get_ticks()
    # 先铺背景再画sprites
    screen.fill(pygame.Color(BackgroundColor))
    # 更新sprites
    # 永远先更新玩家
    grids.update()
    info_bar.update()
    grid.update()
    tower_test.update(event_list)
    enemy_test.update()
    player_bullets.update()
    texts.update()
    # 不会有重叠，所以画不分先后
    grids.draw(screen)
    info_bar.draw(screen)
    grid.draw(screen)
    tower_test.draw(screen)
    enemy_test.draw(screen)
    player_bullets.draw(screen)
    texts.draw(screen)
    # 更新画布
    pygame.display.flip()
