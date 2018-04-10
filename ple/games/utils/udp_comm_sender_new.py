import socket
import struct
import time


class CommSender:
    def __init__(self, addr, port):
        """
        :param addr: the socket connect address
        :type str
        :param port: the port which socket connect to
        :type int
        """
        self._addr = addr
        self._port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._s.connect((addr, port))

        self._group = [1, 2]
        self._group_params = {key: {} for key in self._group}

        self._start_h = struct.pack("BBB", 5, 0, 0)
        self._stop_h = struct.pack("BBB", 4, 0, 0)
        self._reset_h = struct.pack("BBB", 1, 0, 0)
        # new Functions (as of Jun. 26th,2017)
        self._off_all_h = struct.pack("BBB", 8, 0,0)
        self._on_all_h = struct.pack("BBB", 9, 0, 0)
        self._restore_h = struct.pack("BBB",10, 0, 0)

        self._params_h = struct.pack("BBB", 3, 0, 2)
        self._params_t = struct.pack("BBB", 0, 0, 0)

        for key in self._group_params.keys():
            self._group_params[key].update(
                {"illumination": 255, "vSpeed": 0, "hSpeed": 0, "hDirection": 3, "vDirection": 3})

    def send(self, ops, *args):
        """
        :param ops: the type of operation
        :type ops: str
        :param *arg for params, arg[0] is group, arg[1] is param's name, arg[2] is param's value
        """
        sleep_period = 0.001 #这里改时间
        if ops == "start_left":
            # self._intensity = 255
            head = self._start_h
            g = self._group[0]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            # time.sleep(sleep_period)
            self._s.sendall(str)
            # time.sleep(sleep_period)
        elif ops == "start_right":
            head = self._start_h
            g = self._group[1]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            # self._s.sendall(str)
            # time.sleep(sleep_period)
        elif ops == "stop_left":
            head = self._stop_h
            g = self._group[0]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            # time.sleep(sleep_period)
            self._s.sendall(str)
            # time.sleep(sleep_period)
        elif ops == "stop_right":
            head = self._stop_h
            g = self._group[1]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "reset_left":
            head = self._reset_h
            g = self._group[0]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            # time.sleep(sleep_period)
            self._s.sendall(str)
            # time.sleep(sleep_period)
        elif ops == "reset_right":
            head = self._reset_h
            g = self._group[1]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "off_left":
            head = self._off_all_h
            g = self._group[0]
            g_b = struct.pack("B",g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "off_right":
            head = self._off_all_h
            g = self._group[1]
            g_b = struct.pack("B",g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "restore_left":
            head = self._restore_h
            g = self._group[0]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "restore_right":
            head = self._restore_h
            g = self._group[1]
            g_b = struct.pack("B", g)
            str = head + g_b
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "shift_to_left":
            #step 1: Turn off the right section
            head_off = self._off_all_h
            g_off = struct.pack("B", self._group[1])
            str = head_off + g_off
            self._s.sendall(str)
            time.sleep(sleep_period)
            #step 2: project to the left side
            right_speed = args[0]
            right_hDirection = args[1]
            head = self._params_h
            tail = self._params_t
            left_hSpeed = right_speed
            left_hDirection = 1
            if right_hDirection == 0:
                left_hDirection = 0
            #restore left side first(if needed)
            head_re = self._restore_h
            g_re = struct.pack("B",self._group[0])
            self._s.sendall(head_re + g_re)
            time.sleep(sleep_period)
            #send the project data to the left
            str = head + struct.pack("BBBBBB", self._group[0], 255, left_hSpeed, 0, left_hDirection,
                                     3) + tail
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "shift_to_right":
            #Step 1: Turn off the left section
            head_off = self._off_all_h
            g_off = struct.pack("B", self._group[0])
            self._s.sendall(head_off + g_off)
            time.sleep(sleep_period)
            #Step 2: project to the right side
            head = self._params_h
            tail = self._params_t
            left_speed = args[0]
            left_hDirection = args[1]
            right_hSpeed = left_speed
            right_hDirection = 0
            if left_hDirection == 0:
                right_hDirection = 1
            #restore right side first(if needed)
            head_re = self._restore_h
            g_re = struct.pack("B",self._group[1])
            self._s.sendall(head_re + g_re)
            time.sleep(sleep_period)
            #project the data to the right
            str = head + struct.pack("BBBBBB", self._group[1], 255, right_hSpeed, 0, right_hDirection,
                                     3) + tail
            self._s.sendall(str)
            time.sleep(sleep_period)
        elif ops == "params":
            head = self._params_h
            tail = self._params_t

            if len(args) < 3:
                raise ValueError("args must include group, params_n and params_v three args, but now got less than 3")
            group = args[0]
            param_n = args[1]
            param_v = args[2]
            group_params = self._group_params[group]

            if param_n == "illumination":
                illumination_value = param_v
                if illumination_value == "" or illumination_value < 0 or illumination_value > 255:
                    raise ValueError
                group_params[param_n] = param_v
            # elif param_n == "vSpeed":
            #     speed_value = param_v
            #     if speed_value == "" or speed_value < 0 or speed_value > 255:
            #         raise ValueError
                group_params[param_n] = param_v
            elif param_n == "hSpeed":
                speed_value = param_v
                if speed_value == "" or speed_value < 0 or speed_value > 255:
                    raise ValueError
                group_params[param_n] = param_v
            elif param_n == "hDirection":
                direction = param_v
                if direction == "left":
                    dir_byte = 0
                elif direction == "right":
                    dir_byte = 1
                elif direction == "round":
                    dir_byte = 2
                elif direction == "none":
                    dir_byte = 3
                else:
                    raise ValueError
                group_params[param_n] = dir_byte

            # elif param_n == "vDirection":
            #     direction = param_v
            #     if direction == "up":
            #         dir_byte = 0
            #     elif direction == "down":
            #         dir_byte = 1
            #     elif direction == "round":
            #         dir_byte = 2
            #     elif direction == "none":
            #         dir_byte = 3
            #     else:
            #         raise ValueError
                group_params[param_n] = dir_byte

            else:
                raise ValueError

            #获取发送参数
            illumination = group_params["illumination"]
            hSpeed = group_params["hSpeed"]
            vSpeed = group_params["vSpeed"]
            hDirection = group_params["hDirection"]
            vDirection = group_params["vDirection"]
            str = head + struct.pack("BBBBBB", group, illumination, hSpeed, vSpeed, hDirection, vDirection) + tail
            self._s.sendall(str)
            time.sleep(sleep_period)
            self._s.sendall(str)
            time.sleep(sleep_period)
