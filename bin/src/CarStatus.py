#!/usr/bin/python3
#-*- coding: utf-8 -*-

class CarStatus:
    def __init__(self):
        self.statusCar = {'network': {'wifi': False, 'video': False, 'control': False},
                 'car': {'speed': 0, 'turn': 0, 'light': False, 'winch': 0}
                 }
    
        self.statusRemote = {'network': {'wifi': False, 'video': False, 'control': False},
                        'car': {'speed': 0, 'turn': 0, 'light': False, 'winch': 0}
                        }
    
    def __del__(self):
        pass
    
carStatus = CarStatus()
carStatusDefault = CarStatus()
