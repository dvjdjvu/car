#!/usr/bin/python3
# Server is stay in GAZ-66.

import sys, time
import socket
from threading import Thread 
from socketserver import ThreadingMixIn 

import conf
from help import *

conn = None

class ServerThread(Thread, conf.conf):
    def __init__(self): 
        Thread.__init__(self) 

    def run(self): 
        TCP_IP = self.confServerIP
        TCP_PORT = self.confServerPort
        BUFFER_SIZE = self.confServerBufferSize
        tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        tcpServer.bind((TCP_IP, TCP_PORT)) 
        threads = [] 

        tcpServer.listen(4) 
        while True:
            print("Multithreaded Python server : Waiting for connections from TCP clients...") 
            global conn
            (conn, (ip,port)) = tcpServer.accept() 
            newthread = ClientThread(ip, port) 
            newthread.start() 
            threads.append(newthread)         

        for t in threads: 
            t.join() 



class ClientThread(Thread, conf.conf): 

    def __init__(self, ip, port): 
        Thread.__init__(self) 
        self.ip = ip 
        self.port = port 
        print("[+] New server socket thread started for " + ip + ":" + str(port)) 

    def run(self): 
        while True : 
            global conn
            data = conn.recv(2048) 
            print(data)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, service_shutdown)
    signal.signal(signal.SIGINT,  service_shutdown)    

    serverThread = ServerThread()
    serverThread.start()