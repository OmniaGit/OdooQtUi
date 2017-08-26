'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from objects.fieldTemplate import OdooFieldTemplate
import os
import base64
import tempfile


class Binary(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Binary, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.xmlWidget = self.fieldXmlAttributes.get('widget')
        self.imageWidth = 100
        self.imageHeight = 100
        self.fileName = self.fieldXmlAttributes.get('filename') # File name has to be take here
        try:
            self.imageWidth = eval(self.fieldXmlAttributes.get('img_width'))
            self.imageHeight = eval(self.fieldXmlAttributes.get('img_height'))
        except Exception, _ex:
            pass
        self.getQtObject()

    def getQtObject(self):
        if self.xmlWidget == 'image':
            self.widgetQtObj = QtGui.QLabel()
            self.pixmap = QtGui.QPixmap()
            self.pixmap = self.pixmap.scaled(self.imageWidth,
                                             self.imageHeight,
                                             aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                             transformMode=QtCore.Qt.FastTransformation)
            self.widgetQtObj.setPixmap(self.pixmap)
            self.widgetQtObj.resize(self.imageWidth, self.imageHeight)
            self.widgetQtObj.setText('aaa')
        else:
            self.labelQtObj = QtGui.QLabel(self.labelString)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            self.widgetQtObj = QtGui.QLineEdit()
            self.widgetQtObj.setToolTip(self.tooltip)
            self.widgetQtObj.editingFinished.connect(self.valueChanged)
            self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)
            self.buttonEdit = QtGui.QPushButton('Edit')
            self.buttonEdit.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.buttonEdit.clicked.connect(self.editField)
            self.buttonClear = QtGui.QPushButton('Clear')
            self.buttonClear.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.buttonClear.clicked.connect(self.clearField)
            self.buttonDownload = QtGui.QPushButton('Download')
            self.buttonDownload.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE + 'min-width:100px;')
            self.buttonDownload.clicked.connect(self.downloadFile)
            self.buttonOpen = QtGui.QPushButton('Open')
            self.buttonOpen.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE + 'min-width:50px;')
            self.buttonOpen.clicked.connect(self.openFile)
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, '')
            self.widgetLyQtObject.addWidget(self.widgetQtObj)
            self.widgetLyQtObject.addWidget(self.buttonEdit)
            self.widgetLyQtObject.addWidget(self.buttonClear)
            self.widgetLyQtObject.addWidget(self.buttonDownload)
            self.widgetLyQtObject.addWidget(self.buttonOpen)
            self.widgetLyQtObject.setSpacing(10)
            if self.translatable:
                self.connectTranslationButton()
                self.widgetLyQtObject.addWidget(self.translateButton)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)

    def openFile(self):
        filePath = self.downloadFile()
        if not utils.openByDefaultEditor(filePath):
            utils.launchMessage('Unable to open file!', 'warning')
        
    def downloadFile(self):
        statingPath = self.fieldStringInterface
        newFilePath = utils.getDirectoryFileToSaveSystem(None, statingPath=statingPath)
        if not self.currentValue:
            utils.launchMessage('Unable to save the file!', 'warning')
            utils.logMessage('warning', 'Empty file content in binary field', 'downloadFile')
        filePath = unicode(newFilePath)
        utils.unpackFile(self.currentValue, filePath)
        return filePath

    def editField(self):
        filePath = utils.getFileFromSystem('Open', '')
        if not filePath:
            return
        fileContent = utils.packFile(unicode(filePath))
        self.currentValue = fileContent
        self.fieldStringInterface = os.path.split(filePath) [1]
        self.widgetQtObj.setText(self.fieldStringInterface)

    def clearField(self):
        self.currentValue = ''
        self.fieldStringInterface = ''
        self.widgetQtObj.setText('')

    def valueChanged(self, val):
        print 'To implement valueChanged changed for binary'
        self.valueTemplateChanged()

    def setValue(self, newVal):
        self.currentValue = newVal
        if self.xmlWidget == 'image':
            self.pixmap = QtGui.QPixmap()
            if newVal:
                self.pixmap.loadFromData(base64.b64decode(newVal))
            self.pixmap = self.pixmap.scaled(self.imageWidth,
                                             self.imageHeight,
                                             aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                             transformMode=QtCore.Qt.FastTransformation)
            self.widgetQtObj.setPixmap(self.pixmap)
            self.widgetQtObj.resize(self.imageWidth, self.imageHeight)

    def setReadonly(self, val=False):
        if self.xmlWidget != 'image':
            super(Binary, self).setReadonly(val)
            self.widgetQtObj.setEnabled(False)
            self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE + constants.READONLY_STYLE)
            self.buttonClear.setHidden(val)
            self.buttonEdit.setHidden(val)
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)

    def setInvisible(self, val=False):
        super(Binary, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
        if self.xmlWidget != 'image':
            self.buttonClear.setHidden(val)
            self.buttonEdit.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.fieldStringInterface

    def eraseValue(self):
        # To clear also datas
        self.setValue('')
        