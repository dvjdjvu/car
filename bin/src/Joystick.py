#!/usr/bin/python3
#-*- coding: utf-8 -*-

import time
from threading import Thread 
from PyQt5.QtCore import QThread, pyqtSignal

# Import the ADS1x15 module.
import Adafruit_ADS1x15

from HardwareSetting import HardwareSetting 

class Joystick(QThread, HardwareSetting):
    x = 0.0
    y = 0.0
    
    signalSendCmd = pyqtSignal(object)
    
    def __init__(self, parent = None):
        #Thread.__init__(self) 
        QThread.__init__(self, parent) 
         
        self.adc = Adafruit_ADS1x15.ADS1115()
        self.GAIN = 1
        
    def run(self):
        while True:
            X = self.adc.read_adc(0, gain=self.GAIN) / HardwareSetting.valueStep
            Y = self.adc.read_adc(1, gain=self.GAIN) / HardwareSetting.valueStep
            
            if X > HardwareSetting.xZero :
                X = X - HardwareSetting.xZero
            else :
                X = -1 * (HardwareSetting.xZero - X)
            
            if Y > HardwareSetting.yZero :
                Y = Y - HardwareSetting.yZero
            else :
                Y = -1 * (HardwareSetting.yZero - Y)
            
            if (abs(self.x - X) >= 0.05 or abs(self.y - Y) >= 0.05) :
                #print(round(X, 1), round(Y, 1))
                self.sendCmd(round(X, 1), round(Y, 1))
            
            self.x = X
            self.y = Y
            
            time.sleep(0.05)
        
    def sendCmd(self, x, y):
        cmd = {}
        cmd['type'] = 'remote'
        cmd['cmd'] = 'turn'
        cmd['x'] = x
        cmd['y'] = y
        
        self.signalSendCmd.emit(cmd)
