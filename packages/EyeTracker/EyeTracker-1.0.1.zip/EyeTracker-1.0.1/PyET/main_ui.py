'''
Created on Dec 7, 2015

@author: rcbyron
'''
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread

from PyET import PyETCore
from ui.main_window import Ui_MainWindow as MainUi
from classes.frame_updater import FrameUpdater

class TrackerGui(MainUi):
 
    def update_cam_list(self):
        cam_list = [str(cam) for cam in PyETCore.inst.cameras.values()]
        self.eye_cam_combo_box.clear()
        self.seeing_cam_combo_box.clear()
        self.eye_cam_combo_box.addItems(cam_list)
        self.seeing_cam_combo_box.addItems(cam_list)
        
    def update_res_list(self):
        self.eye_res_combo_box.clear()
        self.seeing_res_combo_box.clear()
        if PyETCore.inst.eye_cam:
            r_list = PyETCore.inst.eye_cam.str_resolutions
            self.eye_res_combo_box.addItems(r_list)
        if PyETCore.inst.seeing_cam:
            r_list = PyETCore.inst.seeing_cam.str_resolutions
            self.seeing_res_combo_box.addItems(r_list)
    
    def setup_ui(self, MainWindow):
        super().setupUi(MainWindow)
        self.f_updater = FrameUpdater()
        self.thread = QThread()
        self.f_updater.eye_frame_ready.connect(self.on_frame_ready)
        self.f_updater.seeing_frame_ready.connect(self.on_frame_ready)
        self.f_updater.moveToThread(self.thread)
        self.thread.started.connect(self.f_updater.process)
        self.thread.start()
        
        self.update_cam_list()
        self.update_res_list()
        
        self.start_cap_btn.released.connect(PyETCore.inst.record)
        self.stop_cap_btn.released.connect(PyETCore.inst.stop_record)

    def on_frame_ready(self, pixmap, cam_type):
        pixmap = pixmap.scaled(self.cam_view.size(), Qt.KeepAspectRatio)
        if cam_type is 1:
            self.cam_view_2.setPixmap(pixmap)
        elif cam_type is 2:
            self.cam_view.setPixmap(pixmap)
        app = QtCore.QCoreApplication.instance()
        app.processEvents()