import socket
import struct

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
        # first byte meaning
        self._start = 1
        self._stop = 2
        self._reset = 3
        self._illumination = 4
        self._vSpeed = 5
        self._hSpeed = 6
        self._hDirection = 7
        self._vDirection = 8

    def send(self, ops, *args):
        """
        :param ops: the type of operation
        :type ops: str
        :param *arge some operation's params
        """
        if ops == "start":
            str = struct.pack("B", self._start)
            self._s.sendall(str)
        elif ops == "stop":
            str = struct.pack("B", self._stop)
            self._s.sendall(str)
        elif ops == "reset":
            str = struct.pack("B", self._reset)
            self._s.sendall(str)
        elif ops == "illumination":
            illumination_value = args[0]
            if illumination_value == "" or illumination_value < 0 or illumination_value > 255:
                raise ValueError
            str = struct.pack("BB", self._illumination, illumination_value)
            self._s.sendall(str)
        elif ops == "vSpeed":
            speed_value = args[0]
            if speed_value == "" or speed_value < 0 or speed_value > 255:
                raise  ValueError
            str = struct.pack("BB", self._vSpeed, speed_value)
            self._s.sendall(str)
        elif ops == "hSpeed":
            speed_value = args[0]
            if speed_value == "" or speed_value < 0 or speed_value > 255:
                raise  ValueError
            str = struct.pack("BB", self._hSpeed, speed_value)
            self._s.sendall(str)
        elif ops == "hDirection":
            direction = args[0]
            if direction == "left":
                dir_byte = 0
            elif direction == "right":
                dir_byte = 1
            elif direction == "round":
                dir_byte = 2
            elif direction == "none":
                dir_byte = 3
            else:
                raise  ValueError
            str = struct.pack("BB", self._hDirection, dir_byte)
            self._s.sendall(str)
        elif ops == "vDirection":
            direction = args[0]
            if direction == "up":
                dir_byte = 0
            elif direction == "down":
                dir_byte = 1
            elif direction == "round":
                dir_byte = 2
            elif direction == "none":
                dir_byte = 3
            else:
                raise  ValueError
            str = struct.pack("BB", self._vDirection, dir_byte)
            self._s.sendall(str)
        else:
            raise ValueError


