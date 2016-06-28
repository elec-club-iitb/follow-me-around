import cv2
from time import sleep
import serial
from serial.tools.list_ports import comports
from util import get_motion_mask, cleanup_mask, get_bounding_rect


class MotionTracker():
    arduino_port = ""
    arduino = None

    frames = []
    center = (0, 0)

    prev_size = (0, 0)
    size_dev = 1000
    size_dev_thres = 50
    size_steady_time = 0

    STATE_ID_TEMPL = 1
    STATE_FOLLOW = 2
    state = STATE_ID_TEMPL

    def __init__(self):
        self.camera = cv2.VideoCapture(0)

        ports = comports()
        for p in ports:
            print p[1]
            if "Arduino" in p.manufacturer:
                self.arduino_port = p[0]
        if self.arduino_port:
            self.arduino = serial.Serial(self.arduino_port, 38400)

    def turnCamera(self):
        if self.center != (0, 0):
            w, h, _ = self.im.shape
            delta_theta = self.center[0] - w/2
            delta_theta *= -120.0 / w
            print delta_theta
            if self.arduino:
                self.arduino.write(str(delta_theta).encode('ascii'))
                self.frames = []
                self.center = (0, 0)
                sleep(1)


    def get_frame_diff_template(self):
        diff = get_motion_mask(self.frames, 40)
        diff = cleanup_mask(diff, 4, 10)

        rect = get_bounding_rect(diff)
        if rect:
            cv2.rectangle(self.im, rect[0], rect[1], [0, 0, 255])
            size = rect[1][0] - rect[0][0], rect[1][1] - rect[0][1]
            size_dev = ((self.prev_size[0] - size[0])**2 +
                        (self.prev_size[1] - size[1])**2)**0.5
            if size_dev < self.size_dev_thres:
                self.size_steady_time += 1
            else:
                self.size_steady_time = 0
            self.prev_size = size
        else:
            self.prev_size = (0, 0)
            self.size_steady_time = 0

        cv2.imshow("diff", diff)

        if self.size_steady_time > 10:
            return self.im[rect[0][1]:rect[1][1],
                           rect[0][0]:rect[1][0],:]
        else:
            return None


    def findTemplate(self):
        match = cv2.matchTemplate(self.im, self.template, cv2.TM_CCORR_NORMED)
        mv, Mv, ml, Ml = cv2.minMaxLoc(match)
        print Ml, Mv

        size = self.template.shape
        cv2.rectangle(self.im, Ml, (Ml[0]+size[0], Ml[1]+size[1]), [0,255,0])

        if Mv > 0.96:
            return Ml
        else:
            return None


    def run(self):
        while True:
            s, self.im = self.camera.read()

            if self.state == self.STATE_ID_TEMPL:
                self.frames.append(self.im.copy())

                if len(self.frames) == 3:
                    self.template = self.get_frame_diff_template()
                    if self.template != None:
                        self.state = self.STATE_FOLLOW
                        self.frames = []
                    else:
                        self.frames.pop(0)
            elif self.state == self.STATE_FOLLOW:
                loc = self.findTemplate()
                if loc == None:
                    self.state = self.STATE_ID_TEMPL

            cv2.imshow("Test frame", self.im)

            k = cv2.waitKey(5)
            if k & 0xFF == 27:
                break

if __name__ == '__main__':
    MotionTracker().run()
