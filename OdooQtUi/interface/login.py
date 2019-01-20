'''
Created on Mar 28, 2017

@author: daniel
'''
import json
from OdooQtUi.RPC.rpc import connectionObj
from .ui.ui_login import Ui_dialog_login
from PySide2 import QtWidgets
from PySide2 import QtCore
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants


class LoginDial(QtWidgets.QDialog, Ui_dialog_login):

    def __init__(self, connType, availableConnTypes=[]):
        super(LoginDial, self).__init__()
        self.availableConnTypes = availableConnTypes
        self.connType = connType
        self.setupUi(self)
        self.setStyleWidgets()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setEvents()

    def setEvents(self):
        self.pushButton_cancel.clicked.connect(self.cancelDial)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_back.clicked.connect(self.previousPage)

    def setStyleWidgets(self):
        self.label_conn_type.setStyleSheet(constants.LOGIN_LABEL)
        self.label_database.setStyleSheet(constants.LOGIN_LABEL)
        self.label_password.setStyleSheet(constants.LOGIN_LABEL)
        self.label_port.setStyleSheet(constants.LOGIN_LABEL)
        self.label_server.setStyleSheet(constants.LOGIN_LABEL)
        self.label_username.setStyleSheet(constants.LOGIN_LABEL)
        self.label_scheme.setStyleSheet(constants.LOGIN_LABEL)

        self.lineEdit_password.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.lineEdit_port.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.lineEdit_scheme.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.lineEdit_server.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
        self.lineEdit_username.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)

        self.comboBox_conn_type.setStyleSheet(constants.LOGIN_COMBO_STYLE)
        self.comboBox_database.setStyleSheet(constants.LOGIN_COMBO_STYLE)

        self.stackedWidget.setStyleSheet(constants.LOGIN_STACKED_WIDGET)

        self.pushButton_ok.setStyleSheet(constants.LOGIN_ACCEPT_BUTTON)
        self.pushButton_next.setStyleSheet(constants.LOGIN_NEXT_BACK_BUTTONS)
        self.pushButton_back.setStyleSheet(constants.LOGIN_NEXT_BACK_BUTTONS)
        self.pushButton_cancel.setStyleSheet(constants.LOGIN_CANCEL_BUTTON)

        self.setStyleSheet(constants.LOGIN_MAIN)

    def initFields(self, userLogged, userpass, serverPort, scheme, serverIp, username, dbName, dbList):
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pushButton_ok.setHidden(True)
        self.pushButton_back.setHidden(True)
        self.comboBox_conn_type.setEditable(True)
        self.comboBox_database.setEditable(True)
        # self.page.layout().setMargin(70)
        # self.page_2.layout().setMargin(70)

        self.lineEdit_password.setText(userpass)
        self.lineEdit_port.setText(str(serverPort))
        self.lineEdit_scheme.setText(scheme)
        self.lineEdit_server.setText(serverIp)
        self.lineEdit_username.setText(username)
        items = ['']
        items.extend(self.availableConnTypes)
        self.comboBox_conn_type.clear()
        self.comboBox_conn_type.addItems(items)
        if self.connType in items:
            typeIndex = items.index(self.connType)
            self.comboBox_conn_type.setCurrentIndex(typeIndex)
        dbItems = ['']
        dbItems.extend(dbList)
        self.comboBox_database.clear()
        self.comboBox_database.addItems(dbItems)
        if dbName in dbItems:
            typeIndex2 = dbItems.index(dbName)
            self.comboBox_database.setCurrentIndex(typeIndex2)
        if userLogged:
            self.stackedWidget.setCurrentIndex(1)
            self.pushButton_back.setHidden(False)
            self.pushButton_ok.setHidden(False)
            self.pushButton_next.setHidden(True)
        else:
            self.stackedWidget.setCurrentIndex(0)
            self.pushButton_back.setHidden(True)
            self.pushButton_next.setHidden(False)
            self.pushButton_ok.setHidden(True)

    def previousPage(self):
        self.pushButton_ok.setHidden(True)
        self.pushButton_back.setHidden(True)
        self.pushButton_next.setHidden(False)
        self.stackedWidget.setCurrentIndex(0)

    def cancelDial(self):
        self.reject()

    def acceptDial(self):
        self.dbName = str(self.comboBox_database.currentText())
        self.username = str(self.lineEdit_username.text())
        self.userpass = str(self.lineEdit_password.text())
        self.serverIp = str(self.lineEdit_server.text())
        self.serverPort = str(self.lineEdit_port.text())
        self.scheme = str(self.lineEdit_scheme.text())
        self.connType = str(self.comboBox_conn_type.currentText())

    def acceptDialForce(self):
        self.accept()


