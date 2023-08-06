'''
Created on Jan 27, 2016

@author: rcbyron
'''
import sys, cv2

from PyQt5 import QtWidgets

from PyET.classes.enhanced_cam import EnhancedCam

inst = None

def init():
    global inst
    inst = PyETCore()
    
def find_cameras():
    cameras = {}
    for i in range(10):
        temp_cam = cv2.VideoCapture(i)
        if temp_cam.isOpened():
            print('Found camera '+str(i)+'...')
            cameras[i] = EnhancedCam(i, temp_cam)
            print('Registered', cameras[i])
            cameras[i].release()
    return cameras

class PyETCore():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        
        self.cameras = {}
        self.eye_cam = None
        self.seeing_cam = None

        self.cameras = find_cameras()
        
        if len(self.cameras.items()) >= 2:
            self.eye_cam = self.cameras[0]
            self.eye_cam.cam_type = 'eye'
            self.seeing_cam = self.cameras[1]
            self.seeing_cam.cam_type = 'seeing'
            
    def record(self):
        #print('Attempting to record...')
        if self.eye_cam and self.seeing_cam:
            print('Recording cameras...')
            self.eye_cam.start_recording()
            self.seeing_cam.start_recording()
        else:
            print('Both cameras must be available for recording!')
    
    def stop_record(self):
        if self.eye_cam and self.seeing_cam:
            self.eye_cam.stop_recording()
            self.seeing_cam.stop_recording()
            print('Recording stopped!')
