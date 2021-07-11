import os
import re
import cv2
import glob
import time
import shutil
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
        logfile = "/var/gluster/logs/dogsitter.log"
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
            handler.close()
            root.removeHandler(handler)
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
            sock.send(bytes(message,'utf-8'))
            sock.close()
        except Exception as sendMessageException:
            Logging.log("ERROR","(Client.send_message) - Exception sendMessageException: "
                + str(sendMessageException))
            pass

class DistributedProcessing(object):

    image_path = '/var/gluster/capture/'

    def __init__(self,config_dict={}):

        self.pngs    = []

        self.ipaddr  = config_dict['ip']
        self.port    = config_dict['server_port']
        self.lock_id = DistributedProcessing.create_lock(4) 

    def process_image_with_tensorflow(self,tagged_image,pair=('Person','Dog'),verbose=False):

        img = cv2.imread(DistributedProcessing.image_path+tagged_image)
        bbox, label, conf = cv.detect_common_objects(img)
        
        if(pair[0] and pair[1]) in label:

            try:

                client = Client(self.ipaddr,self.port)
                client.send_message('start_recording:'+self.lock_id)

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
                + tagged_image, verbose)

    # This method removes tagged pngs from a list of pngs
    # ['capture2_D4ff_.png','capture2.png','capture22.png','capture22_D4ff_.png']
    # In the example above, 'capture2_D4ff_.png' and 'capture22_D4ff_.png' will be
    # removed from the above list. That would leave us with ['capture2.png','capture22.png'].
    def remove_tagged_pngs_from_pngs(self,pngs):
        # Grabs tagged pngs only
        tagged_pngs = [r for r in [re.search('(capture\d+_[\d\w]+_.png)',png) for png in pngs] if r]
        # removed tagged pngs from the original list
        [pngs.remove(png.group()) for png in tagged_pngs]

    def process(self):

        os.chdir(DistributedProcessing.image_path)
    
        if not self.pngs:
            self.pngs = glob.glob(DistributedProcessing.image_path+'capture[1-9]*.png')

        self.remove_tagged_pngs_from_pngs(self.pngs)

        for png in self.pngs[:2]:

            _png = re.search('(capture)(\d+)(.png)', png)

            if not _png is None:

                locked_png = _png.group(1)+_png.group(2)+'_'+self.lock_id+'_'+_png.group(3)

                try:
                    DistributedProcessing.mv(DistributedProcessing.image_path+png,DistributedProcessing.image_path+locked_png)
                    self.process_image_with_tensorflow(locked_png,('person','bottle'),True)
                    Logging.log('INFO','(DistributedProcessing.process) - Processed image => '+str(DistributedProcessing.image_path+png))
                except Exception as exception:
                    Logging.log('ERROR','(DistributedProcessing.process) - Exception exception(1)('+png+') => '+str(exception),True)
                    continue

                self.pngs.remove(png)

    @staticmethod
    def copyfile(filename,linkname):
        shutil.copyfile(filename,linkname)

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
        time.sleep(0.5)
        mutex.acquire()
        dp.process()
        mutex.release()
