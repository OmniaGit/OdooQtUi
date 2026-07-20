'''
Created on Mar 28, 2017

@author: daniel
'''
import os
import sys
import json
import time
from .ui.ui_login import Ui_dialog_login
from PySide2 import QtWidgets
from PySide2 import QtCore

from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from PySide2.QtWidgets import QProgressBar
from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QSplashScreen
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, QSettings
from PySide2.QtCore import Slot


class RainbowMan(QSplashScreen):
    def __init__(self, parent=None):
        super(RainbowMan, self).__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        # rainbow_man_png = os.path.join(resource_path(), "rainbow_man.png")
       
        pixmap = QPixmap(utils.getImagePath("rainbow_man.png"))
        if os.path.exists(os.path.dirname(sys.executable)):
            pixmap = QPixmap(os.path.join(os.path.dirname(sys.executable), 'src', 'images', 'rainbow_man.png'))

        self.setPixmap(pixmap)

    def progress(self):
        for i in range(10):
            QApplication.processEvents()
            time.sleep(0.1)
        self.hide()
        QApplication.processEvents()
        self.close()
        QApplication.processEvents()
            
class LoginDial(QtWidgets.QDialog, 
                Ui_dialog_login):

    def __init__(self, 
                 connType='xmlrpc', 
                 availableConnTypes=[]):
        super(LoginDial, self).__init__()
        self.availableConnTypes = availableConnTypes
        self.connType = connType
        self.setupUi(self)
        self.setStyleWidgets()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setEvents()
        self.progress = QProgressBar()
        self.page_2.layout().addWidget(self.progress, 4, 0, 1,2)
        self.progress.setRange(0,1)
        self._settings = QSettings("OmniaQtUI", "login")
         
    def save_login_settings(self):
        #
        currentText = str(self.comboBox_conn_type.currentText())
        self.settings.setValue("comboBox_conn_type", currentText)
        #
        database = str(self.comboBox_database)
        self.settings.setValue("comboBox_database", database)
        #
        self.settings.setValue('lineEdit_password',self.lineEdit_password.Text())
        self.settings.setValue('lineEdit_port',self.lineEdit_port.Text())
        self.settings.setValue('lineEdit_scheme',self.lineEdit_scheme.Text())
        self.settings.setValue('lineEdit_server',self.lineEdit_server.Text())
        self.settings.setValue('lineEdit_username',self.lineEdit_username.Text())
    
    def get_login_settings(self):
        #
        self.comboBox_conn_type.setCurrentIndex(self.settings.value("comboBox_conn_type", 4, int))
        #
        self.lineEdit_password.setText(self.settings.setValue('lineEdit_password'))
        self.lineEdit_port.setText(self.settings.setValue('lineEdit_port'))
        self.lineEdit_scheme.setText(self.settings.setValue('lineEdit_scheme'))
        self.lineEdit_server.setText(self.settings.setValue('lineEdit_server'))
        self.lineEdit_username.setText(self.settings.setValue('lineEdit_username'))
            
    def setEvents(self):
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

    def transferDbInfoFromInterface(self):
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
        super(LoginDialComplete, self).__init__(connType, availableConnTypes=self.availableConnTypes)
        self.connType = connType
        if not self.odooConnector.rpc_connector.userLogged:
            self.connectFromFile(self.app_name)
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

    def connectFromFile(self, app_name='odoo_plm'):
        self.dbName,  \
        self.username, \
        self.userpass, \
        self.serverIp, \
        self.serverPort, \
        self.scheme, \
        self.connType, \
        self.dbList = utils.loadFromFile(app_name)
        utils.logMessage('info',
                         'Try login with stored settings:',
                         'connectFromFile')
        try:
            self.loginWithUserDial()
        except Exception as ex:
            utils.logWarning("Unable to get login information from file", "connectFromFile")
        
    def setEvents(self):
        self.pushButton_next.clicked.connect(self.nextPage)
        self.pushButton_ok.clicked.connect(self.acceptDial)
        self.pushButton_cancel.clicked.connect(self.cancelDial)
        self.pushButton_back.clicked.connect(self.previousPage)

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
        self.progress.setRange(0,0)
        try:
            QApplication.processEvents() 
            self.transferDbInfoFromInterface()
            self.loginWithUserDial()
            if self.odooConnector.rpc_connector.userLogged:
                utils.writeToFile(self.dbName, 
                                  self.username, 
                                  self.userpass, 
                                  self.serverIp, 
                                  self.serverPort,
                                  self.scheme, 
                                  self.connType, 
                                  self.dbList, 
                                  self.app_name)
                self.label_status.setText('User Logged')
                self.lineEdit_username.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
                self.lineEdit_password.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE)
                self.label_status.setStyleSheet('')
                splash = RainbowMan(self)
                splash.show()
                splash.progress()
                self.accept()
            else:
                raise Exception('Bad Username or Password!')
        except Exception as ex:
            self.lineEdit_username.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.lineEdit_password.setStyleSheet(constants.LOGIN_LINEEDIT_STYLE + constants.BACKGROUND_RED)
            self.label_status.setText(str(ex))
            self.label_status.setHidden(False)
            self.label_status.setStyleSheet('color: red;')
            QApplication.processEvents()            
        finally:
            self.progress.setRange(0,1)


    def cancelDial(self):
        self.close()

    def showPleaseWaitDialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle('Please wait')
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setModal(True)
        dialog.setAttribute(Qt.WA_StyledBackground, True)
        dialog.setAutoFillBackground(True)
        dialog.setFixedSize(320, 100)
        dialog.setStyleSheet("""
            QDialog { background-color: white; border: 1px solid #ccc; }
            QLabel { color: black; }
        """)
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        label = QtWidgets.QLabel('Please wait... connecting with server')
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        dialog.setLayout(layout)
        global_center = self.mapToGlobal(self.rect().center())
        dialog.move(global_center.x() - dialog.width() // 2,
                   global_center.y() - dialog.height() // 2)
        dialog.show()
        QApplication.processEvents()
        return dialog
    
    def nextPage(self):
        xmlrpcServerIP = str(self.lineEdit_server.text())
        xmlrpcPort = str(self.lineEdit_port.text())
        scheme = str(self.lineEdit_scheme.text())
        loginType = str(self.comboBox_conn_type.currentText())

        wait_dialog = self.showPleaseWaitDialog()
        try:
            self.odooConnector.rpc_connector.initConnection(loginType,
                                         '',
                                         '',
                                         '',
                                         xmlrpcPort,
                                         scheme,
                                         xmlrpcServerIP)

            self.dbList = self.odooConnector.rpc_connector.listDb() or []
        finally:
            wait_dialog.close()

        self.label_status.setText('')
        self.comboBox_database.clear()
        self.comboBox_database.addItems(self.dbList)
        if not self.dbList:
            self.comboBox_database.setEditable(True)
            self.comboBox_database.setFocus()
            self.comboBox_database.lineEdit().setPlaceholderText('Enter the database name')
        else:
            self.comboBox_database.setEditable(False)
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
        utils.logMessage('info', '''
                        Try login with settings:
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
                               self.connType), 'loginWithUserDial')
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

