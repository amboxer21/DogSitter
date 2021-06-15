import os
import cv2
import time
import threading
import concurrent.futures

import numpy as np
import cvlib as cv

from optparse import OptionParser
from cvlib.object_detection import draw_bbox

class RTCObjectDetection(object):

    # locate object_detection.py
    # bbox.append([int(x), int(y), int(x+w), int(y+h)])

    bbox, label, conf = str(), str(), str()

    def __init__(self,config_dict={}):

        self.camera     = config_dict['camera']
        self.object     = config_dict['object']
        self.logfile    = config_dict['logfile']
        self.verbose    = config_dict['verbose']
        self.filename   = config_dict['filename']
        self.disable_ui = config_dict['disable_ui']

        self.capture = cv2.VideoCapture(self.camera)
        self.capture.set(3,1080)
        self.capture.set(4,1080)

        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        
        self.video_writer = cv2.VideoWriter(
            self.filename, cv2.VideoWriter_fourcc(*'MJPG'), self.fps,
            (int(self.capture.get(3)), int(self.capture.get(4)))
        )
        
        if self.verbose:
            print('[INFO] (RTCObjectDetection.__init__) - fps => '+str(self.fps))

    @staticmethod
    def detect_common_objects(frame, worker_count=4):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers = worker_count) as executor:
                thread = executor.submit(cv.detect_common_objects, frame)
                RTCObjectDetection.bbox, RTCObjectDetection.label, RTCObjectDetection.conf = thread.result()
        except Exception as eStartThread:
            print("[ERROR] (RTCObjectDetection.detect_common_objects) - Threading exception eStartThread => " + str(eStartThread))

    def find_index_of_label(self,labels=[],label=str()):
        for index in range(0,len(labels)):
            if label in labels[index]:
                return int(index)
        return 0

    def main(self):

        # Initialize the frame count tracker to 0
        counter = 0
        o_bbox  = None

        while(True):
        
            ret, frame = self.capture.read()

            # frame number
            counter += 1

            if(counter % (int(self.fps)/4)) == 0:
                # reset frame counter
                counter = 0
                RTCObjectDetection.detect_common_objects(frame)

            if RTCObjectDetection.label:

                frame = draw_bbox(frame, RTCObjectDetection.bbox, RTCObjectDetection.label, RTCObjectDetection.conf)
                index = self.find_index_of_label(RTCObjectDetection.label,self.object)

                if self.verbose:
                    print('[INFO] (RTCObjectDetection.main) - All labels: '+str(RTCObjectDetection.label))

                if self.object in RTCObjectDetection.label:

                    if self.verbose:
                        print('[INFO] (RTCObjectDetection.main) - Object label: '+str(RTCObjectDetection.label))

                    # Initialize original bbox if no value has been assigned yet
                    if o_bbox is None or not o_bbox:
                        o_bbox = RTCObjectDetection.bbox[index]

                    # Set bbox to the corresponding label index
                    bbox = RTCObjectDetection.bbox[index]

                    # Numpy arrays are needed so we can compare 2d array elements
                    # to their corresponding indexes, i.e., n1[0] -> n2[0], n1[1] -> n2[1], etc.
                    n1 = np.array(o_bbox)
                    n2 = np.array(bbox)

                    try:
                        if (abs(n1-n2) > 50).any():
                            print('[INFO] (RTCObjectDetection.main) - '+self.object+' movement detected!')
                            print('[INFO] (RTCObjectDetection.main) - o_bbox numpy(n1) array => '+str(n1))
                            print('[INFO] (RTCObjectDetection.main) - bbox numpy(n2) array   => '+str(n2))
                            # If movement of desired(specified) object is detected re-init o_bbox's values
                            o_bbox = RTCObjectDetection.bbox[index]
                    except Exception as exception:
                        print('[ERROR] (RTCObjectDetection.main) - Exception exception => '+str(exception))
                        pass

                RTCObjectDetection.label = None
        
            if not self.disable_ui:
                cv2.imshow('output', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.capture.release()
                    self.video_writer.release()
                    break


if __name__ == '__main__':

    parser = OptionParser()

    parser.add_option('-c', '--camera-location',
        dest='camera', default='/dev/cam0',
        help='This is the default camera path.')

    parser.add_option('-o', '--object',
        dest='object', default='bottle',
        help='This is the default object we will be tracking.')

    parser.add_option('-v', '--verbose',
        dest='verbose', action='store_true', default=False,
        help="Turns on verbose output. This is turned off by default.")

    parser.add_option('-l', '--log-file',
        dest='logfile', default='/var/log/opencv-tracker.log',
        help='Log file defaults to /var/log/opencv-tracker.log.')

    parser.add_option('-f', '--file-name',
        dest='filename', default='/home/anthony/video.avi',
        help='Filename defaults to /home/anthony/video.avi.')

    parser.add_option('-d', '--disable-ui',
        dest='disable_ui', action='store_true', default=False,
        help="This option disables the UI and only pushes output to the console.")

    (options, args) = parser.parse_args()

    config_dict = {
        'object': options.object, 'verbose': options.verbose,
        'logfile': options.logfile, 'filename': options.filename,
        'camera': options.camera, 'disable_ui': options.disable_ui,
    }

    rtc_object_detection = RTCObjectDetection(config_dict)
    rtc_object_detection.main()

    cv2.destroyAllWindows()
