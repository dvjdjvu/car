"""
Created on 12.07.2019

:author: djvu
CAR - программа управления машинкой на дистанционном управлении.
"""

import sys
sys.path.append('../src')

from CarStatus import * 

from flask import Flask, render_template, Response, request
import cv2
import serial
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
winch, winchM, winchP = 0, 0, 0  # глобальные переменные положения джойстика с web-страницы

def getFramesGenerator():
    """ Генератор фреймов для вывода в веб-страницу, тут же можно поиграть с openCV"""
    while True:
        time.sleep(0.01)    # ограничение fps (если видео тупит, можно убрать)
        success, frame = camera.read()  # Получаем фрейм с камеры
        if success:
            frame = cv2.resize(frame, (640, 360), interpolation=cv2.INTER_AREA)  # уменьшаем разрешение кадров (если видео тупит, можно уменьшить еще больше)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # перевод изображения в градации серого
            # _, frame = cv2.threshold(frame, 127, 255, cv2.THRESH_BINARY)  # бинаризуем изображение
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


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

if __name__ == '__main__':
    # пакет, посылаемый на робота
    statusRemote = {
        'network': {'wifi': True, 'video': True, 'control': True},
        'car': {'speed': 0, 'turn': 0, 'light': False, 'winch': 0}
    }

    # параметры робота
    speedScale = 0.65  # определяет скорость в процентах (0.50 = 50%) от максимальной абсолютной
    maxAbsSpeed = 100  # максимальное абсолютное отправляемое значение скорости
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
            
            statusRemote
            
            #serialPort.write(json.dumps(msg, ensure_ascii=False).encode("utf8"))  # отправляем пакет в виде json файла
            #time.sleep(1 / sendFreq)
            
            print(carStatus.statusCar)
            print("speed:", speedY, speedX, ", turn:", turnY, turnX, ", light:", light, ", winch:", winchM, winchP)
            #print(json.dumps(msg, ensure_ascii=False).encode("utf8"))
            time.sleep(1)
            
            # data: {'car': {'speed': -0.9979622641509434, 'winch': 0, 'turn': 88, 'light': True}, 'network': {'control': True, 'wifi': True, 'video': False}}

    threading.Thread(target=sender, daemon=True).start()    # запускаем тред отправки пакетов по uart с демоном

    app.run(debug=False, host=args.ip, port=args.port)   # запускаем flask приложение

'''
background-color: #04AA6D; /* Green */
            border: none;
            color: white;
            padding: 50px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 32px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 50%;
            position: absolute;
            left: 60px;
'''