#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
from PyQt5.QtCore import QThread

#import platform
#print(platform.machine())

from helper.log import log

import os
try :
    import picamera
except (ImportError, RuntimeError) :
    log.Print('[error]: import picamera')

import sys
sys.path.append('../../conf')

import conf
import camera


class StreamerThread(QThread, conf.conf):
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent)    
    
    def video_server_mjpg_streamer(self):
        #os.system("/home/pi/projects/mjpg-streamer-experimental/start.sh")
        cmd = "cd /home/pi/projects/mjpg-streamer-experimental && "
        cmd += './mjpg_streamer -o "./output_http.so -p {0} -w ./www" -i "./input_raspicam.so -x {1} -y {2} -fps {3} -ex auto -awb auto -vs -ISO 10 -rot 180"'.format(conf.conf.videoServerPort, conf.conf.VideoWidth, conf.conf.VideoHeight, conf.conf.VideoRate)
            
        print(cmd)
        os.system(cmd)
        
    def video_server_picamera(self):
        with picamera.PiCamera(resolution = str(conf.conf.VideoWidth) + 'x' + str(conf.conf.VideoHeight) , framerate = conf.conf.VideoRate) as Camera:
            output = camera.StreamingOutput()
            Camera.rotation = 180
            camera.output = output
            Camera.start_recording(output, format = 'mjpeg')
            try:
                address = (conf.conf.ServerIP, conf.conf.videoServerPort)
                server = camera.StreamingServer(address, camera.StreamingHandler)
                server.serve_forever()
            finally:
                Camera.stop_recording()
            
    def run(self):
        
        ##
        #  Использовать mjpg-streamer или picamera как видео сервер.
        ##
        
        if conf.conf.VideoServerType == 'm' :
            self.video_server_mjpg_streamer()
        else :
            self.video_server_picamera()
