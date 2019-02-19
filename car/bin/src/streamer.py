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
from help import *
from camera import *

class StreamerThread(Thread, conf.conf):
    
    def __init__(self): 
        Thread.__init__(self)     
    
    def run(self):
        with picamera.PiCamera(resolution = str(conf.conf.VideoWidth) + 'x' + str(conf.conf.VideoHeight) , framerate = conf.conf.VideoRate) as camera:
            output = StreamingOutput()
            camera.start_recording(output, format = 'mjpeg')
            try:
                address = ('', conf.conf.ServerPort)
                server = StreamingServer(address, StreamingHandler)
                server.serve_forever()
            finally:
                camera.stop_recording()
