#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Created on 12.07.2019

:author: djvu
CAR - программа управления машинкой на дистанционном управлении.
"""

import sys
sys.path.append('src')
sys.path.append('../conf')

import os
import time

import conf
import client
from help import *

if __name__ == "__main__":
    """
    Программа управления машинкой.
    """
    
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)
    
    remote = client.Remote()
    remote.start()
    