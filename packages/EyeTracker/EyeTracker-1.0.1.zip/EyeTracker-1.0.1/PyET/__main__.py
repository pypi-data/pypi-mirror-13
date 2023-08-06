import sys, logging

import PyET.PyETCore as PyETCore

from PyET import settings
from PyET.main_ui import TrackerGui

from PyQt5 import QtWidgets

logging.basicConfig(filename=settings.MAIN_LOG_FILE, level=logging.INFO)
logging.info('-------- PyET INSTANCE STARTED --------')

""" Initialize core instance """
PyETCore.init()

"""Create GUI """
MainWindow = QtWidgets.QMainWindow()

gui = TrackerGui()
gui.setup_ui(MainWindow)

MainWindow.show()

sys.exit(PyETCore.inst.app.exec_())