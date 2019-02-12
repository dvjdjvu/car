import os
import threading, signal, time

def service_shutdown(signum, frame):
    print('Caught signal %d' % signum)
    raise ServerExit