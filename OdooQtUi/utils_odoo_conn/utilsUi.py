# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 20/set/2015

@author: Daniel
'''
import os
import sys
import base64
import xmlrpc
import html
import inspect
import logging
import functools
import traceback

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets
#
import OdooQtUi
#
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn.utils import logMessage
from OdooQtUi.RPC.errors import OdooRpcError

DEFAULT_ICON_PATH = ''

QPROGRESS_STYLESHEET = """QDialog {border: 1.5px solid;
                                       border-radius: 5px;
                                       border-color: #9d5e96;
                                       color: white;
                                       }
                              QProgressBar{text-align: center;
                                            border-radius: 5px;  
                                            border: 1px solid grey; 
                                          }
                              QProgressBar::chunk {background-color:  #9d5e96;
                                                   width: 10px;
                                                  }
                                       """


class OpenProgressBar(QtWidgets.QProgressDialog):

    def __init__(self, parentHWnd=None):
        super(OpenProgressBar, self).__init__()
        # self.setStyleSheet(QPROGRESS_STYLESHEET)
        self.setCancelButton(None)
        self._parentHWnd = parentHWnd
        self.hide()
                     
    def _init(self,
              maxIndex=100,
              message="Progress",
              step=7): 
        try:
            self.setWindowTitle(message)
            self.setLabelText(message)
            self.setRange(0, maxIndex)
            self._step = step
            self._actualIndex = 0
            self.message = message
            self.repaint()
        except Exception as e:
            self.showError(e)  
            
    def reInit(self, maxIndex=100, message="Progress", step=7):
        try:
            self.show()
            self._init(maxIndex, message, step)
        except Exception as e:
            self.showError(e)
            
    def goOn(self,
             message=None):
        if (message == None) or (len(message) < 1):
            message = self.message
        self.setLabelText(message)
        self._actualIndex = self._actualIndex + self._step
        self.setValue(self._actualIndex)
        self.repaint()

    def close(self):
        """
            overwrite the close event
        """
        try:
            super(OpenProgressBar, self).close()
        except Exception as ex:
            logging.error('Error closing the progressbar window. Error: %r' % (ex))


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


def commonPopulateTable(headers,
                        values,
                        tableWidget,
                        flags={},
                        add=False,
                        fontSize=False):
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
            if isinstance(colVal, QtWidgets.QWidget):
                tableWidget.setCellWidget(rowPosition, colIndex, colVal)
            else:
                twItem = QtWidgets.QTableWidgetItem(colVal)
                if fontSize:
                    font = QtGui.QFont()
                    try:
                        if isinstance(fontSize, str):
                            digits = ''.join(filter(str.isdigit, fontSize))
                            font_val = int(digits) if digits else 12
                        else:
                            font_val = int(fontSize)
                        font.setPointSize(font_val)
                    except Exception:
                        font.setPointSize(12)
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
    widgetQtObj.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                background-color: #d6d6d6;
                padding: 10px;
                border: none;
                }
            """)


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

    def __init__(self,
                 parent,
                 messageBody="",
                 mess_type='warning',
                 short_text_header=''):
        QtWidgets.QDialog.__init__(self, parent)
        self.mainLayout = QtWidgets.QVBoxLayout(self)
        top_widget = QtWidgets.QWidget()
        hlay = QtWidgets.QHBoxLayout(top_widget)
        messageShortError = QtWidgets.QLabel()
        messageShortError.setWordWrap(True)
        messageShortError.setMaximumWidth(420)
        hlay.addWidget(messageShortError)
        more_button = QtWidgets.QPushButton('More')
        more_button.clicked.connect(self.showMore)
        self.lineEdit = QtWidgets.QTextEdit(self)
        self.lineEdit.setMaximumHeight(0)
        self.lineEdit.setMaximumWidth(0)
        # Focus only when clicked. As the first child it took the focus at open
        # while hidden, and ate Ctrl+C before the dialog's shortcut saw it --
        # measured on 2026-09-14: the clipboard did not change.
        self.lineEdit.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self._messageShortError = messageShortError
        self._short_text_header = short_text_header
        SHORT_TEXT_LIMIT = 300
        self._has_more = len(messageBody) > SHORT_TEXT_LIMIT
        if self._has_more:
            hlay.addStretch(1)
            hlay.addWidget(more_button)
            more_button.setStyleSheet('background-color:white;')
            messageShortError.setText(messageBody[:SHORT_TEXT_LIMIT] + '...')
            # Only beside More: a message short enough to be read whole is
            # copied with Ctrl+C, and a button for it would be noise.
            copy_button = QtWidgets.QToolButton()
            copy_icon = getattr(getattr(QtGui.QIcon, 'ThemeIcon', None), 'EditCopy', None)
            if copy_icon is not None and not QtGui.QIcon.fromTheme(copy_icon).isNull():
                copy_button.setIcon(QtGui.QIcon.fromTheme(copy_icon))
            else:
                # Theme icons arrived with Qt 6.7; before that, and on a system
                # with no icon theme, the button says what it does instead.
                copy_button.setText('Copy')
            copy_button.setToolTip('Copy the whole message (Ctrl+C)')
            copy_button.setStyleSheet('background-color:white;')
            copy_button.clicked.connect(self.copyMessage)
            hlay.addWidget(copy_button)
        else:
            messageShortError.setText(messageBody)
        if short_text_header:
            messageShortError.setText(short_text_header)
        # Ctrl+C always copies, whatever has the focus in the dialog -- except
        # a selection in the detail, which the text box copies by itself.
        copy_shortcut = QtGui.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy), self)
        copy_shortcut.activated.connect(self.copyMessage)
        self.lineEdit.setHtml(messageBody)
        closeButton = QtWidgets.QPushButton("Close")
        closeButton.clicked.connect(self.close)
        closeButton.setFocus()
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
        messageShortError.setStyleSheet('font-weight: bold; padding: 12px;')
        self.setMinimumWidth(450)
        self.setMaximumSize(1200, 250)
        QtCore.QTimer.singleShot(0, self.resizeMe)
        self._lineEditVisible = False

    def showMore(self):
        self._lineEditVisible = not self._lineEditVisible
        if self._lineEditVisible:
            self.lineEdit.setMinimumSize(600, 400)
            self.lineEdit.setMaximumHeight(12000)
            self.lineEdit.setMaximumWidth(12000)
            self.setMaximumSize(12000, 12000)
        else:
            self.lineEdit.setMinimumSize(0, 0)
            self.setMaximumSize(1200, 250)
            self.lineEdit.setMaximumHeight(0)
            self.lineEdit.setMaximumWidth(0)
        QtCore.QTimer.singleShot(0, self.resizeMe)

    def resizeMe(self):
        self.resize(self.minimumSizeHint())

    def copyMessage(self):
        """The message on the clipboard as plain text.

        With More, all of it, header first: the detail under More is where the
        file, the line and the arguments are, which is the part somebody asked to
        look at the problem needs. Without More, what the label says, since that
        is the whole message.
        """
        if self._has_more:
            text = self.lineEdit.toPlainText()
            if self._short_text_header and self._short_text_header not in text:
                text = '%s\n\n%s' % (self._short_text_header, text)
        else:
            text = self._messageShortError.text()
            if QtGui.Qt.mightBeRichText(text):
                document = QtGui.QTextDocument()
                document.setHtml(text)
                text = document.toPlainText()
        QtWidgets.QApplication.clipboard().setText(text)


def popError(parent, ex):
    """
        pop an error message
    """
    messageBody = utils.html_traceback(ex)
    err = ''
    if isinstance(ex, TypeError):
        err = ex.args[0]
    elif isinstance(ex, xmlrpc.client.Fault) or hasattr(ex, 'faultCode'):
        err = str(ex.faultCode)
    elif isinstance(ex, Exception):
        err = str(ex)
    else:
        err = str(ex.faultCode)
    popMessage(parent,
               messageBody,
               'ERROR',
               err)


def popWarning(parent, ex):
    """
        pop an warning message
        :parent qt parent windows
        :ex python Exception object
    """
    popMessage(parent, ex, 'WARNING')


def popInfo(parent,
            ex):
    """
        pop an warning message
        :parent qt parent windows
        :ex python Exception object
    """
    popMessage(parent, ex, 'INFO')


def popMessage(parent,
               ex,
               msg_type='info',
               short_text_header=''):
    """
        pop an warning message
        :parent qt parent windows
        :ex python Exception object or string 
    """
    dialObj = AdvancedErrorPopUP(parent,
                                 messageBody=ex,
                                 mess_type=msg_type,
                                 short_text_header=short_text_header)
    logMessage(msg_type, ex, 'popMessage')
    dialObj.exec()


def showRpcError(parent, error):
    """Tell the user a call to Odoo failed: what Odoo said, and the detail under More.

    :parent a QWidget or None
    :error  an OdooRpcError
    :return whether a window was shown

    Only in the GUI thread of a running application; anywhere else -- a script,
    a test, a worker thread, where a dialog would block or crash -- the error is
    logged and nothing more.
    """
    logMessage('error', str(error), 'showRpcError')
    application = QtWidgets.QApplication.instance()
    if application is None or QtCore.QThread.currentThread() is not application.thread():
        return False
    where = '%s.%s' % (error.model, error.method) if getattr(error, 'model', '') else getattr(error, 'method', '')
    body = '<b>%s</b><pre>%s</pre>' % (html.escape(where), html.escape(str(getattr(error, 'faultString', error))))
    if not isinstance(parent, QtWidgets.QWidget):
        parent = None
    popMessage(parent, body, 'ERROR', getattr(error, 'summary', str(error)))
    return True


def rpcErrorBoundary(method):
    """For a Qt slot: an OdooRpcError it raises is shown to the user, not lost.

    The RPC layer raises and shows nothing; a slot is where the user's action
    ends, and so where the error is told -- once, with the widget as parent.

    Qt hands a slot as many signal arguments as the slot accepts, and would
    read that off this wrapper; the wrapper hands on only as many as the
    method takes, so `clicked(bool)` still reaches a `def buttonClicked(self)`.
    """
    parameters = list(inspect.signature(method).parameters.values())[1:]
    if any(parameter.kind == parameter.VAR_POSITIONAL for parameter in parameters):
        accepted = None
    else:
        accepted = sum(1 for parameter in parameters
                       if parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD))

    @functools.wraps(method)
    def boundary(self, *args, **kwargs):
        if accepted is not None:
            args = args[:accepted]
        try:
            return method(self, *args, **kwargs)
        except OdooRpcError as error:
            showRpcError(self, error)
            return None
    return boundary
