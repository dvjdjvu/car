#!/usr/bin/python3
#-*- coding: utf-8 -*-

import Adafruit_PCA9685

###
## !!! Частота должна быть 50 гц, так как серво машинка работает на ней, 
## а плата ШИМ имеет только 1 частотный канал. Двигателю все равно какой частоты ШИМ подавать на него.
###

class PWM_Servo:
    """
    Класс управления сервоприводом.
    """
    
    def __init__(self, pin):
        self.pin = pin
        self.pwm = Adafruit_PCA9685.PCA9685()

    def set(self, val):
        """
        Установка уровня ШИМ.
        
        Args:
            val: Уровень заполнения.
        """

        try:
            self.pwm.set_pwm(self.pin, 0, int(val))
        except Exception as error:
            return
    
    def setFreq(self, freq = 50):
        """
        Частота ШИМ.
        
        Args:
            freq: Частота в герцах.
        """
        
        self.pwm.set_pwm_freq(freq)
   
class PWM_L298N_Motor:
    """
    Класс управления драйвером мотора L298N.
    """
    
    LOW  = 0
    HIGH = 4095
    
    def __init__(self, ena, in1, in2, in3, in4, enb):
        self.ena = ena
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.enb = enb
        self.pwm = Adafruit_PCA9685.PCA9685()

    def stop(self):
        """
        Остановка мотора.
        """
        
        self.pwm.set_pwm(self.ena, 0, self.LOW)
        self.pwm.set_pwm(self.enb, 0, self.LOW)

        self.pwm.set_pwm(self.in1, 0, self.LOW)
        self.pwm.set_pwm(self.in4, 0, self.LOW)
        self.pwm.set_pwm(self.in2, 0, self.LOW)
        self.pwm.set_pwm(self.in3, 0, self.LOW)

    def forward(self, speed):
        """
        Движение вперед.
        
        Args:
            speed: Задаест скорость движение от 0 до 1.
        """
        
        # защита от выходы за диапазоны
        speed = self.sign(speed) * abs(speed)
        
        self.pwm.set_pwm(self.ena, 0, int(speed * self.HIGH))
        self.pwm.set_pwm(self.enb, 0, int(speed * self.HIGH))
        
        self.pwm.set_pwm(self.in1, 0, self.HIGH)
        self.pwm.set_pwm(self.in4, 0, self.HIGH)
        self.pwm.set_pwm(self.in2, 0, self.LOW)
        self.pwm.set_pwm(self.in3, 0, self.LOW)        
        
    def back(self, speed):
        """
        Движение назад.
        
        Args:
            speed: Задаест скорость движение от 0 до 1.
        """
        
        # защита от выходы за диапазоны
        speed = self.sign(speed) * abs(speed)
        
        self.pwm.set_pwm(self.ena, 0, int(speed * self.HIGH))
        self.pwm.set_pwm(self.enb, 0, int(speed * self.HIGH))
        
        self.pwm.set_pwm(self.in1, 0, self.LOW)
        self.pwm.set_pwm(self.in4, 0, self.LOW)
        self.pwm.set_pwm(self.in2, 0, self.HIGH)
        self.pwm.set_pwm(self.in3, 0, self.HIGH)        
    
    def setFreq(self, freq = 50):
        """
        Частота ШИМ.
        
        Args:
            freq: Частота в герцах.
        """
        
        self.pwm.set_pwm_freq(freq)
        
    def sign(self, a):
        """
        Знак числа
        
        Args:
            a: Число.
        """
        
        if a > 0 :
            return 1
        elif a < 0 :
            return -1
        
        return 0
            
        
