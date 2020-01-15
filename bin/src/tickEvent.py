#!/usr/bin/python3
#-*- coding: utf-8 -*-

from CarStatus import *
import HardwareControl
from threading import Thread, Lock, Timer

class tickEvent(Thread):
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
    
    def __init__(self, time=2):
        """
        Инициализация
        
        Args:
            time: Время между тиками в миллисекундах.
        """
        
        self.mutex = Lock()
        
        self.statusActual = CarStatus().statusCar
        self.statusUser   = CarStatus().statusCar
    
        self.HC = HardwareControl.HardwareControl()
    
        # шаг плавности изменения хода
        self.step = 0.10
        self.stepStart = 0.15
        
        self.time = time
        
        self.start()
    
    def __del__(self):
        """
        Деструктор
        """
        #self.timer.cancel()

    def start(self):
        self.timer = Timer(self.time, self.update)
        self.timer.start()

    def update(self):
        """
        Работает по таймеру.
        Пока что эта функция отвечает только за обработку скорости и направления
        движения.
        """
        
        # Блокировка на получение данных
        self.mutex.acquire()
        
        sA = self.statusActual['car']['speed']
        sU = self.statusUser['car']['speed']
        delta = sU - sA
        
        self.mutex.release()
        
        step = self.step
        if delta < self.step:
            step = delta
        
        if sA < sU:
            sA += step
            if sA == 0:
                self.HC.moveStop()
            elif sA < 0.0:
                self.HC.moveBack(sA * (1 - self.stepStart) + self.stepStart)
            elif sA > 0.0:
                self.HC.moveForward(sA * (1 - self.stepStart) + self.stepStart)
                
        if sA > sU:
            sA -= step
            if sA == 0:
                self.HC.moveStop()
            elif sA < 0.0:
                self.HC.moveBack(sA * (1 - self.stepStart) + self.stepStart)
            elif sA > 0.0:
                self.HC.moveForward(sA * (1 - self.stepStart) + self.stepStart)
            
            #if sA == 0 :
            #    HC.moveStop()        
            #elif sA > 0 : # Вперед            
            #    HC.moveForward(speed * (1 - self.stepStart) + self.stepStart)
            #elif sA < 0 : # Назад
            #    HC.moveBack(speed * (1 - self.stepStart) + self.stepStart)
        
        self.statusActual['car']['speed'] = sA
        
        self.start()
        
    def newStatus(self, status):
        print("TC newStatus")
        print("self.statusUser", id(status))
        print("self.statusActual", id(self.statusActual))
        
        """
        server.py послылает в newStatus сигнал содержащий пользовательское состояние управления(состоние пульта управления)
        """
        
        # Блокировка на обновлении данных
        self.mutex.acquire()
        
        self.statusUser = status
        
        self.mutex.release()
        
        # Поворот колес обрабатывается моментально т.к. сервопривод имеет механические задержки в работе.
        # За счет чего достигается плавность поворота колес.
        if self.statusActual['car']['turn'] != self.statusUser['car']['turn']:
            self.statusActual['car']['turn'] = self.statusUser['car']['turn']
            
            if self.statusActual['car']['turn'] == 0: # Колеса ровно
                self.HC.turnCenter()
            elif self.statusActual['car']['turn'] > 0: # Право
                self.HC.turnRight(turn)
            elif self.statusActual['car']['turn'] < 0: # Лево
                self.HC.turnLeft(turn)
            
        # Включение и выключение фар так же можно делать в режиме реального времени.
        #print("self.statusActual['car']['light'] != self.statusUser['car']['light']", self.statusActual['car']['light'], self.statusUser['car']['light'])
        if self.statusActual['car']['light'] != self.statusUser['car']['light']:
            self.statusActual['car']['light'] = self.statusUser['car']['light']
            
            self.HC.lightSet(statusActual['car']['light'])
            
            print("light change");
        
        #self.start()

if __name__ == "__main__":

    tE = tickEvent()
    
