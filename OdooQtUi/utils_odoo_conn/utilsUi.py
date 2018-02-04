'''
Created on 20/set/2015

@author: Daniel
'''
import os
import sys
import json
import stat
import time
import base64
import logging
import datetime
import traceback

from PyQt4 import QtGui, QtCore
from os.path import expanduser
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utils

DEFAULT_ICON_PATH = ''


def getQtImageFromContent(content, imageWidth=100, imageHeight=100):
    label = QtGui.QLabel()
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
    messBox = QtGui.QMessageBox()
    messBox.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    messBox.setWindowTitle('Odoo Plm Connector')
    messBox.setText(unicode(message))
    if msgType == 'message':
        messBox.setIcon(QtGui.QMessageBox.Information)
        messBox.setStandardBuunicodttons(QtGui.QMessageBox.Ok)
    if msgType == 'warning':
        messBox.setIcon(QtGui.QMessageBox.Warning)
        messBox.setStandardButtons(QtGui.QMessageBox.Ok)
    if msgType == 'error':
        messBox.setIcon(QtGui.QMessageBox.Critical)
        messBox.setStandardButtons(QtGui.QMessageBox.Ok)
    elif msgType == 'question':
        messBox.setIcon(QtGui.QMessageBox.Question)
        messBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
    messBox.setWindowIcon(QtGui.QIcon(DEFAULT_ICON_PATH))
    
    if (messBox.exec_() == QtGui.QMessageBox.Ok):
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
    if not add:
        tableWidget.clear()
        tableWidget.setRowCount(0)
    outDict = {}
    colCount = len(headers)
    colIndexList = range(0, colCount)
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
            twItem = QtGui.QTableWidgetItem(colVal)
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
    return unicode(QtGui.QFileDialog.getExistingDirectory(parent, "Select Directory", pathToOpen))


def getFileFromSystem(desc='Open', startPath='/home/'):
    fileName = QtGui.QFileDialog.getOpenFileName(None, desc, startPath)
    if os.path.exists(fileName):
        return unicode(fileName)
    return ''


def getDirectoryFileToSaveSystem(parent, statingPath='', fileType=''):
    filename = QtGui.QFileDialog.getSaveFileName(None, "Save file", statingPath, fileType)
    logging.info('[getDirectoryFileToSaveSystem] filename: %s' % filename)
    return filename

def getButtonBox(spacer='right'):
    mainLay = QtGui.QHBoxLayout()
    okButt = QtGui.QPushButton('Ok')
    cancelButt = QtGui.QPushButton('Cancel')
    if spacer == 'right':
        mainLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
    mainLay.addWidget(okButt)
    mainLay.addWidget(cancelButt)
    if spacer == 'left':
        mainLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
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
    lay.setSpacing(5)
    lay.setMargin(0)
    