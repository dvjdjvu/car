#!/usr/bin/python3
#-*- coding: utf-8 -*-
# Client is stay in Remote.

import sys,time
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QScrollBar,QSplitter,QTableWidgetItem,QTableWidget,QComboBox,QVBoxLayout,QGridLayout,QDialog,QWidget, QPushButton, QApplication, QMainWindow,QAction,QMessageBox,QLabel,QTextEdit,QProgressBar,QLineEdit
from PyQt5.QtCore import QCoreApplication
import socket
from threading import Thread 
from socketserver import ThreadingMixIn 
 
import sys
sys.path.append('../../conf')

import conf
from help import *
 
tcpClientA = None
 
class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.flag=0
        self.chatTextField=QLineEdit(self)
        self.chatTextField.resize(480, 100)
        self.chatTextField.move(10, 350)
        self.btnSend=QPushButton("Send",self)
        self.btnSend.resize(480, 30)
        self.btnSendFont=self.btnSend.font()
        self.btnSendFont.setPointSize(15)
        self.btnSend.setFont(self.btnSendFont)
        self.btnSend.move(10, 460)
        self.btnSend.setStyleSheet("background-color: #F7CE16")
        self.btnSend.clicked.connect(self.send)
 
        self.chatBody=QVBoxLayout(self)
        # self.chatBody.addWidget(self.chatTextField)
        # self.chatBody.addWidget(self.btnSend)
        # self.chatWidget.setLayout(self.chatBody)
        splitter=QSplitter(QtCore.Qt.Vertical)
 
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
 
        splitter.addWidget(self.chat)
        splitter.addWidget(self.chatTextField)
        splitter.setSizes([400, 100])
 
        splitter2=QSplitter(QtCore.Qt.Vertical)
        splitter2.addWidget(splitter)
        splitter2.addWidget(self.btnSend)
        splitter2.setSizes([200,10])
 
        self.chatBody.addWidget(splitter2)
 
 
        self.setWindowTitle("Chat Application")
        self.resize(500, 500)
 
    def send(self):
        text=self.chatTextField.text()
        font=self.chat.font()
        font.setPointSize(13)
        self.chat.setFont(font)
        textFormatted='{:>80}'.format(text)
        self.chat.append(textFormatted)
        tcpClientA.send(text.encode())
        self.chatTextField.setText("")
        
    def exitCall(self):
        sys.exit(app.exec_())    
 
class ClientThread(Thread, conf.conf):
    
    def __init__(self, window): 
        Thread.__init__(self) 
        self.window = window
  
    def run(self): 
       host = self.confServerIP
       port = self.confServerPort
       BUFFER_SIZE = self.confServerBufferSize
       global tcpClientA
       tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
       tcpClientA.connect((host, port))
        
       while True:
           data = tcpClientA.recv(BUFFER_SIZE)
           window.chat.append(data.decode("utf-8"))
       tcpClientA.close() 
 
class Remote():
    
    def __init__(self):
        pass
    
    def start(self):
        app = QApplication(sys.argv)
        window = Window()
        clientThread=ClientThread(window)
        clientThread.start()
        window.exec()
        sys.exit(app.exec_())        
 
if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)
    
    app = QApplication(sys.argv)
    window = Window()
    clientThread=ClientThread(window)
    clientThread.start()
    window.exec()
    sys.exit(app.exec_())