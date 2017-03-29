'''
Created on Mar 28, 2017

@author: daniel
'''
import os
from ui.ui_login import Ui_dialog_login
from PyQt4 import QtGui
from PyQt4 import QtCore
from utils import utils
import json


class LoginDial(QtGui.QDialog, Ui_dialog_login):

    def __init__(self, parent=None):
        super(LoginDial, self).__init__()
        self.setupUi(self)
        self.parent = parent
        self.setEvents()
        self.setStyleWidgets()
        self.parent.loginNoUser()
        self.rpc = self.parent.rpc
        self.initFields()
        if self.rpc.userLogged:
            self.logged = True
        else:
            self.logged = self.loginWithUserDial()
        if self.logged:
            self.stackedWidget.setCurrentIndex(1)
            self.pushButton_back.setHidden(False)
            self.pushButton_ok.setHidden(False)
            self.pushButton_next.setHidden(True)
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.pushButton_back.setHidden(True)
            self.pushButton_next.setHidden(False)
            self.pushButton_ok.setHidden(True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

    def setEvents(self):
        self.pushButton_cancel.clicked.connect(self.cancelDial)
        self.pushButton_next.clicked.connect(self.nextPage)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_back.clicked.connect(self.previousPage)

    def acceptDial(self):
        self.dbName = unicode(self.comboBox_database.currentText())
        self.username = unicode(self.lineEdit_username.text())
        self.userpass = unicode(self.lineEdit_password.text())
        self.serverIp = unicode(self.lineEdit_server.text())
        self.serverPort = int(unicode(self.lineEdit_port.text()))
        self.scheme = unicode(self.lineEdit_scheme.text())
        self.connType = unicode(self.comboBox_conn_type.currentText())
        self.writeToFile()
        self.logged = self.loginWithUserDial()
        if self.logged:
            utils.launchMessage('Logged in successfully.', 'info')
            self.accept()
        else:
            utils.launchMessage('Bad Login Infos! Check Better.', 'warning')

    def loginWithUserDial(self):
        return self.parent.loginWithUser(self.username,
                                         self.userpass,
                                         self.dbName,
                                         self.serverIp,
                                         self.serverPort,
                                         self.scheme,
                                         self.connType)

    def cancelDial(self):
        self.reject()

    def nextPage(self):
        xmlrpcServerIP = unicode(self.lineEdit_server.text())
        xmlrpcPort = unicode(self.lineEdit_port.text())
        scheme = unicode(self.lineEdit_scheme.text())
        loginType = unicode(self.comboBox_conn_type.currentText())
        self.parent.loginNoUser(xmlrpcServerIP, xmlrpcPort, scheme, loginType)
        self.rpc = self.parent.rpc

        self.dbList = self.rpc.listDb()
        self.comboBox_database.addItems(self.dbList)
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
        self.lineEdit_password.setEchoMode(QtGui.QLineEdit.Password)
        self.pushButton_ok.setHidden(True)
        self.pushButton_back.setHidden(True)
        self.comboBox_conn_type.setEditable(True)
        self.comboBox_database.setEditable(True)
        self.page.layout().setMargin(70)
        self.page_2.layout().setMargin(70)
        self.loadFromFile()

    def writeToFile(self):
        toWriteDict = {
            'db_name': self.dbName,
            'user_name': self.username,
            'user_pass': self.userpass,
            'server_ip': self.serverIp,
            'server_port': self.serverPort,
            'scheme': self.scheme,
            'conn_type': self.connType,
            'conn_list': self.availableConnTypes,
            'db_list': self.dbList,
        }
        toWrite = json.dumps(toWriteDict)
        filePath = utils.getLoginFile()
        with open(filePath, 'w') as outFile:
            outFile.write(toWrite)

    def loadFromFile(self):
        self.dbName = ''
        self.username = ''
        self.userpass = ''
        self.serverIp = ''
        self.serverPort = ''
        self.scheme = ''
        self.connType = ''
        self.availableConnTypes = []
        self.dbList = []
        filePath = utils.getLoginFile()
        fileDict = {}
        if os.path.exists(filePath):
            with open(filePath, 'r') as readFile:
                content = readFile.read()
                fileDict = json.loads(content)
            if fileDict:
                self.dbName = fileDict.get('db_name', '')
                self.username = fileDict.get('user_name', '')
                self.userpass = fileDict.get('user_pass', '')
                self.serverIp = fileDict.get('server_ip', '')
                self.serverPort = fileDict.get('server_port', '')
                self.scheme = fileDict.get('scheme', '')
                self.connType = fileDict.get('conn_type', '')
                self.availableConnTypes = fileDict.get('conn_list', [])
                self.dbList = fileDict.get('db_list', [])

        if not self.availableConnTypes:
            self.availableConnTypes = self.rpc.availableConnTypes
        self.lineEdit_password.setText(self.userpass)
        self.lineEdit_port.setText(unicode(self.serverPort))
        self.lineEdit_scheme.setText(self.scheme)
        self.lineEdit_server.setText(self.serverIp)
        self.lineEdit_username.setText(self.username)
        items = ['']
        items.extend(self.availableConnTypes)
        self.comboBox_conn_type.addItems(items)
        if self.connType in items:
            typeIndex = items.index(self.connType)
            self.comboBox_conn_type.setCurrentIndex(typeIndex)
        dbItems = ['']
        dbItems.extend(self.dbList)
        self.comboBox_database.addItems(dbItems)
        if self.dbName in dbItems:
            typeIndex2 = dbItems.index(self.dbName)
            self.comboBox_database.setCurrentIndex(typeIndex2)

    def setStyleWidgets(self):
        lineditStyle = 'min-width:200px;height: 16px;padding: 6px 12px;font-size: 14px;border: 1px solid #ccc;border-radius: 4px;background-color: rgb(250, 255, 189);color: rgb(0, 0, 0);'
        comboStyle = 'min-width:200px;height: 16px;padding: 6px 12px;font-size: 14px;border: 1px solid #ccc;border-radius: 4px;background-color: #eee;color: rgb(0, 0, 0);'
        acceptButtonStyle = 'border-radius: 4px;color: white;background-color: #337ab7;border: 2px solid black;padding: 5px 10px;font-size: 12px;'
        goodButtonStyle = acceptButtonStyle + 'background-color: #59be50;'
        cancelButtonStyle = acceptButtonStyle + 'background-color: #f05050;'
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

        self.pushButton_ok.setStyleSheet(acceptButtonStyle)
        self.pushButton_next.setStyleSheet(goodButtonStyle)
        self.pushButton_back.setStyleSheet(goodButtonStyle)
        self.pushButton_cancel.setStyleSheet(cancelButtonStyle)

        self.setStyleSheet(mainStyle)
