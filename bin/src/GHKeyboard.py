#!/usr/bin/python3
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO                 # Импортируем библиотеку по работе с GPIO
import time                             # Импортируем класс для работы со временем
import sys, traceback                   # Импортируем библиотеки для обработки исключений
import os

from threading import Thread 
from PyQt5.QtCore import QThread, pyqtSignal

import json
import socket

class GHK(QThread):
    
    #pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
    pins = [4, 5, 6, 13, 19, 26, 18, 23, 12, 16, 20, 21]
    
    Bouncetime = 100
    pins = None

    signalSendCmd = pyqtSignal(object)
    
    def run(self):
        while True:
            time.sleep(5)
    
    def __init__(self, parent = None):
        #Thread.__init__(self) 
        QThread.__init__(self, parent) 
        
        self.pins = {4 :  {'pin': 'Select', 'description' : '', 'status': False, 'callback': self.callbackSelect, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     5 :  {'pin': 'Up',     'description' : '', 'status': False, 'callback': self.callbackUp, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     6 :  {'pin': 'Down',   'description' : '', 'status': False, 'callback': self.callbackDown, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     13 : {'pin': 'Left',   'description' : '', 'status': False, 'callback': self.callbackLeft, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     19 : {'pin': 'Right',  'description' : '', 'status': False, 'callback': self.callbackRight, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     26 : {'pin': 'A',      'description' : '', 'status': False, 'callback': self.callbackA, 'Bouncetime': 100, 'input': GPIO.BOTH},  
                     18 : {'pin': 'TR',     'description' : 'правый поворотник', 'status': False, 'callback': self.callbackTR, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     23 : {'pin': 'TL',     'description' : 'левый поворотник', 'status': False, 'callback': self.callbackTL, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     12 : {'pin': 'B',      'description' : 'понизить передачу', 'status': False, 'callback': self.callbackB, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     16 : {'pin': 'X',      'description' : 'повысить передачу', 'status': False, 'callback': self.callbackX, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     20 : {'pin': 'Y',      'description' : '',  'status': False, 'callback': self.callbackY, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     21 : {'pin': 'Start',  'description' : 'свет', 'status': False, 'callback': self.callbackStart, 'Bouncetime': 400, 'input': GPIO.BOTH}
                     }         
        
        # Инициализация пинов
        GPIO.setmode(GPIO.BCM)
    
        for pin in self.pins:
            p = self.pins[pin]
            
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        
            GPIO.add_event_detect(pin, p['input'], callback=p['callback'])#, bouncetime=p['Bouncetime'])
            #GPIO.add_event_detect(pin, GPIO.RISING, callback=p['callback'])#, bouncetime=self.Bouncetime)
            #GPIO.add_event_detect(pin, GPIO.FALLING, callback=p['callback'])#, bouncetime=self.Bouncetime)
    
    def sendCmd(self, p, pin):
        
        def retBool(x):
            if x == 1 :
                return False
            return True
        
        status = retBool(GPIO.input(p))
        
        if (pin['status'] != status):
            pin['status'] = status
            #print(pin['status'])
            
            cmd = {}
            cmd['type'] = 'remote'
            cmd['cmd'] = pin['pin']
            cmd['status'] = pin['status']
        
            self.signalSendCmd.emit(cmd)            
        
        return
        
    def callbackSelect(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackUp(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackDown(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackLeft(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackRight(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackA(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackTR(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackTL(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackB(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackX(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackY(self, pin) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackStart(self, pin) :
        self.sendCmd(pin, self.pins[pin])
   