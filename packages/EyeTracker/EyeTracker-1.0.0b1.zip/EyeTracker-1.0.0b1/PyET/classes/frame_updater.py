'''
Created on Nov 30, 2015

@author: rcbyron
'''
import cv2

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from PyET import PyETCore

def frame_to_pixmap(f):
    mimage = QImage(f, f.shape[1], f.shape[0], f.strides[0], QImage.Format_RGB888).rgbSwapped()
    return QPixmap.fromImage(mimage)

class FrameUpdater(QObject):
    eye_frame_ready = pyqtSignal(QPixmap, int)
    seeing_frame_ready = pyqtSignal(QPixmap, int)

    def process(self): # A slot takes no params
        print('Processing frames...')
        while True:
            if PyETCore.inst.eye_cam:
                if not PyETCore.inst.eye_cam.is_open():
                    PyETCore.inst.eye_cam.open()
                ret, f = PyETCore.inst.eye_cam.read()
                #print('read')
                if ret:
                    f = cv2.flip(f, 0)
                    if PyETCore.inst.eye_cam.recording:
                        #print('recording')
                        PyETCore.inst.eye_cam.record(f)
                        #print('postrecord')
                    self.eye_frame_ready.emit(frame_to_pixmap(f), 1)
                    
            if PyETCore.inst.seeing_cam:
                #print('seeing')
                if not PyETCore.inst.seeing_cam.is_open():
                    PyETCore.inst.seeing_cam.open()
                #print('in')
                ret, f = PyETCore.inst.seeing_cam.read()
                if ret:
                    #print('yoo')
                    if PyETCore.inst.seeing_cam.recording:
                        PyETCore.inst.seeing_cam.record(f)
                    self.seeing_frame_ready.emit(frame_to_pixmap(f), 2)
                    #print('double yo')