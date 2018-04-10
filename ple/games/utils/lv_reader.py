# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import zmq
import time
#import matplotlib.pyplot as plt

class LabviewReader:

    def __init__(self, port="5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.msg = "tcp://127.0.0.1"
        self.port = port
        self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        self.socket.connect(self.msg +":"+ self.port)
        self.result = []
        # self.socket.setsockopt_string(zmq.SUBSCRIBE, '')
        # self.socket.bind(self.msg +":"+ self.port)
        # poller = zmq.Poller()
        # poller.register(self.sub, zmq.POLLIN)
        # self.sock = dict(poller.poll(1000))
        print ("tcp ready, please activate the Labview component")
        print (self.msg,"port:",self.port)

    def get_data(self):
    #print ("waiting to get Data....")
        # time_start = time.time()
        try:
            message = self.socket.recv_multipart()
            msg = message[0].decode()
            data_recv = eval(msg) / 10000

            # self.socket.send(bytearray(str(1),'utf-8'))
            # time_end = time.time()
            # print ("data: " + str(data_recv))
            return data_recv
        except zmq.Again as e:
            # print("No message received yet from labview")
            # time.sleep(1)
            pass

    def get_num_data(self,num):
        """
        :param num: 
        :return: 
        """
        i = 0
        self.result = []
        while i < num:
            self.result.append(self.get_data())
            i += 1
        return self.result

    def get_slide_num_data(self,num,slide_num):
        i = 0
        while len(self.result) < (num+slide_num):
            self.result.append(self.get_data())
        else:
            self.result = self.result[slide_num:]
        return self.result