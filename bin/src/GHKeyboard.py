#!/usr/bin/python3
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO                 # Импортируем библиотеку по работе с GPIO
import time                             # Импортируем класс для работы со временем
import sys, traceback                   # Импортируем библиотеки для обработки исключений
import os

from threading import Thread 
from PyQt5.QtCore import QThread, pyqtSignal
from HardwareSetting import HardwareSetting 

import time
import json
import socket

class GHK(QThread):
    
    signalSendCmd = pyqtSignal(object)
    
    def run(self):
        try:
            while True:
                time.sleep(HardwareSetting.keyboardTime)
                for pin in self.pins :
                    p = self.pins[pin]
                    
                    status = p['status']
                    
                    if GPIO.input(pin) == GPIO.HIGH :
                        p['status'] = False
                    else :
                        p['status'] = True
                        
                    if p['status'] != status :
                        p['callback'](pin, status)
            
        except KeyboardInterrupt:
            GPIO.cleanup()    
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent) 
        
        self.pins = {4 :  {'pin': 'Select', 'description' : '', 'status': False, 'callback': self.callbackSelect, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     5 :  {'pin': 'Up',     'description' : '', 'status': False, 'callback': self.callbackUp, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     6 :  {'pin': 'Down',   'description' : '', 'status': False, 'callback': self.callbackDown, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     13 : {'pin': 'Left',   'description' : '', 'status': False, 'callback': self.callbackLeft, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     19 : {'pin': 'Right',  'description' : '', 'status': False, 'callback': self.callbackRight, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     26 : {'pin': 'A',      'description' : '', 'status': False, 'callback': self.callbackA, 'Bouncetime': 100, 'input': GPIO.BOTH},  
                     18 : {'pin': 'TR',     'description' : '', 'status': False, 'callback': self.callbackTR, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     23 : {'pin': 'TL',     'description' : '', 'status': False, 'callback': self.callbackTL, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     12 : {'pin': 'B',      'description' : '', 'status': False, 'callback': self.callbackB, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     16 : {'pin': 'X',      'description' : 'Лебедка разматать', 'status': False, 'callback': self.callbackX, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     20 : {'pin': 'Y',      'description' : 'Лебедка тащить',  'status': False, 'callback': self.callbackY, 'Bouncetime': 100, 'input': GPIO.BOTH}, 
                     21 : {'pin': 'Start',  'description' : 'свет', 'status': False, 'callback': self.callbackStart, 'Bouncetime': 400, 'input': GPIO.BOTH}
                     }
        
        # Инициализация пинов
        GPIO.setmode(GPIO.BCM)
        
        for pin in self.pins:
            p = self.pins[pin]
            
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        
            #GPIO.add_event_detect(pin, p['input'], callback=p['callback'])#, bouncetime=p['Bouncetime'])
            #GPIO.add_event_detect(pin, GPIO.RISING, callback=p['callback'])#, bouncetime=self.Bouncetime)
            #GPIO.add_event_detect(pin, GPIO.FALLING, callback=p['callback'])#, bouncetime=self.Bouncetime) 
    
    def __del__(self):    
        GPIO.cleanup()    
    
    def sendCmd(self, p, pin, val = 0.0):
        cmd = {}
        cmd['type'] = 'remote'
        cmd['cmd'] = pin['pin']
        cmd['status'] = pin['status']
        cmd['val'] = val
        
        self.signalSendCmd.emit(cmd)
    
    def callbackSelect(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackUp(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackDown(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackLeft(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackRight(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackA(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackTR(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackTL(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackB(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
    
    def callbackX(self, pin, status) :
        if not status :
            self.sendCmd(pin, self.pins[pin], 1.0)
        else :
            self.sendCmd(pin, self.pins[pin], 0.0)
    
    def callbackY(self, pin, status) :
        if not status :
            self.sendCmd(pin, self.pins[pin], -1.0)
        else :
            self.sendCmd(pin, self.pins[pin], 0.0)
    
    def callbackStart(self, pin, status) :
        self.sendCmd(pin, self.pins[pin])
   