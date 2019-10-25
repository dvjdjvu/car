#!/usr/bin/python3
#-*- coding: utf-8 -*-

from threading import Timer
from PyQt5.QtCore import QThread, pyqtSignal

from CarStatus import *

class tickEvent(QThread):
    """
    Класс управления машиной.
    Для управления будет использоваться 2-ва состояния, фактическое и пользовательское.
    Фактическое состояние, в котором машина находится (с какой скоростью движется, 
    направление движения, состояние поворота колес).
    Пользовательское состояние, в каком находится пульт управления (в каком положении джойстик аксилиратора и т.п.)
    
    Два состояния нужны для сглаживания управления, т.к. без него будет резкий отклик на изменении состояния акселератора.
    (Машинка будет с максимальной скорости тут же тормозить, с 0-я максимально ускоряться)
    Что негативно скажется на механических элементах машины.
    
    Система управления будет сделана на таймере. 
    На каждом новом тике фактическое состояние будет плавно доводиться до пользовательского.
    """
    
    signalSendStatus = pyqtSignal(object)
    signalSendStatus.connect(self.newStatus)
    
    statusActual = CarStatus().statusCar
    statusUser   = CarStatus().statusCar
    
    def __init__(self, time = 2):
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

        if statusActual['car']['speed'] != statusUser['car']['speed'] :
            pass
        
        self.start()
        
    def newStatus(self, status):
        self.statusUser = status
        
        if statusActual['car']['turn'] != statusUser['car']['turn'] :
            statusActual['car']['turn'] = statusUser['car']['turn']
        
        if statusActual['car']['light'] != statusUser['car']['light'] :
            statusActual['car']['light'] = statusUser['car']['light']
        
        self.start()

if __name__ == "__main__":

    tE = tickEvent()
    
