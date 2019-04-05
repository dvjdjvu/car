#!/usr/bin/python3
#-*- coding: utf-8 -*-

import time
from threading import Thread 

# Import the ADS1x15 module.
import Adafruit_ADS1x15

class Joystick(Thread):
    x = 0.0
    y = 0.0
    xZero = 4.5 
    yZero = 4.5
    valueMax = 26500
    valueStep = 2944
    
    clientThread = None
    
    def setClientThread(self, clientThread):
        self.clientThread = clientThread    
    
    def __init__(self, window):
        Thread.__init__(self) 
        
        self.window = window    
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.GAIN = 1
        
    def run(self):
        while True:
            X = self.adc.read_adc(0, gain=self.GAIN) / self.valueStep
            Y = self.adc.read_adc(1, gain=self.GAIN) / self.valueStep
            
            if X > self.xZero :
                X = X - self.xZero
            else :
                X = -1 * (self.xZero - X)
            
            if Y > self.yZero :
                Y = Y - self.yZero
            else :
                Y = -1 * (self.yZero - Y)
            
            if (abs(self.x - X) >= 0.3 or abs(self.y - Y) >= 0.3) :
                print(round(X, 1), round(Y, 1))
            
            self.x = X
            self.y = Y
            
            time.sleep(0.1)
        