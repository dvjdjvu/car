#!/usr/bin/python3
#-*- coding: utf-8 -*-
# PyQt5 Video player

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QAction
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import QThread, pyqtSignal

import socket
from threading import Thread, Lock 
from socketserver import ThreadingMixIn 

import sys, os
sys.path.append('../../conf')

import json
import sys
import time
import conf
import helper
import subprocess

import GHKeyboard
import Joystick
import WifiCheck

from CarStatus import * 

class VideoWindow(QMainWindow, conf.conf):

    textSize = 48
    timerVideoRecconect = QtCore.QTimer()
    
    def __init__(self, parent = None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Car screen.")

        # Create a widget for window contents
        self.mainWidget = QWidget(self.centralWidget())
        self.videoWidget = QVideoWidget()
        self.setCentralWidget(self.mainWidget)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)
        self.mediaPlayer.error.connect(self.handleError)
        #self.mediaPlayer.error.connect(self.displayErrorMessage)
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.mediaStatusChanged.connect(self.statusChanged)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        layoutVideo = QVBoxLayout()
        layoutVideo.addWidget(self.videoWidget)
        layoutVideo.setContentsMargins(0,0,0,0)
        layoutVideo.setSpacing(0)
        
        # Set widget to contain window contents
        self.mainWidget.setLayout(layoutVideo)
        
        self.labelVideoStatus = QLabel(self.videoWidget)
        self.labelVideoStatus.setStyleSheet("QLabel { background-color : black; color : red; font-size:" + str(self.textSize) + "px}")
        self.labelVideoStatus.setGeometry(0, 0, self.textSize, self.textSize)
        #self.labelVideoStatus.setAttribute(Qt.WA_TranslucentBackground)
        self.labelVideoStatus.raise_()
        self.displayPrint("В-")
        
        self.labelControlStatus = QLabel(self.videoWidget)
        self.labelControlStatus.setGeometry(0, 0, self.textSize, self.textSize)
        self.labelControlStatus.setStyleSheet("QLabel { background-color : black; color : red; font-size:" + str(self.textSize) + "px}")
        self.labelControlStatus.raise_()
        self.displayPrint("У-")
        
        self.labelWifiStatus = QLabel(self.videoWidget)
        self.labelWifiStatus.setGeometry(0, 0, self.textSize, self.textSize)
        self.labelWifiStatus.setStyleSheet("QLabel { background-color : black; color : red; font-size:" + str(self.textSize) + "px}")
        self.labelWifiStatus.raise_()
        self.displayPrint("wifi-")
        
        self.mediaPlayer.setMedia(QMediaContent(QUrl("http://{}:{}/?action=stream".format(conf.conf.ServerIP, conf.conf.videoServerPort))))
        self.mediaPlayer.play()
        
        self.timerVideoRecconect.timeout.connect(self.videoReconnect)

    def videoReconnect(self):
        self.timerVideoRecconect.stop()
        
        self.mediaPlayer.setMedia(QMediaContent(QUrl("http://{}:{}/?action=stream".format(conf.conf.ServerIP, conf.conf.videoServerPort))))
        self.mediaPlayer.play()

    def resizeEvent(self, e):
        self.labelVideoStatus.move(10.0, self.mainWidget.height() - self.textSize)
        self.labelControlStatus.move(self.mainWidget.width() - self.textSize, self.mainWidget.height() - self.textSize)
        self.labelWifiStatus.move(10.0, 10.0)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def statusChanged(self, status):
        #print('statusChanged', status)
        
        if status == QMediaPlayer.UnknownMediaStatus :
            pass
        elif status == QMediaPlayer.NoMedia :
            pass
        elif status == QMediaPlayer.LoadingMedia :
            pass
        elif status == QMediaPlayer.LoadedMedia :
            pass
        elif status == QMediaPlayer.StalledMedia :
            self.labelVideoStatus.hide()
        elif status == QMediaPlayer.BufferingMedia :
            pass
        elif status == QMediaPlayer.BufferedMedia :
            pass
        elif status == QMediaPlayer.EndOfMedia :
            self.displayPrint("В-")
            self.timerVideoRecconect.start(conf.conf.timeRecconect * 1000)
            carStatus.statusRemote['network']['video'] = False
        elif status == QMediaPlayer.InvalidMedia :
            self.displayPrint("В-")
            self.timerVideoRecconect.start(conf.conf.timeRecconect * 1000)
            carStatus.statusRemote['network']['video'] = False

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def displayErrorMessage(self):
        print(self.mediaPlayer.errorString())    

    def handleError(self, *args, **kwargs):
        errors = dict({0 : "NoError", 1 : "ResourceError", 2 : "FormatError", 3 : "NetworkError", 4 : "AccessDeniedError", 5 : "ServiceMissingError"})
        errorString = self.mediaPlayer.errorString()
        message = "[error]: "
        if errorString:
            message += errorString
        else:
            error = int(self.mediaPlayer.error())
            #message += F' self.mediaPlayer.currentMedia().canonicalUrl()'
            message += 'self.mediaPlayer.currentMedia().canonicalUrl()'

    def displayPrint(self, _str) :
        #print(_str)
        
        if _str == 'У-' :
            self.labelControlStatus.setText("У")
            self.labelControlStatus.show()
            carStatus.statusRemote['network']['control'] = False
        elif _str == 'У+' :
            self.labelControlStatus.hide()
            carStatus.statusRemote['network']['control'] = True
        elif _str == 'В-' :
            self.labelVideoStatus.setText("В");
            self.labelVideoStatus.show()
            carStatus.statusRemote['network']['video'] = False
        elif _str == 'В+' :
            self.labelControlStatus.hide()
            carStatus.statusRemote['network']['video'] = True
        elif _str == 'wifi-' :
            self.labelWifiStatus.setText("W")
            self.labelWifiStatus.show()
            carStatus.statusRemote['network']['wifi'] = False
        elif _str == 'wifi+' :
            self.labelWifiStatus.hide()
            carStatus.statusRemote['network']['video'] = True
            

    def event(self, e):
        if e.type() == QtCore.QEvent.KeyPress:
            if e.key() == QtCore.Qt.Key_Escape:
                os._exit(1)
                
        '''
        if e.type() == QtCore.QEvent.KeyPress:
            print("Нажата клавиша на клавиатуре")
            print("Код:", e.key(), ", текст:", e.text())
            
            cmd = '{"type": "remote", "cmd": "' + e.text() + '", "status": "Ok"}'
            
            if self.clientThread.tcpClient :
            try:
                self.clientThread.tcpClient.send(cmd.encode())
                self.labelControlStatus.hide()
            except:
                self.labelControlStatus.setText("У")
                self.labelControlStatus.show()
                
            
        elif e.type() == QtCore.QEvent.Close:
            print("Окно закрыто")
            os._exit(1)
        elif e.type() == QtCore.QEvent.MouseButtonPress:
            print("Щелчок мышью. Координаты:", e.x(), e.y())
        ''' 
        return QtWidgets.QWidget.event(self, e) # Отправляем дальше
    
    '''
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setFullScreen(False)
            event.accept()
        elif event.key() == Qt.Key_Enter and event.modifiers() & Qt.Key_Alt:
            self.setFullScreen(not self.isFullScreen())
            event.accept()
        else:
            super(VideoWindow, self).keyPressEvent(event)    
    '''
    
