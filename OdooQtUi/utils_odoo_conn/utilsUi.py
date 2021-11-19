'''
Created on 20/set/2015

@author: Daniel
'''
import os
import sys
import base64
import logging
import traceback

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utils
import OdooQtUi

DEFAULT_ICON_PATH = ''


def getQtImageFromContent(content, imageWidth=100, imageHeight=100, b64decode=True):
    label = QtWidgets.QLabel()
    pixmap = QtGui.QPixmap()
    if b64decode:
        content = base64.b64decode(content)
    pixmap.loadFromData(content)
    pixmap = pixmap.scaled(imageWidth,
                           imageHeight,
                           aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                           transformMode=QtCore.Qt.FastTransformation)
    label.setPixmap(pixmap)
    label.resize(imageWidth, imageHeight)
    return label


def setDefaultIconPath(iconPath):
    global DEFAULT_ICON_PATH
    DEFAULT_ICON_PATH = iconPath


def launchMessage(message='', msgType='MESSAGE'):
    utils.logMessage('info', message, 'launchMessage')
    messBox = QtWidgets.QDialog()
    messBox.setWindowTitle('Odoo Plm Connector')
    messBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    
    main_lay = QtWidgets.QHBoxLayout()
    widget = QtWidgets.QWidget()
    main_lay.setMargin(5)
    main_lay.setSpacing(5)
    main_lay.addWidget(widget)
    content_layout = QtWidgets.QVBoxLayout()
    buttons_layout = QtWidgets.QHBoxLayout()
    
    text_edit = QtWidgets.QTextEdit()

    ok_button = QtWidgets.QPushButton('Ok')
    ok_button.clicked.connect(messBox.accept)
    cancel_butt = QtWidgets.QPushButton('Cancel')
    cancel_butt.clicked.connect(messBox.reject)
    spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
    buttons_layout.addSpacerItem(spacer)
    buttons_layout.addWidget(ok_button)
    buttons_layout.addWidget(cancel_butt)
    
    text_edit.setText(message)
    text_edit.setReadOnly(True)
    
    tmp_msg_box = QtWidgets.QMessageBox()

    color = 'white'
    msgType = msgType.upper()
    if msgType == 'MESSAGE':
        color = '#5bd3ff'
        tmp_msg_box.setIcon(QtWidgets.QMessageBox.Information)
        cancel_butt.setHidden(True)
    if msgType == 'WARNING':
        color = '#ffb600'
        tmp_msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        cancel_butt.setHidden(True)
    if msgType == 'ERROR':
        color = '#ed6363'
        tmp_msg_box.setIcon(QtWidgets.QMessageBox.Critical)
        cancel_butt.setHidden(True)
    elif msgType == 'QUESTION':
        tmp_msg_box.setIcon(QtWidgets.QMessageBox.Question)
    
    icon_lable = QtWidgets.QLabel()
    text_lable = QtWidgets.QLabel()
    text_lable.setText(msgType)
    text_edit.setFrameStyle(QtWidgets.QFrame.NoFrame)
    font = QtGui.QFont()
    font.setPointSize(10)
    text_edit.setFont(font)
    icon_lable.setPixmap(tmp_msg_box.iconPixmap())
    content_layout.addWidget(icon_lable)
    content_layout.addWidget(text_lable)
    content_layout.addWidget(text_edit)
    content_layout.addLayout(buttons_layout)
    widget.setLayout(content_layout)
    messBox.setLayout(main_lay)
    messBox.setWindowIcon(QtGui.QIcon(DEFAULT_ICON_PATH))
    messBox.resize(700, 700)
    messBox.setStyleSheet('background-color:%r;' % (color))
    widget.setStyleSheet('background-color:white;')
    cancel_butt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
    ok_button.setStyleSheet(constants.BUTTON_STYLE_OK)
    text_edit.setStyleSheet(constants.TEXT_STYLE)
    if messBox.exec_() == QtWidgets.QDialog.Accepted:
        return True
    else:
        return False


