#!/usr/bin/python3
#-*- coding: utf-8 -*-

class HardwareSetting:
    # Максимальные углы поворота колес. Значения сервопривода.
    #_turnCenter = 150
    #_turnLeft   = 195
    #_turnRight  = 105
    #_turnDelta  = 40
    
    _turnCenter = 307
    _turnLeft   = 369
    _turnRight  = 245
    _turnDelta  = 62    
        
    # Отклонение по X имеет значение от 0 до 100
    xZero = 100
    # Отклонение по Y(поворот колес) имеет значение от 0 до 100
    yZero = 100
    
    # Максимальное значение резисторов на джойстике управления.
    valueMax = 26500
    # Шаг изменения состояния резистора.
    valueStep = 265 / 2
        
    #Максимальные скоростные значения.
    _moveForward = 1.0
    _moveBack = -1.0   
        