from PyQt5.QtWidgets import (QApplication, QMainWindow,QDesktopWidget)
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QObject, QSettings, QThread)
# from PyQt5 import QtCore
from ui_catcher_discrete_controller import Ui_MainWindow
from PyQt5.QtGui import QTextCursor
from ple import PLE
from ple.games.catcher_discrete2 import Catcher_Discrete
# from plane.
# from ple.games.utils.udp_comm_sender_new import CommSender
# from ple.games.utils.lv_reader import LabviewReader
import time
import numpy as np
import _thread
# import threading
import multiprocessing
import sys
import pandas as pd


# import random
# from sklearn import preprocessing

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        # game config
        self.screen_width = 860
        self.screen_height = 800
        self.move( (screen.width()-size.width())/4*3,
                   (screen.height()-size.height())/2)
        self.action_num = 8

        # ple config
        self.fps = 50
        self.num_steps = 1
        self.force_fps = False
        self.frame_skip = 1
        self.display = True
        self.crack_init_x = (1/4) * self.screen_width

        self.command_delay = 0.001
        self.is_simple_AI_clicked = False

        # connect
        # control buttons
        self.ui.manual_start.clicked.connect(self._manual_start_clicked)
        self.ui.manual_reset.clicked.connect(self._manual_reset_clicked)
        # self.ui.auto_start.clicked.connect(self._auto_start_clicked)
        # self.ui.auto_reset.clicked.connect(self._auto_reset_clicked)

        # actions group
        # self.ui.paddle_x_1.clicked.connect(self._paddle_x_1_clicked)
        # self.ui.paddle_x_2.clicked.connect(self._paddle_x_2_clicked)
        # self.ui.paddle_x_3.clicked.connect(self._paddle_x_3_clicked)
        # self.ui.paddle_x_4.clicked.connect(self._paddle_x_4_clicked)
        # self.ui.paddle_x_5.clicked.connect(self._paddle_x_5_clicked)
        # self.ui.paddle_x_6.clicked.connect(self._paddle_x_6_clicked)
        # self.ui.paddle_x_7.clicked.connect(self._paddle_x_7_clicked)
        # self.ui.paddle_x_8.clicked.connect(self._paddle_x_8_clicked)

        # self.ui.left_very_fast.clicked.connect(self._left_very_fast_clicked)
        # self.ui.left_fast.clicked.connect(self._left_fast_clicked)
        # self.ui.left_slow.clicked.connect(self._left_slow_clicked)
        # self.ui.left_very_slow.clicked.connect(self._left_very_slow_clicked)
        # self.ui.right_very_slow.clicked.connect(self._right_very_slow_clicked)
        # self.ui.right_slow.clicked.connect(self._right_slow_clicked)
        # self.ui.right_fast.clicked.connect(self._right_fast_clicked)
        # self.ui.right_very_fast.clicked.connect(self._right_very_fast_clicked)

        # self.ui.paddle_x_spinbox.setRange(0,self.screen_width)
        self.ui.obst_x_spinbox.setRange(0,self.screen_width*2)
        self.ui.obst_fall_speed_spinbox.setRange(0,20)
        # self.ui.right_very_slow_spinbox.setRange(0,200)
        # self.ui.right_slow_spinbox.setRange(0, 200)
        # self.ui.right_fast_spinbox.setRange(0, 200)
        # self.ui.right_very_fast_spinbox.setRange(0, 200)
        # self.ui.left_very_slow_spinbox.setRange(0, 200)
        # self.ui.left_slow_spinbox.setRange(0, 200)
        # self.ui.left_fast_spinbox.setRange(0, 200)
        # self.ui.left_very_fast_spinbox.setRange(0, 200)
        self.ui.x_max_spinbox.setRange(1,1000)
        self.ui.data_num_spinbox.setRange(1,3000)
        self.ui.x_coord_factor_spinbox.setRange(100,1000)

        #game parameters:
        # paddle_x_signal = pyqtSignal(int)
        # fruit_x_signal = pyqtSignal(int)
        self.paddle_init_x = 0.25 * self.screen_width
        self.fall_speed_ratio = 20
        # paddle_x_signal.emit(self.paddle_init_x)
        self.fruit0_init_x = self.crack_init_x -(5/8) * self.screen_width
        self.fruit1_init_x = (5/8) * self.screen_width + self.crack_init_x
        # fruit_x_signal.emit(self.fruit_init_x)
        self.fruit_fall_speed = 0.05
        self.angle_speed_list = [30,50,70,90]

        # self.ui.paddle_x_spinbox.setValue(self.paddle_init_x)
        self.ui.obst_x_spinbox.setValue(self.fruit0_init_x)
        self.ui.obst_fall_speed_spinbox.setValue(self.fruit_fall_speed*self.fall_speed_ratio)
        # self.ui.left_very_fast_spinbox.setValue(self.angle_speed_list[3])
        # self.ui.left_fast_spinbox.setValue(self.angle_speed_list[2])
        # self.ui.left_slow_spinbox.setValue(self.angle_speed_list[1])
        # self.ui.left_very_slow_spinbox.setValue(self.angle_speed_list[0])
        # self.ui.right_very_fast_spinbox.setValue(self.angle_speed_list[3])
        # self.ui.right_fast_spinbox.setValue(self.angle_speed_list[2])
        # self.ui.right_slow_spinbox.setValue(self.angle_speed_list[1])
        # self.ui.right_very_slow_spinbox.setValue(self.angle_speed_list[0])
        self.ui.x_max_spinbox.setValue(15)
        self.ui.x_max_actual.setText(str(1.5))
        self.ui.data_num_spinbox.setValue(150)
        self.ui.x_coord_factor_spinbox.setValue(420)
        self.ui.right_dir_speed_spinbox.setValue(40)
        self.ui.left_dir_speed_spinbox.setValue(40)

        # self.ui.acce_a.setValue(3)
        # self.ui.acce_seconds.setValue(3)
        # self.ui.acce_curr_light_speed.setText("光速:0")

        # self.ui.acce_left_then_right.setEnabled(False)
        # self.ui.acce_right_then_left.setEnabled(False)
        self.isLeftAcceUpdate = False
        self.isRightAcceUptate = False


        self._init_ple()

    def _init_ple(self):
        # init game
        self.game = Catcher_Discrete(width=self.screen_width, height=self.screen_height,
                                     action_num=self.action_num,
                                     fruit0_init_x=self.fruit0_init_x,
                                     fruit1_init_x=self.fruit1_init_x,
                                     paddle_init_x=self.paddle_init_x,
                                    fruit_fall_speed=self.fruit_fall_speed)
        # init env
        self.env = PLE(game=self.game, fps=self.fps,
                       force_fps=self.force_fps,
                       frame_skip=self.frame_skip,
                       display_screen=self.display, num_steps=self.num_steps)
        self.env.init()
        self.env.act(self.env.NOOP)
        self.action_list = [1,2,3,4,5,6,7,8]

        self.paddle = self.game.player
        self.fruit0 = self.game.fruit0
        self.fruit1 = self.game.fruit1
        # self.fruit2 = self.game.fruit2
        self.offset_fruit = 50
        self.game.is_simple_AI = False
        self.is_simple_AI_clicked_count = 0

    def closeEvent(self, event):
        # if self.maybeSave():
        #     self.writeSettings()
            event.accept()
        # else:
        #     event.ignore()

    def _init_text_brower(self):
        self.reward = 0
        self.leaves = self.env.lives()
        self.score = self.env.score()
        self._update_text_brower(self.reward, self.leaves, self.score)

    def _update_text_brower(self, reward, leaves, score):
        self.ui.information.append("Reward:%1d, Lives_left:%2d, Score:%2d" % (reward, leaves, score))
        cursor = self.ui.information.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.ui.information.setTextCursor(cursor)

    def run_moving_instance(self):
        self.moving_instance = MovingInstance(env=self.env,
                                              side_train_times=self.RL_train_side_train_times
                                             ,time_delay_temp=self.RL_train_time_delay_temp)
        self.moving_thread = QThread()
        self.moving_thread.started.connect(self.moving_instance.update_all)
        # self.moving_instance.started_signal.connect(self.ui.)
        # self.moving_thread.finished.connect(self.ui.manual_reset)
        #get the required signals:
        self.moving_instance.paddle_x_signal.connect(self.ui.paddle_x.setText)
        self.moving_instance.paddle_y_signal.connect(self.ui.paddle_y.setText)
        self.moving_instance.fruit0_x_signal.connect(self.ui.obst1_x.setText)
        self.moving_instance.fruit0_y_signal.connect(self.ui.obst1_y.setText)
        self.moving_instance.fruit1_x_signal.connect(self.ui.obst2_x.setText)
        self.moving_instance.fruit1_y_signal.connect(self.ui.obst2_y.setText)
        self.moving_instance.fruit2_x_signal.connect(self.ui.obst3_x.setText)
        self.moving_instance.fruit2_y_signal.connect(self.ui.obst3_y.setText)
        self.moving_instance.torque_data_signal.connect(self.ui.torque_data_avg.setText)
        self.moving_instance.timer_signal.connect(self.ui.timer_display.display)
        self.moving_instance.to_update_text_signal.connect(self.to_update_text)
        self.moving_instance.fruit_rand_signal.connect(self.ui.rand_next_pos.setText)
        self.moving_instance.seq_digit_signal.connect(self.ui.seq_digit.setText)

        self.moving_thread.finished.connect(self.moving_thread.deleteLater)

        # moving the thread
        self.moving_instance.moveToThread(self.moving_thread)
        self.moving_thread.start()
        pass

    def _manual_start_clicked(self):
        # _thread.start_new_thread()
        self.set_actions_enable()
        # self._init_ple()
        self._init_text_brower()
        self.ui.manual_start.setEnabled(False)
        self.ui.manual_reset.setEnabled(True)
        # self.ui.auto_start.setEnabled(True)
        # self.ui.auto_reset.setEnabled(False)
        self.ui.pause_fruit.setEnabled(True)
        # self.paddle_init_x = self.ui.paddle_x_spinbox.value()
        self.fruit_init_x = self.ui.obst_x_spinbox.value()
        self.fruit_falling_speed = self.ui.obst_fall_speed_spinbox.value()
        # print (self.paddle_init_x, self.fruit_init_x, self.fruit_falling_speed)
        self.game.left_shift_speed = 0
        self.game.right_shift_speed = 0

        self.RL_train_time_delay_temp = 3
        self.RL_train_side_train_times = 1

        is_left = True
        is_right = False
        self.human_algo = MimicHuman(env=self.game, is_simple_AI=self.game.is_simple_AI,
                                     is_left=is_left, is_right=is_right, ui=self.ui)

        # _thread.start_new_thread(self.run_moving_instance,())
        self.moving_instance = MovingInstance(env=self.env,
                                              side_train_times=self.RL_train_side_train_times
                                             ,time_delay_temp=self.RL_train_time_delay_temp)
        self.moving_thread = QThread()
        self.moving_thread.started.connect(self.moving_instance.update_all)

        #get the required signals:
        self.moving_instance.paddle_x_signal.connect(self.ui.paddle_x.setText)
        self.moving_instance.paddle_y_signal.connect(self.ui.paddle_y.setText)
        self.moving_instance.fruit0_x_signal.connect(self.ui.obst1_x.setText)
        self.moving_instance.fruit0_y_signal.connect(self.ui.obst1_y.setText)
        self.moving_instance.fruit1_x_signal.connect(self.ui.obst2_x.setText)
        self.moving_instance.fruit1_y_signal.connect(self.ui.obst2_y.setText)
        self.moving_instance.fruit2_x_signal.connect(self.ui.obst3_x.setText)
        self.moving_instance.fruit2_y_signal.connect(self.ui.obst3_y.setText)
        self.moving_instance.torque_data_signal.connect(self.ui.torque_data_avg.setText)
        self.moving_instance.timer_signal.connect(self.ui.timer_display.display)
        self.moving_instance.to_update_text_signal.connect(self.to_update_text)
        self.moving_instance.fruit_rand_signal.connect(self.ui.rand_next_pos.setText)
        self.moving_instance.seq_digit_signal.connect(self.ui.seq_digit.setText)

        self.moving_thread.finished.connect(self.moving_thread.deleteLater)
        self.moving_instance.moveToThread(self.moving_thread)
        self.moving_thread.start()

        # self.moving_instance = MovingInstance(env=self.env,
        #                                       side_train_times=self.RL_train_side_train_times
        #                                      ,time_delay_temp=self.RL_train_time_delay_temp)
        # self.moving_thread = QThread()
        # self.moving_thread.started.connect(self.moving_instance.update_all)
        # # self.moving_instance.started_signal.connect(self.ui.)
        # # self.moving_thread.finished.connect(self.ui.manual_reset)
        # #get the required signals:
        # self.moving_instance.paddle_x_signal.connect(self.ui.paddle_x.setText)
        # self.moving_instance.paddle_y_signal.connect(self.ui.paddle_y.setText)
        # self.moving_instance.fruit0_x_signal.connect(self.ui.obst1_x.setText)
        # self.moving_instance.fruit0_y_signal.connect(self.ui.obst1_y.setText)
        # self.moving_instance.fruit1_x_signal.connect(self.ui.obst2_x.setText)
        # self.moving_instance.fruit1_y_signal.connect(self.ui.obst2_y.setText)
        # self.moving_instance.fruit2_x_signal.connect(self.ui.obst3_x.setText)
        # self.moving_instance.fruit2_y_signal.connect(self.ui.obst3_y.setText)
        # self.moving_instance.torque_data_signal.connect(self.ui.torque_data_avg.setText)
        # self.moving_instance.timer_signal.connect(self.ui.timer_display.display)
        # self.moving_instance.to_update_text_signal.connect(self.to_update_text)
        # self.moving_instance.fruit_rand_signal.connect(self.ui.rand_next_pos.setText)
        # self.moving_instance.seq_digit_signal.connect(self.ui.seq_digit.setText)
        #
        # self.moving_thread.finished.connect(self.moving_thread.deleteLater)
        #
        # # moving the thread
        # self.moving_instance.moveToThread(self.moving_thread)
        # self.moving_thread.start()

        # self.isLeftAcceUpdate = False
        # _thread.start_new_thread(self.acce_update_left,(self.isLeftAcceUpdate))
        # acce_left_process = multiprocessing.Process(target=self.acce_update_left,args=False)
        # acce_right_process = multiprocessing.Process(target=self.acce_update_right,args=False)
        # acce_left_process.start()
        # acce_left_process.join()
        # acce_right_process.start()
        # acce_right_process.join()

        # self.RL_train = AutoMethod(self.env, self.is_left_gap, self.is_right_gap)

    def _manual_reset_clicked(self):
        self.env.reset_game()
        self.env.init()
        self.env.act(self.env.NOOP)
        self.ui.information.clear()
        self._init_text_brower()

        self.ui.manual_start.setEnabled(False)
        self.ui.manual_reset.setEnabled(True)
        # self.ui.auto_start.setEnabled(True)
        # self.ui.auto_reset.setEnabled(False)
        self.moving_instance.time_start = time.time()

    def set_actions_enable(self):
        # self.ui.paddle_x_1.setEnabled(True)
        # self.ui.paddle_x_2.setEnabled(True)
        # self.ui.paddle_x_3.setEnabled(True)
        # self.ui.paddle_x_4.setEnabled(True)
        # self.ui.paddle_x_5.setEnabled(True)
        # self.ui.paddle_x_6.setEnabled(True)
        # self.ui.paddle_x_7.setEnabled(True)
        # self.ui.paddle_x_8.setEnabled(True)

        # self.ui.left_very_slow.setEnabled(True)
        # self.ui.left_slow.setEnabled(True)
        # self.ui.left_fast.setEnabled(True)
        # self.ui.left_very_fast.setEnabled(True)
        #
        # self.ui.right_very_slow.setEnabled(True)
        # self.ui.right_slow.setEnabled(True)
        # self.ui.right_fast.setEnabled(True)
        # self.ui.right_very_fast.setEnabled(True)

        # self.ui.action_9.setEnabled(True)
        # self.ui.action_10.setEnabled(True)
        # self.ui.action_11.setEnabled(True)
        # self.ui.action_12.setEnabled(True)
        # self.ui.action_13.setEnabled(True)
        # self.ui.action_14.setEnabled(True)
        # self.ui.action_15.setEnabled(True)
        # self.ui.action_16.setEnabled(True)
        # self.ui.action_17.setEnabled(True)
        # self.ui.action_18.setEnabled(True)
        # self.ui.action_19.setEnabled(True)
        # self.ui.action_20.setEnabled(True)
        pass

    @pyqtSlot()
    def on_obst_x_spinbox_editingFinished(self):
        self.game.fruit0_init_x = self.ui.obst_x_spinbox.value()
        self.game.fruit1_init_x = self.ui.obst_x_spinbox.value()
        self.game.fruit0.reset_manually(self.ui.obst_x_spinbox.value(),0)
        self.game.fruit1.reset_manually(self.ui.obst_x_spinbox.value(),0)

    @pyqtSlot()
    def on_paddle_x_spinbox_editingFinished(self):
        self.game.player.set_paddle_x(self.ui.paddle_x_spinbox.value())

    @pyqtSlot()
    def on_obst_fall_speed_spinbox_editingFinished(self):
        self.game.fruit0.set_fruit_fall_speed(self.ui.obst_fall_speed_spinbox.value()/self.fall_speed_ratio)
        self.game.fruit1.set_fruit_fall_speed(self.ui.obst_fall_speed_spinbox.value()/self.fall_speed_ratio)

    # @pyqtSlot()
    # def on_left_very_fast_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.left_very_fast_spinbox.value(),1)
    #
    # @pyqtSlot()
    # def on_left_fast_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.left_fast_spinbox.value(),1)
    #
    # @pyqtSlot()
    # def on_left_slow_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.left_slow_spinbox.value(),1)
    #
    # @pyqtSlot()
    # def on_left_very_slow_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.left_very_slow_spinbox.value(),1)
    #
    # @pyqtSlot()
    # def on_right_very_fast_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.right_very_fast_spinbox.value(),2)

    # @pyqtSlot()
    # def on_right_fast_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.right_fast_spinbox.value(),2)
    #
    # @pyqtSlot()
    # def on_right_slow_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.right_slow_spinbox.value(),2)
    #
    # @pyqtSlot()
    # def on_right_very_slow_spinbox_editingFinished(self):
    #     self.game._action_lightStream_map(self.ui.right_very_slow_spinbox.value(),2)

    @pyqtSlot()
    def on_x_max_spinbox_editingFinished(self):
        self.moving_instance.parameter_div = self.ui.x_max_spinbox.value()/10
        self.ui.x_max_actual.setText(str(self.moving_instance.parameter_div))

    @pyqtSlot()
    def on_data_num_spinbox_editingFinished(self):
        self.moving_instance.data_num = self.ui.data_num_spinbox.value()

    @pyqtSlot()
    def on_x_coord_factor_editingFinished(self):
        self.moving_instance.x_coord_factor = self.ui.x_coord_factor_spinbox.value()

    @pyqtSlot()
    def on_left_dir_speed_spinbox_editingFinished(self):
        self.game._action_single_screen(self.ui.left_dir_speed_spinbox.value(), "left")

    @pyqtSlot()
    def on_right_dir_speed_spinbox_editingFinished(self):
        self.game._action_single_screen(self.ui.right_dir_speed_spinbox.value(), "right")

    @pyqtSlot()
    def on_reset_all_clicked(self):
        self.game._action_single_screen(0,"reset_all")

    @pyqtSlot()
    def on_stop_all_clicked(self):
        self.game._action_single_screen(0,"stop_all")

    @pyqtSlot()
    def on_left_fruit_appear_clicked(self):
        #crack = 2/8
        self.game.fruit0_init_x = -3/8 * self.screen_width #215
        self.game.fruit1_init_x = 7/8 * self.screen_width  # 215
        self.game.fruit0.reset_manually(self.game.fruit0_init_x, 0)
        self.game.fruit1.reset_manually(self.game.fruit1_init_x ,0)
        # self.ui.obst_x_spinbox.setValue(self.game.fruit1_init_x)
        self.ui.rand_next_pos.setText("人工模式:左")
        # self.ui.rand_next_pos.setEnabled(True)
        self.game.is_random = False
        self.game.is_sequence = False
        self.is_left_gap = True
        self.is_right_gap = False

    @pyqtSlot()
    def on_middle_fruit_appear_clicked(self):
        #crack = 4/8
        self.game.fruit0_init_x = -1 / 8 * self.screen_width  # 215
        self.game.fruit1_init_x = 9 / 8 * self.screen_width  # 215
        self.game.fruit0.reset_manually(self.game.fruit0_init_x, 0)
        self.game.fruit1.reset_manually(self.game.fruit1_init_x, 0)
        # self.ui.obst_x_spinbox.setValue(self.game.fruit1_init_x)
        self.ui.rand_next_pos.setText("人工模式:中间")
        # self.ui.rand_next_pos.setEnabled(True)
        self.game.is_random = False
        self.game.is_sequence = False

        self.is_left_gap = False
        self.is_right_gap = False

    @pyqtSlot()
    def on_right_fruit_appear_clicked(self):
        #crack = 6/8
        self.game.fruit0_init_x = 1 / 8 * self.screen_width  # 215
        self.game.fruit1_init_x = 11 / 8 * self.screen_width  # 215
        self.game.fruit0.reset_manually(self.game.fruit0_init_x, 0)
        self.game.fruit1.reset_manually(self.game.fruit1_init_x, 0)
        # self.ui.obst_x_spinbox.setValue(self.game.fruit1_init_x)
        self.ui.rand_next_pos.setText("人工模式:右")
        # self.ui.rand_next_pos.setEnabled(True)
        self.game.is_random = False
        self.game.is_sequence = False

        self.is_left_gap = False
        self.is_right_gap = True

    @pyqtSlot()
    def on_fruit_fall_random_clicked(self):
        self.game.is_random = True
        self.game.is_sequence = False
        self.game.fruit_offset = self.offset_fruit
        self.ui.rand_next_pos.setText("随机模式")
        # self.ui.rand_next_pos.setEnabled(False)

    @pyqtSlot()
    def on_pause_fruit_clicked(self):
        if self.ui.pause_fruit.text() == "暂停":
            self.game_fruit_speed = self.game.fruit0.speed
            self.game.fruit0.speed = 0
            self.game.fruit1.speed = 0
            self.ui.pause_fruit.setText("继续")
        else:
            self.game.fruit0.speed = self.game_fruit_speed
            self.game.fruit1.speed = self.game_fruit_speed
            self.ui.pause_fruit.setText("暂停")

    @pyqtSlot()
    def on_single_left_shift_clicked(self):
        temp = self.ui.left_dir_speed_spinbox.value()
        self.game._action_single_screen(temp, "left")
        # time.sleep(self.command_delay)
        self.game._action_single_screen(temp, "left")
        # time.sleep(self.command_delay)
        # self.game._action_single_screen(self.game.left_shift_speed, "left")
        self.game.left_shift_speed = temp
        self.game.right_shift_speed = 0

    @pyqtSlot()
    def on_single_right_shift_clicked(self):
        temp = self.ui.right_dir_speed_spinbox.value()
        self.game._action_single_screen(temp, "right")
        # time.sleep(self.command_delay)
        self.game._action_single_screen(temp, "right")
        # time.sleep(self.command_delay)
        # self.game._action_single_screen(self.game.right_shift_speed, "right")
        self.game.right_shift_speed = temp
        self.game.left_shift_speed = 0

    @pyqtSlot()
    def on_fruit_fall_sequence_editingFinished(self):
        self.game.is_sequence = True
        self.game.seq_i = 0
        self.game.seq_msg = self.ui.fruit_fall_sequence.text()
        self.ui.rand_next_pos.setText("序列模式")
        self.ui.sequence_display.setText(self.game.seq_msg[0:len(self.game.seq_msg)-1])

    @pyqtSlot()
    def on_simple_AI_clicked(self):
        if self.is_simple_AI_clicked_count == 0:
            self.ui.AI_mode.setText("模拟人工 模式")
            self.ui.simple_AI.setText("暂停")
            self.is_RL_test = False

            self.is_RL_train = False
            self.ui.RL_test.setEnabled(True)
            self.ui.RL_train.setEnabled(True)

            self.game.is_simple_AI = True
            self.human_algo.run_thread()

            self.is_simple_AI_clicked = False
            self.is_simple_AI_clicked_count += 1

        else:
            if self.is_simple_AI_clicked == True:
                self.human_algo.is_paused = False
                self.ui.simple_AI.setText("暂停")
                self.ui.AI_mode.setText("running...")
                self.is_simple_AI_clicked = False

            elif self.is_simple_AI_clicked == False:
                self.human_algo.is_paused = True
                self.human_algo.step -= 1
                self.ui.simple_AI.setText("继续")
                self.ui.AI_mode.setText("Paused")
                self.is_simple_AI_clicked = True

    @pyqtSlot()
    def on_RL_train_clicked(self):
        self.ui.AI_mode.setText("自动调参中...")
        # self.auto_method = AutoMethod(self.env, self.is_left_gap, self.is_right_gap)
        self.is_RL_train_run = True
        self.ui.simple_AI.setEnabled(True)
        self.ui.RL_train.setEnabled(False)
        self.ui.RL_test.setEnabled(True)

        self.game.is_simple_AI = False
        self.is_RL_train = True
        self.is_RL_test = False

        self.RL_train_thread = QThread()
        self.RL_train_time_delay_temp = 3
        self.RL_train_side_train_times = 1
        self.RL_train = AutoMethod( env=self.env, is_RL_train=self.is_RL_train,
                                    side_train_times = self.RL_train_side_train_times,
                                    time_delay_temp=self.RL_train_time_delay_temp
                                    )
        self.RL_train_thread.started.connect(self.RL_train.update_RL)
        # a
        self.RL_train.left_stream_change_signal.connect(self.ui.RL_left_display.setText)
        # self.RL_train.left_stream_change_signal.connect(self.env.game.left_shift_speed)
        self.RL_train.right_stream_change_signal.connect(self.ui.RL_right_display.setText)
        # self.RL_train.right_stream_change_signal.connect(self.env.game.right_shift_speed)
        #
        self.RL_train_thread.finished.connect(self.RL_train_thread.deleteLater)
        #
        self.RL_train.moveToThread(self.RL_train_thread)
        # self.RL_train_thread.setTerminationEnabled(True)
        self.RL_train_thread.start()

        # p2 = multiprocessing.Process(target=self.RL_train.run,args=())
        # p2.start()

        # p.start()
        # self.RL_train_process = multiprocessing.Process(target=self.RL_train.linear_test, args=())
        # self.RL_train_process.start()
        # self.RL_test_process.join()
        # self.RL_train.left_stream_change_signal.connect(self.ui.RL_left_display.setText)
        # self.RL_train.right_stream_change_signal.connect(self.ui.RL_right_display.setText)

        # self.ui.right_fast_spinbox.setValue(10)
        # self.ui.left_fast_spinbox.setValue(10)
        print("training...")

    @pyqtSlot()
    def on_RL_test_clicked(self):
        self.ui.AI_mode.setText("自动避障中...")
        self.ui.simple_AI.setEnabled(True)
        self.ui.RL_train.setEnabled(True)
        self.ui.RL_test.setEnabled(False)

        self.game.is_simple_AI = False
        self.RL_train.is_RL_train = False
        self.is_RL_test = True

        self.is_left_gap = True
        self.is_right_gap = False

        print("testing....")

    @pyqtSlot()
    def on_stop_recording_clicked(self):
        # self.data_record.stop_recording()
        self.moving_instance.is_recording = False
        self.moving_instance.stop_recording()
        self.ui.start_recording.setEnabled(True)
        self.ui.stop_recording.setEnabled(False)
        self.ui.recording_status.setText("记录完成！文件：" + self.moving_instance.file_name)
        pass

    @pyqtSlot()
    def on_start_recording_clicked(self):
        self.moving_instance.is_recording = True
        self.ui.start_recording.setEnabled(False)
        self.ui.stop_recording.setEnabled(True)
        self.ui.recording_status.setText("记录中。。。")
        # self.record_interval = 50 #in ms
        self.moving_instance.data = []
        self.moving_instance.start_time = time.time()
        self.moving_instance.start_recording()
        self.moving_instance.is_first_time = False
        #
        # self.data_record_thread = QThread()
        # self.data_record = DataRecord(env=self.env)
        # self.data_record_thread.started.connect(self.data_record.run)
        # self.data_record_thread.finished.connect(self.data_record_thread.deleteLater)
        # self.data_record.moveToThread(self.data_record_thread)
        # self.data_record_thread.start()
        pass

    @pyqtSlot()
    def on_acce_left_start_clicked(self):
        self.left_speed_count = 0
        self.acce_a = self.ui.acce_a.value()
        self.acce_seconds = self.ui.acce_seconds.value()
        self.isInterchange = False

        self.game.right_shift_speed = 0

        self.game.isToLeft = True
        self.game.isToRight = False
        self.ui.acce_left_start.setEnabled(False)
        self.ui.acce_right_start.setEnabled(True)
        print("left!")
        # self.acce_update_left(True)
        # self.acce_update_right(False)
        pass

    @pyqtSlot()
    def on_acce_right_start_clicked(self):
        self.right_speed_count = 0
        self.moving_instance.acce_a = self.ui.acce_a.value()
        self.moving_instance.acce_seconds = self.ui.acce_seconds.value()
        self.isInterchange = False

        self.game.isToLeft = False
        self.game.isToRight = True
        self.game.left_shift_speed = 0
        self.ui.acce_left_start.setEnabled(True)
        self.ui.acce_right_start.setEnabled(False)
        # self.acce_update_left(False)
        # self.acce_update_right(True)
        print ("right!")
        pass

    @pyqtSlot()
    def on_acce_left_then_right_clicked(self):
        self.acce_a = self.ui.acce_a.value()
        self.acce_seconds = self.ui.acce_seconds.value()
        self.isInterchange = True

        while self.isInterchange:
            self.acce_update_left(True)
            self.acce_update_right(False)
            self.acce_update_right(True)
            self.acce_update_left(False)
        pass

    @pyqtSlot()
    def on_acce_right_then_left_clicked(self):
        self.acce_a = self.ui.acce_a.value()
        self.acce_seconds = self.ui.acce_seconds.value()
        self.isInterchange = True

        while self.isInterchange:
            self.acce_update_left(False)
            self.acce_update_right(True)
            self.acce_update_right(False)
            self.acce_update_left(True)
        pass

    @pyqtSlot()
    def on_acce_seconds_editingFinished(self):
        self.game.acce_a = self.ui.acce_a.value()
        self.game.acce_sec = self.ui.acce_seconds.value()
        pass

    @pyqtSlot()
    def on_acce_a_editingFinished(self):
        self.game.acce_a = self.ui.acce_a.value()
        self.game.acce_sec = self.ui.acce_seconds.value()

        pass

    def to_update_text(self):
        # if self.moving_instance.to_update_text_signal == True:
        self.reward = self.env.act(self.env.NOOP)
        self.score = self.env.score()
        self.leaves = self.env.lives()
        self._update_text_brower(self.reward, self.leaves, self.score)
        self.moving_instance.catcher_game.to_update_text = 0

    # def acce_update_left(self,isToLeft):
    #     if isToLeft:
    #         self.left_last = time.time()
    #         speed = 30
    #         while speed < 95:
    #             if isToLeft and (time.time()- self.left_last> self.acce_seconds):
    #                 self.game.left_shift_speed = speed
    #                 self.game._action_single_screen(self.game.left_shift_speed, "left")
    #                 self.ui.acce_curr_light_speed.setText("左光流: ",speed)
    #                 self.left_last = time.time()
    #                 speed += self.acce_a
    #             if speed > 100:
    #                 speed = 30
    #     pass
    #
    # def acce_update_right(self,isToRight):
    #     if isToRight:
    #         self.right_last = time.time()
    #         for speed in range(30,96,self.acce_a):
    #             if isToRight and (time.time() - self.right_last > self.acce_seconds):
    #                 self.game.right_shift_speed = speed
    #                 self.game._action_single_screen(self.game.right_shift_speed, "right")
    #                 self.ui.acce_curr_light_speed.setText("右光流: ", speed)
    #                 self.right_last = time.time()
    #     pass
    #
    # def acce_update_alternative(self,isAlternating,isToAlter):
    #     self.alter_last_left = time.time()
    #     self.alter_last_right = time.time()
    #     while isAlternating:
    #         for speed in range(30,96,self.acce_a):
    #             if isToAlter and (self.alter_last_left - time.time() > self.acce_seconds):
    #                 self.game.left_shift_speed = speed
    #                 self.game._action_single_screen(self.game.left_shift_speed, "left")
    #                 self.ui.acce_curr_light_speed.setText("左光流: ", speed)
    #                 self.alter_last_left = time.time()
    #             if isToAlter and (self.alter_last_right - time.time() > self.acce_seconds):
    #                 self.game.right_shift_speed = speed
    #                 self.game._action_single_screen(self.game.right_shift_speed, "right")
    #                 self.ui.acce_curr_light_speed.setText("右光流: ", speed)
    #                 self.alter_last_right = time.time()
    #     pass

