from PyQt5.QtWidgets import (QApplication, QMainWindow,QDesktopWidget)
from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QObject, QSettings, QThread,QBasicTimer,QTimer)
from ui_plane_controller import Ui_MainWindow
from plane2 import plane
import _thread
import sys
import time
import pandas as pd
import numpy as np
from ple.games.utils.udp_comm_sender_new import CommSender
from ple.games.utils.lv_reader import LabviewReader
from signal_center import SignalCenter
# import pygame
# from multiprocessing import Process

class MainWindow(QMainWindow):

    #init the control panel and the game parameters
    def __init__(self,is_keyboard):
        super(MainWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.freq = 50

        self.min_period = 10  # 0.01 s
        #move the control panel to the center of the monitor
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 4 * 3,
                  (screen.height() - size.height()) / 2)

        #define the light-control sender
        self._sender = CommSender("localhost", 5888)

        #init the control panel parameters:
        self.ui.data_record_interval_spinbox.setMaximum(1000)
        self.ui.data_num_spinbox.setMaximum(1000)
        self.ui.x_coord_factor_spinbox.setMaximum(1000)
        self.ui.obst_freq_spinbox.setMaximum(5000)
        self.ui.obst_freq_spinbox.setMinimum(1)

        self.ui.obst_fall_speed_spinbox.setValue(2.5)
        self.ui.left_dir_speed_spinbox.setValue(40)
        self.ui.right_dir_speed_spinbox.setValue(40)
        self.ui.obst_freq_spinbox.setValue(100)
        self.ui.x_max_spinbox.setValue(15)
        self.ui.x_max_actual.setText(str(1.5))
        self.ui.data_num_spinbox.setValue(100)
        self.ui.data_num_display.setText(str(100))
        self.ui.x_coord_factor_spinbox.setValue(300)
        self.ui.x_coord_factor_display.setText(str(300))

        #buttons:
        self.ui.manual_start.setEnabled(True)
        self.ui.manual_pause.setEnabled(False)
        self.ui.manual_reset.setEnabled(False)
        self.ui.RL_test.setEnabled(False)
        self.ui.AI_mode.setText("人工控制")

        # init the signals exchanging center:
        self.signal_center = SignalCenter()
        self.is_keyboard = self.signal_center.is_keyboard
        self.signal_center.is_keyboard = is_keyboard # whether to control via keyboard
        self.signal_center.is_running= False # whether the game is paused or started
        #game-related:
        self.plane_game = plane.PlaneGame(signal_center=self.signal_center,
                                          keyboard_control=False)
        self.plane_game.plane_game_init(signal_center=self.signal_center)
        # self.game_thread = QThread()
        # self.game_thread.started.connect(self.plane_game.run_game)
        # self.game_thread.finished.connect(self.game_thread.deleteLater)
        # self.plane_game.moveToThread(self.game_thread)
        # self.game_thread.start()
        _thread.start_new_thread(self.plane_game.run_game,(self.signal_center,)) # start the game thread
        #
        self.labview_reader = LvReader(signal_center=self.signal_center)
        # start the movingInstance thread
        #  self.moving_thread = QThread()
        # self.moving_thread.started.connect(self.movingInstance.torque_update)
        # self.moving_thread.finished.connect(self.moving_thread.deleteLater)
        # self.movingInstance.moveToThread(self.moving_thread)
        # self.moving_thread.start()
        _thread.start_new_thread(self.labview_reader.torque_update,(self.signal_center,))
        self.labview_reader.torque_value_signal.connect(self.ui.torque_data_avg.setText)

        #TIMERS
        self.timer_clock = QTimer()
        self.timer_record = QTimer()
        self.timer_rule_algo = QTimer()
        # self.timer_game = QTimer()
        # self.timer_lv_reader = QTimer()

        # self.time_temp = 0
        self.time_count = 0
        self.data = []
        self.signal_center.is_recording = False
        self.x_intervals = [83, 166, 249, 332, 415, 498, 581, 666]

        self.timer_clock.timeout.connect(self.run_timer)
        self.timer_record.timeout.connect(self.record_data)
        #testing difference algorithms
        # self.timer_rule_algo.timeout.connect(self.rule_algo)
        self.timer_rule_algo.timeout.connect(self.rule_fuzzy)


    def run_timer(self):
        self.time_count += 0.1
        self.signal_center.time_sec = self.time_count
        self.ui.timer_display.display(int(self.time_count))

    def record_data(self):
        if self.signal_center.is_recording:
            left_light_stream = self.signal_center.left_dir_speed_spinbox  ###
            right_light_stream = self.signal_center.right_dir_speed_spinbox  ###
            # bee_pos_x = self.signal_center.player_x  ###
            try:
                torque_data = round(self.signal_center.reader_data, 3)  ###
            except:
                torque_data = "None"
            curr_data = [self.signal_center.time_sec, left_light_stream,
                         right_light_stream, self.signal_center.player_x
                         , torque_data, self.signal_center.parameter_div
                         , self.signal_center.score
                         , self.plane_game.get_closest_x()
                         , self.plane_game.player_life+1
                         ]
            self.data.append(curr_data)

        if self.signal_center.to_save:
            self.signal_center.recording_status = "储存中...."
            df = pd.DataFrame(self.data, columns=["时间(秒)", "光流左", "光流右", "熊蜂x",
                                                  "扭矩", "最大参数"
                                                  # , "每边更新次数", "每次持续时间"
                                                  , "得分","敌机位置","生命值"
                                                  # , "区域"
                                                  # , "acce_a", "acce_seconds"
                                                  ])

            local_time = time.localtime(int(time.time()))
            time_format = "%Y-%m-%d %Hh-%Mm-%Ss"
            file_name = "./data/" + str(time.strftime(time_format, local_time)) + ".csv"
            df.to_csv(file_name, encoding="gbk")
            self.timer_record.stop()
            self.signal_center.to_save = False
        pass

    #简单规则算法
    def rule_algo(self):
        if self.is_rule == True:
            closest_x = self.plane_game.get_closest_x()
            if closest_x <  self.x_intervals[0]:
                self._action_single_screen(70, "left")
                self.ui.AI_mode.setText("70 左")
                self.signal_center.left_dir_speed_spinbox = 70
            elif closest_x <  self.x_intervals[1]:
                self._action_single_screen(50, "left")
                self.ui.AI_mode.setText("50 左")
                self.signal_center.left_dir_speed_spinbox = 50
            elif closest_x <  self.x_intervals[2]:
                self._action_single_screen(30, "left")
                self.ui.AI_mode.setText("30 左")
                self.signal_center.left_dir_speed_spinbox = 30
            elif closest_x <  self.x_intervals[3]:
                self._action_single_screen(10, "left")
                self.ui.AI_mode.setText("10 左")
                self.signal_center.left_dir_speed_spinbox = 10
            elif closest_x <  self.x_intervals[4]:
                self._action_single_screen(10, "right")
                self.ui.AI_mode.setText("10 右")
                self.signal_center.left_dir_speed_spinbox = 10
            elif closest_x <  self.x_intervals[5]:
                self._action_single_screen(30, "right")
                self.ui.AI_mode.setText("30 右")
                self.signal_center.right_dir_speed_spinbox = 30
            elif closest_x <  self.x_intervals[6]:
                self._action_single_screen(50, "right")
                self.ui.AI_mode.setText("50 右")
                self.signal_center.right_dir_speed_spinbox = 50
            elif closest_x <  self.x_intervals[7]:
                self._action_single_screen(70, "right")
                self.ui.AI_mode.setText("70 右")
                self.signal_center.right_dir_speed_spinbox = 70
            else:
                self._action_single_screen(5, "right")
                self.ui.AI_mode.setText("不给予光流")

    #mamdani模糊算法
    def rule_fuzzy(self):
        Al3_mv = [1.0, 0.962, 0.259, 0.333, 0]  # y
        Al3_a = [-70, -60, -50, -40, -30]  # x
        al3_line = [(-0.0038000000000000035, 0.7339999999999998),
                    (-0.0703, -3.2560000000000002),
                    (0.007400000000000001, 0.629),
                    (-0.0333, -0.9990000000000001),
                    ]

        Al2_mv = [0.131, 0.174, 1.0, 0.783, 0.869, 0.174, 0]
        Al2_a = [-70, -60, -50, -40, -30, -20, -10]
        al2_line = [(0.004299999999999998, 0.4319999999999999),
                    (0.0826, 5.130000000000001),
                    (-0.021699999999999997, -0.08499999999999996),
                    (0.008599999999999997, 1.1269999999999998),
                    (-0.0695, -1.216),
                    (-0.0174, -0.174)]

        Al1_mv = [0, 0.107, 0.357, 0.892, 1.0]
        Al1_a = [-50, -40, -30, -20, -10]
        al1_line = [(0.0107, 0.5349999999999999),
                    (0.025, 1.107),
                    (0.053500000000000006, 1.9620000000000002),
                    (0.010799999999999999, 1.108)]

        Ar1_mv = [0.892, 1.0, 0.714, 0.357, 0.071, 0]
        Ar1_a = [10, 20, 30, 40, 50, 60]
        ar1_line = [(0.010799999999999999, 0.784),
                    (-0.028600000000000004, 1.572),
                    (-0.035699999999999996, 1.785),
                    (-0.028599999999999997, 1.501)]

        Ar2_mv = [0.185, 0, 0.37, 0.74, 1.0, 0.889, 0.185]
        Ar2_a = [10, 20, 30, 40, 50, 60, 70]
        ar2_line = [(-0.0185, 0.37),
                    (0.037, -0.74),
                    (0.037, -0.7399999999999999),
                    (0.026000000000000002, -0.30000000000000004),
                    (-0.011099999999999999, 1.555),
                    (-0.07039999999999999, 5.1129999999999995)]

        Ar3_mv = [0, 0.04, 0.24, 1.0]
        Ar3_a = [40, 50, 60, 70]
        ar3_line = [(0.004, -0.16),
                    (0.019999999999999997, -0.9599999999999999),
                    (0.076, -4.319999999999999)]

        a_mf = [al3_line, al2_line, al1_line, ar1_line, ar2_line, ar3_line]
        a_mv = [Al3_mv, Al2_mv, Al1_mv,
                Ar1_mv, Ar2_mv, Ar3_mv]
        zones = {"L3": (0, 107), "L2": (107, 215), "L1": (215, 322),
                 "R1": (538, 645), "R2": (645, 752), "R3": (752, 860)}

        def L_mf_trimf(left_bound, right_bound, data):
            center_x = (right_bound - left_bound) / 2 + left_bound
            if data < center_x:
                k = (0 - 1) / (left_bound - center_x)
                b = (0 - k * left_bound)
                return k * data + b
            else:
                k = (1 - 0) / (center_x - right_bound)
                b = (1 - k * center_x)
                return k * data + b
            pass

        def mamdani_inference(data_in):
            """
            input:
                -input_mfs: list [[regions],[correspoding mf]]
                -output_mfs:
            assume one-input and one-output
            """
            # find the input mf and output mf , mv
            marker = 0
            k = 0
            for i in zones:
                if data_in > zones[i][0] and data_in <= zones[i][1]:
                    in_region = zones[i]
                    out_mf = a_mf[k]
                    out_mv_region = a_mv[k]
                    marker = 1
                    break
                k += 1
            if marker == 0:
                return 5
            # get the membership value from input
            mv = L_mf_trimf(in_region[0], in_region[1], data_in)

            # get the output light speed
            for j in range(len(out_mv_region) - 1):
                temp_max = max(out_mv_region[j], out_mv_region[j + 1])
                temp_min = min(out_mv_region[j], out_mv_region[j + 1])
                if mv > temp_min and mv <= temp_max:
                    target_mf = out_mf[j]
                    break
            speed = (mv - target_mf[1]) / target_mf[0]
            return speed

        speed = int(mamdani_inference(self.plane_game.get_closest_x()))
        if speed < 0:
            direction = "left"
            self.signal_center.left_dir_speed_spinbox = abs(speed)
        else:
            direction = "right"
            self.signal_center.right_dir_speed_spinbox = abs(speed)

        self._action_single_screen(abs(speed),direction)
        self.signal_center.left_dir_speed_spinbox
        self.ui.AI_mode.setText(str(abs(speed))+" "+direction)
        # print(mamdani_inference(208))

    #策略梯度算法
    def RL_gradient(self):
        pass

    def _action_single_screen(self,angle_speed,direction):
        if direction == "left":
            self._sender.send("params", 1, "hDirection", direction)
            self._sender.send("params", 1, "hSpeed", angle_speed)
            self._sender.send("start_left")
            self.signal_center.left_dir_speed_spinbox = angle_speed
            self.signal_center.right_dir_speed_spinbox = 0
        if direction =="right":
            self._sender.send("params", 1, "hDirection", direction)
            self._sender.send("params", 1, "hSpeed", angle_speed)
            self._sender.send("start_left")
            self.signal_center.right_dir_speed_spinbox = angle_speed
            self.signal_center.left_dir_speed_spinbox = 0
        elif direction == "reset_all":
            self._sender.send("reset_left")
        elif direction == "stop_all":
            self._sender.send("stop_left")

    @pyqtSlot()
    def on_manual_start_clicked(self):
        self.signal_center.enemy_speed = self.ui.obst_fall_speed_spinbox.value()
        self.signal_center.is_running = True  #This line starts the game
        self.signal_center.is_recording = False

        self.signal_center.obst_fall_speed = self.ui.obst_fall_speed_spinbox.value()
        self.signal_center.freq = self.ui.obst_freq_spinbox.value()

        self.signal_center.is_keyboard = False  # whether to control via keyboard
        self.timer_clock.start(100)

        # #update the buttons
        self.ui.manual_start.setEnabled(False)
        self.ui.manual_start.setText("继续")
        self.ui.manual_pause.setEnabled(True)
        self.ui.manual_reset.setEnabled(True)

        # self.time_temp = 0
        # self.time_count = 0
        # self.data = []
        # self.timer_clock.start()
        # self.timer_record.start()

    @pyqtSlot()
    def on_manual_pause_clicked(self):
        self.prev_speed = self.plane_game.enemy_speed
        # pause all objects except the player
        self.signal_center.obst_fall_speed = 0
        # self.signal_center.plane_appear_freq = self.ui.obst_freq_spinbox

        #update buttons
        self.ui.manual_start.setEnabled(True)
        self.ui.manual_pause.setEnabled(False)
        self.ui.manual_reset.setEnabled(True)
        pass

    @pyqtSlot()
    def on_manual_reset_clicked(self):
        # self.plane_game = plane.PlaneGame(self.signal_center)
        # self.signal_center.freq = self.freq
        self.plane_game.reset_game(self.signal_center)
        self.signal_center.is_running = True  # whether the game is paused or started
        self.signal_center.time_sec = 0
        self.time_count = 0
        # self.plane_game
        self.signal_center.freq = self.ui.obst_freq_spinbox.value()
        self.signal_center.obst_fall_speed = self.ui.obst_fall_speed_spinbox.value()

        # self.signal_center.is_keyboard = False
        # _thread.exit_thread(self.plane_game.run_game,(self.signal_center))
        # _thread.start_new_thread(self.plane_game.run_game,(self.signal_center,))

        # self.labview_reader = LvReader(signal_center=self.signal_center)
        # _thread.start_new_thread(self.labview_reader.torque_update, (self.signal_center,))
        # self.data_record = DataRecord(signal_center=self.signal_center)
        # _thread.start_new_thread(self.data_record.recording, (self.signal_center,))

        # init the data recorder
        # self.data_record = DataRecord(self.ui, self.plane_game)
        # _thread.start_new_thread(self.data_record.recording, ())

        # p_game = Process(target=self.plane_game.run_game,args=())
        # p_game.start()
        # p_game.join()
        #buttons:
        self.ui.manual_start.setEnabled(False)
        self.ui.manual_pause.setEnabled(True)
        self.ui.manual_reset.setEnabled(True)

    @pyqtSlot()
    def on_left_dir_speed_spinbox_editingFinished(self):
        self._action_single_screen(self.ui.left_dir_speed_spinbox.value(), "left")

    @pyqtSlot()
    def on_right_dir_speed_spinbox_editingFinished(self):
        self._action_single_screen(self.ui.right_dir_speed_spinbox.value(), "right")

    @pyqtSlot()
    def on_reset_light_clicked(self):
        self._action_single_screen(0, "reset_all")

    @pyqtSlot()
    def on_stop_light_clicked(self):
        self._action_single_screen(0, "stop_all")

    # @pyqtSlot()
    # def on_stop_recording_clicked(self):
    #     # self.data_record.stop_recording()
    #     self.signal_center.is_recording = False
    #     # self.data_record.stop_recording(self.signal_center)
    #     self.ui.start_recording.setEnabled(True)
    #     self.ui.stop_recording.setEnabled(False)
    #     # self.ui.recording_status.setText("记录完成！文件：" + self.data_record.file_name)
    #     self.ui.recording_status.setText("记录完成！")
    #     pass

    @pyqtSlot()
    def on_start_recording_clicked(self):
        self.data = []
        self.signal_center.to_save = False
        self.signal_center.is_recording = True
        self.timer_record.start(1)

        self.ui.start_recording.setEnabled(False)
        self.ui.stop_recording.setEnabled(True)
        self.ui.recording_status.setText("记录中。。。")

        pass

    @pyqtSlot()
    def on_stop_recording_clicked(self):
        self.signal_center.is_recording = False
        self.signal_center.to_save = True
        # self.timer_record.stop()

        self.ui.start_recording.setEnabled(True)
        self.ui.stop_recording.setEnabled(False)
        # self.ui.recording_status.setText("记录完成！文件：" + self.data_record.file_name)
        self.ui.recording_status.setText("记录完成！")
        pass

    @pyqtSlot()
    def on_single_left_shift_clicked(self):
        self.is_rule = False
        temp = self.ui.left_dir_speed_spinbox.value()
        self._action_single_screen(temp, "left")
        self._action_single_screen(temp, "left")
        self.left_shift_speed = temp
        self.right_shift_speed = 0
        # self.ui.RL_left_display.setText()

    @pyqtSlot()
    def on_single_right_shift_clicked(self):
        self.is_rule = False
        temp = self.ui.right_dir_speed_spinbox.value()
        self._action_single_screen(temp, "right")
        self._action_single_screen(temp, "right")
        self.right_shift_speed = temp
        self.left_shift_speed = 0

    @pyqtSlot()
    def on_x_max_spinbox_editing_finished(self):
        value = self.ui.x_max_spinbox.value() / 10
        self.signal_center.parameter_div = value
        self.ui.x_max_actual.setText(str(value))

    @pyqtSlot()
    def on_data_num_spinbox_editing_finished(self):
        value = self.ui.data_num_spinbox.value()
        self.signal_center.data_num = value
        self.ui.data_num_display.setText(str(value))

    @pyqtSlot()
    def on_x_coord_factor_editing_finished(self):
        value = self.ui.x_coord_factor_spinbox.value()
        self.signal_center.x_coord_factor = value
        self.ui.x_coord_factor_display.setText(str(value))

    @pyqtSlot()
    def on_obst_freq_spinbox_editing_finished(self):
        self.signal_center.plane_appear_freq = \
            self.ui.obst_freq_spinbox.value()

    @pyqtSlot()
    def on_obst_fall_speed_spinbox_editing_finished(self):
        self.signal_center.plane_appear_freq = \
            self.ui.obst_fall_speed_spinbox.value()

    @pyqtSlot()
    def on_data_record_interval_spinbox_editing_finished(self):
        value = self.ui.data_record_interval_spinbox.value() / 100
        self.data_record.record_interval = value
        self.ui.actual_record_interval_display.setText(str(value))

    @pyqtSlot()
    def on_simple_AI_clicked(self):
        # light_intervals =   [-70,-50,-30,-10,  0,  10, 30, 50, 70]
        self.is_rule = True
        self.timer_rule_algo.start(2500)
        self.ui.RL_test.setEnabled(True)
        self.ui.simple_AI.setEnabled(False)

    @pyqtSlot()
    def on_RL_test_clicked(self):
        self.is_rule = False
        self.timer_rule_algo.stop()

        self.ui.simple_AI.setEnabled(True)
        self.ui.RL_test.setEnabled(False)
        self.ui.AI_mode.setText("人工控制中")

