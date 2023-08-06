'''
Created on Feb 1, 2016

@author: rcbyron
'''
import logging, os, cv2

from PyET import settings

class Recorder():
    def __init__(self, res, cam_type):
        logging.info('Creating recorder...')
        """ Find available file names to record to """
        self.id = 0
        self.vid_file = lambda: os.path.join(settings.RECORDINGS_DIR, cam_type+'-'+str(self.id)+'.avi')
        self.log_file = lambda: os.path.join(settings.RECORDINGS_DIR, cam_type+'-'+str(self.id)+'.csv')
        while os.path.isfile(self.vid_file()) or os.path.isfile(self.log_file()):
            self.id += 1
        
        #logging.info('using id: '+str(self.id))
        
        """ Create video writer """
        fourcc = cv2.VideoWriter_fourcc(*'MP4V')
        self.vw = cv2.VideoWriter(self.vid_file(), fourcc, settings.DEFAULT_RECORDING_FPS, res)
        
        """ Create csv logger """
        self.log = logging.getLogger(self.log_file())
        self.log.setLevel(logging.INFO)
        fh = logging.FileHandler(self.log_file())
        fh.setLevel(logging.INFO)
        self.log.addHandler(fh)
    
        self.wrap_vw()
        
        logging.info('Recorder object created!')
        logging.info('Recording to: '+self.vid_file()+', '+self.log_file())
    
    def wrap_vw(self):
        self.is_open = lambda: self.vw.isOpened()
        self.open = lambda: self.vw.open(self.id)
        self.write = lambda f: self.vw.write(f)
        self.release = lambda: self.vw.release()