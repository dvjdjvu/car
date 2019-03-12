#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
from threading import Thread 

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

import sys
sys.path.append('../../conf')

import conf
import camera


class StreamerThread(Thread, conf.conf):
    
    def __init__(self): 
        Thread.__init__(self)     
    
    def run(self):
        
        ##
        #  Использовать mjpg-streamer или picamera как видео сервер.
        ##
        
        if conf.conf.VideoServerType == 'm' :
            pass
        else :
            with picamera.PiCamera(resolution = str(conf.conf.VideoWidth) + 'x' + str(conf.conf.VideoHeight) , framerate = conf.conf.VideoRate) as Camera:
                output = camera.StreamingOutput()
                camera.output = output
                Camera.start_recording(output, format = 'mjpeg')
                try:
                    address = (conf.conf.ServerIP, conf.conf.videoServerPort)
                    server = camera.StreamingServer(address, camera.StreamingHandler)
                    server.serve_forever()
                finally:
                    Camera.stop_recording()
