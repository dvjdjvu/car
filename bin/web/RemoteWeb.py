#!/usr/bin/python3
#-*- coding: utf-8 -*-

"""
Created on 12.07.2019

:author: djvu
CAR - программа управления машинкой на дистанционном управлении.
"""

import sys
sys.path.append('../src')
sys.path.append('../../conf')

from helper.log import log

import conf
from CarStatus import * 
import tickEvent

from threading import Thread 

from flask import Flask, render_template, Response, request
#import cv2
import threading
import time
import json
import argparse
import logging

app = Flask(__name__)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)
#camera = cv2.VideoCapture(0)  # веб камера

#speedX, speedY = 0, 0  # глобальные переменные положения джойстика с web-страницы
#turnX, turnY = 0, 0  # глобальные переменные положения джойстика с web-страницы
#light = True
#winchM, winchP = 0, 0  # глобальные переменные положения джойстика с web-страницы

sendFreq = 1 # слать sendFreq пакетов в секунду

# пакет, посылаемый на робота
statusRemote = carStatus.statusRemote
statusRemote['car']['light'] = True

# Управление через tickEvent
TE = tickEvent.tickEvent()

@app.route('/test')
def test():
    """ Крутим test страницу """
    return '<html><head>Flask is working.</head></html>'

@app.route('/')
def index():
    """ Крутим html страницу """
    return render_template('index.html')

@app.route('/speed')
def speed():
    """ Пришел запрос на управления роботом """
    global statusRemote
    
    speedX, speedY = int(request.args.get('speedX')), int(request.args.get('speedY'))
    statusRemote['car']['speed'] = (-1.0 *  speedY) / 100.0
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/turn')
def turn():
    """ Пришел запрос на управления роботом """
    global statusRemote
    
    turnX, turnY = int(request.args.get('turnX')), int(request.args.get('turnY'))
    statusRemote['car']['turn'] = turnX
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/light')
def light():
    """ Пришел запрос на управления роботом """
    global statusRemote
    
    light = request.args.get('light')
    if (light == 'false') :
        statusRemote['car']['light'] = False
    elif (light == 'true') :
        statusRemote['car']['light'] = True
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/winch')
def winch():
    """ Пришел запрос на управления роботом """
    global statusRemote
    #winchM = int(request.args.get('winch'))
    
    statusRemote['car']['winch'] = int(request.args.get('winch'))
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

def send_cmd():
    global statusRemote, TE
    log.Print('[info]: data: web:', statusRemote)
    #TE.newStatus(statusRemote)

class RemoteWeb(Thread, conf.conf):
    def __init__(self): 
        Thread.__init__(self)
        
    def __del__(self):
        pass
    
    def sender(self):
        """ функция цикличной отправки пакетов по uart """        
        global sendFreq, statusRemote, TE
        
        while True:
            #time.sleep(1 / sendFreq)
            
            # пакет, посылаемый на робота
            #statusRemote = carStatus.statusRemote
            
            # не используются, т.к. управление теперь на стороне сервера
            statusRemote['network']['video'] = True
            statusRemote['network']['control'] = True
            statusRemote['network']['wifi'] = True
            
            # Т.к. на пульте управления джойстик стоит вверх ногами, а здесь нет ;)
            ##statusRemote['car']['speed'] = (-1.0 *  speedY) / 100.0
            ##statusRemote['car']['turn'] = turnX
            
            ##statusRemote['car']['light'] = light
            
            '''
            if (winchM != 0) :
                statusRemote['car']['winch'] = winchM
            elif (winchP != 0) :
                statusRemote['car']['winch'] = winchP
            else :
                statusRemote['car']['winch'] = 0
            '''
            
            send_cmd()
            
            
            time.sleep(1.0 / sendFreq)
            
            # пример посылки управления
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}
    
    def run(self):
        # запускаем тред отправки пакетов управления
        threading.Thread(target=self.sender, daemon=True).start()

        # запускаем flask приложение
        app.run(debug=False, host=conf.conf.ServerIP, port=conf.conf.webServerPort)

if __name__ == '__main__':
    rw = RemoteWeb()

    threading.Thread(target=rw.sender(), daemon=True).start()    # запускаем тред отправки пакетов управления
    
    print('Start')
    app.run(debug=False, host='0.0.0.0', port=8080)   # запускаем flask приложение
    #socketio.run(app, host=args.ip, port=args.port, debug=True, use_reloader=True)
