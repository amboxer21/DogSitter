import os
import re
import cv2
import glob
import time
import string
import random
import logging
import threading
import logging.handlers

import cvlib as cv
import numpy as np

from threading import Thread, Lock

class Logging(object):

    @staticmethod
    def log(level,message,verbose=True):
        logfile = "/home/pi/.dogsitter/logs/dogsitter.log"
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
                    + " - ImageCapture - "
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

class DistributedProcessing(object):

    def __init__(self):

        self.pi      = {}
        self.path    = '/var/gluster/pi/'
        self.lock_id = DistributedProcessing.create_lock(14) 

        os.chdir('/var/gluster/pi')

    def process_image_with_tensorflow(self,image,pair=('Person','Dog'),verbose=False):

        bbox, label, conf = cv.detect_common_objects(cv2.imread(image))
        
        if(pair[0] and pair[1]) in label:
            Logging.log("INFO","(DistributedProcessing.process_image_with_tensorflow) - "
                + pair[0] + " and "
                + pair[1] + " found in image "
                + image, verbose)
            os.remove(image) 
            #os.system('speaker-test -tsine -f1000 -l1')

    def process(self):
    
        pngs = glob.glob("*.png")
        pngs.sort()

        for png in pngs[:2]:
            locked_png = png + "." + self.lock_id
            try:

                DistributedProcessing.mv(self.path+png,self.path+locked_png)
                self.process_image_with_tensorflow(locked_png,('person','bottle'),True)

            except Exception as exception:
                Logging.log('ERROR','(DistributedProcessing.process) - Exception exception => '+str(exception),True)
                pass

    @staticmethod
    def mv(filename,linkname):
        os.rename(filename,linkname)

    @staticmethod
    def create_lock(str_len=14):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k = str_len))

if __name__ == '__main__':

    mutex = Lock()
    dp    = DistributedProcessing()

    while(True):
        mutex.acquire()
        dp.process()
        mutex.release()
