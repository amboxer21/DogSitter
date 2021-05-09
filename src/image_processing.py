import os
import re
import cv2
import glob
import time
import socket
import string
import random
import logging
import threading
import logging.handlers

import cvlib as cv
import numpy as np

from optparse import OptionParser
from threading import Thread, Lock

class Logging(object):

    @staticmethod
    def log(level,message,logfile=str(),verbose=True):
        logfile = "/var/gluster/pi/dogsitter.log"
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE",logfile)
            )
            formatter = logging.Formatter(logging.BASIC_FORMAT)
            handler.setFormatter(formatter)
            root = logging.getLogger()
            root.setLevel(os.environ.get("LOGLEVEL", str(level)))
            root.addHandler(handler)
            # Log all calls to this class in the logfile no matter what.
            if comm is None:
                print(str(level) + " is not a level. Use: WARN, ERROR, or INFO!")
                return
            elif comm.group() == 'ERROR':
                logging.error(str(time.asctime(time.localtime(time.time()))
                    + " - DogSitter - "
                    + str(message)))
            elif comm.group() == 'INFO':
                logging.info(str(time.asctime(time.localtime(time.time()))
                    + " - DogSitter - "
                    + str(message)))
            elif comm.group() == 'WARN':
                logging.warn(str(time.asctime(time.localtime(time.time()))
                    + " - DogSitter - "
                    + str(message)))
            if verbose or str(level) == 'ERROR':
                print("(" + str(level) + ") "
                    + str(time.asctime(time.localtime(time.time()))
                    + " - DogSitter - "
                    + str(message)))
        except IOError as eIOError:
            if re.search('\[Errno 13\] Permission denied:', str(eIOError), re.M | re.I):
                print("(ERROR) DogSitter - Must be sudo to run DogSitter!")
                sys.exit(0)
            print("(ERROR) DogSitter - IOError in Logging class => "
                + str(eIOError))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - DogSitter - IOError => "
                + str(eIOError)))
        except Exception as eLogging:
            print("(ERROR) DogSitter - Exception in Logging class => "
                + str(eLogging))
            logging.error(str(time.asctime(time.localtime(time.time()))
                + " - DogSitter - Exception => "
                + str(eLogging)))
            pass
        return

class Client(object):

    __timeout__ = 1
    __sleep__   = 0.5

    def __init__(self,ipaddr,port):
        self.port   = port
        self.ipaddr = ipaddr

    def send_message(self,message=str()):
        try:
            time.sleep(Client.__sleep__)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(Client.__timeout__)
            sock.connect((self.ipaddr,self.port))
            sock.send(message)
            sock.close()
        except Exception as sendMessageException:
            Logging.log("ERROR","(Client.send_message) - Exception sendMessageException: "
                + str(sendMessageException))
            pass

class DistributedProcessing(object):

    def __init__(self,config_dict={}):

        self.ipaddr  = config_dict['ip']
        self.port    = config_dict['server_port']
        self.lock_id = DistributedProcessing.create_lock(14) 

    def process_image_with_tensorflow(self,image,pair=('Person','Dog'),verbose=False):

        bbox, label, conf = cv.detect_common_objects(cv2.imread(image))
        
        if(pair[0] and pair[1]) in label:

            try:

                client = Client(self.ipaddr,self.port)
                client.send_message('start_recording')

                Logging.log("INFO","(DistributedProcessing.process_image_with_tensorflow) - "
                    + " Sent 'start_recording' string to "
                    + "address " + str(self.ipaddr)
                    + ":" + str(self.port) + ".")
            except Exception as clientException:
                Logging.log("ERROR","(DistributedProcessing.process_image_with_tensorflow) - Exception clientException: "
                    + str(clientException))

            Logging.log("INFO","(DistributedProcessing.process_image_with_tensorflow) - "
                + pair[0] + " and "
                + pair[1] + " found in image "
                + image, verbose)

            #os.system('speaker-test -tsine -f1000 -l1')
        else:
            os.remove(image) 

    def process(self):

        os.chdir('/var/gluster/pi')
    
        pngs = glob.glob("*.png")
        pngs.sort()

        for png in pngs[:3]:

            locked_png = png + "." + self.lock_id

            try:
                DistributedProcessing.mv(png,locked_png)
            except Exception as exception:
                Logging.log('ERROR','(DistributedProcessing.process)(1) - Exception exception => '+str(exception),True)
                continue

            try:
                self.process_image_with_tensorflow(locked_png,('person','bottle'),True)
            except Exception as exception:
                Logging.log('ERROR','(DistributedProcessing.process)(2) - Exception exception => '+str(exception),True)
                continue

    @staticmethod
    def mv(filename,linkname):
        os.rename(filename,linkname)

    @staticmethod
    def create_lock(str_len=14):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-i', '--ip',
        dest='ip', default='0.0.0.0',
        help='This is the IP address of the server.')

    parser.add_option('-S', '--server-port',
        dest='server_port', type='int', default=50050,
        help='Server port defaults to port 50050.'
            + 'This is the port the command server runs on. '
            + 'This server listens for specific commands from '
            + 'the Android app and controls the handling of the '
            + 'camera lock thats passed abck and forth between the '
            + 'streaming server and the motion detection system.')

    (options, args) = parser.parse_args()


    config_dict = {
        'ip': options.ip, 'server_port': options.server_port,
    }

    mutex = Lock()
    dp    = DistributedProcessing(config_dict)

    while(True):
        mutex.acquire()
        dp.process()
        mutex.release()
