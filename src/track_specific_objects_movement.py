import os
import cv2
import time
import threading
import multiprocessing
import concurrent.futures

import numpy as np
import cvlib as cv
from cvlib.object_detection import draw_bbox

class RTCObjectDetection(object):

    bbox, label, conf = str(), str(), str()

    def __init__(self,filename='/home/anthony/video.avi'):

        self.capture = cv2.VideoCapture('/dev/cam0')
        self.capture.set(3,1080)
        self.capture.set(4,1080)

        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        
        self.video_writer = cv2.VideoWriter(
            filename, cv2.VideoWriter_fourcc(*'MJPG'), self.fps,
            (int(self.capture.get(3)), int(self.capture.get(4)))
        )
        
        print('[INFO] (RTCObjectDetection.__init__) - fps => '+str(self.fps))

    @staticmethod
    def detect_common_objects(frame,queue={}):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers = 4) as executor:
                thread = executor.submit(cv.detect_common_objects, frame)
                RTCObjectDetection.bbox, RTCObjectDetection.label, RTCObjectDetection.conf = thread.result()
        except Exception as eStartThread:
            print("[ERROR] (RTCObjectDetection.detect_common_objects) - Threading exception eStartThread => " + str(eStartThread))

    def find_index_of_label(self,labels=[],label=str()):
        for index in range(0,len(labels)):
            if label in labels[index]:
                return int(index)
        return None

    def init_bbox(self,bbox):
        pass

    def init_o_bbox(self,o_bbox):
        pass

    def main(self, queue):

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
                index = int(self.find_index_of_label(RTCObjectDetection.label))

                if 'cell phone' in RTCObjectDetection.label:

                    # Initialize original bbox if no value has been assigned yet
                    if o_bbox is None or not o_bbox:
                        o_bbox = RTCObjectDetection.bbox[index]

                    # Set bbox to the corresponding label index
                    bbox = RTCObjectDetection.bbox[index]

                    print('[INFO] (RTCObjectDetection.main) - bbox(NO MOVEMENT) => '+str(bbox))
                    print('[INFO] (RTCObjectDetection.main) - o_bbox(NO MOVEMENT) => '+str(o_bbox))

                    # Numpy arrays are needed so we can compare 2d array elements
                    # to their corresponding indexes, i.e., n1[0] -> n2[0], n1[1] -> n2[1], etc.
                    n1 = np.array(o_bbox)
                    n2 = np.array(bbox)

                    try:
                        if ((n1-n2) > 50).any():
                            print('Cell phone movement detected!')
                            print('[INFO] (RTCObjectDetection.main) - n1 => '+str(n1))
                            print('[INFO] (RTCObjectDetection.main) - n2 => '+str(n2))
                            # If movement of desired(specified) object is detected re-init o_bbox's values
                            o_bbox = RTCObjectDetection.bbox[index]
                            print('[INFO] (RTCObjectDetection.main) - o_bbox(MOVEMENT) => '+str(o_bbox))
                    except Exception as exception:
                        print('Exception exception => '+str(exception))
                        pass

                RTCObjectDetection.label = None
        
            cv2.imshow('output', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.capture.release()
                self.video_writer.release()
                break


if __name__ == '__main__':
    queue = multiprocessing.Queue(maxsize=3)

    rtc_object_detection = RTCObjectDetection()
    rtc_object_detection.main(queue)

    cv2.destroyAllWindows()
