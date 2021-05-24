import cv2
import glob

import numpy as np

from optparse import OptionParser

class VideoRenderer(object):
 
    def __init__(self,config_dict):

        self.size       = ()
        self.images     = []

        self.path       = config_dict['path']
        self.fps        = int(config_dict['fps'])
        self.glob_regex = config_dict['glob_regex']
        self.fourcc     = cv2.VideoWriter_fourcc(*config_dict['fourcc_ext'])

    def populate_images_array(self):
        for _file in glob.glob(self.path+self.glob_regex):
            image = cv2.imread(_file)
            height, width, layers = image.shape
            self.size = (width,height)
            self.images.append(image)
 
    def render(self):

        filename = self.path + 'capture.avi'

        video_writer = cv2.VideoWriter(filename, self.fourcc, self.fps, self.size)
 
        for index in range(len(self.images)):
            video_writer.write(self.images[index])
            video_writer.release()

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-f', '--fps',
        dest='fps', type='int', default='25',
        help='.')

    parser.add_option('-p', '--path',
        dest='path', default='/home/anthony/Pictures/capture/',
        help='.')

    parser.add_option('-g', '--glob-regex',
        dest='glob_regex', default='*.png',
        help='.')

    parser.add_option('-e', '--fourcc-ext',
        dest='fourcc_ext', default='MJPG',
        help='.')

    (options, args) = parser.parse_args()


    config_dict = {
        'fps': options.fps,
        'path': options.path,
        'glob_regex': options.glob_regex,
        'fourcc_ext': options.fourcc_ext,
    }

    video_renderer = VideoRenderer(config_dict)
    video_renderer.populate_images_array()
    video_renderer.render()
