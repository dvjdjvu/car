#!/usr/bin/python3
#-*- coding: utf-8 -*-

import random

class ADS1115:
    
    def read_adc(self, i, gain):
        return random.randint(1, 100)

class PCA9685:
    
    def set_pwm(self, channel, on, off):
        pass
    
    def set_pwm_freq(self, freq_hz):
        pass
    
    def set_all_pwm(self, on, off):
        pass