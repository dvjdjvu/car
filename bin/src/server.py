#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Server is stay in GAZ-66.

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
    threads = [] 
    
    def __init__(self): 
        Thread.__init__(self) 
        
    def __del__(self):
        pass

    def run(self): 
        TCP_IP = conf.conf.ServerIP
        TCP_PORT = conf.conf.controlServerPort
        BUFFER_SIZE = conf.conf.ServerBufferSize
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.tcpServer.bind((TCP_IP, TCP_PORT)) 
        threads = [] 

        # Максимальное колличество подключений в очереди.
        self.tcpServer.listen(1)
        while True:
            print("Car server up : Waiting for connections from TCP clients...") 
            (conn, (ip, port)) = self.tcpServer.accept() 
            newthread = ClientThread(conn, ip, port) 
            newthread.start() 
            self.threads.append(newthread)         

    def wait(self):
        for t in self.threads: 
            t.join() 

# Класс отвечает за обработку команд пульта управления.
class ClientThread(Thread, conf.conf, HardwareSetting):    
    
    def __init__(self, conn, ip, port): 
        Thread.__init__(self) 
        self.conn = conn
        self.ip = ip 
        self.port = port 
        print("[+] Новое подключение " + ip + ":" + str(port))      
        
        # Управление через tickEvent
        self.TE = tickEvent.tickEvent()

    def __del__(self):
        pass

    def run(self): 
        while True : 
            data = self.conn.recv(2048)
            data = data.decode()
            if data == '' :
                break
            
            # Обработка полученных команд.
            #print(data)
            data = data.replace('}{', '}\n\n{')
            data = data.split('\n\n')
            
            #for i in reversed(data):
            for i in data:
                try:
                    cmd = json.loads(i)
                except:                
                    continue
                
                #print(cmd)
            
                answer = {}
                answer['type'] = 'car'
                answer['cmd'] = cmd['cmd']            
            
                # Свет.
                if cmd['cmd'] == 'Start':
                    print(cmd)
                    if cmd['status'] == True :                        
                        self.statusLight = not self.statusLight
                        
                        CarStatus.statusCar['car']['light'] = self.statusLight
                elif cmd['cmd'] == 'speed':
                    speed = cmd['x']
                    CarStatus.statusCar['car']['speed'] = speed
                elif cmd['cmd'] == 'turn':
                    turn = cmd['y']
                    CarStatus.statusCar['car']['turn'] = turn
                        
                answer['state'] = CarStatus.statusCar['car']
                self.conn.send(json.dumps(answer, ensure_ascii=False).encode())
            
            # Т.к. не в цикле, то мы избавляемся от флуда команд. 
            # Будет передано последнее актуальное состояние.
            self.TE.signalSendStatus.emit(CarStatus.statusCar)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()