def commonPopulateTable(headers, values, tableWidget, flags={}, add=False, fontSize=False):
    '''
        @headers: [header1, header2, ...]
        @flags: {'colIndex': flags}
        @values: [[val1, val2, ...], ...] or [obj1, obj2, ...]
    '''
    if not tableWidget:
        logging.warning("No table widget set")
        return {}
    if not add:
        tableWidget.clear()
        tableWidget.setRowCount(0)
    outDict = {}
    colCount = len(headers)
    colIndexList = list(range(0, colCount))
    tableWidget.setColumnCount(colCount)
    tableWidget.setHorizontalHeaderLabels(headers)
    rowPosition = tableWidget.rowCount()
    for menuObj in values:
        tableWidget.setRowCount(rowPosition + 1)
        rowDict = {}
        for colIndex in colIndexList:
            colName = headers[colIndex]
            if isinstance(menuObj, (list, tuple)):
                if colIndex >= len(menuObj):
                    colVal = ''
                else:
                    colVal = menuObj[colIndex]
            else:
                colVal = menuObj.__dict__.get(colName, '')
            rowDict[colName] = colVal
            twItem = QtWidgets.QTableWidgetItem(colVal)
            if fontSize:
                font = QtGui.QFont()
                font.setPointSize(fontSize)
                twItem.setFont(font)
            if colIndex in flags:
                flagsToAdd = flags[colIndex]
                twItem.setFlags(flagsToAdd)
                if flagsToAdd & QtCore.Qt.ItemIsUserCheckable:
                    twItem.setCheckState(QtCore.Qt.Unchecked)
            else:
                twItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            tableWidget.setItem(rowPosition, colIndex, twItem)
        outDict[rowPosition] = rowDict
        rowPosition = rowPosition + 1
    return outDict


def getDirectoryFromSystem(parent, pathToOpen=''):
    return str(QtWidgets.QFileDialog.getExistingDirectory(parent, "Select Directory", pathToOpen))


def getFileFromSystem(desc='Open', startPath='/home/'):
    fileName = QtWidgets.QFileDialog.getOpenFileName(None, desc, startPath)
    if os.path.exists(fileName):
        return str(fileName)
    return ''


def getDirectoryFileToSaveSystem(parent, statingPath='', fileType=''):
    filename = QtWidgets.QFileDialog.getSaveFileName(None, "Save file", statingPath, fileType)
    logging.info('[getDirectoryFileToSaveSystem] filename: %s' % filename)
    return filename


def getButtonBox(spacer='right'):
    mainLay = QtWidgets.QHBoxLayout()
    okButt = QtWidgets.QPushButton('Ok')
    cancelButt = QtWidgets.QPushButton('Cancel')
    if spacer == 'right':
        mainLay.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    mainLay.addWidget(okButt)
    mainLay.addWidget(cancelButt)
    if spacer == 'left':
        mainLay.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    return mainLay, okButt, cancelButt


def exceptionManagement(ex, message=''):
    traceback.print_exc(file=sys.stdout)
    traceBackMess = traceback.format_exc()
    logging.error(ex)
    logging.error(traceBackMess)
    launchMessage(message + ': %s \n %s' % (ex, traceBackMess))


def setRequiredBackground(widgetQtObj, baseBackground):
    widgetQtObj.setStyleSheet(baseBackground + constants.COMMON_FIELDS_REQUIRED_BACKGROUND)


def setLayoutMarginAndSpacing(lay, forceVal=False):
    if not forceVal:
        forceVal = constants.LAY_OUT_SPACING
    lay.setSpacing(forceVal)
    lay.setContentsMargins(forceVal, forceVal, forceVal, forceVal)


def getIconPath(iconName):
    currDir = os.path.dirname(__file__)
    imagesDir = os.path.join(currDir, 'images')
    if not os.path.exists(imagesDir):
        imagesDir = os.path.join(os.path.dirname(currDir), 'images')
    image_path = os.path.join(imagesDir, iconName)
    if not os.path.exists(image_path):
        return ''
    return image_path
