#!/usr/bin/python3
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO                 # Импортируем библиотеку по работе с GPIO
import time                             # Импортируем класс для работы со временем
import sys, traceback                   # Импортируем библиотеки для обработки исключений
import os

class GHK():
    
    #pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]
    pins = [4, 5, 6, 13, 19, 26, 18, 23, 12, 16, 20, 21]
    
    Bouncetime = 50
    pins = None

    def __init__(self):
        self.pins = {4 :  {'pin': 'Select', 'status': False, 'callback': self.callbackSelect}, 
                     5 :  {'pin': 'Up',     'status': False, 'callback': self.callbackUp}, 
                     6 :  {'pin': 'Down',   'status': False, 'callback': self.callbackDown}, 
                     13 : {'pin': 'Left',   'status': False, 'callback': self.callbackLeft}, 
                     19 : {'pin': 'Right',  'status': False, 'callback': self.callbackRight}, 
                     26 : {'pin': 'A',      'status': False, 'callback': self.callbackA},  
                     18 : {'pin': 'TR',     'status': False, 'callback': self.callbackTR}, 
                     23 : {'pin': 'TL',     'status': False, 'callback': self.callbackTL}, 
                     12 : {'pin': 'B',      'status': False, 'callback': self.callbackB}, 
                     16 : {'pin': 'X',      'status': False, 'callback': self.callbackX}, 
                     20 : {'pin': 'Y',      'status': False, 'callback': self.callbackY}, 
                     21 : {'pin': 'Start',  'status': False, 'callback': self.callbackStart}
                     }         
        
        # Инициализация пинов
        GPIO.setmode(GPIO.BCM)
    
        for pin in self.pins:
            p = self.pins[pin]
            
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)        
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=p['callback'], bouncetime=self.Bouncetime)
    
    def callbackSelect(self, pin) :
        p = self.pins[pin]
        p['status'] = not p['status']
        print('press', p['pin'], p['status'])
    
    def callbackUp(self, pin) :
        print('press', pin)
    
    def callbackDown(self, pin) :
        print('press', pin)
    
    def callbackLeft(self, pin) :
        print('press', pin)
    
    def callbackRight(self, pin) :
        print('press', pin)
    
    def callbackA(self, pin) :
        print('press', pin)
    
    def callbackTR(self, pin) :
        print('press', pin)
    
    def callbackTL(self, pin) :
        print('press', pin)
    
    def callbackB(self, pin) :
        print('press', pin)
    
    def callbackX(self, pin) :
        print('press', pin)
    
    def callbackY(self, pin) :
        print('press', pin)
    
    def callbackStart(self, pin) :
        print('press', pin)
   

keyboard = GHK()
        
while True:                    
    time.sleep(5.1)
           
os._exit(0)