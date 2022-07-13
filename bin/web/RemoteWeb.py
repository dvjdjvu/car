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

speedX, speedY = 0, 0  # глобальные переменные положения джойстика с web-страницы
turnX, turnY = 0, 0  # глобальные переменные положения джойстика с web-страницы
light = True
winchM, winchP = 0, 0  # глобальные переменные положения джойстика с web-страницы

sendFreq = 2 # слать sendFreq пакетов в секунду

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
    global speedX, speedY
    speedX, speedY = int(request.args.get('speedX')), int(request.args.get('speedY'))
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/turn')
def turn():
    """ Пришел запрос на управления роботом """
    global turnX, turnY
    turnX, turnY = int(request.args.get('turnX')), int(request.args.get('turnY'))
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/light')
def _light():
    """ Пришел запрос на управления роботом """
    global light
    light = request.args.get('light')
    if (light == 'false') :
        light = False
    elif (light == 'true') :
        light = True
        
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/winch_m')
def _winch_m():
    """ Пришел запрос на управления роботом """
    global winchM
    winchM = int(request.args.get('winch'))
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/winch_p')
def _winch_p():
    """ Пришел запрос на управления роботом """
    global winchP
    winchP = int(request.args.get('winch'))
    return '', 200, {'Content-Type': 'text/plain'}

class RemoteWeb(Thread, conf.conf):
    def __init__(self): 
        Thread.__init__(self)
        
        # Управление через tickEvent
        self.TE = tickEvent.tickEvent()
        
    def __del__(self):
        pass
    
    def sender(self):
        """ функция цикличной отправки пакетов по uart """
        global speedX, speedY
        global turnX, turnY
        global light
        global winchM, winchP
        
        global sendFreq
        
        while True:
            #time.sleep(1 / sendFreq)
            
            # пакет, посылаемый на робота
            statusRemote = carStatus.statusRemote
            
            # не используются, т.к. управление теперь на стороне сервера
            statusRemote['network']['video'] = True
            statusRemote['network']['control'] = True
            statusRemote['network']['wifi'] = True
            
            # Т.к. на пульте управления джойстик стоит вверх ногами, а здесь нет ;)
            statusRemote['car']['speed'] = (-1.0 *  speedY) / 100.0
            statusRemote['car']['turn'] = turnX
            
            statusRemote['car']['light'] = light
            
            if (winchM != 0) :
                statusRemote['car']['winch'] = winchM
            elif (winchP != 0) :
                statusRemote['car']['winch'] = winchP
            else :
                statusRemote['car']['winch'] = 0
            
            log.Print('[info]: data: web:', statusRemote)
            #self.TE.newStatus(statusRemote)

            time.sleep(1.0 / sendFreq)
            
            # пример посылки управления
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}
    
    def run(self):
        # запускаем тред отправки пакетов управления
        threading.Thread(target=self.sender, daemon=True).start()

        # запускаем flask приложение
        app.run(debug=False, host=conf.conf.ServerIP, port=conf.conf.webServerPort)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='127.0.0.1', help="Ip address")
    parser.add_argument('-s', '--serial', type=str, default='/dev/ttyUSB0', help="Serial port")
    args = parser.parse_args()

    rw = RemoteWeb()

    threading.Thread(target=rw.sender(), daemon=True).start()    # запускаем тред отправки пакетов управления

    app.run(debug=False, host=args.ip, port=args.port)   # запускаем flask приложение
    #socketio.run(app, host=args.ip, port=args.port, debug=True, use_reloader=True)
