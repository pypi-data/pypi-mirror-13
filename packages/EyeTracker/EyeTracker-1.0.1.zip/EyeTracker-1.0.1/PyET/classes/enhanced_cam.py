'''
Created on Nov 30, 2015

@author: rcbyron
'''
import time, cv2

from PyET.classes.recorder import Recorder

DEFAULT_RESOLUTIONS = {#(480, 360),
                       #(1920, 1080),
                       (640, 480),
                       #(720, 480),
                       #(800, 600),
                       #(1280, 720),
                       #(1920, 1080)}
                       }

class EnhancedCam():
    def __init__(self, cam_id, cam, cam_type='undefined'):
        self.id = cam_id
        self.cam = cam
        self.cam_type = cam_type
        self.recording = False
    
        self.wrap_get()
        self.wrap_vc()
        
        self.resolutions = {self.res()}
        self.resolutions.update(set(self.get_available_resolutions()))
        self.str_resolutions = [str(res[0])+' x '+str(res[1]) for res in self.resolutions]
    
    def wrap_get(self):
        self.res =              lambda: (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                         int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.aperture =         lambda: self.cam.get(cv2.CAP_PROP_APERTURE)
        self.auto_exposure =    lambda: self.cam.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        self.backlight =        lambda: self.cam.get(cv2.CAP_PROP_BACKLIGHT)
        self.brightness =       lambda: self.cam.get(cv2.CAP_PROP_BRIGHTNESS)
        self.contrast =         lambda: self.cam.get(cv2.CAP_PROP_CONTRAST)
        self.exposure =         lambda: self.cam.get(cv2.CAP_PROP_EXPOSURE)
        self.focus =            lambda: self.cam.get(cv2.CAP_PROP_FOCUS)
        self.format =           lambda: self.cam.get(cv2.CAP_PROP_FORMAT)
        self.fps =              lambda: self.cam.get(cv2.CAP_PROP_FPS)
        self.frame_count =      lambda: self.cam.get(cv2.CAP_PROP_FRAME_COUNT)
        self.gain =             lambda: self.cam.get(cv2.CAP_PROP_GAIN)
        self.gamma =            lambda: self.cam.get(cv2.CAP_PROP_GAMMA)
        self.hue =              lambda: self.cam.get(cv2.CAP_PROP_HUE)
        self.saturation =       lambda: self.cam.get(cv2.CAP_PROP_SATURATION)
        self.sharpness =        lambda: self.cam.get(cv2.CAP_PROP_SHARPNESS)
        self.speed =            lambda: self.cam.get(cv2.CAP_PROP_SPEED)
        self.w_balance_u =      lambda: self.cam.get(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U)
        self.w_balance_v =      lambda: self.cam.get(cv2.CAP_PROP_WHITE_BALANCE_RED_V)
        self.zoom =             lambda: self.cam.get(cv2.CAP_PROP_ZOOM)
    
    def wrap_vc(self):
        self.is_open = lambda: self.cam.isOpened()
        self.open = lambda: self.cam.open(self.id)
        self.read = lambda: self.cam.read()
        self.release = lambda: self.cam.release()
    
    def start_recording(self):
        self.recorder = Recorder(self.res(), self.cam_type)
        self.start_time = time.time()
        self.recording = True
        print('Recording on', str(self))
        
    def record(self, frame):
        if self.recording and self.recorder:
            self.recorder.write(frame)
            meta = []
            meta.append(time.time()-self.start_time)
            meta.append(self.res())
            self.recorder.log.info(str(meta)[1:-1])
            
    def stop_recording(self):
        self.recording = False
        if self.recorder:
            self.recorder.release()
        print('Finished recording on', str(self))

    def set_resolution(self, res):
        """ Return true if successful """
        flag_1 = self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        flag_2 = self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
        return flag_1 and flag_2
    
    def try_resolution(self, res, revert=False):
        orig_res = self.res()
        if self.set_resolution(res):
            if revert:
                print('Successfully tried resolution:', res)
                self.set_resolution(orig_res)
            else:
                print('Successfully updated resolution:', res)
            return True
        else:
            print('Setting resolution failed. Reverting to original resolution.')
            self.set_resolution(orig_res)
            return False
    
    def get_available_resolutions(self):
        return {res for res in DEFAULT_RESOLUTIONS if self.try_resolution(res, revert=False)}

    def __str__(self):
        return 'Device ' + str(self.id)