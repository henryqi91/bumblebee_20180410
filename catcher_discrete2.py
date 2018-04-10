import sys
import pygame
from .utils import percent_round_int

from ple.games import base
# from ple.games.utils.udp_comm_sender_new import CommSender
from ple.games.utils.lv_reader import LabviewReader
# from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QObject, QSettings, QThread)
import random
import time
import numpy as np

class Paddle(pygame.sprite.Sprite):

    def __init__(self, speed, width, height, action_x_map_list,
                 SCREEN_WIDTH, SCREEN_HEIGHT):
        self.speed = speed
        self.width = width

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.xCoor_list = action_x_map_list
        self.vel = 0.0

        pygame.sprite.Sprite.__init__(self)

        image = pygame.Surface((width, height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, width, height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (
            SCREEN_WIDTH / 2 - width / 2,
            SCREEN_HEIGHT - height - 3)

    #    def update(self, dx, dt):
    def update(self, target_x):
        # !!!-- add your classification method here!--!!!
        # if target_x > xx and target_x < yy:
        #            res = x_all[0]
        #         ...
            _, y = self.rect.center
            n_x = self.xCoor_list[target_x - 1] - self.width / 2
        #        if n_x <= 0:
        #            n_x = 0
        #
        #        if n_x + self.width >= self.SCREEN_WIDTH:
        #            n_x = self.SCREEN_WIDTH - self.width
            self.rect.center = (n_x, y)

    def draw(self, screen):
        # screen.blit(self.image, self.rect.center)
        pos = (self.rect.center[0] - self.width / 2, self.rect.center[1])
        screen.blit(self.image, pos)

    def set_paddle_x(self,pad_x):
        y = 777
        self.rect.center = (pad_x,y)
        pass

class Fruit(pygame.sprite.Sprite):
    def __init__(self, speed, width, height,
                 gap,
                 SCREEN_WIDTH, SCREEN_HEIGHT, rng,
                 center_x,center_y):
        self.speed = speed
        self.width = width
        self.height = height
        self.init_x = 430
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        self.rng = rng

        pygame.sprite.Sprite.__init__(self)

        image = pygame.Surface((width, height + gap))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 120, 120),
            (0, 0, width, height),
            0
        )
        self.image = image
        self.rect = image.get_rect()
        self.rect.center = (center_x, center_y)

    def update(self, dt):
        x, y = self.rect.center
        n_y = y + self.speed * dt

        self.rect.center = (x, n_y)


    def reset_auto(self, gap):
        x = self.rng.choice(
                range(
                    self.width,
                    self.SCREEN_WIDTH - self.width,
                    1
                )
            )

        y = self.height - gap
        # self.rng.choice(
            # range(
            #     self.height,
            #     # int(self.SCREEN_HEIGHT / 3),
            #     10,
            #     self.height)
            # )
        self.rect.center = (x, -1 * y)

    def reset_manually(self, init_x, gap):
        x = init_x
        y = self.height - gap
        self.rect.center = (x, -1 * y)

    def set_fruit_fall_speed(self,fru_fall_speed):
        self.speed = fru_fall_speed/1
        # print(self.speed)

    def draw(self, screen):
        pos = (self.rect.center[0] - self.width / 2, self.rect.center[1])
        screen.blit(self.image, pos)
        # self.rect.center

