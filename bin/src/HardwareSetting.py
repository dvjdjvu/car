#!/usr/bin/python3
#-*- coding: utf-8 -*-

class HardwareSetting:
    
    def __init__(self):
        # Максимальные углы поворота колес. Значения сервопривода.
        #self._turnCenter = 150
        #self._turnLeft   = 195
        #self._turnRight  = 105
        #self._turnDelta  = 40
    
        self._turnCenter = 307
        self._turnLeft   = 369
        self._turnRight  = 245
        self._turnDelta  = 62    
        
        # Отклонение по X имеет значение от 0 до 100
        self.xZero = 100
        # Отклонение по Y(поворот колес) имеет значение от 0 до 100
        self.yZero = 100
    
        # Максимальное значение резисторов на джойстике управления.
        self.valueMax = 26500
        # Шаг изменения состояния резистора.
        self.valueStep = 265/2
        
        #Максимальные скоростные значения.
        self._moveForward = 1.0
        self._moveBack = -1.0   
        