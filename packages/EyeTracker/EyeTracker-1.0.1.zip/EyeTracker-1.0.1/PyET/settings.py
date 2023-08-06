'''
Created on Dec 7, 2015

@author: rcbyron
'''
import os

def ensure_dir(d):
    if not os.path.exists(d):
        os.mkdir(d)
    

DEFAULT_RECORDING_FPS = 20.0
CLIENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CLIENT_DIR)
HAARCASCADES_DIR = os.path.join(CLIENT_DIR, 'haarcascades')
RECORDINGS_DIR = os.path.join(CLIENT_DIR, 'recordings')
LOGS_DIR = os.path.join(CLIENT_DIR, 'logs')
CASCADE_FILE = os.path.join(HAARCASCADES_DIR, 'haarcascade_eye.xml')
MAIN_LOG_FILE = os.path.join(LOGS_DIR, 'PyET.log')

DIRS = [HAARCASCADES_DIR, LOGS_DIR, RECORDINGS_DIR]
for folder in DIRS:
    ensure_dir(folder)

