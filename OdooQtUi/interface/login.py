'''
Created on Mar 28, 2017

@author: daniel
'''
import json
from .ui.ui_login import Ui_dialog_login
from PySide2 import QtWidgets
from PySide2 import QtCore

from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from PySide2.QtWidgets import QProgressBar


class LoginDial(QtWidgets.QDialog, Ui_dialog_login):

    def __init__(self, connType='xmlrpc', availableConnTypes=[]):
        super(LoginDial, self).__init__()
        self.availableConnTypes = availableConnTypes
        self.connType = connType
        self.setupUi(self)
        self.setStyleWidgets()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setEvents()
        self.progress = QProgressBar()
        self.page_2.layout().addWidget(self.progress)

    def setEvents(self):
        self.pushButton_cancel.clicked.connect(self.cancelDial)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_back.clicked.connect(self.previousPage)
        self.comboBox_conn_type.currentIndexChanged.connect(self.connTypeChanged)
        self.lineEdit_scheme.textChanged.connect(self.schemeChanged)

    def schemeChanged(self, newText):
        strText = str(newText)
        lowerTxt = strText.lower()
        self.lineEdit_scheme.setText(lowerTxt)
        index = None
        searchItem = ''
        if lowerTxt == 'http':
            searchItem = 'xmlrpc'
        elif lowerTxt == 'https':
            searchItem = 'secure-xmlrpc'
        if searchItem in self.availableConnTypes:
            index = self.availableConnTypes.index(searchItem)
        if index:
            self.comboBox_conn_type.setCurrentIndex(index)
        
    def connTypeChanged(self, index):
        currentText = str(self.comboBox_conn_type.currentText())
        if currentText.lower() == 'xmlrpc':
            self.lineEdit_scheme.setText('http')
        elif currentText.lower() == 'secure-xmlrpc':
            self.lineEdit_scheme.setText('https')

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
        #self.page.layout().setMargin(70)
        #self.page_2.layout().setMargin(70)
        
        self.lineEdit_password.setText(userpass)
        self.lineEdit_port.setText(str(serverPort))
        self.lineEdit_scheme.setText(scheme)
        self.lineEdit_server.setText(serverIp)
        self.lineEdit_username.setText(username)
        items = ['']
        items.extend(self.availableConnTypes)
        self.comboBox_conn_type.clear()
        self.comboBox_conn_type.addItems(items)
        self.comboBox_conn_type._items = items
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


