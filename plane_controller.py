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
        self.timer_rule_algo.timeout.connect(self.rule_algo)
        # self.timer_game.timeout.connect(self.run_game)
        # self.timer_lv_reader.timeout.connect(self.lv_reader)
        # self.timer_lv_reader.start(0.01)

    def run_timer(self):
        self.time_count += 1
        self.signal_center.time_sec = self.time_count
        self.ui.timer_display.display(self.time_count)

    def record_data(self):
        if self.signal_center.is_recording:
            left_light_stream = self.signal_center.left_dir_speed_spinbox  ###
            right_light_stream = self.signal_center.right_dir_speed_spinbox  ###
            bee_pos_x = self.signal_center.player_x  ###
            try:
                torque_data = round(self.signal_center.reader_data, 5)  ###
            except:
                torque_data = "None"
            curr_data = [self.signal_center.time_sec_signal, left_light_stream, right_light_stream, bee_pos_x
                , torque_data, self.signal_center.parameter_div
                , self.signal_center.score
                         ]
            self.data.append(curr_data)
        if self.signal_center.to_save:
            self.signal_center.recording_status = "储存中...."
            df = pd.DataFrame(self.data, columns=["时间", "光流左", "光流右", "熊蜂x",
                                                  "扭矩", "最大参数"
                                                  # , "每边更新次数", "每次持续时间"
                , "得分"
                                                  # , "区域"
                                                  # , "acce_a", "acce_seconds"
                                                  ])

            local_time = time.localtime(int(time.time()))
            time_format = "%Y-%m-%d %Hh-%Mm-%Ss"
            file_name = "./data/" + str(time.strftime(time_format, local_time)) + ".csv"
            df.to_csv(file_name)
            self.signal_center.to_save = False
        pass
    #
    # def run_game(self):
    #     self.plane_game.run_game(self.signal_center)
    #
    # def lv_reader(self):
    #     self.labview_reader.torque_update(signal_center=self.signal_center)
    #     pass
    # #
    def rule_algo(self):
        if self.is_rule == True:
            closest_x = self.plane_game.get_closest_x()
            if closest_x <  self.x_intervals[0]:
                self._action_single_screen(70, "left")
                self.ui.AI_mode.setText("70 左")
            elif closest_x <  self.x_intervals[1]:
                self._action_single_screen(50, "left")
                self.ui.AI_mode.setText("50 左")
            elif closest_x <  self.x_intervals[2]:
                self._action_single_screen(30, "left")
                self.ui.AI_mode.setText("30 左")
            elif closest_x <  self.x_intervals[3]:
                self._action_single_screen(10, "left")
                self.ui.AI_mode.setText("10 左")
            elif closest_x <  self.x_intervals[4]:
                self._action_single_screen(10, "right")
                self.ui.AI_mode.setText("10 右")
            elif closest_x <  self.x_intervals[5]:
                self._action_single_screen(30, "right")
                self.ui.AI_mode.setText("30 右")
            elif closest_x <  self.x_intervals[6]:
                self._action_single_screen(50, "right")
                self.ui.AI_mode.setText("50 右")
            elif closest_x <  self.x_intervals[7]:
                self._action_single_screen(70, "right")
                self.ui.AI_mode.setText("70 右")
            else:
                self._action_single_screen(0, "right")
                self.ui.AI_mode.setText("不给予光流")

    def _action_single_screen(self,angle_speed,direction):
        if direction == "left" or direction =="right":
            self._sender.send("params", 1, "hDirection", direction)
            self._sender.send("params", 1, "hSpeed", angle_speed)
            self._sender.send("start_left")
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
        self.timer_clock.start(1000)

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
        self.timer_record.start(10)

        self.ui.start_recording.setEnabled(False)
        self.ui.stop_recording.setEnabled(True)
        self.ui.recording_status.setText("记录中。。。")

        pass

    @pyqtSlot()
    def on_stop_recording_clicked(self):
        self.signal_center.is_recording = False
        self.signal_center.to_save = True
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
        self.timer_rule_algo.start(500)
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
            data = self.reader.get_slide_num_data(data_num,40)
            data_avg = np.average(data)  # cal their average
            signal_center.torque_value = str(data_avg)
            data_para = data_avg / signal_center.parameter_div  # divided by the parameter(5 in this case)

            self.torque_value_signal.emit(str(data_avg))
            # map the data onto the coordinate
            data_mapped = data_para * signal_center.x_coord_factor
            data_mapped += int(screen_width / 2)
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



