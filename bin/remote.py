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

import signal

from helper.proc import proc

if __name__ == "__main__":
    """
    Программа управления машинкой.
    """
    
    signal.signal(signal.SIGTERM, proc.shutdown)
    signal.signal(signal.SIGINT,  proc.shutdown)
    
    remote = client.Remote()
    remote.start()
    