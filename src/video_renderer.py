import re
import os
import cv2
import glob

import numpy as np

from optparse import OptionParser

class VideoRenderer(object):

 
    def __init__(self,config_dict):

        self.path       = config_dict['path']
        self.fps        = int(config_dict['fps'])
        self.glob_regex = config_dict['glob_regex']
        self.fourcc     = cv2.VideoWriter_fourcc(*config_dict['fourcc_ext'])

    @staticmethod
    def change_directory(path):
        os.chdir(path)

    def convert_list_into_sorted_dict(self,tagged_images_list=[],image_dict={}):
        for index in range(0,len(tagged_images_list)):
            grouped = re.search('(capture)(\d+)(.png)\.([\w\d]+)', tagged_images_list[index], re.I)
            if not grouped is None:
                if not grouped.group(4) in image_dict:
                    image_dict[grouped.group(4)] = []
                image_dict[grouped.group(4)].append(grouped.group())
        return image_dict


    def images_list(self,tagged_images_dict={}):
        VideoRenderer.change_directory(self.path)
        return glob.glob(self.glob_regex+'.*')
 
    def render(self):
        for key,data in self.convert_list_into_sorted_dict(self.images_list()).items():
            for f in data:
                image = cv2.imread(f)
                height, width, layers = image.shape
                size = (width,height)

                video_writer = cv2.VideoWriter(key+'.avi', self.fourcc, self.fps, size)
                video_writer.write(image)
                video_writer.release()

if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-f', '--fps',
        dest='fps', type='int', default='25',
        help='.')

    parser.add_option('-p', '--path',
        dest='path', default='/var/gluster/videos/',
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
    video_renderer.render()
