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
sys.path.append('web')

import RemoteWeb

import os
import time

import conf
import server
import streamer
import signal

from helper.proc import proc
from helper.log import log

def ProcessingInit(conf):
    """
    Запускаем сервер.
    
    Args:
            conf:   (class(conf)) Конфигурация.
    """
    
    # Видео сервер.
    streamerThread = streamer.StreamerThread()
    streamerThread.start()
    
    # Обработка команд.
    if (conf.controller == 'web_controller') :
        # Web сервер управления.
        remoteWeb = RemoteWeb.RemoteWeb()
        
        remoteWeb.run()
        
        #remoteWeb.start()
        #remoteWeb.join()
    else :
        # Пульт управления.
        serverThread = server.ServerThread()
        serverThread.start()
        serverThread.join()
        
    streamerThread.wait()

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
            proc.setName('car[server]')
            
            ProcessingInit(Conf)
            
            break
        elif pid > 0: 
            # Watchdog.
            print('watchdog ', os.getpid())
            
            proc.setName('car[watchdog]')
            
            finished = os.waitpid(pid, 0) # Ожидаем завершение работы worker-a.
            log.Print('[critical]: worker finished:', finished)
            
            # Время(секунды) через которое поднимаем воркер в случае падения.
            time.sleep(5)
            log.Print('[info]: restart')
        else : 
            log.Print('[error]: os.fork()')
        

if __name__ == "__main__":
    """
    Программа управления машинкой.
    """
    
    signal.signal(signal.SIGTERM, proc.shutdown)
    signal.signal(signal.SIGINT,  proc.shutdown)     
    
    ProcessingWatchdog()