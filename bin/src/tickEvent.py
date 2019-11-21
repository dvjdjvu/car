#!/usr/bin/python3
#-*- coding: utf-8 -*-

from CarStatus import *
import HardwareControl
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from threading import Timer

class tickEvent(QThread):
    """
    Класс управления машиной.
    Для управления будет использоваться 2-ва состояния, фактическое и пользовательское.
    Фактическое состояние, в котором машина находится (с какой скоростью движется, 
    направление движения, состояние поворота колес).
    Пользовательское состояние, в каком находится пульт управления (в каком положении джойстик аксилиратора, управления колес и т.п.)
    
    Два состояния нужны для сглаживания управления, т.к. без него будет резкий отклик на изменение состояния акселератора.
    (Машинка будет с максимальной скорости тут же тормозить, с места максимально ускоряться. Что дает нежелательный рывок и доп. нугрузку на трансмиссию)
    Что негативно скажется на механических элементах машины.
    
    Система управления будет сделана на таймере. 
    На каждом новом тике фактическое состояние будет пошагово доводиться до пользовательского.
    """
    
    signalSendStatus = pyqtSignal(object)
    signalSendStatus.connect(self.newStatus)
    
    statusActual = CarStatus().statusCar
    statusUser   = CarStatus().statusCar
    
    HC = HardwareControl.HardwareControl()
    
    # шаг плавности изменения хода
    step = 0.10
    stepStart = 0.15
    
    def __init__(self, time=2):
        """
        Инициализация
        
        Args:
            time: Время между тиками в миллисекундах.
        """
        
        self.time = time
        
        self.start()
    
    def __del__(self):
        """
        Деструктор
        """
        self.timer.cancel()

    def start(self):
        self.timer = Timer(self.time, self.update)
        self.timer.start()

    def update(self):
        """
        Работает по таймеру.
        Пока что эта функция отвечает только за обработку скорости и направления
        движения.
        """
        
        sA = statusActual['car']['speed']
        sU = statusUser['car']['speed']
        delta = sU - sA
        
        step = self.step
        if delta < self.step:
            step = delta
        
        if sA < sU:
            sA += step
            if sA == 0:
                HC.moveStop()
            elif sA < 0.0:
                HC.moveBack(sA * (1 - self.stepStart) + self.stepStart)
            elif sA > 0.0:
                HC.moveForward(sA * (1 - self.stepStart) + self.stepStart)
                
        if sA > sU:
            sA -= step
            if sA == 0:
                HC.moveStop()
            elif sA < 0.0:
                HC.moveBack(sA * (1 - self.stepStart) + self.stepStart)
            elif sA > 0.0:
                HC.moveForward(sA * (1 - self.stepStart) + self.stepStart)
            
            #if sA == 0 :
            #    HC.moveStop()        
            #elif sA > 0 : # Вперед            
            #    HC.moveForward(speed * (1 - self.stepStart) + self.stepStart)
            #elif sA < 0 : # Назад
            #    HC.moveBack(speed * (1 - self.stepStart) + self.stepStart)
        
        statusActual['car']['speed'] = sA
        
        self.start()
        
    def newStatus(self, status):
        """
        server.py послылает в newStatus сигнал содержащий пользовательское состояние управления(состоние пульта управления)
        """
        self.statusUser = status
        
        # Поворот колес обрабатывается моментально т.к. сервопривод имеет механические задержки в работе.
        # За счет чего достигается плавность поворота колес.
        if statusActual['car']['turn'] != statusUser['car']['turn']:
            statusActual['car']['turn'] = statusUser['car']['turn']
            
            if statusActual['car']['turn'] == 0: # Колеса ровно
                HC.turnCenter()
            elif statusActual['car']['turn'] > 0: # Право
                HC.turnRight(turn)
            elif statusActual['car']['turn'] < 0: # Лево
                HC.turnLeft(turn)
            
        # Включение и выключение фар так же можно делать в режиме реального времени.
        if statusActual['car']['light'] != statusUser['car']['light']:
            statusActual['car']['light'] = statusUser['car']['light']
            
            HC.lightSet(statusActual['car']['light'])
        
        self.start()

if __name__ == "__main__":

    tE = tickEvent()
    
