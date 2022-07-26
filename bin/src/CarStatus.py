#!/usr/bin/python3
#-*- coding: utf-8 -*-

import conf

class CarStatus:
    def __init__(self):
        self.statusCar = {'network': {'wifi': False, 'video': False, 'control': False},
                          'car': {'speed': 0, 'turn': 0, 'light': False, 'winch': 0},
                          'video': {'VideoRate': conf.conf.VideoRate, 'VideoWidth': conf.conf.VideoWidth, 'VideoHeight': conf.conf.VideoHeight},
                          'raspberry': {'temp': '', 'volt': ''}
                         }
    
        self.statusRemote = {'network': {'wifi': False, 'video': False, 'control': False},
                             'car': {'speed': 0, 'turn': 0, 'light': False, 'winch': 0},
                             'raspberry': {'temp': '', 'volt': ''}
                            }
    
    def __del__(self):
        pass
    
carStatus = CarStatus()
carStatusDefault = CarStatus()
