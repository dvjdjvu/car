#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Server is stay in GAZ-66.

import sys, time
import socket
import json
from threading import Thread 
from socketserver import ThreadingMixIn 

import RPi.GPIO as GPIO

import sys
sys.path.append('../../conf')

import conf

conn = None

class ServerThread(Thread, conf.conf):
    tcpServer = None
    threads = [] 
    
    def __init__(self): 
        Thread.__init__(self) 
        
    def __del__(self):
        GPIO.cleanup()

    def run(self): 
        TCP_IP = conf.conf.ServerIP
        TCP_PORT = conf.conf.controlServerPort
        BUFFER_SIZE = conf.conf.ServerBufferSize
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.tcpServer.bind((TCP_IP, TCP_PORT)) 
        threads = [] 

        self.tcpServer.listen(4)
        while True:
            print("Car server up : Waiting for connections from TCP clients...") 
            global conn
            (conn, (ip,port)) = self.tcpServer.accept() 
            newthread = ClientThread(ip, port) 
            newthread.start() 
            self.threads.append(newthread)         

    def wait(self):
        for t in self.threads: 
            t.join() 


class ClientThread(Thread, conf.conf): 

    def __init__(self, ip, port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print("[+] New server socket thread started for " + ip + ":" + str(port)) 
        
        # Инициализация пинов
        GPIO.setmode(GPIO.BCM)
        
        self.statusLight = False
        
        self.gpioLight = 17
        GPIO.setup(self.gpioLight, GPIO.OUT)
        GPIO.output(self.gpioLight, GPIO.LOW)

    def __del__(self):
        GPIO.output(self.gpioLight, GPIO.LOW)
        GPIO.cleanup()

    def run(self): 
        while True : 
            global conn
            data = conn.recv(2048)
            data = data.decode()
            if data == '' :
                break
            
            # Дальше здесь будут обрабатываться полученные команды.
            
            cmd = json.loads(data)
            print(cmd)
            
            answer = {}
            answer['type'] = 'car'
            answer['cmd'] = cmd['cmd']            
            
            # Свет.
            if cmd['cmd'] == 'Start':
                if cmd['status'] == True :
                    if self.statusLight == False :
                        # Включить свет.
                        GPIO.output(self.gpioLight, GPIO.HIGH)
                    else :
                        # Выключить свет.
                        GPIO.output(self.gpioLight, GPIO.LOW)
                        
                    self.statusLight = not self.statusLight
                    answer['status'] = self.statusLight
                    
            conn.send(json.dumps(answer, ensure_ascii=False).encode())
            

    def handler(self):
        pass

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()