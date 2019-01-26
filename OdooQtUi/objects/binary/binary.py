'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import os
import base64
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Binary(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Binary, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = False
        self.xmlWidget = self.fieldXmlAttributes.get('widget')
        self.imageWidth = 100
        self.imageHeight = 100
        self.fileName = self.fieldXmlAttributes.get('filename')  # File name has to be take here
        try:
            self.imageWidth = eval(self.fieldXmlAttributes.get('img_width'))
            self.imageHeight = eval(self.fieldXmlAttributes.get('img_height'))
        except Exception as _ex:
            pass
        self.getQtObject()

    def getQtObject(self):
        if self.xmlWidget == 'image':
            self.qDoubleSpinBoxValue = QtWidgets.QLabel()
            self.pixmap = QtGui.QPixmap()
            self.pixmap = self.pixmap.scaled(self.imageWidth,
                                             self.imageHeight,
                                             aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                             transformMode=QtCore.Qt.FastTransformation)
            self.qDoubleSpinBoxValue.setPixmap(self.pixmap)
            self.qDoubleSpinBoxValue.resize(self.imageWidth, self.imageHeight)
            self.qDoubleSpinBoxValue.setText('aaa')
        else:
            self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            self.qDoubleSpinBoxValue = QtWidgets.QLineEdit()
            self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
            self.qDoubleSpinBoxValue.editingFinished.connect(self.valueChanged)
            self.qDoubleSpinBoxValue.setStyleSheet(constants.CHAR_STYLE)
            self.buttonEdit = QtWidgets.QPushButton('Edit')
            self.buttonEdit.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.buttonEdit.clicked.connect(self.editField)
            self.buttonClear = QtWidgets.QPushButton('Clear')
            self.buttonClear.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.buttonClear.clicked.connect(self.clearField)
            self.buttonDownload = QtWidgets.QPushButton('Download')
            self.buttonDownload.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE + 'min-width:100px;')
            self.buttonDownload.clicked.connect(self.downloadFile)
            self.buttonOpen = QtWidgets.QPushButton('Open')
            self.buttonOpen.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE + 'min-width:50px;')
            self.buttonOpen.clicked.connect(self.openFile)
            if self.required:
                utils.setRequiredBackground(self.qDoubleSpinBoxValue, '')
            self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
            self.qtHorizontalWidget.addWidget(self.buttonEdit)
            self.qtHorizontalWidget.addWidget(self.buttonClear)
            self.qtHorizontalWidget.addWidget(self.buttonDownload)
            self.qtHorizontalWidget.addWidget(self.buttonOpen)
            self.qtHorizontalWidget.setSpacing(10)
            if self.translatable:
                self.connectTranslationButton()
                self.addWidget(self.translateButton)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)

    def openFile(self):
        filePath = self.downloadFile()
        if not utils.openByDefaultEditor(filePath):
            utilsUi.launchMessage('Unable to open file!', 'warning')

    def downloadFile(self):
        statingPath = self.fieldStringInterface
        newFilePath = utilsUi.getDirectoryFileToSaveSystem(None, statingPath=statingPath)
        if not self.currentValue:
            utilsUi.launchMessage('Unable to save the file!', 'warning')
            utils.logMessage('warning', 'Empty file content in binary field', 'downloadFile')
        filePath = str(newFilePath)
        utils.unpackFile(self.currentValue, filePath)
        return filePath

    def editField(self):
        filePath = utilsUi.getFileFromSystem('Open', '')
        if not filePath:
            return
        fileContent = utils.packFile(str(filePath))
        self.currentValue = fileContent
        self.fieldStringInterface = os.path.split(filePath)[1]
        self.qDoubleSpinBoxValue.setText(self.fieldStringInterface)

    def clearField(self):
        self.currentValue = ''
        self.fieldStringInterface = ''
        self.qDoubleSpinBoxValue.setText('')

    def valueChanged(self, val):
        utils.logDebug('To implement valueChanged changed for binary', 'valueChanged')
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
            self.qDoubleSpinBoxValue.setPixmap(self.pixmap)
            self.qDoubleSpinBoxValue.resize(self.imageWidth, self.imageHeight)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.fieldStringInterface

    def eraseValue(self):
        # To clear also datas
        self.setValue('')
