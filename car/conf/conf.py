#!/usr/bin/python3
#-*- coding: utf-8 -*-
# class conf

class conf :
    
    Type = "server" # "server"/"client"
    
    #VideoUrl = "http://192.168.2.71:8080/?action=stream"
    VideoUrl = "http://192.168.2.71:8000/stream.mjpg"
    
    ServerIP = "192.168.2.71"
    videoServerPort = 8000
    controlServerPort = 8001
    ServerBufferSize = 100
    
    # Video settings
    VideoRate = 24
    VideoWidth = 640
    VideoHeight = 480
    
    timeRecconect = 5000
    
    