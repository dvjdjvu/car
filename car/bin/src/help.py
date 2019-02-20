#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import re
import threading
import signal
import time
import datetime

class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def service_shutdown(signum, frame):
    Print('[info]: Caught signal %d' % signum)
    os._exit(1)

def set_proc_name(newName):
    """
    Изменение имени процесса для ps, в top не работает.
            
    Args:
        newName:   (String) Новое имя.
    """    
    
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newName)+1)
    buff.value = newName.encode('utf-8')
    libc.prctl(15, byref(buff), 0, 0, 0)

def get_proc_name():
    """
    Получить имя этого процесса.
            
    Returns:
        (String)
    """  
    
    from ctypes import cdll, byref, create_string_buffer
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(128)
    # 16 == PR_GET_NAME from <linux/prctl.h>
    libc.prctl(16, byref(buff), 0, 0, 0)
    
    return buff.value.decode("utf-8")

def Print(objs, sep=' ', end='', file='', flush='') :
    objs = get_proc_name() + ':' + str(os.getpid()) + ':[' + datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ']' + str(objs)
    
    if re.search(r'\[info\]', objs) :
        objs = objs.replace('[info]', '')
        objs =  BColors.OKGREEN + '[info]' + BColors.ENDC + ':' + objs
    elif re.search(r'\[notice\]', objs) :
        objs = objs.replace('[notice]', '')
        objs =  BColors.OKBLUE + '[notice]' + BColors.ENDC + ':' + objs
    elif re.search(r'\[error\]', objs) :
        objs = objs.replace('[error]', '')
        objs =  BColors.HEADER + '[error]' + BColors.ENDC + ':' + objs
    elif re.search(r'\[critical\]', objs) :
        objs = objs.replace('[critical]', '')
        objs =  BColors.FAIL + '[critical]' + BColors.ENDC + ':' + objs
    elif re.search(r'\[warning\]', objs) :
        objs = objs.replace('[warning]', '')
        objs =  BColors.WARNING + '[warning]' + BColors.ENDC + ':' + objs
    
    print(objs, sep, end, file, flush)