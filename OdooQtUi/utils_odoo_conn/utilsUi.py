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

DEFAULT_ICON_PATH = ''


def getQtImageFromContent(content, imageWidth=100, imageHeight=100):
    label = QtWidgets.QLabel()
    pixmap = QtGui.QPixmap()
    pixmap.loadFromData(base64.b64decode(content))
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


def launchMessage(message='', msgType='message'):
    utils.logMessage('info', message, 'launchMessage')
    messBox = QtWidgets.QMessageBox()
    messBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    messBox.setWindowTitle('Odoo Plm Connector')
    messBox.setText(str(message))
    if msgType == 'message':
        messBox.setIcon(QtWidgets.QMessageBox.Information)
        messBox.setStandardBuunicodttons(QtWidgets.QMessageBox.Ok)
    if msgType == 'warning':
        messBox.setIcon(QtWidgets.QMessageBox.Warning)
        messBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    if msgType == 'error':
        messBox.setIcon(QtWidgets.QMessageBox.Critical)
        messBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
    elif msgType == 'question':
        messBox.setIcon(QtWidgets.QMessageBox.Question)
        messBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
    messBox.setWindowIcon(QtGui.QIcon(DEFAULT_ICON_PATH))
    if (messBox.exec_() == QtWidgets.QMessageBox.Ok):
        messBox.accept()
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
        mainLay.addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    mainLay.addWidget(okButt)
    mainLay.addWidget(cancelButt)
    if spacer == 'left':
        mainLay.addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
    return mainLay, okButt, cancelButt


def exceptionManagement(ex, message=''):
    traceback.print_exc(file=sys.stdout)
    traceBackMess = traceback.format_exc()
    logging.error(ex)
    logging.error(traceBackMess)
    launchMessage(message + ': %s \n %s' % (ex, traceBackMess))


def setRequiredBackground(widgetQtObj, baseBackground):
    widgetQtObj.setStyleSheet(baseBackground + constants.COMMON_FIELDS_REQUIRED_BACKGROUND)


def setLayoutMarginAndSpacing(lay):
    lay.setSpacing(constants.LAY_OUT_SPACING)