class LoginDialComplete(object):
    def __init__(self, connType='xmlrpc'):
        self.connType = connType
        self.dbName, self.username, self.userpass, self.serverIp, self.serverPort, self.scheme, self.connType, self.dbList = utils.loadFromFile()
        utils.logMessage('info', '''
Try login with stored settings:\n
database= %r\n
user= %r\n
server= %r\n
port= %r\n
scheme= %r\n
connection type=%r\n
''' % (self.dbName, self.username, self.serverIp, self.serverPort, self.scheme, self.connType), '__init__')
        connectionObj.initConnection(self.connType,
                                     '',
                                     '',
                                     '',
                                     self.serverPort,
                                     self.scheme,
                                     self.serverIp)
        self.availableConnTypes = connectionObj.availableConnTypes
        self.interfaceDial = LoginDial(self.connType, self.availableConnTypes)
        self.setEvents()
        utils.logMessage('info', 'Try login using stored data', '__init__')
        self.loginWithUserDial()
        if connectionObj.userLogged:
            utils.logMessage('info', 'User logged reading from stored file', '__init__')
            self.interfaceDial.label_status.setText('User Already Logged!')
            self.interfaceDial.stackedWidget.setCurrentIndex(1)
            self.interfaceDial.pushButton_back.setHidden(False)
            self.interfaceDial.pushButton_ok.setHidden(False)
            self.interfaceDial.pushButton_next.setHidden(True)
            self.interfaceDial.label_status.setHidden(False)
        else:
            utils.logMessage('warning', 'User not logged reading from stored file', '__init__')
            self.interfaceDial.label_status.setHidden(True)
            self.interfaceDial.stackedWidget.setCurrentIndex(0)
            self.interfaceDial.pushButton_back.setHidden(True)
            self.interfaceDial.pushButton_next.setHidden(False)
            self.interfaceDial.pushButton_ok.setHidden(True)
        self.initFields()

    def setEvents(self):
        self.interfaceDial.pushButton_next.clicked.connect(self.nextPage)
        self.interfaceDial.pushButton_ok.clicked.connect(self.acceptDial)

    def initFields(self):
        self.interfaceDial.initFields(connectionObj.userLogged,
                                      self.userpass,
                                      self.serverPort,
                                      self.scheme,
                                      self.serverIp,
                                      self.username,
                                      self.dbName,
                                      self.dbList)

    def acceptDial(self):
        self.dbName = self.interfaceDial.dbName
        self.username = self.interfaceDial.username
        self.userpass = self.interfaceDial.userpass
        self.serverIp = self.interfaceDial.serverIp
        self.serverPort = self.interfaceDial.serverPort
        self.scheme = self.interfaceDial.scheme
        self.connType = self.interfaceDial.connType
        self.writeToFile()
        self.loginWithUserDial()
        if connectionObj.userLogged:
            self.interfaceDial.acceptDial()
            self.interfaceDial.accept()
        else:
            self.interfaceDial.lineEdit_username.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.interfaceDial.lineEdit_password.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.interfaceDial.label_status.setText('Bad Username or Password!')
            self.interfaceDial.label_status.setHidden(False)
            self.interfaceDial.label_status.setStyleSheet('color: red;')

    def nextPage(self):
        xmlrpcServerIP = str(self.interfaceDial.lineEdit_server.text())
        xmlrpcPort = str(self.interfaceDial.lineEdit_port.text())
        scheme = str(self.interfaceDial.lineEdit_scheme.text())
        loginType = str(self.interfaceDial.comboBox_conn_type.currentText())
        connectionObj.initConnection(loginType,
                                     '',
                                     '',
                                     '',
                                     xmlrpcPort,
                                     scheme,
                                     xmlrpcServerIP)

        self.dbList = connectionObj.listDb()
        if not self.dbList:
            self.interfaceDial.label_status.setText('User not logged! Unable to get database list.')
        else:
            self.interfaceDial.label_status.setText('')
        self.dbList = self.dbList or []
        self.interfaceDial.comboBox_database.clear()
        self.interfaceDial.comboBox_database.addItems(self.dbList)
        self.interfaceDial.pushButton_ok.setHidden(False)
        self.interfaceDial.pushButton_back.setHidden(False)
        self.interfaceDial.pushButton_next.setHidden(True)
        self.interfaceDial.stackedWidget.setCurrentIndex(1)

    def loginWithUserDial(self):
        connectionObj.initConnection(self.connType,
                                     self.username,
                                     self.userpass,
                                     self.dbName,
                                     self.serverPort,
                                     self.scheme,
                                     self.serverIp)
        return connectionObj.loginWithUser(self.connType,
                                           self.username,
                                           self.userpass,
                                           self.dbName,
                                           self.serverPort,
                                           self.scheme,
                                           self.serverIp)

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