class LoginDialComplete(LoginDial):
    def __init__(self,
                 connType='xmlrpc',
                 context={},
                 app_name='OdooQtUi',
                 odooConnector=None):
        self.app_name = app_name
        self.odooConnector = odooConnector
        self.availableConnTypes = self.odooConnector.rpc_connector.availableConnTypes
        super(LoginDialComplete, self).__init__(connType, availableConnTypes=[])
        self.connType = connType
        if not self.odooConnector.rpc_connector.userLogged:
            self.connectFromFile()
        else:
            self.dbName = self.odooConnector.rpc_connector.databaseName
            self.username = self.odooConnector.rpc_connector.userName
            self.userpass = self.odooConnector.rpc_connector.userPassword
            self.serverIp = self.odooConnector.rpc_connector.xmlrpcServerIP
            self.serverPort = self.odooConnector.rpc_connector.xmlrpcPort
            self.scheme = self.odooConnector.rpc_connector.scheme
            self.connType = self.odooConnector.rpc_connector.connectionType
            self.dbList = self.odooConnector.rpc_connector.listDb()
            
        if self.odooConnector.rpc_connector.userLogged:
            self.setLogged()
        else:
            self.setNotLogged()
        self.initFields()
        self.setEvents()
    
    def setLogged(self):
        utils.logMessage('info', 'User logged reading from stored file', '__init__')
        self.label_status.setText('User Already Logged!')
        self.stackedWidget.setCurrentIndex(1)
        self.pushButton_back.setHidden(False)
        self.pushButton_ok.setHidden(False)
        self.pushButton_next.setHidden(True)
        self.label_status.setHidden(False)
        
    def setNotLogged(self):
        utils.logMessage('warning', 'User not logged reading from stored file', '__init__')
        self.label_status.setHidden(True)
        self.stackedWidget.setCurrentIndex(0)
        self.pushButton_back.setHidden(True)
        self.pushButton_next.setHidden(False)
        self.pushButton_ok.setHidden(True)

    def connectFromFile(self):
        self.dbName, self.username, self.userpass, self.serverIp, self.serverPort, self.scheme, self.connType, self.dbList = utils.loadFromFile(app_name)
        utils.logMessage('info', '''
                                Try login with stored settings:
                                database= %r
                                user= %r
                                server= %r
                                port= %r
                                scheme= %r
                                connection type=%r
                                ''' % (self.dbName,
                                       self.username,
                                       self.serverIp,
                                       self.serverPort,
                                       self.scheme,
                                       self.connType), '__init__')
        self.odooConnector.rpc_connector.initConnection(self.connType,
                                         '',
                                         '',
                                         '',
                                         self.serverPort,
                                         self.scheme,
                                         self.serverIp)
        self.loginWithUserDial()
        
    def setEvents(self):
        self.pushButton_next.clicked.connect(self.nextPage)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_cancel.clicked.connect(self.cancelDial)

    def initFields(self):
        super(LoginDialComplete, self).initFields(self.odooConnector.rpc_connector.userLogged,
                                      self.userpass,
                                      self.serverPort,
                                      self.scheme,
                                      self.serverIp,
                                      self.username,
                                      self.dbName,
                                      self.dbList)
    def accept(self)->None:
        super(LoginDialComplete, self).accept()
        
    def acceptDial(self):
        self.writeToFile()
        self.loginWithUserDial()
        if self.odooConnector.rpc_connector.userLogged:
            self.accept()
        else:
            self.lineEdit_username.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.lineEdit_password.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.label_status.setText('Bad Username or Password!')
            self.label_status.setHidden(False)
            self.label_status.setStyleSheet('color: red;')

    def cancelDial(self):
        self.loginWithUserDial()

    def nextPage(self):
        xmlrpcServerIP = str(self.lineEdit_server.text())
        xmlrpcPort = str(self.lineEdit_port.text())
        scheme = str(self.lineEdit_scheme.text())
        loginType = str(self.comboBox_conn_type.currentText())
        self.odooConnector.rpc_connector.initConnection(loginType,
                                     '',
                                     '',
                                     '',
                                     xmlrpcPort,
                                     scheme,
                                     xmlrpcServerIP)

        self.dbList = self.odooConnector.rpc_connector.listDb()
        if not self.dbList:
            self.label_status.setText('User not logged! Unable to get database list.')
        else:
            self.label_status.setText('')
        self.dbList = self.dbList or []
        self.comboBox_database.clear()
        self.comboBox_database.addItems(self.dbList)
        self.pushButton_ok.setHidden(False)
        self.pushButton_back.setHidden(False)
        self.pushButton_next.setHidden(True)
        self.stackedWidget.setCurrentIndex(1)
        if self.dbName:
            if self.dbName in self.dbList:
                index = self.dbList.index(self.dbName)
                self.comboBox_database.setCurrentIndex(index)
        if self.userpass:
            self.lineEdit_password.setText(self.userpass)
        if self.username:
            self.lineEdit_username.setText(self.username)

    def loginWithUserDial(self):
        self.odooConnector.rpc_connector.initConnection(self.connType,
                                                        self.username,
                                                        self.userpass,
                                                        self.dbName,
                                                        self.serverPort,
                                                        self.scheme,
                                                        self.serverIp)
        return self.odooConnector.rpc_connector.loginWithUser(self.connType,
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
        filePath = utils.getLoginFile(self.app_name)
        with open(filePath, 'w') as outFile:
            outFile.write(toWrite)
