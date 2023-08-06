# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\rcbyron\Documents\Workspace\py\python-eye-tracker\PyET\ui\secondary_window.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SecondaryWindow(object):
    def setupUi(self, SecondaryWindow):
        SecondaryWindow.setObjectName("SecondaryWindow")
        SecondaryWindow.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SecondaryWindow)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SecondaryWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(SecondaryWindow)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(SecondaryWindow)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SecondaryWindow)
        QtCore.QMetaObject.connectSlotsByName(SecondaryWindow)

    def retranslateUi(self, SecondaryWindow):
        _translate = QtCore.QCoreApplication.translate
        SecondaryWindow.setWindowTitle(_translate("SecondaryWindow", "Secondary Camera View"))
        self.label.setText(_translate("SecondaryWindow", "(secondary camera view)"))
        self.pushButton.setText(_translate("SecondaryWindow", "Seeing Camera"))
        self.pushButton_2.setText(_translate("SecondaryWindow", "Eye Camera"))

