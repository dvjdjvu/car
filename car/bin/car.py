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
import server
import streamer
from help import *

def ProcessingInit(conf):
    """
    Запускаем сервер.
    
    Args:
            conf:   (class(conf)) Конфигурация.
    """
        
    # Обработка команд.
    serverThread = server.ServerThread()
    serverThread.start()
        
    # Видео сервер.
    streamerThread = streamer.StreamerThread()
    streamerThread.start()
        
    serverThread.wait()
    streamerThread.join()
        

def ProcessingWatchdog(): 
    """
    Watchdog за ProcessingInit().
    """
    
    Conf = conf.conf()
    
    while True:
        pid = os.fork()
        if pid == 0: 
            # Worker.
            print('child ', os.getpid())
            # Меняем имя процесса.
            set_proc_name('car[server]')
            
            ProcessingInit(Conf)
            
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
        

if __name__ == "__main__":
    """
    Программа управления машинкой.
    """
    
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)     
    
    ProcessingWatchdog()