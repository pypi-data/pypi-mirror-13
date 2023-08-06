PyET - Python 3 Eye Tracking & Recording Software
=================================================

**DISCLAIMER:** This software only records camera frames and information at the moment. The eye tracking vector calculations have yet to be implemented. Recordings are stored in site-packages/PyET/recordings. The recordings can then be processed for eye tracking by the advanced "Yarbus" software provided by http://www.positivescience.com/software/

This software relies on a seeing camera (looking away from you) and an eye camera (monitoring your eye). They eye camera should be viewed in gray-scale (infrared) for easy processing. For more information on the hardware we use, check out: https://pupil-labs.com/pupil/

**Other Notes:**

* Requires OpenCV 3 (unofficial package: http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv)
* Requires PyQT5 (https://riverbankcomputing.com/software/pyqt/download5)
* Tested on Python 3.4 and 3.5

Contribute
==========

Feel free to send pull requests to the GitHub repository. We are also looking to add eye tracking calculation software in the future. Frames can be accessed for calculation in the frame_updater.py class.

**GitHub:** https://github.com/rcbyron/python-eye-tracker