class Catcher_Discrete(base.PyGameWrapper):
    """
    Based on `Eder Santana`_'s game idea.

    .. _`Eder Santana`: https://github.com/EderSantana

    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    init_lives : int (default: 3)
        The number lives the agent has.

    """

    def __init__(self, width=860, height=860, init_lives=10000,
                 action_num=8, udp_comm=True,fall_speed=0.0015,
                 fruit0_init_x=10, fruit1_init_x=10,
                 paddle_init_x=10, fruit_fall_speed=0.05):

        self.fruit0_init_x = fruit0_init_x
        self.fruit1_init_x = fruit1_init_x
        self.paddle_init_x = paddle_init_x
        self.fruit_fall_speed = fruit_fall_speed

        self.action_num = action_num
        actions = self._init__action_dict()
        base.PyGameWrapper.__init__(self, width, height, actions=actions)

        self.fruit_width = percent_round_int(width, 1)
        self.screen_width = width
        self.fruit_height = percent_round_int(height, 0.04)
        #        self.fruit_gap = 0.2 * height
        # self.fruit_fall_speed = fall_speed * height
        self.fruit_fall_speed = fruit_fall_speed

        self.player_speed = 0.010 * width
        self.paddle_width = 20
        self.paddle_height = 20

        self._dx = 0.0
        self.last_action = None
        self.cur_action = None
        self.init_lives = init_lives
        self.action_x_map_list = self._action_map_x()
        # self.angle_speed = 90

        # # new Thread for fruits' position update
        # self.fruits_thread = QThread()
        # new pygame events
        self.CUR_ACTION = pygame.USEREVENT + 1
        self.LAST_ACTION = pygame.USEREVENT + 2

        self._udp_comm = udp_comm
        self.to_update_text = 0
        self.is_manual_reset = True
        self.is_random = False
        self.is_sequence = False
        self.seq_msg = "0"
        self.fruit_rand_next_pos = None
        self.fruit_offset = 80
        self.seq_i = 0
        self.is_simple_AI = False
        self.is_Q_learning_AI = False
        self.simple_AI_left_speed = 40
        self.simple_AI_right_speed = 40
        self.ai_light_command = ""
        self.random_num = 0
        self.counter_shape = 0

        self.isToLeft = False
        self.isToRight= False
        self.acce_a = 3
        self.acce_sec = 3

        self.is_RL_to_send = False
        #draw the grid lines:
        # self.draw_grid()
        if self._udp_comm:
            # the addr is localhost and port is 5888
            self._sender = CommSender("localhost", 5888)
            self._reader = LabviewReader()


    def _handle_player_events(self):
        self._dx = 0.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == self.CUR_ACTION:
                self.cur_action = event.idx

            if event.type == self.LAST_ACTION:
                self.last_action = event.idx

    def _action_map_x(self):
        action_num = self.action_num
        action_xCoor = []
        # x_unit = self.width / (action_num * 2-1)
        x_unit = self.width / (action_num-1)
        # for i in range(0, action_num * 2-1, 2):
        action_xCoor.append(self.paddle_width/2)
        # print (self.paddle_width, self.width)
        for i in range(1, action_num):
            to_append = int(x_unit * i)
            if i == action_num - 1:
                to_append -= self.paddle_width / 2
            action_xCoor.append(to_append)
        # print (action_xCoor)
        return action_xCoor

    def _init__action_dict(self):
        actions = {}
        for i in range(self.action_num):
            tmp = {str(i + 1): i + 1}
            actions.update(tmp)
        return actions

    def init(self):
        self.score = 0
        self.lives = self.init_lives
        self.player = Paddle(self.player_speed, self.paddle_width,
                             self.paddle_height, self.action_x_map_list,
                             self.width, self.height)

        self.fruit0 = Fruit(self.fruit_fall_speed,
                            self.fruit_width, self.fruit_height,
                            0,
                            self.width, self.height, self.rng,-1,-1)

        self.fruit1 = Fruit(self.fruit_fall_speed,
                            self.fruit_width, self.fruit_height,
                            0,
                            self.width, self.height, self.rng,-1,-1)
        #
        # self.fruit2 = Fruit(self.fruit_fall_speed,
        #                     self.fruit_width, self.fruit_height,
        #                     0,
        #                     self.width, self.height, self.rng)

        # self.gap = int(self.height/1.5)
        if self.is_manual_reset == True:
            self.fruit0.reset_manually(self.fruit0_init_x,0)
            self.fruit1.reset_manually(self.fruit1_init_x,0)
        else:
            self.fruit0.reset_auto(0)
            self.fruit1.reset_auto(0)
        # self.fruit1.reset_manually(self.fruit_init_x,self.gap)
        # self.fruit2.reset_manually(self.fruit_init_x,(self.gap)*2)

        #draw grid lines:
        # self.draw_grid()

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player x position.
            * players velocity.
            * fruits x position.
            * fruits y position.

            See code for structure.

        """
        state = {
            "player_x": self.player.rect.center[0],
            "player_y": self.player.rect.center[1],
            "player_vel": self.player.vel,
            "fruit0_x": self.fruit0.rect.center[0],
            "fruit0_y": self.fruit0.rect.center[1],
            "to_update_text": self.to_update_text,
            # "fruit_rand_pos": self.random_num
            "fruit1_x": self.fruit1.rect.center[0],
            "fruit1_y": self.fruit1.rect.center[1]
            # "fruit2_x": self.fruit2.rect.center[0],
            # "fruit2_y": self.fruit2.rect.center[1],
        }

        return state

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives == 0

    def step(self, dt):
        self.screen.fill((0, 0, 0))
        self._handle_player_events()

        self.score += self.rewards["tick"]

        if self.fruit0.rect.center[1] >= self.height or self.fruit1.rect.center[1] >= self.height:
            self.score += self.rewards["positive"]
            self.seq_i += 1
            self.random_num = random.randint(1, 3)
            #print("score: ", self.score)
            if self.is_manual_reset == True:
                self.fruit0.reset_manually(self.fruit0_init_x, 0)
                self.fruit1.reset_manually(self.fruit1_init_x, 0)
            else:
                self.fruit0.reset_auto(0)
                self.fruit1.reset_auto(0)

            #self.to_update_text = 1

        if pygame.sprite.collide_rect(self.player, self.fruit0) or pygame.sprite.collide_rect(self.player, self.fruit1):
        # print(ret)
            self.score += self.rewards["negative"]
            self.lives -= 1
            self.seq_i += 1
            self.random_num = random.randint(1, 3)

            if self.is_manual_reset == True:
                self.fruit0.reset_manually(self.fruit0_init_x, 0)
                self.fruit1.reset_manually(self.fruit1_init_x, 0)
            else:
                self.fruit0.reset_auto(0)
                self.fruit1.reset_auto(0)


            self.to_update_text = 1

        if any([self.cur_action == idx for idx in list(self.actions.values())]):
            self.player.update(self.cur_action)

        self.fruit0.update(dt)
        self.fruit1.update(dt)
        # self.fruit2.update(dt)

        if self.lives == 0:
            self.score += self.rewards["loss"]

        self.player.draw(self.screen)
        self.fruit0.draw(self.screen)
        self.fruit1.draw(self.screen)
        self.draw_grid()

        if self.is_random == True:
            if self.random_num == 1: #left
                self.fruit0_init_x = -3 / 8 * self.screen_width
                self.fruit1_init_x = 7 / 8 * self.screen_width
                # self.fruit0.width = percent_round_int(self.screen_width, 0.5)
                # self.fruit0.fruit_width = percent_round_int(self.screen_width, 0.5)
                # self.reset_fruit_param(self.fruit_width)
            elif self.random_num == 2: #middle
                self.fruit0_init_x = -1 / 8 * self.screen_width
                self.fruit1_init_x = 9 / 8 * self.screen_width
                # self.fruit0.width = percent_round_int(self.screen_width, 0.25)
                # self.reset_fruit_param(self.fruit0.fruit_width)

            elif self.random_num == 3: #right
                self.fruit0_init_x = 1 / 8 * self.screen_width
                self.fruit1_init_x = 11 / 8 * self.screen_width
                # self.fruit0.width = percent_round_int(self.screen_width, 0.5)
                # self.reset_fruit_param(self.fruit0.fruit_width)

        if self.is_sequence == True:
            seq = self.seq_msg
            length = len(seq)
            if seq[self.seq_i] == "0" and self.seq_i < length:
                self.fruit_init_x = 215 + self.fruit_offset
            if seq[self.seq_i] == "1" and self.seq_i < length:
                self.fruit_init_x = 430
            if seq[self.seq_i] == "2" and self.seq_i < length:
                self.fruit_init_x = 645 - self.fruit_offset
            if self.seq_i == length-1:
                self.seq_i = 0

        if self.is_simple_AI == True:
            fruit_x = self.fruit0.rect.center[0]
            fruit_y = self.fruit0.rect.center[1]
            if fruit_x > 480 and fruit_y > 170 and fruit_y < 180:
                self.ai_light_command = "left"
                self._action_single_screen(self.simple_AI_left_speed, "left")
            elif fruit_x <= 480 and fruit_y > 170 and fruit_y < 180:
                self.ai_light_command = "right"
                self._action_single_screen(self.simple_AI_right_speed, "right")

        if self.is_Q_learning_AI == True:
            num_heights = 4
            num_fruit_x = 3
            num_pad_x = 7

            pad_x_bounds = []
            for i in range(num_pad_x):
                pad_x_bounds.append(self.width / num_pad_x * (i))
            fruit_height_bounds = []
            for j in range(num_heights):
                fruit_height_bounds.append(self.height / num_pad_x * (j))

            num_states = num_heights * num_fruit_x * num_pad_x
            num_actions = 8 # light streams
            self.R = np.zeros([num_states, num_actions])
            self.Q = np.zeros([num_states, num_actions])
            GAMMA = 0.8

            self.init_R_table(self.R)

            if self.fruit_init_x < 480:
                self.game._action_single_screen(40, "left")
            else:
                self.game._action_single_screen(40, "right")

        if self.getGameState()["fruit0_y"] == 0:
            # if self.fruit_init_x < 430:
            #     token = self.fruit_init_x
            #     self.reset_fruit_param(percent_round_int(self.screen_width, 0.5))
            #     self.fruit_init_x = token
            # elif self.fruit_init_x == 430:
            #     token = self.fruit_init_x
            #     self.reset_fruit_param(percent_round_int(self.screen_width, 0.25))
            #     self.fruit_init_x = token
            # elif self.fruit_init_x > 430:
            #     token = self.fruit_init_x
            #     self.reset_fruit_param(percent_round_int(self.screen_width, 0.5))
            #     self.fruit_init_x = token
            pass
        time.sleep(0.01)  #for slowing down the fps

        # self.fruit1.draw(self.screen)
        # self.fruit2.draw(self.screen)

    # def _action_lightStream_map(self, action,action_list,angle_speed_list):
    def _action_lightStream_map(self, angle_speed,group_num):
        # angle_speed = 0
        self._sender.send("params", 1, "hDirection", "left")
        self._sender.send("params", 2, "hDirection", "right")
        self._sender.send("start_right")
        self._sender.send("start_left")
        #acquire: speed, group_num
        # for i in range(0,8):
            # if angle_speed = angle_speed_list[i]:
        # if angle_speed < 0:
            # group_num = 1  #left group
        # angle_speed = abs(angle_speed)
        if group_num == 1:
            self._sender.send("restore_left")
            self._sender.send("params", group_num, "hSpeed", angle_speed)
            self._sender.send("off_right")
        # else:
        #     group_num = 2  #right group
        # angle_speed = abs(angle_speed)
        if group_num == 2:
            self._sender.send("restore_right")
            self._sender.send("params", group_num, "hSpeed", angle_speed)
            self._sender.send("off_left")
                    # angle_speed = abs(angle_speed)

    def _action_single_screen(self,angle_speed,direction):
        # if self.is_RL_to_send:
            if direction == "left" or direction =="right":
                self._sender.send("params", 1, "hDirection", direction)
                self._sender.send("params", 2, "hDirection", direction)
                self._sender.send("params", 1, "hSpeed", angle_speed)
                self._sender.send("params", 2, "hSpeed", angle_speed)
                self._sender.send("start_right")
                self._sender.send("restore_right")
                self._sender.send("start_left")
                self._sender.send("restore_left")
            elif direction == "reset_all":
                self._sender.send("reset_right")
                self._sender.send("reset_left")
            elif direction == "stop_all":
                self._sender.send("stop_right")
                self._sender.send("stop_left")

    def _setAction(self, action, last_action):
        """
        Pushes the action to the pygame event queue.
        """
        if action is None:
            action = self.NOOP

        if last_action is None:
            last_action = self.NOOP

        curr_ac_num = pygame.event.Event(self.CUR_ACTION, idx= action)
        last_ac_num = pygame.event.Event(self.LAST_ACTION, idx=last_action)

        pygame.event.post(curr_ac_num)
        pygame.event.post(last_ac_num)

    def get_states(self,string):
        game_states = {
            "player_x": self.player.rect.center[0],
            "player_y": self.player.rect.center[1],
            "player_vel": self.player.vel,
            "fruit0_x": self.fruit0.rect.center[0],
            "fruit0_y": self.fruit0.rect.center[1],
            "to_update_text": self.to_update_text,
        }
        return game_states[string]

    def init_R_table(self,side_name):
        self.reward = np.zeros([860, 18])  # rows(states): x-coord (1~860), cols(actions): light stream speed (5~90)
        self.Q_table = np.zeros([860, 18])
        self.Gamma = 0.8
        # self.

        # For left side, the left-mid point is considered the reward point
        # For the right side, the right-mid point is considered the reward point
        if side_name == "left":
            for i in range (200,230):   # 215 is the center, +15, -15 is the acceptable reward range
                self.reward[i,:] = 10
        if side_name == "right":
            for j in range (630,660):
                self.reward[j,:] = 10   # 615 is the center.

    def update_Q_table(self,Q,R,state,action,next_state):
        Q[state, action] = R(state, action) + self.Gamma * max(Q[next_state, :])
        return Q

    def train_model(self):
        pass

    def draw_grid(self):
        #draw grid lines:
        line_color = 255, 200, 255
        line_width = 2
        line_gap = self.width / 8
        #horizontal Line:
        pygame.draw.line(self.screen, line_color, (0,int(self.height*2/8)),
                         (self.width,int(self.height*2/8)), line_width)

        for i in range(1,9):
            if i != 4:
                pygame.draw.line(self.screen, line_color, (line_gap*i, 0), (line_gap*i, self.height), line_width)

