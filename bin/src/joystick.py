#!/usr/bin/python3
#-*- coding: utf-8 -*-

import time
from threading import Thread 

# Import the ADS1x15 module.
import Adafruit_ADS1x15

class Joystick(Thread):
    x = 13435
    y = 13289
    
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
            X = self.adc.read_adc(0, gain=self.GAIN)
            Y = self.adc.read_adc(1, gain=self.GAIN)
            
            if (abs(self.x - X) > 500 or abs(self.y - Y) > 500) :
                print(X, Y)
            
            self.x = X
            self.y = Y
            
            time.sleep(0.1)
        