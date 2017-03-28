'''
Created on Mar 28, 2017

@author: daniel
'''

from ui.ui_login import Ui_dialog_login
from PyQt4 import QtGui
from utils import constants


class LoginDial(QtGui.QDialog, Ui_dialog_login):
    
    def __init__(self, parent=None):
        super(LoginDial, self).__init__()
        self.setupUi(self)
        self.setEvents()
        self.setStyleWidgets()
        self.initFields()
        
    def setEvents(self):
        self.pushButton_cancel.clicked.connect(self.cancelDial)
        self.pushButton_next.clicked.connect(self.nextPage)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_back.clicked.connect(self.previousPage)

    def acceptDial(self):
        self.accept()

    def cancelDial(self):
        self.reject()

    def nextPage(self):
        self.pushButton_ok.setHidden(False)
        self.pushButton_back.setHidden(False)
        self.pushButton_next.setHidden(True)
        self.stackedWidget.setCurrentIndex(1)

    def previousPage(self):
        self.pushButton_ok.setHidden(True)
        self.pushButton_back.setHidden(True)
        self.pushButton_next.setHidden(False)
        self.stackedWidget.setCurrentIndex(0)

    def initFields(self):
        self.pushButton_ok.setHidden(True)
        self.pushButton_back.setHidden(True)
        
    def setStyleWidgets(self):
        lineditStyle = 'height: 25px;padding: 6px 12px;font-size: 14px;border: 1px solid #ccc;border-radius: 4px;background-color: rgb(250, 255, 189);color: rgb(0, 0, 0);'
        comboStyle = 'height: 25px;padding: 6px 12px;font-size: 14px;border: 1px solid #ccc;border-radius: 4px;background-color: #eee;color: rgb(0, 0, 0);'
        labelStyle = 'font-weight: bold;'
        mainStyle = 'background-color:#893b74;'
        stackedStyle = 'background-color:white;'
        
        self.label_conn_type.setStyleSheet(labelStyle)
        self.label_database.setStyleSheet(labelStyle)
        self.label_password.setStyleSheet(labelStyle)
        self.label_port.setStyleSheet(labelStyle)
        self.label_server.setStyleSheet(labelStyle)
        self.label_username.setStyleSheet(labelStyle)
        self.label_scheme.setStyleSheet(labelStyle)
        
        self.lineEdit_password.setStyleSheet(lineditStyle)
        self.lineEdit_port.setStyleSheet(lineditStyle)
        self.lineEdit_scheme.setStyleSheet(lineditStyle)
        self.lineEdit_server.setStyleSheet(lineditStyle)
        self.lineEdit_username.setStyleSheet(lineditStyle)
        
        self.comboBox_conn_type.setStyleSheet(comboStyle)
        self.comboBox_database.setStyleSheet(comboStyle)
        
        self.stackedWidget.setStyleSheet(stackedStyle)
        
        self.pushButton_ok.setStyleSheet(constants.BUTTON_STYLE_OK)
        self.pushButton_next.setStyleSheet(constants.BUTTON_STYLE_OK)
        self.pushButton_back.setStyleSheet(constants.BUTTON_STYLE_OK)
        self.pushButton_cancel.setStyleSheet(constants.BUTTON_STYLE_CANCEL)

        self.setStyleSheet(mainStyle)
        
        
        