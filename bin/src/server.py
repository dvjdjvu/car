#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Server is stay in GAZ-66.

import sys, time
import socket
import json
from threading import Thread 
from socketserver import ThreadingMixIn 

import RPi.GPIO as GPIO

import os
import sys
sys.path.append('../../conf')

import conf

conn = None

class PWM:
    def __init__(self, pin):
        self.pin = pin

    def set(self, value):
        cmd = 'echo "%d=%.2f" > /dev/pi-blaster' % (self.pin, value)
        os.system(cmd)


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
            (conn, (ip, port)) = self.tcpServer.accept() 
            newthread = ClientThread(ip, port) 
            newthread.start() 
            self.threads.append(newthread)         

    def wait(self):
        for t in self.threads: 
            t.join() 

# Класс отвечает за обработку команд пульта управления.
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

        #self.gpioMove = 24
        #self.PWMmove = PWM(self.gpioMove)
        
        # Управление L298
        self.L298_IN1 = 23
        self.L298_IN2 = 24
        self.L298_ENB = 25
        
        self.PWMmove = PWM(self.L298_ENB)
        self.PWMmove.set(0)
        
        GPIO.setup(self.L298_IN1, GPIO.OUT)
        GPIO.output(self.L298_IN1, GPIO.LOW)
        
        GPIO.setup(self.L298_IN2, GPIO.OUT)
        GPIO.output(self.L298_IN2, GPIO.LOW)    

    def __del__(self):
        GPIO.output(self.gpioLight, GPIO.LOW)
        
        GPIO.output(self.L298_IN1, GPIO.LOW)
        GPIO.output(self.L298_IN2, GPIO.LOW)
        self.PWMmove.set(0)
        
        GPIO.cleanup()

    def run(self): 
        while True : 
            global conn
            data = conn.recv(2048)
            data = data.decode()
            if data == '' :
                break
            
            # Обработка полученных команд.
            print(data)
            data = data.replace('}{', '}\n\n{')
            data = data.split('\n\n')
            
            for i in data:
                cmd = json.loads(i)
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
                # Повысить передачу.
                elif cmd['cmd'] == 'X':
                    pass
                # Понизить передачу.
                elif cmd['cmd'] == 'B':
                    pass
                elif cmd['cmd'] == 'move':
                    speed = cmd['x']
                
                    if speed == 0 :
                        GPIO.output(self.L298_IN1, GPIO.LOW)
                        GPIO.output(self.L298_IN2, GPIO.LOW)
                    elif speed > 0 :
                        GPIO.output(self.L298_IN2, GPIO.LOW)
                        GPIO.output(self.L298_IN1, GPIO.HIGH)
                        self.PWMmove.set(speed / 4.5)
                    
                    else :
                        GPIO.output(self.L298_IN1, GPIO.LOW)
                        GPIO.output(self.L298_IN2, GPIO.HIGH)
                        self.PWMmove.set(speed / 4.5)
            
                conn.send(json.dumps(answer, ensure_ascii=False).encode())
            

    def handler(self):
        pass

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()