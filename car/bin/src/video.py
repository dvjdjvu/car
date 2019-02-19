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

import sys
sys.path.append('../../conf')

import sys
import conf
from help import *

class VideoWindow(QMainWindow, conf.conf):

    def __init__(self, parent = None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("Car screen.")

        # Create a widget for window contents
        self.widVideo = QWidget(self.centralWidget())
        self.videoWidget = QVideoWidget()
        self.setCentralWidget(self.widVideo)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.StreamPlayback)
        self.mediaPlayer.error.connect(self.handleError)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        layoutVideo = QVBoxLayout()
        layoutVideo.addWidget(self.videoWidget)
        layoutVideo.setContentsMargins(0,0,0,0)
        layoutVideo.setSpacing(0)
        
        # Set widget to contain window contents
        self.widVideo.setLayout(layoutVideo)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        
        self.labelText = QLabel(self.videoWidget)
        #self.labelText.setWindowFlag(Qt.SplashScreen)
        #self.labelText.setAttribute(Qt.WA_TranslucentBackground);
        #self.labelText.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum);
        self.labelText.setStyleSheet("QLabel { background-color : transparent; color : red; font-size:24px}")
        #self.labelText.adjustSize()
        #self.labelText.setGeometry(0, 0, self.widVideo.width(), self.widVideo.height())
        #self.labelText.setGeometry(0, 0, 0, 0)
        #self.labelText.adjustSize()
        self.labelText.raise_()
        self.labelText.show()        
        
        self.labelText2 = QLabel(self.videoWidget)
        #self.labelText2.setWindowFlag(Qt.SplashScreen)
        #self.labelText2.setAttribute(Qt.WA_TranslucentBackground);
        #self.labelText2.setGeometry(0, 0, 100, 10)
        self.labelText2.setStyleSheet("QLabel { background-color : transparent; color : green; font-size:24px}")
        self.labelText2.raise_()
        self.labelText2.show()        
        
        self.mediaPlayer.setMedia(QMediaContent(QUrl(conf.conf.VideoUrl)))
        self.mediaPlayer.play()

    def resizeEvent(self, e):
        self.labelText.move(10.0, self.widVideo.height() - self.labelText.height() - 10.0)
        self.labelText2.move(20.0, 20.0)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self, *args, **kwargs):
        errors = dict({0 : "NoError", 1 : "ResourceError", 2 : "FormatError", 3 : "NetworkError", 4 : "AccessDeniedError", 5 : "ServiceMissingError"})
        errorString = self.mediaPlayer.errorString()
        message = "[error]: "
        if errorString:
            message += errorString
        else:
            error = int(self.mediaPlayer.error())
            message += F' self.mediaPlayer.currentMedia().canonicalUrl()'
        
        self.labelText.setText(message);
        self.labelText2.setText('*');

    def event(self, e):
        if e.type() == QtCore.QEvent.KeyPress:
            print("Нажата клавиша на клавиатуре")
            print("Код:", e.key(), ", текст:", e.text())
        elif e.type() == QtCore.QEvent.Close:
            print("Окно закрыто")
        elif e.type() == QtCore.QEvent.MouseButtonPress:
            print("Щелчок мышью. Координаты:", e.x(), e.y())
        return QtWidgets.QWidget.event(self, e) # Отправляем дальше

class Remote():
    
    def __init__(self):
        pass
    
    def start(self):
        app = QApplication(sys.argv)
        player = VideoWindow()
        player.resize(640, 480)
        player.show()
        sys.exit(app.exec_())  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    #player.showFullScreen()
    sys.exit(app.exec_())
