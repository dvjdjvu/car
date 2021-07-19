#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Server is stay in GAZ-66.

import zmq
import time

import sys, time
import socket
import json
from threading import Thread 
from socketserver import ThreadingMixIn 

import RPi.GPIO as GPIO
import PWM

import os
import sys
sys.path.append('../../conf')

import conf
from HardwareSetting import HardwareSetting 

from CarStatus import * 

import tickEvent

class ServerThread(Thread, conf.conf):
    tcpServer = None
    tcpServerTimeWait = 200
    
    def __init__(self): 
        Thread.__init__(self) 
        self.TE = None
        
        context = zmq.Context()
        self.tcpServer = context.socket(zmq.PAIR)
        self.tcpServer.bind("tcp://" + conf.conf.ServerIP + ":" + str(conf.conf.controlServerPort))
        
        # Управление через tickEvent
        self.TE = tickEvent.tickEvent()
        
    def __del__(self):
        # Потеря связи или прекращение работы, отключение машинки
        if self.TE :
            self.TE.newStatus(carStatusDefault.statusCar)

    def run(self):
        while True:
            data = None
            
            if self.tcpServer.poll(self.tcpServerTimeWait, zmq.POLLIN):
                data = self.tcpServer.recv(zmq.NOBLOCK).decode()
            
            if data == None :
                #self.TE.newStatus(carStatusDefault.statusCar)
                
                continue
            
            # Обработка полученных команд.
            data = data.replace('}{', '}\n\n{')
            data = data.split('\n\n')
            
            for i in data:
                try:
                    cmd = json.loads(i)
                except:                
                    continue
                
                carStatus.statusCar = cmd
                self.tcpServer.send_string(json.dumps(cmd, ensure_ascii=False))
                
                #print(cmd)

            # Т.к. в цикле мы избавляемся от флуда команд. 
            # Здесь Будет передано последнее актуальное состояние.
            print(carStatus.statusCar)
            self.TE.newStatus(carStatus.statusCar)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()