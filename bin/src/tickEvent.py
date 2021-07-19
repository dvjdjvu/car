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
    (Машинка будет с максимальной скорости моментально тормозить до 0, с места максимально ускоряться. Что дает нежелательный рывок и доп. нугрузку на трансмиссию)
    Что негативно скажется на механических элементах машины.
    
    Система управления будет сделана на таймере. 
    На каждом новом тике фактическое состояние будет пошагово доводиться до пользовательского.
    """
    
    def __init__(self, time=0.05):
        """
        Инициализация
        
        Args:
            time: Время между тиками в миллисекундах.
        """
        
        self.mutex = Lock()
        
        self.statusActual = CarStatus().statusCar
        self.statusUser   = CarStatus().statusCar
        # Что бы фары включались после 1-ого нажатия кнопки
        self.statusActual['car']['light'] = not self.statusUser['car']['light']
    
        self.HC = HardwareControl.HardwareControl()
    
        # шаг плавности изменения хода, на сколько уменьшится или увелится скорость за один time
        self.stepSmooth = 0.2
        # минимальная скорость начала движения, диапазон скорости от 0 до 1 переводится в диапазон от self.stepMoving до 1
        self.stepMoving = 0.25
        
        # шаг плавности изменения поворота, на сколько уменьшится или увелится поворот за один time
        self.stepTurn = 10
        
        self.time = time
        
        # Моргаем фарами, что готовы к работе.
        self.HC.lightTest()
        
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
        
        speedA = self.statusActual['car']['speed']
        speedU = self.statusUser['car']['speed']
        
        servoA = self.statusActual['car']['turn']
        servoU = self.statusUser['car']['turn']
        
        self.mutex.release()
        
        ##
        # Управление двигателем.
        ##
        
        if abs(speedA) < self.stepSmooth :
            speedA = 0
        
        if speedA < speedU:
            speedA += self.stepSmooth
            if speedA == 0:
                self.HC.moveStop()
            elif speedA < 0.0:
                self.HC.moveBack(speedA * (1 - self.stepMoving) + self.stepMoving)
            elif speedA > 0.0:
                self.HC.moveForward(speedA * (1 - self.stepMoving) + self.stepMoving)
               
        if speedA > speedU:
            speedA -= self.stepSmooth
            if speedA == 0:
                self.HC.moveStop()
            elif speedA < 0.0:
                self.HC.moveBack(speedA * (1 - self.stepMoving) + self.stepMoving)
            elif speedA > 0.0:
                self.HC.moveForward(speedA * (1 - self.stepMoving) + self.stepMoving)
           
        if speedA == 0 :
            self.HC.moveStop()        
        
        self.statusActual['car']['speed'] = speedA
        
        ##
        # Управление сервоприводом.
        ##
        '''
        if abs(servoA) < self.stepTurn :
            servoA = 0
        
        if servoA < servoU:
            servoA += self.stepTurn
            if servoA == 0 :
                self.HC.turnCenter()
            elif servoA < 0.0:
                self.HC.turnLeft(servoA)
            elif servoA > 0.0:
                self.HC.turnRight(servoA)
        
        if servoA > servoU:
            servoA -= self.stepTurn
            if servoA == 0 :
                self.HC.turnCenter()
            elif servoA < 0.0:
                self.HC.turnLeft(servoA)
            elif servoA > 0.0:
                self.HC.turnRight(servoA)
        
        if servoA == 0 :
            self.HC.turnCenter()
        
        self.statusActual['car']['turn'] = servoA
        '''
        self.start()
        
    def newStatus(self, status):
        #print("TC newStatus")
        #print("self.statusUser", id(status))
        #print("self.statusActual", id(self.statusActual))
        
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
                self.HC.turnRight(self.statusActual['car']['turn'])
            elif self.statusActual['car']['turn'] < 0: # Лево
                self.HC.turnLeft(self.statusActual['car']['turn'])
         
        # Включение и выключение фар так же можно делать в режиме реального времени.
        #print("self.statusActual['car']['light'] != self.statusUser['car']['light']", self.statusActual['car']['light'], self.statusUser['car']['light'])
        if self.statusActual['car']['light'] != self.statusUser['car']['light']:
            self.statusActual['car']['light'] = self.statusUser['car']['light']
            
        self.HC.lightSet(self.statusActual['car']['light'])            
        
        # Управление лебедкой.
        if self.statusActual['car']['winch'] != self.statusUser['car']['winch']:
            self.statusActual['car']['winch'] = self.statusUser['car']['winch']
            
        if self.statusActual['car']['winch'] == 0: # лебедка не работает
            self.HC.winchStop()
        elif self.statusActual['car']['winch'] > 0: # Разматывается
            self.HC.winchForward()
        elif self.statusActual['car']['winch'] < 0: # Тащит
            self.HC.winchBack()

        self.statusActual = self.statusUser
