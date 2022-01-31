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
from datetime import datetime

from helper.log import log

###import RPi.GPIO as GPIO
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
        
        # Управление через tickEvent
        self.TE = tickEvent.tickEvent()
        
        context = zmq.Context()
        self.tcpServer = context.socket(zmq.PAIR)
        self.tcpServer.bind("tcp://" + conf.conf.ServerIP + ":" + str(conf.conf.controlServerPort))
        
    def __del__(self):
        # Потеря связи или прекращение работы, отключение машинки
        if self.TE :
            self.TE.newStatus(carStatusDefault.statusCar)

    def run(self):
        # Защита от частого срабатывания, проверяем на потерю связи каждые dt_check сек.
        dt_last_data = time.time()
        
        cmd = None
        
        while True:
            data = None
            dt_now = time.time()
            
            if self.tcpServer.poll(self.tcpServerTimeWait, zmq.POLLIN):
                data = self.tcpServer.recv(zmq.NOBLOCK).decode()
            
            if data == None :
                dt_diff = dt_now - dt_last_data

                if (dt_diff >= conf.conf.dt_check) :
                    # Вслучае потери связи, машинка останавливается.
                    self.TE.newStatus(carStatusDefault.statusCar)
                    log.Print('[warning]: signal from the remote lost')
                
                continue
            else :
                dt_last_data = dt_now
            
            # Обработка полученных команд.
            data = data.replace('}{', '}\n\n{')
            data = data.split('\n\n')
            
            for i in data:
                try:
                    cmd = json.loads(i)
                except:                
                    continue
            
            carStatus.statusCar = cmd
            # Ответ клиенту, о том что посылка получена (отправляем что и приняли).
            self.tcpServer.send_string(json.dumps(cmd, ensure_ascii=False))
                
            #print(cmd)

            # Т.к. в цикле мы избавляемся от флуда команд. 
            # Здесь Будет передано последнее актуальное состояние.
            log.Print('[info]: data:', carStatus.statusCar)
            self.TE.newStatus(carStatus.statusCar)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()