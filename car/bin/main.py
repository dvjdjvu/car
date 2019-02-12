#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Created on 12.07.2019

:author: djvu
CAR, программа управления машинкой на дистанционном управлении.
"""

import os
import time
import sys
sys.path.append('src')
sys.path.append('../conf')

import conf
import server
import streamer
from help import *

def ProcessingInit(conf):
    """
    Запускаем сервер или клиент.
    
    Args:
            conf:   (class(conf)) Конфигурация.
    """
    
    if conf.confType == 'server' :
        
        # Запускаем сервер по приему команд.
        serverThread = server.ServerThread()
        serverThread.start()
        
        # Запускаем сервер передачи видео.
        streamerThread = streamer.StreamerThread()
        streamerThread.start()
        
        serverThread.wait()
        streamerThread.join()
        
    elif conf.confType == 'client' :
        pass
    else :
        Print('[info]: conf.confType is not correct: ', conf.confType)

def ProcessingWatchdog(): 
    """
    Watchdog за ProcessingInit().
    """
    
    _conf = conf.conf()
    
    while True:
        pid = os.fork()
        if pid == 0: 
            # Worker.
            print('child ', os.getpid())
            # Меняем имя процесса.
            set_proc_name('car[' + _conf.confType + ']')
            
            ProcessingInit(_conf)
            
            break
        elif pid > 0: 
            # Watchdog.
            print('watchdog ', os.getpid())
            
            set_proc_name('car[watchdog]')
            
            finished = os.waitpid(pid, 0) # Ожидаем завершение работы worker-a.
            Print('[critical]: worker finished:', finished)
            
            # Время(секунды) через которое поднимаем воркер в случае падения.
            time.sleep(5)
            Print('[info]: restart')
        else : 
            Print('[error]: os.fork()')
        
##
#  Старт.
##
if __name__ == "__main__":
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)     
    
    ProcessingWatchdog()