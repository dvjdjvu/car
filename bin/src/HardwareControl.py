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
        
        # Управление светом.
        self.statusLight = False
        self.gpioLight = 17
        GPIO.setup(self.gpioLight, GPIO.OUT)
        GPIO.output(self.gpioLight, GPIO.LOW)
        
        # Управление сервоприводом поворота колес.
        self.SERVO = 7
        self.pwm_servo = PWM.PWM_Servo(self.SERVO)
        self.pwm_servo.setFreq()
        
        # Управление L298, мотор движения машинки.
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
        
        self.moveStop()
        self.turnCenter()
        
        GPIO.cleanup()

    def moveStop(self):
        self.pwm_motor.stop()
        
    def moveForward(self, speed):
        #print('val', val)
        self.pwm_motor.forward(speed)
        
    def moveBack(self, speed):        
        self.pwm_motor.back(-1 * speed)
        
    def turnCenter(self):
        val = int(HardwareSetting._turnCenter)
        #print('turnCenter {}', val)
        self.pwm_servo.set(val)
        
    def turnLeft(self, turn):
        #print('turnLeft {}', turn)
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        #print('turnLeft {}', val)
        self.pwm_servo.set(val)
        
    def turnRight(self, turn):
        #print('turnRight {}', turn)
        val = int(HardwareSetting._turnCenter + (-1 * turn * HardwareSetting._turnDelta / HardwareSetting.yZero))
        #print('turnRight {}', val)
        self.pwm_servo.set(val)
