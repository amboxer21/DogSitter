import os
import re
import cv2
import sys
import time
import glob
import socket
import shutil
import smtplib
import logging
import threading
import multiprocessing
import logging.handlers

import cvlib as cv
import numpy as np

from shutil import copyfile
from optparse import OptionParser

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

try:
    import Image
except:
    from PIL import Image

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

class Mail(object):

    __disabled__ = False

    @staticmethod
    def send(sender,to,password,port,subject,body):
        try:
            if not Mail.__disabled__:
                message = MIMEMultipart()
                message['Body'] = body
                message['Subject'] = subject
                message.attach(MIMEImage(open("/var/gluster/capture/capture"
                    + str(MotionDetection.img_num())
                    + ".png","rb").read()))
                mail = smtplib.SMTP('smtp.gmail.com',port)
                mail.starttls()
                mail.login(sender,password)
                mail.sendmail(sender, to, message.as_string())
                Logging.log("INFO", "(Mail.send) - Sent email successfully!")
            else:
                Logging.log("WARN", "(Mail.send) - Sending mail has been disabled!")
        except smtplib.SMTPAuthenticationError:
            Logging.log("WARN", "(Mail.send) - Could not athenticate with password and username!")
        except TypeError as eTypeError:
            Logging.log("INFO", "(Mail.send) - Picture("
                + str(MotionDetection.img_num())
                + ".png) "
                + "TypeError => "
                + str(eTypeError))
            pass
        except Exception as e:
            Logging.log("ERROR",
                "(Mail.send) - Unexpected error in Mail.send() error e => "
                + str(e))
            pass

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

    @staticmethod
    def copyfiles(filename,linkname):
        copyfile(filename,linkname)

    @staticmethod
    def create_file(file_name):
        if FileOpts.file_exists(file_name):
            Logging.log("INFO", "(FileOpts.compress_file) - File "
                + str(file_name)
                + " exists.")
            return
        Logging.log("INFO", "(FileOpts.compress_file) - Creating file "
            + str(file_name)
            + ".")
        open(file_name, 'w')

