#!/usr/bin/env python

import re
import os
import cv2
import glob
import time
import logging
import logging.handlers

import numpy as np

from optparse import OptionParser

class Logging(object):

    @staticmethod
    def log(level,message,verbose=True):
        comm = re.search("(WARN|INFO|ERROR)", str(level), re.M)
        try:
            handler = logging.handlers.WatchedFileHandler(
                os.environ.get("LOGFILE","/var/gluster/logs/dogsitter.log")
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

class VideoRenderer(object):

    def __init__(self,config_dict):

        self.path       = config_dict['path']
        self.fps        = int(config_dict['fps'])
        self.glob_regex = config_dict['glob_regex']
        self.fourcc     = cv2.VideoWriter_fourcc(*config_dict['fourcc_ext'])

    @staticmethod
    def change_directory(path):
        os.chdir(path)

    # Rendered video images are removed after they are rendered
    def cleanup_images(self,image):
        Logging.log('INFO', 'Rendered image -> '+str(image))
        os.remove('/var/gluster/videos/'+image)

    def sort_tagged_images_dict_list(self,array,tag):
        numbers = sorted([int(r.group(2)) for r in [re.search(self.glob_regex,a) for a in array]])
        return ['capture'+str(n)+'_'+tag+'_.png' for n in numbers]

    def sorted_tagged_images_dict(self,tagged_images_dict={}):

        VideoRenderer.change_directory(self.path)

        pngs = glob.glob('*.png')

        for png in pngs:
            result = re.search(self.glob_regex,png)
            if not result is None:
                try:
                    tagged_images_dict[result.group(3)].append(result.group())
                except KeyError:
                    tagged_images_dict[result.group(3)] = []
                    tagged_images_dict[result.group(3)].append(result.group())
        return tagged_images_dict
 
    def render(self):

        sorted_tagged_images_dict = self.sorted_tagged_images_dict()

        for tag,data in sorted_tagged_images_dict.items():
            for frame in self.sort_tagged_images_dict_list(sorted_tagged_images_dict[tag],tag):
                image = cv2.imread(frame)
                height, width, layers = image.shape
                size = (width,height)

                # Video wrtier needs to be fixed! 
                video_writer = cv2.VideoWriter(tag+'.mp4', self.fourcc, self.fps, size)
                video_writer.write(image)
                video_writer.release()
                self.cleanup_images(frame)

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-f', '--fps',
        dest='fps', type='int', default='25',
        help='.')

    parser.add_option('-p', '--path',
        dest='path', default='/var/gluster/videos/',
        help='.')

    parser.add_option('-g', '--glob-regex',
        dest='glob_regex', default='(capture)(\d+)_([\d\w]+)_\.(\w+)',
        help='.')

    parser.add_option('-e', '--fourcc-ext',
        #dest='fourcc_ext', default='MJPG',
        dest='fourcc_ext', default='mp4v',
        help='.')

    (options, args) = parser.parse_args()


    config_dict = {
        'fps': options.fps,
        'path': options.path,
        'glob_regex': options.glob_regex,
        'fourcc_ext': options.fourcc_ext,
    }

    video_renderer = VideoRenderer(config_dict)
    video_renderer.render()
