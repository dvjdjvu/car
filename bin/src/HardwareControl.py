#!/usr/bin/python3
#-*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import PWM

import sys
sys.path.append('../../conf')

from HardwareSetting import HardwareSetting 

from CarStatus import *

class HardwareControl():
    def __init__(self):
        # Очистка состояния пинов.
        GPIO.cleanup() 
        # Инициализация пинов.
        GPIO.setmode(GPIO.BCM)
        
        ##
        # Управление светом.
        ##
        self.statusLight = False
        
        # передний
        self.gpioLight = 17
        GPIO.setup(self.gpioLight, GPIO.OUT)
        GPIO.output(self.gpioLight, GPIO.LOW)
        
        # задний
        self.gpioLightBack = 27
        GPIO.setup(self.gpioLightBack, GPIO.OUT)
        GPIO.output(self.gpioLightBack, GPIO.LOW)
        
        ##
        # Лебедка.
        ##
        
        self.gpioWinchForward = 13
        GPIO.setup(self.gpioWinchForward, GPIO.OUT)
        GPIO.output(self.gpioWinchForward, GPIO.LOW)
        
        self.gpioWinchBack = 19
        GPIO.setup(self.gpioWinchBack, GPIO.OUT)
        GPIO.output(self.gpioWinchBack, GPIO.LOW)
        
        ##
        # Управление сервоприводом поворота колес.
        ##
        self.SERVO = 7
        self.pwm_servo = PWM.PWM_Servo(self.SERVO)
        self.pwm_servo.setFreq()
        
        ##
        # Управление L298, мотор движения машинки.
        ##
        self.L298_ENA = 10
        self.L298_IN1 = 12
        self.L298_IN2 = 13
        self.L298_IN3 = 14
        self.L298_IN4 = 15        
        self.L298_ENB = 11
        self.pwm_motor = PWM.PWM_L298N_Motor(self.L298_ENA, self.L298_IN1, self.L298_IN2, self.L298_IN3, self.L298_IN4, self.L298_ENB)
        self.pwm_motor.setFreq()

    def __del__(self):
        GPIO.output(self.gpioLight, GPIO.LOW)
        GPIO.output(self.gpioLightBack, GPIO.LOW)
        
        self.moveStop()
        self.turnCenter()
        
        GPIO.cleanup()

    def lightSet(self, light):
        if light == False :
            print("light GPIO.HIGH")
            # Включить свет.
            GPIO.output(self.gpioLight, GPIO.HIGH) # передний
            GPIO.output(self.gpioLightBack, GPIO.HIGH) # задний
        else :
            print("light GPIO.LOW")
            # Выключить свет.
            GPIO.output(self.gpioLight, GPIO.LOW) # передний
            GPIO.output(self.gpioLightBack, GPIO.LOW) # задний

    def moveStop(self):
        self.pwm_motor.stop()
        
    def moveForward(self, speed):
        self.pwm_motor.forward(speed)
        
    def moveBack(self, speed):        
        self.pwm_motor.back(-1 * speed)
        
    def turnCenter(self):
        val = int(HardwareSetting._turnCenter)
        self.pwm_servo.set(val)
        
    def turnLeft(self, turn):
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        self.pwm_servo.set(val)
        
    def turnRight(self, turn):
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        self.pwm_servo.set(val)

    def winchForward(self):
        GPIO.output(self.gpioWinchForward, GPIO.HIGH)
        GPIO.output(self.gpioWinchBack, GPIO.LOW)
    
    def winchBack(self):
        GPIO.output(self.gpioWinchForward, GPIO.LOW)
        GPIO.output(self.gpioWinchBack, GPIO.HIGH)
    
    def winchStop(self):
        GPIO.output(self.gpioWinchForward, GPIO.LOW)
        GPIO.output(self.gpioWinchBack, GPIO.LOW)
