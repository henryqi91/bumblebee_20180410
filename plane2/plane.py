#-*-coding:utf-8-*-
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
import pygame
from sys import exit
from pygame.locals import *
import random
# import time

# 子弹类
class Bullet(pygame.sprite.Sprite):

    def __init__(self, bullet_img, init_pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.midbottom = init_pos
        self.speed = 8

    def move(self):
        self.rect.top -= self.speed

# 玩家飞机类
class Player(pygame.sprite.Sprite):

    def __init__(self, plane_img, player_rect, init_pos,
                 SCREEN_WIDTH,SCREEN_HEIGHT,
                 plane_width,plane_height):
        pygame.sprite.Sprite.__init__(self)
        self.image = []                                 # 用来存储玩家飞机图片的列表
        for i in range(len(player_rect)):
            self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
            # curr_img = plane_img.subsurface(player_rect[i])
            # curr_img = pygame.transform.scale(curr_img,(plane_width,plane_height))
            # self.image.append(plane_img.subsurface(player_rect[i]).convert_alpha())
            # self.image.append(curr_img.convert_alpha())

        self.rect = player_rect[0]                      # 初始化图片所在的矩形
        self.rect.topleft = init_pos                    # 初始化矩形的左上角坐标
        self.speed = 8                                  # 初始化玩家飞机速度，这里是一个确定的值
        self.bullets = pygame.sprite.Group()            # 玩家飞机所发射的子弹的集合
        self.img_index = 0                              # 玩家飞机图片索引
        self.is_hit = False                             # 玩家是否被击中

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

    # 发射子弹
    def shoot(self, bullet_img):
        bullet = Bullet(bullet_img, self.rect.midtop)
        self.bullets.add(bullet)

    # 向上移动，需要判断边界
    def moveUp(self):
        if self.rect.top <= 0:
            self.rect.top = 0
        else:
            self.rect.top -= self.speed

    # 向下移动，需要判断边界
    def moveDown(self):
        if self.rect.top >= self.SCREEN_HEIGHT - self.rect.height:
            self.rect.top = self.SCREEN_HEIGHT - self.rect.height
        else:
            self.rect.top += self.speed

    # 向左移动，需要判断边界
    def moveLeft(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        else:
            self.rect.left -= self.speed

    # 向右移动，需要判断边界        
    def moveRight(self):
        if self.rect.left >= self.SCREEN_WIDTH - self.rect.width:
            self.rect.left = self.SCREEN_WIDTH - self.rect.width
        else:
            self.rect.left += self.speed

# 敌机类
class Enemy(pygame.sprite.Sprite,QObject):
    def __init__(self, enemy_img, enemy_down_imgs, init_pos):
       pygame.sprite.Sprite.__init__(self)
       self.image = enemy_img
       self.rect = self.image.get_rect()
       self.rect.topleft = init_pos
       self.down_imgs = enemy_down_imgs
       self.speed = 2
       self.down_index = 0

    # 敌机移动，边界判断及删除在游戏主循环里处理
    def move(self):
        self.rect.top += self.speed

#主游戏
class PlaneGame(pygame.sprite.Sprite,QObject):
    fps_signal = pyqtSignal(int)

    def __init__(self,signal_center,keyboard_control=True,enemy_speed=5):
        super(PlaneGame, self).__init__()
        self.SCREEN_WIDTH = signal_center.SCREEN_WIDTH # ori: 480
        self.SCREEN_HEIGHT = signal_center.SCREEN_HEIGHT
        # self.is_keyboard = signal_center.is_keyboard
        self.player_pos_y = int(self.SCREEN_HEIGHT*18/20)

        self.player_width = 50
        self.player_height = 50
        self.bullet_width = 9
        self.bullet_height = 21

        self.enemy_speed = signal_center.enemy_speed
        self.player_speed = 20
        self.bullet_speed = 50

        self.is_game_over = False
        self.is_running = signal_center.is_running
        self.freq = 50

        self.score = 0
        self.player_life = 2

    def plane_game_init(self,signal_center):
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.background = pygame.image.load('plane/resources/image/background_large.png').convert()
        self.game_over = pygame.image.load('plane/resources/image/gameover_large.png')
        self.plane_img = pygame.image.load('plane/resources/image/shoot.png')
        # self.obstacle_img = pygame.image.load('plane/resources/image/rock_small.png').convert()
        # print (self.obstacle_img)
        # self.obstacle_img = pygame.transform.scale(self.obstacle_img,(200,150))
        # self.plane_img = pygame.transform.scale(self.plane_img,(1000,1000))

        pygame.display.set_caption('飞机躲避小游戏')

        # 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果
        self.player_rect = []
        self.ref_width = 102  #N/A
        self.ref_height = 126
        self.player_rect.append(pygame.Rect(0, 99, self.ref_width, self.ref_height))  # 玩家飞机图片
        # self.player_rect.append(pygame.Rect(165, 360, self.ref_width, self.ref_height))
        # self.player_rect.append(pygame.Rect(165, 234, self.ref_width, self.ref_height))  # 玩家爆炸图片
        # self.player_rect.append(pygame.Rect(330, 624, self.ref_width, self.ref_height))
        # self.player_rect.append(pygame.Rect(330, 498, self.ref_width, self.ref_height))
        # self.player_rect.append(pygame.Rect(432, 624, self.ref_width, self.ref_height))
        self.player_pos = [int(self.SCREEN_WIDTH/2), self.player_pos_y]
        self.player = Player(self.plane_img, self.player_rect, self.player_pos,
                             SCREEN_HEIGHT=self.SCREEN_HEIGHT, SCREEN_WIDTH=self.SCREEN_WIDTH,
                             plane_width=self.player_width,plane_height=self.player_height)

        # 子弹图片
        self.bullet_rect = pygame.Rect(1004, 987, self.bullet_width, self.bullet_height)
        self.bullet_img = self.plane_img.subsurface(self.bullet_rect)

        # 敌机不同状态的图片列表，多张图片展示为动画效果
        self.enemy_width = 57
        self.enemy_height = 43
        self.enemy1_rect = pygame.Rect(534, 612, self.enemy_width, self.enemy_height)
        self.enemy1_img = self.plane_img.subsurface(self.enemy1_rect)
        self.enemy1_down_imgs = []
        # self.enemy1_down_imgs.append(self.plane_img.subsurface(pygame.Rect(267, 347, self.enemy_width, self.enemy_height)))
        # self.enemy1_down_imgs.append(self.plane_img.subsurface(pygame.Rect(873, 697, self.enemy_width, self.enemy_height)))
        # self.enemy1_down_imgs.append(self.plane_img.subsurface(pygame.Rect(267, 296, self.enemy_width, self.enemy_height)))
        # self.enemy1_down_imgs.append(self.plane_img.subsurface(pygame.Rect(930, 697, self.enemy_width, self.enemy_height)))

        # 存储敌机，管理多个对象
        self.enemies1 = pygame.sprite.Group()

        # 存储被击毁的飞机，用来渲染击毁动画
        self.enemies_down = pygame.sprite.Group()

        # 初始化射击及敌机移动频率
        self.shoot_frequency = 0
        self.enemy_frequency = 0

        # 玩家飞机被击中后的效果处理
        self.player_down_index = 16

        # 初始化分数
        self.score = 0
        self.player_life = 2

        # 游戏循环帧率设置
        self.clock = pygame.time.Clock()

        # 判断游戏是否暂停的参数
        self.is_running = signal_center.is_running
        # self.player.speed = self.player_speed

    def reset_game(self,signal_center):

        # 存储敌机，管理多个对象
        self.enemies1 = pygame.sprite.Group()

        # 存储被击毁的飞机，用来渲染击毁动画
        self.enemies_down = pygame.sprite.Group()

        # 设置玩家飞机不同状态的图片列表，多张图片展示为动画效果

        # 玩家飞机被击中后的效果处理
        self.player_down_index = 16
        self.player.is_hit = False

        # 初始化射击及敌机移动频率
        self.shoot_frequency = 0
        self.enemy_frequency = 0

        # 初始化分数
        signal_center.score = 0
        self.player_life = 2

        # 游戏循环帧率设置
        # self.clock = pygame.time.Clock()
        # 判断游戏是否暂停的参数
        self.is_running = signal_center.is_running
        self.player.speed = self.player_speed
        self.is_game_over = False


    def get_enemy_coord(self):
        enemies_x = []
        enemies_y = []
        for enemy in self.enemies1:
            enemies_x.append(enemy.rect.center[0])
            enemies_y.append(enemy.rect.center[1])
        return enemies_x,enemies_y
        pass

    def set_player_x(self,x):
        self.player.rect.center = (x,self.player_pos_y)
        pass

    def getGameState(self):
        enemies_x,enemies_y = self.get_enemy_coord()
        state = {
            "player_x": self.player.rect.center[0],
            "enemies": self.enemies1,
            "enemies_x": enemies_x,
            "enemies_y": enemies_y
        }
        return state

    def set_screen_text(self,text,location,color):
        font = pygame.font.Font(None, 36)
        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.topleft = location
        self.screen.blit(text, rect)

    def get_closest_x(self):
        closest_x = 1000
        for enemy in self.enemies1:
            if enemy.rect.center[0] < closest_x:
                closest_x = enemy.rect.center[0]
        return closest_x

    def run_game(self,signal_center):

        while True:
            # 控制游戏最大帧率
            self.clock.tick(60)

            if not self.is_game_over:
                # self.is_running = signal_center.is_running
                # self.freq = signal_center.plane_appear_freq
                self.is_running = signal_center.is_running
                self.score = signal_center.score
                # self.is_keyboard = signal_center.is_keyboard
                # enemy_selection = 1
                # if enemy_selection == 1:
                # self.enemy1_img = self.plane_img.subsurface(self.enemy1_rect)
                # elif enemy_selection == 2:
                #     self.enemy1_img = self.obstacle_img

                # 生成子弹，需要控制发射频率
                if self.is_running:
                    # 发射子弹
                    if not self.player.is_hit:
                        if self.shoot_frequency % 15 == 0: #15
                            self.player.shoot(self.bullet_img)
                        self.shoot_frequency += 1
                        if self.shoot_frequency >= 15: #15
                            self.shoot_frequency = 0

                    # 生成敌机，需要控制生成频率
                    if self.enemy_frequency % signal_center.plane_appear_freq == 0:
                        if len(self.enemies1) < 5:
                            enemy1_pos = [random.randint(0, self.SCREEN_WIDTH - self.enemy1_rect.width), 0]
                            # enemy_selection = random.randint(1,2) # 1-plane, 2-rock
                            enemy1 = Enemy(self.enemy1_img, self.enemy1_down_imgs, enemy1_pos)
                            self.enemies1.add(enemy1)
                    self.enemy_frequency += 1
                    if self.enemy_frequency >= signal_center.plane_appear_freq:
                        self.enemy_frequency = 0

                    for bullet in self.player.bullets:
                        # 以固定速度移动子弹
                        # if len(self.enemies1) > 0:
                        bullet.move()
                        pygame.display.update()
                        # 移动出屏幕后删除子弹
                        if bullet.rect.bottom < 0:
                            self.player.bullets.remove(bullet)

                    for enemy in self.enemies1:
                        # 如果游戏暂停，则敌机不动
                        if self.is_running:
                            enemy.speed = signal_center.obst_fall_speed
                            # 2. 移动敌机
                            enemy.move()
                        # 3. 敌机与玩家飞机碰撞效果处理
                        if pygame.sprite.collide_rect_ratio(1)(enemy, self.player):
                            self.enemies_down.add(enemy)
                            self.enemies1.remove(enemy)
                            self.player.is_hit = True
                            # self.is_game_over = True
                            break
                        if enemy.rect.top > self.SCREEN_HEIGHT:
                            self.enemies1.remove(enemy)

                    # 敌机被子弹击中效果处理
                    # 将被击中的敌机对象添加到击毁敌机Group中，用来渲染击毁动画
                    enemies1_down = pygame.sprite.groupcollide(self.enemies1, self.player.bullets, 1, 1)
                    for enemy_down in enemies1_down:
                        signal_center.score += 10
                        # 绘制背景
                        self.screen.fill(0)
                        self.screen.blit(self.background, (0, 0))
                        # self.enemies_down.add(enemy_down)

                    # 绘制背景
                    self.screen.fill(0)
                    self.screen.blit(self.background, (0, 0))

                if self.is_running:
                    # 绘制玩家飞机
                    if not self.player.is_hit:
                        self.screen.blit(self.player.image[self.player.img_index],
                                         self.player.rect)
                        # 更换图片索引使飞机有动画效果
                        # self.player.img_index = self.shoot_frequency // 8
                        pass
                    else:
                        # 玩家飞机被击中后的效果处理
                        self.player.is_hit = False
                        self.player.img_index = self.player_down_index // 8
                        self.screen.blit(self.player.image[self.player.img_index],
                                         self.player.rect)
                        if self.player_life == 0:
                            self.player_life -= 1
                            self.is_game_over = True
                            self.is_running = False
                        else:
                            self.player_life -= 1
                            self.player.is_hit = False
                            self.player.img_index = 0
                            self.player_down_index = 16
                        # self.player_down_index += 1
                        # if self.player_down_index > 47:
                        # #     #击中效果处理完成后游戏结束
                        self.is_running = False

                    # for enemy_down in self.enemies_down:
                    #     if enemy_down.down_index == 0:
                    #         pass
                    #     if enemy_down.down_index > 7:
                    #         self.enemies_down.remove(enemy_down)
                    #         self.score += 10
                    #         continue
                    #     self.screen.blit(enemy_down.down_imgs[enemy_down.down_index // 2], enemy_down.rect)
                    #     enemy_down.down_index += 1
                    #显示子弹
                    self.player.bullets.draw(self.screen)

                    # 显示敌机
                    self.enemies1.draw(self.screen)

                    # 绘制分数
                    self.set_screen_text(text= "Score: " + str(self.score),
                                         location=[10,10],color=(128,128,128))
                    # 绘制生命值
                    self.set_screen_text(text="Life: " + str(self.player_life+1),
                                         location=[10, 50], color=(128, 128, 255))
                    # 绘制FPS
                    self.set_screen_text(text="FPS: " + str(int(self.clock.get_fps())),
                                         location=[self.SCREEN_WIDTH-100, 10], color=(128, 255, 128))

                    pygame.display.update()

                    # 处理游戏退出
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()

                    # 获取键盘事件（上下左右按键）
                    key_pressed = pygame.key.get_pressed()
                    # 处理键盘事件（移动飞机的位置）
                    if key_pressed[K_w] or key_pressed[K_UP]:
                        self.player.moveUp()
                    if key_pressed[K_s] or key_pressed[K_DOWN]:
                        self.player.moveDown()
                    if key_pressed[K_a] or key_pressed[K_LEFT]:
                        self.player.moveLeft()
                    if key_pressed[K_d] or key_pressed[K_RIGHT]:
                        self.player.moveRight()
                # else:
                #     self.set_player_x(signal_center.player_x)
                #     pygame.display.update()

            if self.is_game_over:
                # 游戏 Game Over 后显示最终得分
                font = pygame.font.Font(None, 48)
                text = font.render('Score: ' + str(self.score), True, (255, 0, 0))
                text_rect = text.get_rect()
                text_rect.centerx = self.screen.get_rect().centerx
                text_rect.centery = self.screen.get_rect().centery + 24
                self.screen.blit(self.game_over, (0, 0))
                self.screen.blit(text, text_rect)

            # pygame.display.update()

                #显示得分并处理游戏退出
                while 1:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            exit()
                        pygame.display.update()