class MovingInstance(QObject):
    started_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    paddle_x_signal = pyqtSignal(str)
    paddle_y_signal = pyqtSignal(str)
    fruit0_x_signal = pyqtSignal(str)
    fruit0_y_signal = pyqtSignal(str)
    fruit1_x_signal = pyqtSignal(str)
    fruit1_y_signal = pyqtSignal(str)
    fruit2_x_signal = pyqtSignal(str)
    fruit2_y_signal = pyqtSignal(str)
    fruit_rand_signal = pyqtSignal(str)
    seq_digit_signal = pyqtSignal(str)
    left_stream_change_signal = pyqtSignal(int)
    right_stream_change_signal = pyqtSignal(int)

    torque_data_signal = pyqtSignal(str)
    timer_signal = pyqtSignal(int)

    to_update_text_signal = pyqtSignal()

    def __init__(self,env,side_train_times,time_delay_temp):
        super(MovingInstance,self).__init__()
        self.env = env
        self.catcher_game = self.env.game

        self.catcher_game.init() #get paddle, Fruit0~3

        self.paddle = self.catcher_game.player
        self.fruit0 = self.catcher_game.fruit0

        self.parameter_div = 1.5
        self.data_num = 100
        self.x_coord_factor = 430
        self.time_delay_temp = time_delay_temp
        self.side_train_times = side_train_times

        self.time_start = time.time()

        self.data_mapped = 0
        self.light_stream_change_signal = 0
        self.record_interval = 1
        self.data = []
        self.start_time = time.time()
        self.is_recording = False
        self.is_first_time = True

        self.catcher_game.isToLeft = False
        self.catcher_game.isToRight = False
        self.acce_a = 3
        self.acce_seconds = 3

        # self.is_recording = False
        # self.fruit1 = self.catcher_game.fruit1
        # self.fruit2 = self.catcher_game.fruit2

    def update_all(self):
        #self._data.clear()
        # self.started_signal.emit()
        _thread.start_new_thread(self.linear_update, ())
        # _thread.start_new_thread(self.acce_update,())
        # _thread.start_new_thread(self.linear_test, ())
        self.start_recording()
        while True:
            # self.fruit0.set_init_x()
            # self.catcher_game.set_fruit_init_x(self.fruit0.)
            self.game_state = self.catcher_game.getGameState()  # return: state
            self.paddle_x = self.game_state["player_x"]
            self.paddle_y = self.game_state["player_y"]
            # self.fruit0_x.set_fruit_x(fruit_x)
            self.fruit0_x = self.game_state["fruit0_x"]
            self.fruit0_y = self.game_state["fruit0_y"]
            self.to_update_text = self.game_state["to_update_text"]
            seq_digit_i = self.catcher_game.seq_i
            seq_length = len(self.catcher_game.seq_msg)
            i = 0
            self.res = ""
            while i < seq_length:
                if i == seq_digit_i:
                    self.res += "_"
                else:
                    self.res += " "
                i += 1
            # self.fruit_rand_pos = self.game_state["fruit_rand_pos"]
            # self.fruit1_x = str(self.game_state["fruit1_x"])
            # self.fruit1_y = str(self.game_state["fruit1_y"])
            # self.fruit2_x = str(self.game_state["fruit2_x"])
            # self.fruit2_y = str(self.game_state["fruit2_y"])
            self.paddle_x_signal.emit(str(self.paddle_x))
            self.paddle_y_signal.emit(str(self.paddle_y))
            self.fruit0_x_signal.emit(str(self.fruit0_x))
            self.fruit0_y_signal.emit(str(self.fruit0_y))
            self.seq_digit_signal.emit(self.res)
            # if self.fruit0_x == 215 + self.catcher_game.fruit_offset:
            #     self.fruit_rand_signal.emit("左")
            # elif self.fruit0_x == 645 - self.catcher_game.fruit_offset:
            #     self.fruit_rand_signal.emit("右")

            if self.to_update_text == 1:
                self.to_update_text_signal.emit()
                self.catcher_game.to_update_text = 0
            # self.fruit1_x_signal.emit(self.fruit2_x)
            # self.fruit1_y_signal.emit(self.fruit2_y)
            # self.fruit2_x_signal.emit(self.fruit3_x)
            # self.fruit2_y_signal.emit(self.fruit3_y)
            self.env.act(self.env.NOOP)
            #getting data from torque instrument:
            # data_mapped = self.linear_update()
            # print(data_mapped)
            # self.catcher_game.player.set_paddle_x(self.data_mapped)
            time_end = time.time()
            if time_end != self.time_start:
                self.timer_signal.emit(int(time_end - self.time_start))
            # time.sleep(0.01)

            #*********************DATA-RECORDING below*****************
            self.recording()

            # self.acce_update(isLeft=True)
        pass

    def acce_update(self):
        # self.isToLeft = self.catcher_game.isToLeft
        # self.isToRight = self.catcher_game.isToRight
        while True:
            if self.catcher_game.isToLeft:
                self.left_last = time.time()
                speed = 30
                while speed < 95:
                    if self.catcher_game.isToLeft == False:
                        break
                    if self.catcher_game.isToLeft and (time.time()- self.left_last> self.catcher_game.acce_sec):
                        self.catcher_game.left_shift_speed = speed
                        self.catcher_game._action_single_screen(speed, "left")
                        # self.ui.acce_curr_light_speed.setText("左光流: ",speed)
                        print(speed)
                        # print(self.catcher_game.right_shift_speed)
                        self.left_last = time.time()
                        speed += self.catcher_game.acce_a
                    if speed > 90:
                        speed = 30
            if self.catcher_game.isToRight:
                self.right_last = time.time()
                speed = 30
                while speed < 95:
                    if self.catcher_game.isToRight == False:
                        break
                    if self.catcher_game.isToRight and (time.time() - self.right_last > self.catcher_game.acce_sec):
                        self.catcher_game.right_shift_speed = speed
                        self.catcher_game._action_single_screen(speed, "right")
                        # self.ui.acce_curr_light_speed.setText("左光流: ",speed)
                        print(speed)
                        # print(self.catcher_game.left_shift_speed)
                        self.right_last = time.time()
                        speed += self.catcher_game.acce_a
                    if speed > 90:
                        speed = 30

    def recording(self):
        self.start_recording()
        if (not self.is_first_time) and (not self.is_recording):
            self.stop_recording()
            self.is_recording = True

    def start_recording(self):
        # self.data = []
        # self.self.start_time = time.time()
        # self.is_first_time = False
        if self.is_recording:
            time_diff_curr = time.time()-self.start_time
            time_diff = time_diff_curr * 1000
            time_diff_compare = int(time_diff)
            if time_diff_compare % self.record_interval == 0:  # re

                time_diff = round(time_diff_curr, 4)  ###

                left_light_stream = self.catcher_game.left_shift_speed  ###
                right_light_stream = self.catcher_game.right_shift_speed  ###

                game_state = self.catcher_game.getGameState()
                bee_pos_x = game_state["player_x"]  ###

                #Zone calculation: -3, -2, -1, 0, 1, 2, 3
                delta_volt = self.parameter_div / 4
                self.zone_num = 0
                self.state = self.catcher_game.getGameState()
                self.player_x = self.data_to_avg
                if self.player_x < (0-delta_volt) and self.player_x >= (0-delta_volt*2):
                    self.zone_num = -1
                if self.player_x < (0-delta_volt*2) and self.player_x >= (0-delta_volt*3):
                    self.zone_num = -2
                if self.player_x < (0-delta_volt*3) and self.player_x >= (0-delta_volt*4):
                    self.zone_num = -3
                if self.player_x > (delta_volt) and self.player_x <= (delta_volt*2):
                    self.zone_num = 1
                if self.player_x > (delta_volt*2) and self.player_x <= (delta_volt*3):
                    self.zone_num = 2
                if self.player_x > (delta_volt*3) and self.player_x <= (delta_volt*4):
                    self.zone_num = 3
                # else:
                #     self.zone_num = 0


                try:
                    # temp = self.catcher_game._reader.get_slide_num_data(100, 30)
                    torque_data = round(self.data_to_avg,5)  ###
                except:
                    print("请连接扭矩仪")
                    torque_data = 0
                    time.sleep(2)
                # self.side_train_times = side_train_times
                # self.time_delay_temp = time_delay_temp
                curr_data =     [time_diff, left_light_stream, right_light_stream, bee_pos_x,
                                torque_data,self.parameter_div
                                ,self.side_train_times,self.time_delay_temp
                                ,self.zone_num,self.acce_a,self.acce_seconds
                                ]

                self.data.append(curr_data)
            # time.sleep(0.02)

    def stop_recording(self):
        self.df = pd.DataFrame(self.data, columns=["时间", "光流左", "光流右", "熊蜂x",
                                                   "扭矩","最大参数"
                                                    ,"每边更新次数","每次持续时间"
                                                    ,"区域", "acce_a", "acce_seconds"
                                                   ])

        local_time = time.localtime(int(time.time()))
        time_format = "%Y-%m-%d %Hh-%Mm-%Ss"
        self.file_name = "./data/" + str(time.strftime(time_format, local_time)) + ".csv"
        (self.df).to_csv(self.file_name)

    def linear_update(self):
        while True:
            # data = self.catcher_game._reader.get_num_data(self.data_num)  # get 100 data
            data = self.catcher_game._reader.get_slide_num_data(self.data_num, 40)
            data_avg = np.average(data)  # cal their average
            self.data_to_avg = data_avg
            self.torque_data_signal.emit(str(data_avg))
            # data_avg -= 0.015
            data_para = (-1)*data_avg / self.parameter_div  # divided by the parameter(5 in this case)
            # print ("data is :",data_para)
            # map the data onto the coordinate
            self.data_mapped = data_para * self.x_coord_factor
            self.data_mapped += 430
            self.catcher_game.player.set_paddle_x(self.data_mapped)
            # self.catcher_game.player.set_paddle_angle(
            #     int(data_avg * -2.5)
            # )
            # print (self.data_mapped)
        # return data_mapped