class LvReader(QObject):
    torque_value_signal = pyqtSignal(str)
    def __init__(self,signal_center):
        super(LvReader, self).__init__()
        self.signal_center = signal_center
        self.reader = LabviewReader()

    # update plane's coordinate w.r.t the torque's voltage
    def torque_update(self,signal_center):
        while True:
            screen_width = signal_center.SCREEN_WIDTH
            # while signal_center.is_torque_update:
            data_num = signal_center.data_num
            data = self.reader.get_slide_num_data(data_num, 40)
            data_avg = np.average(data)  # cal their average
            signal_center.torque_value = str(data_avg)
            data_para = data_avg / signal_center.parameter_div  # divided by the parameter(5 in this case)

            self.torque_value_signal.emit(str(data_avg))
            # map the data onto the coordinate
            data_mapped = data_para * signal_center.x_coord_factor
            data_mapped += int(screen_width / 2)
            #random noise
            data_mapped += np.random.randint(5,25)
            if data_mapped < 0:
                data_mapped = 50
            if data_mapped > screen_width:
                data_mapped = screen_width - 50
            signal_center.player_x = data_mapped
        # print (data_mapped)

# class Timer(QThread):
#     time_sec_signal = pyqtSignal(int)
#
#     def __init__(self,signal_center,parent=None):
#         super().__init__(parent)
#         self.is_timer_run = signal_center.is_timer_run
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.show_secs)
#         self.time_sec = 0
#         # self.time_elapsed = signal_center.time_sec_signal
#         pass
#
#     def run(self):
#         self.start_time = time.time()
#         while True:
#             if self.is_timer_run:
#                 self.timer.start(1000)
#
#                 # diff = int(1000*(time.time()-self.start_time))
#                 # if time.time() - self.start_time >= 1:
#                 #     # self.time_elapsed += 1
#                 #     self.time_sec += 1
#                 #     self.time_sec_signal.emit(self.time_sec)
#                 #     self.start_time = time.time()
#                 # self.time_sec_signal.emit(self.timer.start(1000))
#             else:
#                 self.timer.stop()
#
#     def show_secs(self):
#         self.time_sec += 1
#         self.time_sec_signal.emit(self.time_sec)
#
#     # @pyqtSlot()
#     # def timerEvent(self, a0: 'QTimerEvent'):
#     #     self.time_sec_signal.emit(self.time_sec)

