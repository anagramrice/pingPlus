import os, sys
import subprocess as sp 
import time
import argparse
import requests
import logging
from datetime import datetime



desc = '''
    options
    1.ping device and send a number of packets to the device's ip address:
    usage: python pingPlus.py -n number_of_packets -i ip -c 1

    2.check embedded device server
    usage: python pingPlus.py -i ip -c 2
'''
class cmdParser(object):

    def __init__(self):

        self.parser = argparse.ArgumentParser(description=desc,add_help=True)
        self.parser.add_argument('-i',required=True,dest="ip",help='ip address of device')
        self.parser.add_argument('-n',dest='count',help='number of packets')
        self.parser.add_argument('-c',default='3',choices=['1', '2', '3'], dest='cmd',help='ping the device (1) or do GET to check if EWS (2) is up and running default (3) both')
        self._args = self.parser.parse_args()
        self.ip = self._args.ip
        self.count = self._args.count if self._args.count is not None else '20'
        self.cmd = self._args.cmd 

        if self.cmd == '1':
            self.instance = pingPlus(self.ip, self.count)
        elif self.cmd == '2':
            self.instance = CheckServer(self.ip)
        elif self.cmd == '3':
            instance = pingPlus(self.ip, self.count)
            instance2 = CheckServer(self.ip)
            
class pingPlus(object):

    def __init__(self,ip,count):
        try:
            from DirectoryManager import logDirectory as ld
            parent = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
            logfile = ld.set_log_file_dest(sys.argv[0].split('\\'),parent)
            logging.basicConfig(format='%(asctime)s (%(threadName)-10s) %(levelname)-8s %(message)s',filename=logfile,level=logging.DEBUG)
        except ImportError:
            logging.basicConfig(format='%(asctime)s (%(threadName)-10s) %(levelname)-8s %(message)s',filename='pingPlus.log',level=logging.DEBUG)             

        self.cmd = 'ping -n '+ ' '.join([count,ip]) if os.name == 'nt' else 'ping -c '+ ' '.join([count,ip])
        if os.name == 'nt':
            p = sp.Popen(self.cmd.split(), stdout=sp.PIPE, stderr=sp.PIPE, creationflags=sp.CREATE_NEW_CONSOLE)
        else:
            p = sp.Popen(self.cmd.split(), stdout=sp.PIPE, stderr=sp.PIPE)

        with p.stdout:
            self.log_subprocess_output(p.stdout)
        exitcode = p.wait() # 0 means success
        logging.info('ping device ip finished')
        
    def log_subprocess_output(self, pipe):
        for line in iter(pipe.readline, b''): # b'\n'-separated lines
            logging.info('%r', line.rstrip('\r\n'))
            
class CheckServer(object):
    def __init__(self, ip):
        try:
            from DirectoryManager import logDirectory as ld
            parent = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
            logfile = ld.set_log_file_dest(sys.argv[0].split('\\'),parent)
            logging.basicConfig(format='%(asctime)s (%(threadName)-10s) %(levelname)-8s %(message)s',filename=logfile,level=logging.DEBUG)
        except ImportError:
            logging.basicConfig(format='%(asctime)s (%(threadName)-10s) %(levelname)-8s %(message)s',filename='pingPlus.log',level=logging.DEBUG)  
        self.url = 'http://'+ip
        self.res = '--'
        try:
            r = requests.head(self.url)
            self.res = str(r.status_code)
        except requests.ConnectionError:
            self.res = 'FAILED: connection error'
        logging.info('%s: %s', self.url, self.res)

if __name__ == '__main__':
    new = cmdParser()



