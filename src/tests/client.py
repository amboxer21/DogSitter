#!/usr/bin/python3.7

import os
import re
import sys
import time
import email
import socket
import signal
import smtplib
import logging
import threading
import logging.handlers

from optparse import OptionParser

class Client(object):

    def __init__(self,options_dict={}):
        self.ip                  = options_dict['ip']
        self.port                = options_dict['port']

    def send_message(self,message=str()):
        try:
            time.sleep(0.5)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((self.ip,self.port))
            sock.send(bytes(message, 'utf-8'))
            sock.close()
        except Exception as exception:
            print('Client.send_message() Exception => '+str(exception))

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', '--ipaddr',
        dest='ipaddr', default='0.0.0.0',
        help='This is the IP address of the server.')

    parser.add_option('-p', '--port',
        dest='port', type='int', default=50050,
        help='Server port defaults to port 50050')

    parser.add_option('-s', '--string',
        dest='string', default='0.0.0.0:start_recording:skij89034l40od',
        help='String to send to the server. This defaults to "0.0.0.0:start_recording:skij89034l40od"')

    (options, args) = parser.parse_args()

    options_dict = {'ip': options.ipaddr, 'port': options.port}

    Client(options_dict).send_message(options.string)