# class DataRecord(QObject):
#
#     def __init__(self,signal_center):
#         super(DataRecord, self).__init__()
#         self.signal_center = signal_center
#         self.data = []
#         self.start_time = time.time()
#
#     def recording(self,signal_center):
#         self.is_recorded = False
#         while True:
#             if signal_center.is_recording:
#                 self.start_recording(signal_center)
#                 self.is_recorded = False
#             if not signal_center.is_recording and not self.is_recorded:
#                 self.stop_recording(signal_center)
#                 self.is_recorded = True
#
#     def start_recording(self,signal_center):
#         self.start_time = time.time()
#         if signal_center.is_recording:
#             curr_time = time.time() * 1000
#             time_diff = curr_time - (self.start_time*1000)
#             if time_diff >= signal_center.record_interval:  # re
#                 # time_diff = round(time_diff,3)
#                 left_light_stream = signal_center.left_dir_speed_spinbox  ###
#                 right_light_stream = signal_center.right_dir_speed_spinbox  ###
#                 bee_pos_x = signal_center.player_x  ###
#                 try:
#                     torque_data = round(signal_center.reader_data, 5)  ###
#                 except:
#                     torque_data = "None"
#                 curr_data = [signal_center.time_sec_signal, left_light_stream, right_light_stream, bee_pos_x
#                             , torque_data, signal_center.parameter_div
#                             , signal_center.score
#                              ]
#                 self.data.append(curr_data)
#                 self.start_time = time.time()
#                 # time.sleep(0.02)
#
#     def stop_recording(self,signal_center):
#         signal_center.recording_status = "储存中...."
#         df = pd.DataFrame(self.data, columns=["时间", "光流左", "光流右", "熊蜂x",
#                                                    "扭矩", "最大参数"
#                                                     # , "每边更新次数", "每次持续时间"
#                                                    ,"得分"
#                                                     # , "区域"
#                                                     # , "acce_a", "acce_seconds"
#                                                    ])
#
#         local_time = time.localtime(int(time.time()))
#         time_format = "%Y-%m-%d %Hh-%Mm-%Ss"
#         file_name = "./data/" + str(time.strftime(time_format, local_time)) + ".csv"
#         df.to_csv(file_name)
#         self.data = []

def run_window():
    app = QApplication(sys.argv)
    mainWin = MainWindow(is_keyboard=False)
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_window()
    # p_window = Process(target=run_window,args=())
    # p_window.start()
    # p_window.join()
    #
    # p_game = mainWin.p_game
    # p_game.start()
    # p_game.join()
    #
    # p_data = mainWin.p_data
    # p_data.start()
    # p_data.join()
    #
    # p_torque = mainWin.p_torque
    # p_torque.start()
    # p_torque.join()



