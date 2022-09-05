'''
Created on 20/set/2015

@author: Daniel
'''
import os
import sys
import base64
import xmlrpc
import logging
import traceback

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
#
import OdooQtUi
#
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn.utils import logMessage

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
            if not isinstance(colVal, str):
                #tableWidget.setCellWidget(rowPosition, colIndex, colVal)
                pass
            else:
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
    file_path, _filter = QtWidgets.QFileDialog.getOpenFileName(None, desc, startPath)
    if os.path.exists(file_path):
        return str(file_path)
    return ''

def getDirectoryFileToSaveSystem(parent, statingPath='', fileType=''):
    file_path, _filter = QtWidgets.QFileDialog.getSaveFileName(None, "Save file", statingPath, fileType)
    logging.info('[getDirectoryFileToSaveSystem] filename: %s' % str(file_path))
    return file_path


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
    popError(None, message + ': %s \n %s' % (ex, traceBackMess))


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


class AdvancedErrorPopUP(QtWidgets.QDialog):
    def __init__(self, parent, messageBody="", mess_type='warning', short_text_header=''):
        QtWidgets.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.MSWindowsFixedSizeDialogHint);
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        top_widget = QtWidgets.QWidget()
        hlay = QtWidgets.QHBoxLayout(top_widget)
        messageShortError = QtWidgets.QLabel()
        hlay.addWidget(messageShortError)
        more_button = QtWidgets.QPushButton('More')
        more_button.clicked.connect(self.showMore)
        self.lineEdit = QtWidgets.QTextEdit(self)
        self.lineEdit.setMaximumHeight(0)
        self.lineEdit.setMaximumWidth(0)        
        if len(messageBody) > 80:
            hlay.addStretch(1)
            hlay.addWidget(more_button)
            top_widget.setFixedHeight(50)
            more_button.setStyleSheet('background-color:white;')
            messageShortError.setText(messageBody[:80])
        else:
            messageShortError.setText(messageBody)
        if short_text_header:
            messageShortError.setText(short_text_header)
        self.lineEdit.setHtml(messageBody)
        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close)
        self.mainLayout.addWidget(top_widget)
        self.mainLayout.addWidget(self.lineEdit)
        self.mainLayout.addWidget(closeButton)
        self.setLayout(self.mainLayout)
        color = 'white'
        mess_type = mess_type.upper()
        if mess_type == 'ERROR':
            color = '#f44336'
        elif mess_type == 'WARNING':
            color = '#ffb600'
        elif mess_type == 'INFO':
            color = '#5bd3ff'
        self.setWindowTitle("%s !!" % (mess_type.capitalize()))
        self.setStyleSheet('background-color:%r;' % (color))
        self.lineEdit.setStyleSheet('background-color:white;')
        closeButton.setStyleSheet('background-color:white;')
        messageShortError.setStyleSheet('font-weight: bold;')
        self.setMaximumSize(1200, 100)
        QtCore.QTimer.singleShot(0, self.resizeMe)
        self._lineEditVisible = False

    def showMore(self):
        self._lineEditVisible = not self._lineEditVisible
        if self._lineEditVisible:
            self.lineEdit.setMinimumSize(600, 400)
            self.lineEdit.setMaximumHeight(12000)
            self.lineEdit.setMaximumWidth(12000)
            self.setMaximumSize(12000,12000)
        else:
            self.lineEdit.setMinimumSize(0, 0)
            self.setMaximumSize(1200, 100)
            self.lineEdit.setMaximumHeight(0)
            self.lineEdit.setMaximumWidth(0)           
        QtCore.QTimer.singleShot(0, self.resizeMe)

    def resizeMe(self):
        self.resize(self.minimumSizeHint())

def popError(parent, ex):
    """
        pop an error message
    """
    messageBody = utils.html_traceback(ex)
    err = ''
    if isinstance(ex, TypeError):
        err = ex.args[0]
    elif isinstance(ex, xmlrpc.client.Fault):
        err = str(ex.faultCode)
    elif isinstance(ex, Exception):
        err = str(ex)
    else:
        err = str(ex.faultCode)
    popMessage(parent, messageBody, 'ERROR', err)

def popWarning(parent, ex):
    """
        pop an warning message
    """
    popMessage(parent, ex, 'WARNING')

def popInfo(parent, ex):
    """
        pop an warning message
    """
    popMessage(parent, ex, 'INFO')

def popMessage(parent, ex, msg_type='info', short_text_header=''):
    """
        pop an warning message
    """
    dialObj = AdvancedErrorPopUP(parent,
                                 messageBody=ex,
                                 mess_type=msg_type,
                                 short_text_header=short_text_header)
    logMessage(msg_type, ex, 'popMessage')
    dialObj.exec_()
