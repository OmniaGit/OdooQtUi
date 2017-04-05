# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/srv/workspace/tray_odoo_connector/interface/ui/login.ui'
#
# Created: Wed Apr  5 13:55:16 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dialog_login(object):
    def setupUi(self, dialog_login):
        dialog_login.setObjectName(_fromUtf8("dialog_login"))
        dialog_login.resize(434, 244)
        self.gridLayout = QtGui.QGridLayout(dialog_login)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.stackedWidget = QtGui.QStackedWidget(dialog_login)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page = QtGui.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.gridLayout_2 = QtGui.QGridLayout(self.page)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lineEdit_port = QtGui.QLineEdit(self.page)
        self.lineEdit_port.setObjectName(_fromUtf8("lineEdit_port"))
        self.gridLayout_2.addWidget(self.lineEdit_port, 2, 1, 1, 1)
        self.label_server = QtGui.QLabel(self.page)
        self.label_server.setObjectName(_fromUtf8("label_server"))
        self.gridLayout_2.addWidget(self.label_server, 1, 0, 1, 1)
        self.label_conn_type = QtGui.QLabel(self.page)
        self.label_conn_type.setObjectName(_fromUtf8("label_conn_type"))
        self.gridLayout_2.addWidget(self.label_conn_type, 3, 0, 1, 1)
        self.label_port = QtGui.QLabel(self.page)
        self.label_port.setObjectName(_fromUtf8("label_port"))
        self.gridLayout_2.addWidget(self.label_port, 2, 0, 1, 1)
        self.comboBox_conn_type = QtGui.QComboBox(self.page)
        self.comboBox_conn_type.setObjectName(_fromUtf8("comboBox_conn_type"))
        self.gridLayout_2.addWidget(self.comboBox_conn_type, 3, 1, 1, 1)
        self.lineEdit_server = QtGui.QLineEdit(self.page)
        self.lineEdit_server.setObjectName(_fromUtf8("lineEdit_server"))
        self.gridLayout_2.addWidget(self.lineEdit_server, 1, 1, 1, 1)
        self.label_scheme = QtGui.QLabel(self.page)
        self.label_scheme.setObjectName(_fromUtf8("label_scheme"))
        self.gridLayout_2.addWidget(self.label_scheme, 0, 0, 1, 1)
        self.lineEdit_scheme = QtGui.QLineEdit(self.page)
        self.lineEdit_scheme.setObjectName(_fromUtf8("lineEdit_scheme"))
        self.gridLayout_2.addWidget(self.lineEdit_scheme, 0, 1, 1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtGui.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.page_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_username = QtGui.QLabel(self.page_2)
        self.label_username.setObjectName(_fromUtf8("label_username"))
        self.gridLayout_3.addWidget(self.label_username, 1, 0, 1, 1)
        self.comboBox_database = QtGui.QComboBox(self.page_2)
        self.comboBox_database.setObjectName(_fromUtf8("comboBox_database"))
        self.gridLayout_3.addWidget(self.comboBox_database, 0, 1, 1, 1)
        self.label_database = QtGui.QLabel(self.page_2)
        self.label_database.setObjectName(_fromUtf8("label_database"))
        self.gridLayout_3.addWidget(self.label_database, 0, 0, 1, 1)
        self.label_password = QtGui.QLabel(self.page_2)
        self.label_password.setObjectName(_fromUtf8("label_password"))
        self.gridLayout_3.addWidget(self.label_password, 2, 0, 1, 1)
        self.lineEdit_username = QtGui.QLineEdit(self.page_2)
        self.lineEdit_username.setObjectName(_fromUtf8("lineEdit_username"))
        self.gridLayout_3.addWidget(self.lineEdit_username, 1, 1, 1, 1)
        self.lineEdit_password = QtGui.QLineEdit(self.page_2)
        self.lineEdit_password.setObjectName(_fromUtf8("lineEdit_password"))
        self.gridLayout_3.addWidget(self.lineEdit_password, 2, 1, 1, 1)
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_back = QtGui.QPushButton(dialog_login)
        self.pushButton_back.setObjectName(_fromUtf8("pushButton_back"))
        self.horizontalLayout.addWidget(self.pushButton_back)
        self.pushButton_next = QtGui.QPushButton(dialog_login)
        self.pushButton_next.setObjectName(_fromUtf8("pushButton_next"))
        self.horizontalLayout.addWidget(self.pushButton_next)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_ok = QtGui.QPushButton(dialog_login)
        self.pushButton_ok.setObjectName(_fromUtf8("pushButton_ok"))
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.pushButton_cancel = QtGui.QPushButton(dialog_login)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(dialog_login)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dialog_login)
        dialog_login.setTabOrder(self.lineEdit_scheme, self.lineEdit_server)
        dialog_login.setTabOrder(self.lineEdit_server, self.lineEdit_port)
        dialog_login.setTabOrder(self.lineEdit_port, self.comboBox_conn_type)
        dialog_login.setTabOrder(self.comboBox_conn_type, self.pushButton_ok)
        dialog_login.setTabOrder(self.pushButton_ok, self.pushButton_cancel)
        dialog_login.setTabOrder(self.pushButton_cancel, self.pushButton_back)
        dialog_login.setTabOrder(self.pushButton_back, self.pushButton_next)
        dialog_login.setTabOrder(self.pushButton_next, self.lineEdit_password)
        dialog_login.setTabOrder(self.lineEdit_password, self.lineEdit_username)
        dialog_login.setTabOrder(self.lineEdit_username, self.comboBox_database)

    def retranslateUi(self, dialog_login):
        dialog_login.setWindowTitle(_translate("dialog_login", "Dialog", None))
        self.label_server.setText(_translate("dialog_login", "Server IP", None))
        self.label_conn_type.setText(_translate("dialog_login", "Connection Type", None))
        self.label_port.setText(_translate("dialog_login", "Port", None))
        self.label_scheme.setText(_translate("dialog_login", "Scheme", None))
        self.lineEdit_scheme.setText(_translate("dialog_login", "http", None))
        self.label_username.setText(_translate("dialog_login", "Username", None))
        self.label_database.setText(_translate("dialog_login", "Database", None))
        self.label_password.setText(_translate("dialog_login", "Password", None))
        self.pushButton_back.setText(_translate("dialog_login", "Back", None))
        self.pushButton_next.setText(_translate("dialog_login", "Next", None))
        self.pushButton_ok.setText(_translate("dialog_login", "Login", None))
        self.pushButton_cancel.setText(_translate("dialog_login", "Cancel", None))