class AutoMethod(QObject):
    right_stream_change_signal = pyqtSignal(str)
    right_shift_speed_signal = pyqtSignal(int)
    left_stream_change_signal = pyqtSignal(str)
    left_shift_speed_signal = pyqtSignal(int)
    # msg_from_job = pyqtSignal(int)

    def __init__(self,env,is_RL_train,side_train_times, time_delay_temp):
        super(AutoMethod, self).__init__()
        self.game = env.game
        self.stop_flag = False
        self.is_left_side = False
        self.is_right_side = True
        self.counter = 0

        #User-defined Variable
        self.side_train_times = side_train_times
        self.game.left_shift_speed = 30
        self.game.right_shift_speed = 30
        self.time_delay_temp = time_delay_temp
        self.speed_limit = 100

        self.left_x_before = 0
        self.right_x_before = 0
        self.is_RL_train = is_RL_train

    def update_RL(self):
        _thread.start_new_thread(self.run, ())

    def left_side_learn(self,light_ratio):
            if self.left_x_before == 0:
                self.game_state = self.game.getGameState()
                self.paddle_x = self.game_state["player_x"]
            else:
                self.paddle_x = self.left_x_before

            if self.paddle_x < 5:
                self.paddle_x = 5
            elif self.paddle_x > 855:
                self.paddle_x = 855
            # print(self.paddle_x)
            x_diff_left = self.paddle_x - 215
            delta_light_left = self.light_ratio * x_diff_left
            # if the x coord exceeds the limit, get it back

            # auto-update algorithm
            if self.paddle_x >= 160 and self.paddle_x <= 230:
                self.delta_light_left = 0
            elif self.paddle_x < 160:
                delta_light_left = self.light_ratio * x_diff_left

            self.game.left_shift_speed += delta_light_left
            if self.game.left_shift_speed <= 0:
                self.game.left_shift_speed = 0
            if self.game.left_shift_speed >= self.speed_limit:
                    self.game.left_shift_speed = self.speed_limit

            self.game.left_shift_speed = int(self.game.left_shift_speed)
            print("left: ", self.game.left_shift_speed)

            self.game._action_single_screen(self.game.left_shift_speed, "left")
            self.left_stream_change_signal.emit("左侧: " + str(self.game.left_shift_speed))

            time.sleep(self.time_delay_temp)

            self.game_state = self.game.getGameState()
            self.left_x_before = self.game_state["player_x"]

            # return self.left_shift_speed

    def right_side_learn(self,light_ratio):

            if self.right_x_before == 0:
                self.game_state = self.game.getGameState()
                self.paddle_x = self.game_state["player_x"]
            else:
                self.paddle_x = self.right_x_before

            if self.paddle_x < 5:
                self.paddle_x = 5
            elif self.paddle_x > 855:
                self.paddle_x = 855
            x_diff_right = 645 - self.paddle_x
            delta_light_right = self.light_ratio * x_diff_right
            # if the x coord exceeds the limit, get it back

            # auto-update algorithm
            if self.paddle_x >= 600 and self.paddle_x <= 690:
                delta_light_right = 0
            elif self.paddle_x < 600:
                delta_light_right = self.light_ratio * x_diff_right
            self.game.right_shift_speed += delta_light_right
            if self.game.right_shift_speed >= self.speed_limit:
                self.game.right_shift_speed = self.speed_limit
            if self.game.right_shift_speed <= 0:
                self.game.right_shift_speed = 0

            self.game.right_shift_speed = int(self.game.right_shift_speed)
            print("right: ", self.game.right_shift_speed)

            self.game._action_single_screen(self.game.right_shift_speed, "right")
            self.right_stream_change_signal.emit("右侧：" + str(self.game.right_shift_speed))

            time.sleep(self.time_delay_temp)
            self.game_state = self.game.getGameState()
            self.right_x_before = self.game_state["player_x"]

            # return self.right_shift_speed

    def run(self):
        self.light_ratio = 0.09
        self.game.left_shift_speed = 30
        self.game.right_shift_speed = 30
        # is_RL_train = True
        # self.left_track = []
        # self.game = self.catcher_game
        # self.counter = 0
        while self.is_RL_train:
            if self.counter % (self.side_train_times+1) == 0: # switch side
                if self.is_left_side:
                    self.is_left_side = False
                    self.is_right_side = True
                    self.counter += 1
                    # self.right_side_learn(self.light_ratio)
                else:
                    self.is_right_side = False
                    self.is_left_side = True
                    self.counter += 1
                    # self.left_side_learn(self.light_ratio)
            else:
                if self.is_left_side:
                    self.left_side_learn(self.light_ratio)
                    self.left_shift_speed_signal.emit(self.game.left_shift_speed)
                    self.right_shift_speed_signal.emit(self.game.right_shift_speed)
                    self.counter += 1
                if self.is_right_side:
                    self.right_side_learn(self.light_ratio)
                    self.left_shift_speed_signal.emit(self.game.left_shift_speed)
                    self.right_shift_speed_signal.emit(self.game.right_shift_speed)
                    self.counter += 1

        # while True:
        #     # while self.is_left_gap:
        #     self.game_state = self.game.getGameState()
        #     self.paddle_x = self.game_state["player_x"]
        #     x_diff_left = self.paddle_x - 215
        #     delta_light_left = self.light_ratio * x_diff_left
        #     # if the x coord exceeds the limit, get it back
        #     if self.paddle_x < 10:
        #         self.paddle_x = 20
        #     elif self.paddle_x > 850:
        #         self.paddle_x = 840
        #     # auto-update algorithm
        #     if self.paddle_x > 160 and self.paddle_x < 230:
        #         self.delta_light_left = 0
        #     elif self.paddle_x < 160:
        #         delta_light_left = self.light_ratio * x_diff_left
        #     self.left_shift_speed += delta_light_left
        #     self.left_shift_speed = int(self.left_shift_speed)
        #     # self.left_track.append(self.left_shift_speed)
        #     print(self.left_shift_speed)
        #     self.game._action_single_screen(self.left_shift_speed, "left")
        #     # self.ui.RL_left_display.setText(str(self.left_shift_speed))
        #     if self.left_shift_speed > 120:
        #         self.left_shift_speed = 120
        #     self.left_stream_change_signal.emit(str(self.left_shift_speed))
        #     time.sleep(1)

            # while self.is_right_gap == True:
            #     x_diff_right = abs(self.paddle_x - 645)
            #     delta_light_right = self.light_ratio * x_diff_right
            #     self.right_shift_speed += delta_light_right
            #     self.right_shift_speed = int(self.right_shift_speed)
            #     if self.right_shift_speed > 100:
            #         self.right_shift_speed = 70
            #     self.game._action_single_screen(self.right_shift_speed, "right")
            #     # self.ui.right_dir_speed_spinbox.setValue(int(self.right_shift_speed))
            #     self.right_stream_change_signal.emit(str(self.right_shift_speed))
            #     time.sleep(4)
            #
            # while self.is_middle_gap == True:
            #     self.game._action_single_screen(0, "left")
            #     time.sleep(0.01)
            #     # self.game._action_single_screen(0, "right")
            #     self.light_stream_change_signal.emit(0)
            #     time.sleep(4)

