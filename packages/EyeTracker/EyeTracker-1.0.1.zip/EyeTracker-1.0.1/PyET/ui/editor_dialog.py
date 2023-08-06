# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\rcbyron\Documents\Workspace\py\python-eye-tracker\PyET\ui\editor_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EditorDialog(object):
    def setupUi(self, EditorDialog):
        EditorDialog.setObjectName("EditorDialog")
        EditorDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditorDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tableWidget = QtWidgets.QTableWidget(EditorDialog)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushButton = QtWidgets.QPushButton(EditorDialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(EditorDialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout_2.addWidget(self.pushButton_2)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(EditorDialog)
        QtCore.QMetaObject.connectSlotsByName(EditorDialog)

    def retranslateUi(self, EditorDialog):
        _translate = QtCore.QCoreApplication.translate
        EditorDialog.setWindowTitle(_translate("EditorDialog", "Advanced Property Editor"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("EditorDialog", "Property"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("EditorDialog", "Value"))
        self.pushButton.setText(_translate("EditorDialog", "Reset"))
        self.pushButton_2.setText(_translate("EditorDialog", "Apply"))

