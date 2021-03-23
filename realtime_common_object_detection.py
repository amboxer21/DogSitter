import os
import re
import cv2
import time
import glob

import cvlib as cv

class DogSitter(object):

    FPS    = 24.0
    FOURCC = cv2.VideoWriter_fourcc(*'MJPG')

    def __init__(self):

        self.ret      = None
        self.frame    = None
        self.output   = None
        self.capture  = None

        self.counter  = 0
        self.vidpath  = '/home/anthony/.dogsitter/videos'

    def initialize_video_dot_avi(self, capture, filename):
        self.video_writer(capture, filename)
        self.output.write(self.frame)
        self.capture.release()
        self.out.release()
        
    def img_num(self):
        img_list = []
        os.chdir(self.vidpath)
        for file_name in glob.glob("*.avi"):
            num = re.search("(video)(\d+)(\.avi)", file_name, re.M | re.I)
            img_list.append(int(num.group(2)))
        if not img_list:
            img_list.append(0)
        return max(img_list)

    @staticmethod
    def initialize_capture():
        capture = cv2.VideoCapture(0)
        capture.set(3,320)
        capture.set(4,320)
        return capture

    @staticmethod
    def initialize_output(filename, capture):
        output = cv2.VideoWriter(
            str(filename), DogSitter.FOURCC, DogSitter.FPS, (int(capture.get(3)), int(capture.get(4)))
        )
        return output

    @staticmethod
    def filename_(number, path):
        return path + '/video' + str(number) + '.avi'

    def main(self):

        bbox, label, conf = str(), str(), str()

        capture  = DogSitter.initialize_capture()
        filename = DogSitter.filename_(int(self.img_num() + 1), self.vidpath) 
        output   = DogSitter.initialize_output(filename, capture)

        while(True):

            self.counter += 1
            ret, frame = capture.read()

            if self.counter == 30:
                self.counter = 0
                bbox, label, conf = cv.detect_common_objects(frame)
        
                print(label)
                if 'person' in label and 'bottle' in label:
                    try:
                        filename = DogSitter.filename_(int(self.img_num() + 1), self.vidpath)

                        print('[INFO] writing video to '+filename+'.')

                        output = DogSitter.initialize_output(filename, capture)
                        output.write(frame) 

                        #os.system('speaker-test -tsine -f1000 -l1')
                    except KeyboardInterrupt:
                        capture.release()
                        output.release()

if __name__ == '__main__':
    dogsitter = DogSitter()
    dogsitter.main()
