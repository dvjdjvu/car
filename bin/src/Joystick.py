#!/usr/bin/python3
#-*- coding: utf-8 -*-

import time
from PyQt5.QtCore import QThread, pyqtSignal

# Import the ADS1x15 module.
try :
    import Adafruit_ADS1x15 as Adafruit
except (ImportError, RuntimeError) :
    import emulator as Adafruit
    

from HardwareSetting import HardwareSetting 

class Joystick(QThread, HardwareSetting):
    x = 0.0
    y = 0.0
    
    sx = 0.0
    sy = 0.0
    
    deltaMin = 1.0
    deltaMax = 5
    
    signalSendCmd = pyqtSignal(object)
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent) 
         
        self.adc = Adafruit.ADS1115()
        self.GAIN = 1
        
    def run(self):
        while True:
            # Джойстик поворота колес
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
            
            if (abs(X) < self.deltaMax) :
                X = 0
            if (abs(Y) < self.deltaMax) :
                Y = 0
        
            if (abs(self.x - X) >= self.deltaMin or abs(self.y - Y) >= self.deltaMin) :
                #print(round(X, 1), round(Y, 1))
                #print('x {} y {}'.format(round(X), round(Y)))
                self.sendCmd('turn', round(X), round(Y))
            
            self.x = X
            self.y = Y
            
            # Джойстик скорости движения
            SX = self.adc.read_adc(2, gain=self.GAIN) / HardwareSetting.valueStep
            SY = self.adc.read_adc(3, gain=self.GAIN) / HardwareSetting.valueStep
            
            if SX > HardwareSetting.xZero :
                SX = SX - HardwareSetting.xZero
            else :
                SX = -1 * (HardwareSetting.xZero - SX)
            
            # Джойстик стоит задом на перед.
            if SY > HardwareSetting.yZero :
                SY = SY - HardwareSetting.yZero
            else :
                SY = -1 * (HardwareSetting.yZero - SY)
            
            SY = -1 * SY
            
            if (abs(SX) < self.deltaMax) :
                SX = 0
            if (abs(SY) < self.deltaMax) :
                SY = 0
        
            if (abs(self.sx - SX) >= self.deltaMin or abs(self.sy - SY) >= self.deltaMin) :
                #print(round(X, 1), round(Y, 1))
                #print('x {} y {}'.format(round(X), round(Y)))
                # Джойстик стоит осями вверх ногами.
                self.sendCmd('speed', SY/100.0, SX/100.0)
            
            self.sx = SX
            self.sy = SY
            
            time.sleep(HardwareSetting.joystickTime)
        
    def sendCmd(self, _cmd, x, y):
        cmd = {}
        cmd['type'] = 'remote'
        cmd['cmd'] = _cmd
        cmd['x'] = x
        cmd['y'] = y
        
        self.signalSendCmd.emit(cmd)
