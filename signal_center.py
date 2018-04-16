from PyQt5.QtCore import (pyqtSignal, pyqtSlot, QObject, QSettings, QThread)

class SignalCenter(QObject):
    # Signal Processor for all modules;
    # used for exchanging data between different threads
    # is_data_record_signal = pyqtSignal()
    # recording_status_signal = pyqtSignal
    # recording_interval_signal = pyqtSignal(int)
    #
    # is_keyboard_signal = pyqtSignal(bool)
    # obst_fall_speed_signal = pyqtSignal(int)
    # obst_appear_interval = pyqtSignal(int)
    # player_x_signal = pyqtSignal(int)
    # player_y_signal = pyqtSignal(int)
    #
    # time_sec_signal = pyqtSignal(int)
    # data_num = pyqtSignal(int)
    # torque_value_signal = pyqtSignal(float)
    # x_coord_factor_signal = pyqtSignal(int)
    # parameter_div_signal = pyqtSignal(float)
    # is_torque_update_signal = pyqtSignal(bool)

    def __init__(self):
        # GUI:
        self.left_dir_speed_spinbox = 40
        self.right_dir_speed_spinbox = 40
        self.recording_status = ""

        # Data-recording:
        self.is_recording = False
        self.recording_status = "储存中.."
        self.record_interval = 100 #ms
        self.is_first_time = True
        self.to_save = False

        # Game-related:
        self.SCREEN_WIDTH = 860
        self.SCREEN_HEIGHT = 860
        self.is_keyboard = True
        self.is_running = True
        #出现间隔:
        self.plane_appear_freq = 1000
        #下落速度
        self.obst_fall_speed = 1
        # self.obst_appear_interval = 50
        self.player_x = 0
        self.score = 0
        self.enemy_speed = 0.1

        # Timer
        self.is_timer_run = True
        self.time_sec = 0

        # Labview Reader(read)
        self.reader_data = 0
        self.data_num = 100
        self.torque_value = 0
        self.x_coord_factor = 300
        self.parameter_div = 1.5
        self.is_torque_update = True

        # # light(send)
        # self.light_direction_signal = None
        # self.light_speed = None

    # def emitter(self):
    #     while True:
    #         self.is_data_record_signal.emit(self.is_data_record_signal)