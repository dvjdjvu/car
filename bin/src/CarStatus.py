#!/usr/bin/python3
#-*- coding: utf-8 -*-

class CarStatus:
    def __init__(self):
        self.statusCar = {'network': {'wifi': False, 'video': False, 'control': False},
                 'car': {'speed': 0, 'turn': 0, 'light': False}
                 }
    
        self.statusRemote = {'network': {'wifi': False, 'video': False, 'control': False},
                        'car': {'speed': 0, 'turn': 0, 'light': False}
                        }
    
    def __del__(self):
        pass
    
carStatus = CarStatus()
