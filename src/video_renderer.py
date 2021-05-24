import cv2
import glob

import numpy as np

class VideoRenderer(object):
 
    def __init__(self,ext='MJPG'):
        self.size   = ()
        self.images = []
        self.fps    = 25
        self.fourcc = cv2.VideoWriter_fourcc(*ext)

    def populate_images_array(self,path,regex):
        for filename in glob.glob(path+regex):
            image = cv2.imread(filename)
            height, width, layers = image.shape
            self.size = (width,height)
            self.images.append(image)
 
    def render(self,filename):
        video_writer = cv2.VideoWriter(filename, self.fourcc, self.fps, self.size)
 
        for index in range(len(self.images)):
            video_writer.write(self.images[index])
            video_writer.release()

if __name__ == '__main__':

    path = '/home/anthony/Pictures/capture/'

    video_renderer = VideoRenderer()
    video_renderer.populate_images_array(path,'*.png')
    video_renderer.render(path+'capture.avi')
