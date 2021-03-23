import os
import re
import cv2
import time
import glob
import shutil

import cvlib as cv

from moviepy.editor import VideoFileClip, concatenate_videoclips

class FileOpts(object):

    @classmethod
    def mkdir_p(cls,dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno == errno.EEXIST and self.dir_exists(dir_path):
                pass
            else:
                raise

    @classmethod
    def dir_exists(cls,dir_path):
        return os.path.isdir(dir_path)

    @classmethod
    def file_exists(cls,file_name):
        return os.path.isfile(file_name)

class DogSitter(object):

    FPS    = 25.0
    FOURCC = cv2.VideoWriter_fourcc(*'MJPG')

    def __init__(self):

        self.ret      = None
        self.frame    = None
        self.output   = None
        self.capture  = None

        self.counter  = 0
        self.vidpath  = os.getcwd() + '/videos'
        self.tmp_dir  = os.getcwd() + '/videos/TMP'

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

        video_files = {}

        bbox, label, conf = str(), str(), str()

        capture  = DogSitter.initialize_capture()
        filename = DogSitter.filename_(int(self.img_num() + 1), self.vidpath) 
        output   = DogSitter.initialize_output(filename, capture)

        if not FileOpts.dir_exists(self.tmp_dir):
            FileOpts.mkdir_p(self.tmp_dir)

        while(True):

            self.counter += 1
            ret, frame = capture.read()

            if re.match('(5|10|15|20|25)', str(self.counter)):
                if self.counter == 25:
                    self.counter = 0

                bbox, label, conf = cv.detect_common_objects(frame)
        
                print("[INFO] Label(s): "+str(label))
                if ('person' and 'bottle') in label:
                    try:
                        number     = int(self.img_num() + 1)
                        video_name = "video" + str(number) + ".avi"
                        filename   = DogSitter.filename_(number, self.vidpath)
                        video_files[video_name] = filename

                        print('[INFO] writing video to '+filename+'.')

                        output = DogSitter.initialize_output(filename, capture)
                        output.write(frame) 

                        #os.system('speaker-test -tsine -f1000 -l1')
                    except KeyboardInterrupt:
                        capture.release()
                        output.release()
                elif not ('person' and 'bottle') in label:
                    # copy list of files into tmp dir, email video then delete
                    for _file, _path in video_files.items():
                        shutil.copy(_path, self.tmp_dir+"/"+_file) 
                    video_files.clear()

if __name__ == '__main__':
    dogsitter = DogSitter()
    dogsitter.main()