class MotionDetection(object):

    delta_count    = None
    colored_frame  = None
    camera_object  = None
    current_frame  = None
    previous_frame = None

    verbose = False
    lock    = multiprocessing.Lock()

    def __init__(self,config_dict={}):

        self.tracker           = 0
        self.frame_count       = 0
        self.count             = 60

        self.ip                = config_dict[0]['ip'][1]
        self.fps               = config_dict[0]['fps'][1]
        self.email             = config_dict[0]['email'][1]
        self.verbose           = config_dict[0]['verbose'][1]
        self.password          = config_dict[0]['password'][1]
        self.email_port        = config_dict[0]['email_port'][1]
        self.configfile        = config_dict[0]['configfile'][1]
        self.server_port       = config_dict[0]['server_port'][1]
        self.camview_port      = config_dict[0]['camview_port'][1]
        self.cam_location      = config_dict[0]['cam_location'][1]
        self.disable_email     = config_dict[0]['disable_email'][1]
        self.burst_mode_opts   = config_dict[0]['burst_mode_opts'][1]

        self.delta_thresh_min  = config_dict[0]['delta_thresh_min'][1]
        self.delta_thresh_max  = config_dict[0]['delta_thresh_max'][1]
        self.motion_thresh_min = config_dict[0]['motion_thresh_min'][1]

        Mail.__disabled__ = self.disable_email
        MotionDetection.verbose = self.verbose

        if not self.disable_email and (self.email is None or self.password is None):
            Logging.log("ERROR",
                "(MotionDetection.__init__) - Both E-mail and password are required!")
            parser.print_help()
            sys.exit(0)

    @staticmethod
    def waitforcamera():
        pushed = False
        found  = False
        while not found:
            try:
                open(options.cam_location)
                found = True
            except FileNotFoundError:
                if not pushed:
                    Logging.log("ERROR", "(PRE-ENTRY) - Camera not found at "+options.cam_location)
                pushed = True
                found  = False
                time.sleep(1)

    @staticmethod
    def img_num():
        img_list = []
        os.chdir("/var/gluster/capture")
        if not FileOpts.file_exists('/var/gluster/capture/capture1.png'):
            Logging.log("INFO", "(MotionDetection.img_num) - Creating capture1.png.",MotionDetection.verbose)
            FileOpts.create_file('/var/gluster/capture/capture1.png')
        for file_name in glob.glob("*.png"):
            num = re.search("(capture)(\d+)(\.png)", file_name, re.M | re.I)
            img_list.append(int(num.group(2)))
        return max(img_list)

    @staticmethod
    def copyfiles(filename,linkname):
        copyfile(filename,linkname)
    
    @staticmethod
    def take_picture(frame,path='/var/gluster/capture/',tag=str()):

        capture = 'capture' + str(MotionDetection.img_num() + 1) + '.png'
        picture_name = path + capture + tag

        image = Image.fromarray(frame)
        image.save(picture_name)
        #MotionDetection.copyfiles(picture_name,'/var/gluster/pi/'+capture)

    @staticmethod
    def start_thread(proc,*args):
        try:
            t = threading.Thread(target=proc,args=args)
            t.daemon = False
            t.start()
        except Exception as eStartThread:
            Logging.log("ERROR",
                "(MotionDetection.start_thread) - Threading exception eStartThread => "
                + str(eStartThread))

    @classmethod
    def calculate_delta(cls):
        frame_delta = cv2.absdiff(cls.previous_frame, cls.current_frame)
        (ret, frame_delta) = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        frame_delta = cv2.dilate(frame_delta,np.ones((5,5), np.uint8),iterations=1)
        frame_delta = cv2.normalize(frame_delta, None, 0, 255, cv2.NORM_MINMAX)
        cls.delta_count = cv2.countNonZero(frame_delta)

    @classmethod
    def update_current_frame(cls):
        cls.previous_frame = cls.current_frame
        (ret, cls.current_frame) = cls.camera_object.read()
        cls.colored_frame = cls.current_frame
        cls.current_frame = cv2.cvtColor(cls.current_frame, cv2.COLOR_RGB2GRAY)
        cls.current_frame = cv2.GaussianBlur(cls.current_frame, (21, 21), 0)

    def capture(self,queue=None,bbox=None,label=None,conf=None):

        Logging.log("INFO", "(MotionDetection.capture) - Lock acquired!",self.verbose)
        Logging.log("INFO", "(MotionDetection.capture) - MotionDetection system initialized!", self.verbose)

        #MotionDetection.camera_object = cv2.VideoCapture(self.cam_location)
        MotionDetection.camera_object = cv2.VideoCapture(0)
        MotionDetection.camera_object.set(3, 320)
        MotionDetection.camera_object.set(4, 320)

        MotionDetection.previous_frame = MotionDetection.camera_object.read()[1]
        MotionDetection.colored_frame  = MotionDetection.previous_frame 
        MotionDetection.previous_frame = cv2.cvtColor(MotionDetection.previous_frame, cv2.COLOR_RGB2GRAY)
        MotionDetection.previous_frame = cv2.GaussianBlur(MotionDetection.previous_frame, (21, 21), 0)

        MotionDetection.current_frame = MotionDetection.camera_object.read()[1]
        MotionDetection.current_frame = cv2.cvtColor(MotionDetection.current_frame, cv2.COLOR_RGB2GRAY)
        MotionDetection.current_frame = cv2.GaussianBlur(MotionDetection.current_frame, (21, 21), 0)

        while(True):

            time.sleep(0.1)

            MotionDetection.calculate_delta()

            # The tracker is each time the system detecs movement and the count is each time the system does not detect movement.
            if MotionDetection.delta_count > int(self.delta_thresh_min) and MotionDetection.delta_count < int(self.delta_thresh_max):
                self.tracker += 1
                if self.tracker >= 60 or self.count >= 60:
                    self.count   = 0
                    self.tracker = 0

                    Logging.log("INFO",
                        "(MotionDetection.capture) - Motion detected with threshold levels at "
                        + str(MotionDetection.delta_count)
                        + "!", self.verbose)

                    for placeholder in range(0,self.burst_mode_opts):
                        time.sleep(1)
                        MotionDetection.take_picture(MotionDetection.camera_object.read()[1])
                        MotionDetection.start_thread(Mail.send,self.email,self.email,self.password,self.email_port,
                            'Motion Detected','MotionDetection.py detected movement!')

                        if not queue is None and not queue.empty():
                            res = re.search('(start_recording)(:)([\d\w]+)', str(message), re.I)
                            if not res is None:
                                Logging.log("INFO", "(MotionDetection.capture) - queue.get() "
                                    + str(queue.get()), self.verbose)
                                MotionDetection.lock.acquire()
                                self.frame_count += 1
                                if not self.frame_count == 120:
                                    print(int(self.frame_count))
                                #MotionDetection.take_picture(MotionDetection.camera_object.read()[1],'/var/gluster/videos/',self.lock_id)
                                MotionDetection.lock.release()

            elif MotionDetection.delta_count < self.motion_thresh_min:
                self.count  += 1
                self.tracker = 0

            MotionDetection.update_current_frame()