class ClientThread(QThread, conf.conf):
    
    tcpClient = None
    timerServerRecconect = QtCore.QTimer()
    mutex = QtCore.QMutex()
    
    signalDisplayPrint = pyqtSignal(str)
    
    def __init__(self, parent = None): 
        QThread.__init__(self, parent) 
  
    def getSocket(self):
        return self.tcpClient
  
    def run(self): 
        
        while not self.tcpClient:
            self.tcpClient = None
            
            #if not carStatus.statusRemote['network']['wifi'] :
            #    time.sleep(1.0)
            #    continue
            #print('connect self.tcpClient')
            
            try :
                tcpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                tcpClient.settimeout(2.0)
                tcpClient.connect((conf.conf.ServerIP, conf.conf.controlServerPort))
                self.signalDisplayPrint.emit("У+")
                carStatus.statusRemote['network']['control'] = True
                
                self.tcpClient = tcpClient
            except socket.error as e:
                self.signalDisplayPrint.emit("У-")
                carStatus.statusRemote['network']['control'] = False
                
                time.sleep(conf.conf.timeRecconect)
                self.tcpClient = None
                
                continue        
            
            #print('Ok self.tcpClient', self.tcpClient)
            if self.tcpClient :
                self.tcpClient.settimeout(None)
            
            while True:
                try :
                    data = self.tcpClient.recv(conf.conf.ServerBufferSize)
                    data = data.decode()
                    if data == '' :
                        self.signalDisplayPrint.emit("У-")
                        carStatus.statusRemote['network']['control'] = False
                        self.tcpClient.close() 
                        self.tcpClient = None
                        
                        break
                    
                    #print('Get data:  ', data)
                    
                    self.signalDisplayPrint.emit("У+")
                    carStatus.statusRemote['network']['control'] = True
                except :
                    self.tcpClient.close() 
                    self.tcpClient = None
                    self.signalDisplayPrint.emit("У-")
                    carStatus.statusRemote['network']['control'] = False
                    break
                
            print('Fail self.tcpClient', self.tcpClient)

        self.tcpClient.close()
        self.tcpClient = None
        
    def sendCmd(self, cmd):        
        print('Send data: ', cmd)
        
        if self.tcpClient :
            self.mutex.lock()
            
            try:
                self.tcpClient.send(json.dumps(cmd, ensure_ascii=False).encode())
                self.signalDisplayPrint.emit("У+")
                carStatus.statusRemote['network']['control'] = True
            except:
                print("error", self.tcpClient)
                self.tcpClient.close()
                self.tcpClient = None
                
                self.signalDisplayPrint.emit("У-")
                carStatus.statusRemote['network']['control'] = False

            self.mutex.unlock()
        else :
            print("self.tcpClient", self.tcpClient)
            self.signalDisplayPrint.emit("У-")
            carStatus.statusRemote['network']['control'] = False
    
class Remote(conf.conf):
    
    def start(self):
        app = QApplication(sys.argv)
        
        player = VideoWindow()
        player.resize(conf.conf.VideoWidth, conf.conf.VideoHeight)
        
        #player.show()
        player.showFullScreen()
        
        player.setCursor(Qt.BlankCursor)
        
        clientThread = ClientThread()
        keyboard = GHKeyboard.GHK()
        joystick = Joystick.Joystick()
        wifiCheck = WifiCheck.WifiCheck()
        
        clientThread.signalDisplayPrint.connect(player.displayPrint)
        keyboard.signalSendCmd.connect(clientThread.sendCmd)
        joystick.signalSendCmd.connect(clientThread.sendCmd)
        wifiCheck.signalSendStatus.connect(player.displayPrint)
        
        clientThread.start()
        keyboard.start()
        joystick.start()
        wifiCheck.start()
        
        sys.exit(app.exec_())  

