#!/usr/bin/python3
#-*- coding: utf-8 -*-

import sys, re, time
import subprocess

from PyQt5.QtCore import QThread, pyqtSignal

class WifiCheck(QThread):

    signalSendStatus = pyqtSignal(object)

    def __init__(self, parent = None):
        #Thread.__init__(self) 
        QThread.__init__(self, parent) 

        self.ps = subprocess.Popen(['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def run(self):
        while True:
            time.sleep(0.5)
            try:
                output = subprocess.check_output(('grep', 'ESSID'), stdin=self.ps.stdout)
                print(output)
                if re.search(r'djvu-car-pi3', str(output)) :
                    self.sendStatus('wifi+')
                    continue
                
            except subprocess.CalledProcessError:
                pass
                
            self.sendStatus('wifi-')
            
    def sendStatus(self, status):        
        self.signalSendStatus.emit(status)    
