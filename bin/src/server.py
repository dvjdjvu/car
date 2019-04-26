#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Server is stay in GAZ-66.

import time
import wiringpi

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
        pass

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

    # Максимальные углы поворота колес.
    _turnCenter = 150
    _turnLeft   = 190
    _turnRight  = 110
    _turnDelta  = 40
    
    #Максимальные скоростные значения.
    _moveForward = 4.5
    _moveBack = -4.5
    

    def __init__(self, ip, port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print("[+] New server socket thread started for " + ip + ":" + str(port))      
        
        GPIO.cleanup() 
        # Инициализация пинов
        GPIO.setmode(GPIO.BCM)
        
        self.statusLight = False
        
        self.gpioLight = 17
        #wiringpi.pinMode(self.gpioLight, wiringpi.GPIO.PWM_OUTPUT)
        GPIO.setup(self.gpioLight, GPIO.OUT)
        GPIO.output(self.gpioLight, GPIO.LOW)
        
        # Управление L298, мотор движения машинки.
        self.L298_IN1 = 23
        self.L298_IN2 = 24
        self.L298_ENB = 25
        
        # Управление сервоприводом поворота колес
        self.SERVO = 18
        
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(self.L298_ENB, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pinMode(self.SERVO, wiringpi.GPIO.PWM_OUTPUT)
        
        wiringpi.softPwmCreate(self.L298_ENB, 0, 200)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)          
            
        
        GPIO.setup(self.L298_IN1, GPIO.OUT)
        GPIO.output(self.L298_IN1, GPIO.LOW)
        
        GPIO.setup(self.L298_IN2, GPIO.OUT)
        GPIO.output(self.L298_IN2, GPIO.LOW)    

    def __del__(self):
        GPIO.output(self.gpioLight, GPIO.LOW)
        
        self.moveStop()
        self.turnCenter()
        
        GPIO.cleanup()

    def moveStop(self):
        GPIO.output(self.L298_IN1, GPIO.LOW)
        GPIO.output(self.L298_IN2, GPIO.LOW)
        
    def moveForward(self, speed):
        GPIO.output(self.L298_IN2, GPIO.LOW)
        GPIO.output(self.L298_IN1, GPIO.HIGH)    
        wiringpi.softPwmWrite(self.L298_ENB, int(100 * speed / 4.5))
        
    def moveBack(self, speed):
        GPIO.output(self.L298_IN1, GPIO.LOW)
        GPIO.output(self.L298_IN2, GPIO.HIGH)
        wiringpi.softPwmWrite(self.L298_ENB, int(-100 * speed / 4.5))
        
    def turnCenter(self):
        wiringpi.pwmWrite(self.SERVO, int(self._turnCenter))
        
    def turnLeft(self, turn):
        wiringpi.pwmWrite(self.SERVO, int(self._turnCenter + (-1 * turn * self._turnDelta / 4.5)))
        
    def turnRight(self, turn):
        wiringpi.pwmWrite(self.SERVO, int(self._turnCenter + (-1 * turn * self._turnDelta / 4.5)))

    def run(self): 
        while True : 
            global conn
            data = conn.recv(2048)
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
                        if self.statusLight == False :
                            # Включить свет.
                            GPIO.output(self.gpioLight, GPIO.HIGH)
                        else :
                            # Выключить свет.
                            GPIO.output(self.gpioLight, GPIO.LOW)
                        
                        self.statusLight = not self.statusLight
                        answer['status'] = self.statusLight
                # Движение вперед.
                elif cmd['cmd'] == 'X':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveForward(self._moveForward)
                    else :
                        self.moveStop()
                # Движение назад.
                elif cmd['cmd'] == 'B':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveBack(self._moveBack)
                    else :
                        self.moveStop()                    
                elif cmd['cmd'] == 'move':
                    '''
                    speed = cmd['x']
                    if speed == 0 :
                        self.moveStop()
                    elif speed > 0 :
                        self.moveForward(self, speed)
                    elif speed < 0 :
                        self.moveBack(self, -speed)
                    ''' 
                    
                    turn = cmd['y']
                    if turn == 0 :
                        self.turnCenter()
                    elif turn > 0 : # Право
                        self.turnRight(turn)
                    elif turn < 0 : # Лево
                        self.turnLeft(turn)
                                              
                conn.send(json.dumps(answer, ensure_ascii=False).encode())

    def handler(self):
        pass

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()