class Server(MotionDetection):

    def __init__(self,queue):
        super().__init__(config_dict)

        self.queue = queue

        process = multiprocessing.Process( target=MotionDetection(config_dict).capture,args=(self.queue,) )
        process.daemon = True
        process.start()

        try:
            self.sock = socket.socket()
            self.sock.bind(('0.0.0.0', self.server_port))
        except Exception as eSock:
            #if 'Address already in use' in eSock and PS.aux('motiondetection') is not None:
            if 'Address already in use' in eSock:
                Logging.log("ERROR", "(Server.__init__) - eSock error e => "
                    + str(eSock))
                #os.system('/usr/bin/sudo /sbin/reboot')

    def handle_incoming_message(self,*data):
        for(sock,queue) in data:
            message = sock.recv(1024)
            if('start_recording' in str(message)):
                Logging.log("INFO",
                    "(Server.handle_incoming_message) - Starting to record! -> (start_recording)")
                self.queue.put('start_recording')
            else:
                pass
            sock.close()

    def server_main(self):

        Logging.log("INFO", "(Server.server_main) - Listening for connections.")

        while(True):
            time.sleep(0.05)
            try:
                self.sock.listen(10)
                (con, addr) = self.sock.accept()
                #if not '127.0.0.1' in str(addr):
                if not '1.1.1.1' in str(addr):
                    Logging.log("INFO",
                        "(Server.server_main) - Received connection from "
                        + str(addr))

                Server.handle_incoming_message(self,(con,self.queue))

            except KeyboardInterrupt:
                print('\n')
                Logging.log("INFO", "(Server.server_main) - Caught control + c, exiting now.\n")
                self.sock.close()
                sys.exit(0)
            except Exception as eAccept:
                Logging.log("ERROR", "(Server.server_main) - Socket accept error: "
                    + str(eAccept))

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-i', '--ip',
        dest='ip', default='0.0.0.0',
        help='This is the IP address of the server.')

    parser.add_option('-v', '--verbose',
        dest='verbose', action='store_true', default=False,
        help="Turns on verbose logging. This is turned off by default.")

    parser.add_option('-E', '--email-port',
        dest='email_port', type='int', default=587,
        help='E-mail port defaults to port 587')

    parser.add_option('-l', '--log-file',
        dest='logfile', default='/var/gluster/logs/dogsitter.log',
        help='Log file defaults to /var/gluster/logs/dogsitter.log.')

    parser.add_option('-D', '--disable-email',
        dest='disable_email', action='store_true', default=False,
        help='This option allows you to disable the sending of E-mails.')

    parser.add_option("-g", "--config-file",
        dest="configfile", default=str(),
        help="Configuration file path.")

    parser.add_option('-c', '--camera-location',
        dest='cam_location', default='/dev/video0',
        help='Camera index number that defaults to 0. This is the '
            + 'location of the camera - Which is usually /dev/video0.')

    parser.add_option('-f', '--fps',
        dest='fps', type='int', default='30',
        help='This sets the frames per second for the motion '
            + 'capture system. It defaults to 30 frames p/s.')

    parser.add_option('-e', '--email',
        dest='email',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail address is used to send the pictures taken as '
            + 'well as notify you of motion detected.')

    parser.add_option('-p', '--password',
        dest='password',
        help='This argument is required unless you pass the '
            + 'pass the --disable-email flag on the command line. '
            + 'Your E-mail password is used to send the pictures taken '
            + 'as well as notify you of motion detected.')

    parser.add_option('-C', '--camview-port',
        dest='camview_port', type='int', default=5000,
        help='CamView port defaults to port 5000'
            + 'This is the port the streaming feature runs on. '
            + 'The streaming feature is the ability to view the '
            + 'live feed from the camera via ANdroid app.')

    parser.add_option('-t', '--delta-threshold-min',
        dest='delta_thresh_min', type='int', default=1500,
        help='Sets the minimum movement threshold '
            + 'to trigger the programs image capturing/motion routines. If movement '
            + 'above this level is detected then this is when MotiondDetection '
            + 'goes to work. The default value is set at 1500.')

    parser.add_option('-T', '--delta-threshold-max',
        dest='delta_thresh_max', type='int', default=10000,
        help='Sets the maximum movement threshold when the '
            + 'programs image capturingi/motion routines stops working. '
            + 'If movement above this level is detected then this program '
            + ' will not perform any tasks and sit idle. The default value is set at 10000.')

    parser.add_option('-b', '--burst-mode',
        dest='burst_mode_opts', type='int', default='1',
        help='This allows the motiondetection framework to take '
            + 'multiple pictures instead of a single picture once it '
            + 'detects motion. Example usage for burst mode would look '
            + 'like: --burst-mode=10. 10 being the number of photos to take '
            + 'once motion has been detected.')

    parser.add_option('-m', '--motion-threshold-min',
        dest='motion_thresh_min', type='int', default=500,
        help='Sets the minimum movement threshold to start the framework '
            + 'and trigger the programs main motion detection routine. '
            + 'This is used because even if there is no movement as all '
            + 'the program still receives false hits and the values can '
            + 'range from 1 to around 500 and is what the default is set to - 500.')

    parser.add_option('-S', '--server-port',
        dest='server_port', type='int', default=50050,
        help='Server port defaults to port 50050.'
            + 'This is the port the command server runs on. '
            + 'This server listens for specific commands from '
            + 'the Android app and controls the handling of the '
            + 'camera lock thats passed abck and forth between the '
            + 'streaming server and the motion detection system.')

    (options, args) = parser.parse_args()

    fileOpts = FileOpts()
    #fileOpts = FileOpts(options.logfile)

    # These strings are used to compare against the command line args passed.
    # It could have been done with an action but default values were used instead.
    # These strings are coupled with their respective counterpart in the config_dist
    # data structure declared below.

    config_dict = [{
        'ip': ['', options.ip],
        'fps': ['', options.fps],
        'email': ['', options.email],
        'verbose': ['', options.verbose],
        'logfile': ['', options.logfile],
        'password': ['', options.password],
        'email_port': ['', options.email_port],
        'configfile': ['', options.configfile],
        'server_port': ['', options.server_port],
        'cam_location': ['', options.cam_location],
        'camview_port': ['', options.camview_port],
        'disable_email': ['', options.disable_email],
        'burst_mode_opts': ['', options.burst_mode_opts],
        'delta_thresh_max': ['', options.delta_thresh_max],
        'delta_thresh_min': ['', options.delta_thresh_min],
        'motion_thresh_min': ['', options.motion_thresh_min]
    }, []]

    motiondetection = MotionDetection(config_dict)
    motiondetection.waitforcamera()

    Server(multiprocessing.Queue()).server_main()
