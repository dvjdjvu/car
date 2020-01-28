#!/usr/bin/python3
#-*- coding: utf-8 -*-

class HardwareSetting:
    # Максимальные углы поворота колес. Значения сервопривода.    
    _turnCenter = 307
    _turnDelta  = 75
    _turnLeft   = _turnCenter + _turnDelta
    _turnRight  = _turnCenter - _turnDelta
    
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
        