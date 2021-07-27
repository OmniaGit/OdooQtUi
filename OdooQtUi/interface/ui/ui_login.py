# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/srv/workspace/tray_odoo_connector/interface/ui/login.ui'
#
# Created: Thu Apr 13 13:06:04 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


try:
    _fromUtf8 = QtCore.QObject.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_dialog_login(object):
    def setupUi(self, dialog_login):
        dialog_login.setObjectName(_fromUtf8("dialog_login"))
        dialog_login.resize(424, 190)
        self.gridLayout = QtWidgets.QGridLayout(dialog_login)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.stackedWidget = QtWidgets.QStackedWidget(dialog_login)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.page = QtWidgets.QWidget()
        self.page.setObjectName(_fromUtf8("page"))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.page)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lineEdit_port = QtWidgets.QLineEdit(self.page)
        self.lineEdit_port.setObjectName(_fromUtf8("lineEdit_port"))
        self.gridLayout_2.addWidget(self.lineEdit_port, 2, 1, 1, 1)
        self.label_server = QtWidgets.QLabel(self.page)
        self.label_server.setObjectName(_fromUtf8("label_server"))
        self.gridLayout_2.addWidget(self.label_server, 1, 0, 1, 1)
        self.label_conn_type = QtWidgets.QLabel(self.page)
        self.label_conn_type.setObjectName(_fromUtf8("label_conn_type"))
        self.gridLayout_2.addWidget(self.label_conn_type, 3, 0, 1, 1)
        self.label_port = QtWidgets.QLabel(self.page)
        self.label_port.setObjectName(_fromUtf8("label_port"))
        self.gridLayout_2.addWidget(self.label_port, 2, 0, 1, 1)
        self.comboBox_conn_type = QtWidgets.QComboBox(self.page)
        self.comboBox_conn_type.setObjectName(_fromUtf8("comboBox_conn_type"))
        self.gridLayout_2.addWidget(self.comboBox_conn_type, 3, 1, 1, 1)
        self.lineEdit_server = QtWidgets.QLineEdit(self.page)
        self.lineEdit_server.setObjectName(_fromUtf8("lineEdit_server"))
        self.gridLayout_2.addWidget(self.lineEdit_server, 1, 1, 1, 1)
        self.label_scheme = QtWidgets.QLabel(self.page)
        self.label_scheme.setObjectName(_fromUtf8("label_scheme"))
        self.gridLayout_2.addWidget(self.label_scheme, 0, 0, 1, 1)
        self.lineEdit_scheme = QtWidgets.QLineEdit(self.page)
        self.lineEdit_scheme.setObjectName(_fromUtf8("lineEdit_scheme"))
        self.gridLayout_2.addWidget(self.lineEdit_scheme, 0, 1, 1, 1)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName(_fromUtf8("page_2"))
        self.gridLayout_3 = QtWidgets.QGridLayout(self.page_2)
        self.gridLayout_3.setHorizontalSpacing(9)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_database = QtWidgets.QLabel(self.page_2)
        self.label_database.setObjectName(_fromUtf8("label_database"))
        self.gridLayout_3.addWidget(self.label_database, 1, 0, 1, 1)
        self.lineEdit_password = QtWidgets.QLineEdit(self.page_2)
        self.lineEdit_password.setObjectName(_fromUtf8("lineEdit_password"))
        self.gridLayout_3.addWidget(self.lineEdit_password, 3, 1, 1, 1)
        self.comboBox_database = QtWidgets.QComboBox(self.page_2)
        self.comboBox_database.setMaxVisibleItems(10)
        self.comboBox_database.setObjectName(_fromUtf8("comboBox_database"))
        self.gridLayout_3.addWidget(self.comboBox_database, 1, 1, 1, 1)
        self.label_username = QtWidgets.QLabel(self.page_2)
        self.label_username.setObjectName(_fromUtf8("label_username"))
        self.gridLayout_3.addWidget(self.label_username, 2, 0, 1, 1)
        self.label_password = QtWidgets.QLabel(self.page_2)
        self.label_password.setObjectName(_fromUtf8("label_password"))
        self.gridLayout_3.addWidget(self.label_password, 3, 0, 1, 1)
        self.lineEdit_username = QtWidgets.QLineEdit(self.page_2)
        self.lineEdit_username.setObjectName(_fromUtf8("lineEdit_username"))
        self.gridLayout_3.addWidget(self.lineEdit_username, 2, 1, 1, 1)
        self.label_status = QtWidgets.QLabel(self.page_2)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(QtGui.QFont.Weight(75))
        self.label_status.setFont(font)
        self.label_status.setText(_fromUtf8(""))
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.gridLayout_3.addWidget(self.label_status, 0, 1, 1, 1)
        self.stackedWidget.addWidget(self.page_2)
        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_back = QtWidgets.QPushButton(dialog_login)
        self.pushButton_back.setObjectName(_fromUtf8("pushButton_back"))
        self.horizontalLayout.addWidget(self.pushButton_back)
        self.pushButton_next = QtWidgets.QPushButton(dialog_login)
        self.pushButton_next.setObjectName(_fromUtf8("pushButton_next"))
        self.horizontalLayout.addWidget(self.pushButton_next)
        spacerItem = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButton_ok = QtWidgets.QPushButton(dialog_login)
        self.pushButton_ok.setObjectName(_fromUtf8("pushButton_ok"))
        self.horizontalLayout.addWidget(self.pushButton_ok)
        self.pushButton_cancel = QtWidgets.QPushButton(dialog_login)
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.horizontalLayout.addWidget(self.pushButton_cancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(dialog_login)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(dialog_login)
        dialog_login.setTabOrder(self.lineEdit_scheme, self.lineEdit_server)
        dialog_login.setTabOrder(self.lineEdit_server, self.lineEdit_port)
        dialog_login.setTabOrder(self.lineEdit_port, self.comboBox_conn_type)
        dialog_login.setTabOrder(self.comboBox_conn_type, self.pushButton_next)
        dialog_login.setTabOrder(self.pushButton_next, self.comboBox_database)
        dialog_login.setTabOrder(self.comboBox_database, self.lineEdit_username)
        dialog_login.setTabOrder(self.lineEdit_username, self.lineEdit_password)
        dialog_login.setTabOrder(self.lineEdit_password, self.pushButton_ok)
        dialog_login.setTabOrder(self.pushButton_ok, self.pushButton_cancel)
        dialog_login.setTabOrder(self.pushButton_cancel, self.pushButton_back)

    def retranslateUi(self, dialog_login):
        dialog_login.setWindowTitle(_translate("dialog_login", "Dialog", None))
        self.label_server.setText(_translate("dialog_login", "Server IP", None))
        self.label_conn_type.setText(_translate("dialog_login", "Connection Type", None))
        self.label_port.setText(_translate("dialog_login", "Port", None))
        self.label_scheme.setText(_translate("dialog_login", "Scheme", None))
        self.lineEdit_scheme.setText(_translate("dialog_login", "http", None))
        self.lineEdit_scheme.setPlaceholderText(_translate("dialog_login", "http", None))
        self.label_database.setText(_translate("dialog_login", "Database", None))
        self.label_username.setText(_translate("dialog_login", "Username", None))
        self.label_password.setText(_translate("dialog_login", "Password", None))
        self.pushButton_back.setText(_translate("dialog_login", "Back", None))
        self.pushButton_next.setText(_translate("dialog_login", "Next", None))
        self.pushButton_ok.setText(_translate("dialog_login", "Login", None))
        self.pushButton_cancel.setText(_translate("dialog_login", "Cancel", None))
