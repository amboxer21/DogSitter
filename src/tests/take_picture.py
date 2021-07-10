#!/usr/bin/env python2.7

import re,cv2,sys,time

def takePicture(video):
    camera = cv2.VideoCapture(video)
    time.sleep(0.5)
    if not camera.isOpened():
        print("ImageCapture - No cam available")
        return
    elif not camera.isOpened() and video == 0:
        print("ImageCapture - ImageCapture does not detect a camera.")
        return
    print("ImageCapture - Taking picture.")
    time.sleep(0.1) # Needed or image will be dark.
    image = camera.read()[1]
    cv2.imwrite("/var/gluster/capture/capture0.png", image)
    del(camera)

if __name__ == '__main__':
    takePicture(sys.argv[1])
