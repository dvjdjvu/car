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
from HardwareSetting import HardwareSetting 

class PWM:
    def __init__(self, pin):
        self.pin = pin

    def set(self, value):
        cmd = 'echo "%d=%.2f" > /dev/pi-blaster' % (self.pin, value)
        os.system(cmd) 

class CarStatus:
    def __init__(self):
        self.status = {}
        
        self.status['light'] = False
        self.status['move'] = 0
        self.status['turn'] = 0
    
    def __del__(self):
        return

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
        print("[+] New server socket thread started for " + ip + ":" + str(port))      
        
        # Класс состояния машинки.
        self.CarStatus = CarStatus()
        
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
        
        wiringpi.softPwmCreate(self.L298_ENB, 0, 100)
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
        
        self.CarStatus.status['move'] = 0
        
    def moveForward(self, speed):
        GPIO.output(self.L298_IN2, GPIO.LOW)
        GPIO.output(self.L298_IN1, GPIO.HIGH)
        
        val = int(100 * speed / HardwareSetting._moveForward)
        print('val', val)
        wiringpi.softPwmWrite(self.L298_ENB, val)
        self.CarStatus.status['move'] = val
        
    def moveBack(self, speed):
        GPIO.output(self.L298_IN1, GPIO.LOW)
        GPIO.output(self.L298_IN2, GPIO.HIGH)
        
        val = int(100 * speed / HardwareSetting._moveBack)
        wiringpi.softPwmWrite(self.L298_ENB, val)
        self.CarStatus.status['move'] = val
        
    def turnCenter(self):
        val = int(HardwareSetting._turnCenter)
        wiringpi.pwmWrite(self.SERVO, val)
        self.CarStatus.status['turn'] = val
        
    def turnLeft(self, turn):
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        wiringpi.pwmWrite(self.SERVO, val)
        self.CarStatus.status['turn'] = val
        
    def turnRight(self, turn):
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        wiringpi.pwmWrite(self.SERVO, val)
        self.CarStatus.status['turn'] = val

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
                        if self.statusLight == False :
                            # Включить свет.
                            GPIO.output(self.gpioLight, GPIO.HIGH)
                        else :
                            # Выключить свет.
                            GPIO.output(self.gpioLight, GPIO.LOW)
                        
                        self.statusLight = not self.statusLight
                        
                        self.CarStatus.status['light'] = self.statusLight
                        answer['status'] = self.statusLight
                # Движение вперед. Частичное 0.75
                elif cmd['cmd'] == 'X':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveForward(cmd['val'] * HardwareSetting._moveForward)
                    else :
                        self.moveStop()
                # Движение вперед. Частичное 0.5
                elif cmd['cmd'] == 'Y':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveForward(cmd['val'] * HardwareSetting._moveForward)
                    else :
                        self.moveStop()
                # Движение вперед. Полное 1
                elif cmd['cmd'] == 'A':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveForward(cmd['val'] * HardwareSetting._moveForward)
                    else :
                        self.moveStop()
                # Движение назад. Частичное 0.66
                elif cmd['cmd'] == 'B':
                    print(cmd)
                    if cmd['status'] == True :
                        self.moveBack(cmd['val'] * HardwareSetting._moveBack)
                    else :
                        self.moveStop()
                elif cmd['cmd'] == 'turn':
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
                                              
                self.conn.send(json.dumps(answer, ensure_ascii=False).encode())

    def handler(self):
        pass

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()