class MimicHuman(QObject):

    def __init__(self,env,is_simple_AI,is_left,is_right,ui):
        self.game = env
        self.temp = [i for i in range(0, 86001, int(86000 / 16))]
        for i in range(len(self.temp)):
            self.temp[i] /= 100
        self.is_left = True
        self.is_right = False
        self.game.is_simple_AI = is_simple_AI
        self.ui = ui
        self.is_left = is_left
        self.is_right = is_right

        self.sec_delay = 3  # seconds
        self.SHIFT_TIME = 2
        self.step = 0
        self.case = 0
        self.osci_bound = 5
        self.samp_period = 0.1  # seconds

        self.is_paused = False

        self.is_end = False

    def shift_with_delay(self,delay_time,direction,speed):
        start = time.time()
        if int(time.time() - start) >= shift_time:
            self.game._action_single_screen(speed, direction)
            self.ui.AI_mode.setText(direction,speed)
        start = time.time()
        if int(time.time() - start) >= shift_time:
            self.game._action_single_screen(speed, direction)
            self.ui.AI_mode.setText(direction,speed)

    def oscillation(self,osci_time,step_num):
        self.x_move_region = []
        self.start_time = time.time()
        while (self.step == step_num):
            if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                self.x_move_region.append(self.game.get_states("player_x"))
                self.avg_x_move = np.average(self.x_move_region)
                if int(time.time() - self.start_time) >= osci_time:
                    self.step += 1
                    break

    def oscillation_region(self,region,osci_time,step_num):
        self.x_move_region = []
        self.avg_x_move = np.average([self.temp[region[0]], self.temp[region[1]] ])
        self.start_time = time.time()
        self.left_bound = self.temp[region[1]] - self.osci_bound
        self.right_bound = self.temp[region[0]] + self.osci_bound
        while (self.step == step_num) and (self.avg_x_move<=self.right_bound) and \
                (self.avg_x_move>=self.left_bound) :
            if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                self.x_move_region.append(self.game.get_states("player_x"))
                self.avg_x_move = np.average(self.x_move_region)
                if int(time.time() - self.start_time) >= osci_time:
                    self.step += 1
                    break

    def oscillation_line(self,line_num,osci_time,step_num):
        # self.game._action_single_screen(speed,direction)
        # self.ui.AI_mode.setText(direction,speed)
        line_num = int(line_num)
        self.left_bound = np.average([self.temp[line_num-1], self.temp[line_num]]) - self.osci_bound
        self.right_bound = np.average([self.temp[line_num], self.temp[line_num+1]]) + self.osci_bound
        self.avg_x_move = np.average([self.left_bound, self.right_bound])
        self.start_time = time.time()
        self.x_move_region = []
        while (self.avg_x_move <= self.right_bound) and \
                (self.avg_x_move >= self.left_bound) and (self.step == step_num):
            if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                self.x_move_region.append(self.game.get_states("player_x"))
                self.avg_x_move = np.average(self.x_move_region)
            if int(time.time() - self.start_time) >= osci_time:
                self.step += 1
                break

    def oscillation_pass(self,line_num,left_or_right,osci_time,step_num):
        self.start_time = time.time()
        self.x_move_region = []
        if left_or_right == "left":
            while (self.avg_x_move < self.temp[line_num]) and (self.step == step_num):
                if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                    self.x_move_region.append(self.game.get_states("player_x"))
                    self.avg_x_move = np.average(self.x_move_region)
                if int(time.time() - self.start_time) >= osci_time:
                    self.step += 1
                    break
        if left_or_right == "right":
            while (self.avg_x_move > self.temp[line_num]) and (self.step == step_num):
                if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                    self.x_move_region.append(self.game.get_states("player_x"))
                    self.avg_x_move = np.average(self.x_move_region)
                if int(time.time() - self.start_time) >= osci_time:
                    self.step += 1
                    break

    def run_thread(self):
        _thread.start_new_thread(self.run,())

    def run(self):
        while self.game.is_simple_AI and self.is_left:  #test left side:

            while not self.is_paused:

                # 判断属于哪个case
                if self.case == 0:
                    # 获得40速度下的波动（3秒）
                    if self.step == 0:
                        self.game._action_single_screen(40, "left")
                        self.ui.AI_mode.setText("left:40")
                        self.oscillation(osci_time=5,
                                        step_num=self.step)
                        break

                    # 判断不同的case
                    if self.step == 1:
                        # print (self.case, self.step)
                        # 没有过左第一条蓝线,直接淘汰
                        if (self.avg_x_move > self.temp[7]):
                            self.case = "Failure" # disqualified

                        #如果在40的光流速度下，小方块移动的位置超过了第二条黄线 -> case2
                        if (self.avg_x_move < self.temp[4]):
                            self.case = 2

                        #如果过了左第一条蓝线，但是还没过第一条黄线 -> case 1
                        if (self.avg_x_move <=  self.temp[7]) and \
                                (self.avg_x_move >= self.temp[6]):
                            self.case = 1

                        #如果刚好在区域里面，直接完成
                        if (self.avg_x_move <= self.temp[6] and \
                                    self.avg_x_move >= self.temp[4]):
                            self.case = "Success"

                        break

                # Case 1: 过蓝一，没过黄一
                if self.case == 1:

                    # print(self.case, self.step)
                    if self.step == 1:
                        # 这时需要用45的速度对蜂进行刺激，这时小方块在第一条左黄线附近来回晃动。
                        self.game._action_single_screen(45,"left")
                        self.ui.AI_mode.setText("left:45")
                        # 这时小方块在第一条左黄线附近来回晃动。
                        self.oscillation_line(line_num=self.temp[6], osci_time=self.sec_delay,
                                             step_num=self.step)
                        break

                    # 这时用50的光流速度，刺激熊蜂，
                    if self.step == 2:
                        self.game._action_single_screen(50, "left")
                        # 如果在左第二条蓝线附近摆动
                        self.oscillation_line(line_num=self.temp[5],osci_time=self.sec_delay,
                                             step_num=self.step)
                        break

                    # 左右切换3次，蜂任然可以停留在 “左1”区
                    if self.step == 3 :
                        self.game._action_single_screen(50, "right")
                        self.shift_with_delay(delay_time=self.SHIFT_TIME,direction="left",speed=50)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME, direction="right", speed=50)
                        self.shift_with_delay(delay_time=self.SHIFT_TIME, direction="left", speed=50)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME, direction="right", speed=50)
                        self.shift_with_delay(delay_time=self.SHIFT_TIME, direction="left", speed=50)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME, direction="right", speed=50)

                        self.step = 4
                        break

                    # 蜂任然可以停留在 “左1”区内 ->成功
                    if self.step == 4:
                        self.oscillation_region(region=[4,6],osci_time=self.sec_delay,
                                         step_num=self.step)
                        if self.step == 5:
                            self.case = "Success" # success!
                        else:
                            self.case = "Failure" # Failure
                        break

                #Case 2: 过了第二条黄线
                if self.case == 2:
                    # print(self.case, self.step)
                    #确定当前波动位置的均值
                    if self.step == 1:
                        self.left_bound = np.average([self.temp[3], self.temp[4]]) - self.osci_bound
                        self.right_bound = np.average([self.temp[4], self.temp[5]]) + self.osci_bound
                        self.avg_x_move = np.average([self.left_bound, self.right_bound])
                        self.oscillation(osci_time=self.SHIFT_TIME,step_num=self.step)

                    # 左右切换光溜的的运动方向4次，
                    if self.step == 2:
                        self.game._action_single_screen(40, "right")
                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="left",speed=40)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="right", speed=40)
                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="left", speed=40)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="right", speed=40)
                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="left", speed=40)

                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="right", speed=40)
                        self.shift_with_delay(delay_time=self.SHIFT_TIME,
                                              direction="left", speed=40)
                        self.step = 3
                        break

                    # 确定当前波动位置的均值“比较远” -> 小于temp[3]的位置
                    if self.step == 3:
                        self.avg_x_move = self.game.get_states("player_x")
                        delta = 5
                        self.speed = 45
                        x_move_region = []
                        self.start_time = time.time()
                        while (self.avg_x_move < self.temp[3]) and (self.step == 3):
                            if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                                x_move_region.append(self.game.get_states("player_x"))
                                self.avg_x_move = np.average(x_move_region)
                            if int(time.time() - self.start_time) >= self.sec_delay:
                                self.speed -= delta
                                self.game._action_single_screen("left",self.speed)
                                self.start_time = time.time()
                            if self.avg_x_move > self.temp[3] and self.step == 3:
                                self.step = 4
                                break
                        break
                    # 当前波动位置均值 “靠近些” -> 小于temp[4]的位置
                    if self.step == 4:
                        x_move_region = []
                        self.start_time = time.time()
                        delta = 3
                        while (self.avg_x_move <= self.temp[4]) and (self.step == 3):
                            if int(100 * (time.time() - self.start_time)) % (100 * self.samp_period) == 0:  # sample every 0.1 s
                                x_move_region.append(self.game.get_states("player_x"))
                                self.avg_x_move = np.average(x_move_region)
                            if int(time.time() - self.start_time) >= self.sec_delay:
                                self.speed -= delta
                                self.game._action_single_screen("left",self.speed)
                                self.start_time = time.time()
                                break
                            if (self.avg_x_move > self.temp[4]) and (self.step == 4):
                                self.step = 5
                                break
                        break

                    #如果能到temp[5]附近
                    if self.step == 5:
                        self.oscillation_line(line_num=5,osci_time=self.sec_delay,
                                             step_num=self.step)
                        break

                    #左右切换三次
                    if self.step == 6:
                        self.game._action_single_screen("right",self.speed)
                        self.shift_with_delay(delay_time=self.sec_delay,
                                              direction="left",speed=self.speed)

                        self.shift_with_delay(delay_time=self.sec_delay,direction="right", speed=self.speed)
                        self.shift_with_delay(delay_time=self.sec_delay, direction="left", speed=self.speed)

                        self.shift_with_delay(delay_time=self.sec_delay, direction="right", speed=self.speed)
                        self.shift_with_delay(delay_time=self.sec_delay, direction="left", speed=self.speed)

                        self.step = 7
                        break

                    #如果还能保持在区域里面
                    if self.step == 7:
                        self.oscillation_line(line_num=5, osci_time=self.sec_delay,
                                             step_num=self.step)
                        break

                    #就可以说明这只蜂可以控制在 “左1”区）
                    if self.step == 8:
                        self.case = "Success" # success

                # success: 就可以说明这只蜂可以控制在 “左1”区）
                if self.case == "Success":
                    print ("左一区间控制成功！Speed = ")
                    self.ui.AI_mode.setText("左一区间控制成功")
                    self.is_end = True
                    return 0
                    break

                # failure: 否则这只蜂不可以控制在 “左1”区）
                if self.case == "Failure":
                    print("这个熊蜂淘汰了")
                    self.ui.AI_mode.setText("这个熊蜂淘汰了")
                    self.is_end = True
                    return 0
                    break

                self.is_end = True
                print ("ending outside of cases")

            while self.is_paused == True:
                time.sleep(0.2)

