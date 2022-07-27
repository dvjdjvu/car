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

from flask import Flask, render_template, Response, request, json

import time
import logging
import argparse
import subprocess


app = Flask(__name__)
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)
#camera = cv2.VideoCapture(0)  # веб камера

#speedX, speedY = 0, 0  # глобальные переменные положения джойстика с web-страницы
#turnX, turnY = 0, 0  # глобальные переменные положения джойстика с web-страницы
#light = True
#winchM, winchP = 0, 0  # глобальные переменные положения джойстика с web-страницы

sendFreq = 2 # слать sendFreq пакетов в секунду

# пакет, посылаемый на робота
statusCar = carStatus.statusCar
# по умолчанию свет загорается, поэтому выставляем его
statusCar['car']['light'] = True
 # не используются, т.к. управление теперь на стороне сервера
statusCar['network']['video'] = True
statusCar['network']['control'] = False
statusCar['network']['wifi'] = True

# Управление через tickEvent
TE = tickEvent.tickEvent()

dt_last_data = time.time()

@app.route('/connect_check')
def connect_check():
    """ Функция проверки связи """
    global dt_last_data
            
    dt_last_data = time.time()
    
    statusCar['network']['control'] = True
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/test')
def test():
    """ Крутим test страницу """
    
    try :
        temp = subprocess.check_output(['vcgencmd', 'measure_temp']).decode('utf-8').rstrip()
        volt = subprocess.check_output(['vcgencmd', 'get_throttled']).decode('utf-8').rstrip()
    except :
        temp = 'Emulating'
        volt = ''
    
    statusCar['raspberry']['temp'] = temp
    statusCar['raspberry']['volt'] = volt
    
    response = app.response_class(
        response=json.dumps(statusCar),
        mimetype='application/json'
    )
    
    return response
    
    #return '<html><head>{0}</head></html>'.format(str(ret))

@app.route('/')
def index():
    """ Крутим html страницу """
    return render_template('index.html')

@app.route('/speed')
def speed():
    """ Пришел запрос на управления роботом """
    global statusCar
    
    speedX, speedY = int(request.args.get('speedX')), int(request.args.get('speedY'))
    statusCar['car']['speed'] = (-1.0 *  speedY) / 100.0
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/turn')
def turn():
    """ Пришел запрос на управления роботом """
    global statusCar
    
    turnX, turnY = int(request.args.get('turnX')), int(request.args.get('turnY'))
    statusCar['car']['turn'] = turnX
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/light')
def light():
    """ Пришел запрос на управления роботом """
    global statusCar
    
    light = request.args.get('light')
    
    statusCar['car']['light'] = not statusCar['car']['light']
    
    #if (light == 'false') :
    #    statusCar['car']['light'] = False
    #elif (light == 'true') :
    #    statusCar['car']['light'] = True
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

@app.route('/winch')
def winch():
    """ Пришел запрос на управления роботом """
    global statusCar
    #winchM = int(request.args.get('winch'))
    
    try:
        statusCar['car']['winch'] = int(request.args.get('winch'))
    except ValueError:
        statusCar['car']['winch'] = 0
    
    send_cmd()
    
    return '', 200, {'Content-Type': 'text/plain'}

def send_cmd():
    global statusCar, TE
    log.Print('[info]: data: web:', statusCar)
    TE.newStatus(statusCar)

class RemoteWeb(Thread, conf.conf):
    def __init__(self): 
        Thread.__init__(self)
        
    def __del__(self):
        pass
    
    def sender(self):
        """ функция цикличной отправки пакетов по uart """        
        global sendFreq, dt_last_data, statusCar
        
        while True:
            dt_diff = time.time() - dt_last_data
            if (dt_diff >= conf.conf.dt_check) :
                statusCar = CarStatus().statusCar
            
            send_cmd()

            time.sleep(1.0 / sendFreq)
            
            # пример посылки управления
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}
    
    def run(self):
        # запускаем тред отправки пакетов управления
        Thread(target=self.sender, daemon=True).start()

        # запускаем flask приложение
        app.run(debug=False, host=conf.conf.ServerIP, port=conf.conf.webServerPort)

if __name__ == '__main__':    
    rw = RemoteWeb()

    Thread(target=rw.sender(), daemon=True).start()    # запускаем тред отправки пакетов управления
    
    app.run(debug=False, host='127.0.0.1', port=8080)   # запускаем flask приложение
    #socketio.run(app, host=args.ip, port=args.port, debug=True, use_reloader=True)
