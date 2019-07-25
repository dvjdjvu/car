#!/usr/bin/python3
#-*- coding: utf-8 -*-

class CarStatus:
    statusCar = {'network': {'wifi': False, 'video': False, 'control': False},
                 'car': {'speed': 0, 'turn': 0, 'light': False}
                 }
    
    statusRemote = {'network': {'wifi': False, 'video': False, 'control': False},
                    'car': {'speed': 0, 'turn': 0, 'light': False}
                    }
    
carStatus = SystemStatus()