# class DataRecord(QObject):
#     def __init__(self,env):
#         super(DataRecord, self).__init__()
#         self.game = env
#
#     def run(self):
#         _thread.start_new_thread(self.start_recording,(True))
#
#     def start_recording(self,is_recording,single_time,hold_time):
#
#         self.data = []
#         self.is_recording = is_recording
#         self.self.start_time = time.time()
#         while self.is_recording:
#
#             time_diff = (time.time() - self.self.start_time)*1000
#             if int(time_diff) % self.record_interval == 0: # re
#
#                 time_diff /= 1000
#                 time_diff = round(time_diff,5)  ###
#
#                 left_light_stream = self.game.left_shift_speed  ###
#                 right_light_stream = self.game.right_shift_speed  ###
#
#                 game_state = self.game.getGameState()
#                 bee_pos_x = game_state["player_x"]   ###
#
#                 try:
#                     temp = self.game._reader.get_slide_num_data(self.data_num, 30)
#                     torque_data = np.average(temp)   ###
#                 except:
#                     print ("请连接扭矩仪")
#
#                 curr_data = [time_diff, left_light_stream, right_light_stream,
#                              bee_pos_x, torque_data, ]
#                 self.data.append(curr_data)
#
#     def stop_recording(self):
#         # row_num = np.size(self.data, axis=0)
#         self.df = pd.DataFrame(self.data, columns=["时间", "光流左", "光流右",
#                                                    "熊蜂x", "扭矩","单侧时间",
#                                                    "单侧更新次数","映射参数"])
#         file_name = str(time.strfttime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))) + ".csv"
#         (self.df).to_csv(file_name)
#         self.ui.recording_status.setText("保存到: " + file_name)

# class MyException(Exception):
#     def __init__(self,msg):
#         Exception.__init__(self)
#         # self.msg = msg

def run_game():
    # import sys
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # p1 = multiprocessing.Process(target=run_game,args=())
    # p1.start()
    run_game()