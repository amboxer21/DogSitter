import cv2
import glob
import threading

import numpy as np
import cvlib as cv

from optparse import OptionParser
from threading import Thread, Lock

class ImageParser(object):

    def __init__(self,config_dict={}):
        self.path      = config_dict['path']
        self.remove    = config_dict['remove']
        self.object    = config_dict['object']
        self.verbose   = config_dict['verbose']
        self.extension = config_dict['extension']

    def images(self):
        return glob.glob(self.path+'*.'+self.extension)

    def process(self,image):

        fname = image.split("/")[-1] 
        img   = cv2.imread(image)
        bbox, label, conf = cv.detect_common_objects(img)

        if self.verbose and label:
            print('[INFO] Label('+str(label)+') found in '+str(fname))

        if self.object in label:
            print('[INFO] Dog found in image: '+str(fname))
            if self.remove:
                print('[INFO] Removing image => '+str(fname))

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-b', '--object',
        dest='object', default='dog',
        help='This is the object that we are looking for in our pictures.')

    parser.add_option('--remove',
        dest='remove', action='store_true', default=False,
        help='Option to remove Photos.')

    parser.add_option('--verbose',
        dest='verbose', action='store_true', default=False,
        help='Option to make output more verbose.')

    parser.add_option('-e', '--extension',
        dest='extension', default='png',
        help='The extension type of the images that we are parsing '
            + 'without the period. An example would be: png, jpg, etc.')

    parser.add_option('-p', '--path',
        dest='path', default='/var/gluster/capture/',
        help='The full path of where the images we are to process..')

    (options, args) = parser.parse_args()

    config_dict = {
        'path': options.path,
        'object': options.object,
        'remove': options.remove,
        'verbose': options.verbose,
        'extension': options.extension,
    }

    mutex        = Lock()
    image_parser = ImageParser(config_dict)

    for image in image_parser.images():
        mutex.acquire()
        image_parser.process(image)
        mutex.release()
