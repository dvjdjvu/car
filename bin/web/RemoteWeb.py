"""
Created on 12.07.2019

:author: djvu
CAR - программа управления машинкой на дистанционном управлении.
"""

import sys
sys.path.append('../src')
sys.path.append('../../conf')

import conf
from CarStatus import * 

from threading import Thread 
from PyQt5.QtCore import QThread, pyqtSignal

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
import cv2
import threading
import time
import json
import argparse
import logging

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
camera = cv2.VideoCapture(0)  # веб камера

speedX, speedY = 0, 0  # глобальные переменные положения джойстика с web-страницы
turnX, turnY = 0, 0  # глобальные переменные положения джойстика с web-страницы
light = True
winchM, winchP = 0, 0  # глобальные переменные положения джойстика с web-страницы

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    while True:
        time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv2.resize(frame, (conf.conf.VideoWidth, conf.conf.VideoHeight), interpolation=cv2.INTER_AREA)  # уменьшаем разрешение кадров (если видео тупит, можно уменьшить еще больше)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # перевод изображения в градации серого
            # _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)  # бинаризуем изображение
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

socketio = SocketIO(app, logge=True)
clients = 0
@socketio.on("connect", namespace="/")
def connect():
    global clients
    print("fired connect")
    clients += 1
    #emit("users", {"user_count": clients}, broadcast=True)
 

@socketio.on("disconnect", namespace="/")
def disconnect():
    global clients
    print("fired disconnect")
    clients -= 1
    #emit("users", {"user_count": clients}, broadcast=True)

@app.route('/video_feed')
def video_feed():
    """ Генерируем и отправляем изображения с камеры"""
    return Response(getFramesGenerator(), mimetype='multipart/x-mixed-replace; boundary=frame')


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
    else :
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
        
    def __del__(self):
        pass
    
    def sender(self):
        """ функция цикличной отправки пакетов по uart """
        global speedX, speedY
        global turnX, turnY
        global light
        global winchM, winchP
        
        while True:
            #time.sleep(1 / sendFreq)
            
            # пакет, посылаемый на робота
            statusRemote = carStatus.statusRemote
            
            # не используются, т.к. управление теперь на стороне сервера
            statusRemote['network'][''] = True
            statusRemote['network'][''] = True
            statusRemote['network'][''] = True
            
            statusRemote['car']['speed'] = speedY / 100.0
            statusRemote['car']['turn'] = turnX
            
            statusRemote['car']['light'] = light
            
            if (winchM != 0) :
                statusRemote['car']['winch'] = winchM
            elif (winchP != 0) :
                statusRemote['car']['winch'] = winchP
            else :
                statusRemote['car']['winch'] = 0
            
            
            print(json.dumps(statusRemote, ensure_ascii=False))

            time.sleep(1)
            
            # пример посылки управления
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}
    
    def run(self):
        # запускаем тред отправки пакетов управления
        threading.Thread(target=self.sender, daemon=True).start()

        # запускаем flask приложение
        app.run(debug=False, host=conf.conf.clientweb_ip, port=conf.conf.clientweb_port)
        #socketio.run(app, host=conf.conf.clientweb_ip, port=conf.conf.clientweb_port, debug=True, use_reloader=True)

if __name__ == '__main__':
    
    sendFreq = 10  # слать 10 пакетов в секунду

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=5000, help="Running port")
    parser.add_argument("-i", "--ip", type=str, default='127.0.0.1', help="Ip address")
    parser.add_argument('-s', '--serial', type=str, default='/dev/ttyUSB0', help="Serial port")
    args = parser.parse_args()

    #serialPort = serial.Serial(args.serial, 9600)   # открываем uart

    def sender():
        """ функция цикличной отправки пакетов по uart """
        global speedX, speedY
        global turnX, turnY
        global light
        global winch
        
        while True:
            #time.sleep(1 / sendFreq)
            
            # пакет, посылаемый на робота
            statusRemote = carStatus.statusRemote
            
            # не используются, т.к. управление теперь на стороне сервера
            statusRemote['network'][''] = True
            statusRemote['network'][''] = True
            statusRemote['network'][''] = True
            
            statusRemote['car']['speed'] = speedY / 100.0
            statusRemote['car']['turn'] = turnX
            
            statusRemote['car']['light'] = light
            
            if (winchM != 0) :
                winch = winchM
            elif (winchP != 0) :
                winch = winchP
            else :
                winch = 0
            
            statusRemote['car']['winch'] = winch
            
            #print("speed:", speedY, speedX, ", turn:", turnY, turnX, ", light:", light, ", winch:", winchM, winchP)
            print(json.dumps(statusRemote, ensure_ascii=False))
            #print(json.dumps(msg, ensure_ascii=False).encode("utf8"))
            time.sleep(1)
            
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}

    threading.Thread(target=sender, daemon=True).start()    # запускаем тред отправки пакетов управления

    app.run(debug=False, host=args.ip, port=args.port)   # запускаем flask приложение
