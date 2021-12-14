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
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        self.isChatterWidget = isChatterWidget
        self.qtParent = qtParent
        super(Binary, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
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
            self.widgetQtObj = QtWidgets.QLabel()
            self.pixmap = QtGui.QPixmap()
            self.pixmap = self.pixmap.scaled(self.imageWidth,
                                             self.imageHeight,
                                             # not supported on pyside aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                             #transformMode=QtCore.Qt.FastTransformation
                                             )
            self.widgetQtObj.setPixmap(self.pixmap)
            self.widgetQtObj.resize(self.imageWidth, self.imageHeight)
            self.widgetQtObj.setText('aaa')
        else:
            self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface, self.qtParent)
            self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
            self.widgetQtObj = QtWidgets.QLineEdit()
            self.widgetQtObj.setToolTip(self.tooltip)
            self.widgetQtObj.editingFinished.connect(self.valueChanged)
            self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)
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
                utilsUi.setRequiredBackground(self.widgetQtObj, '')
            self.qtHorizontalWidget.addWidget(self.widgetQtObj)
            self.qtHorizontalWidget.addWidget(self.buttonEdit)
            self.qtHorizontalWidget.addWidget(self.buttonClear)
            self.qtHorizontalWidget.addWidget(self.buttonDownload)
            self.qtHorizontalWidget.addWidget(self.buttonOpen)
            self.qtHorizontalWidget.setSpacing(10)
            if self.translatable:
                self.connectTranslationButton()
                self.addWidget(self.translateButton)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)

    def openFile(self):
        filePath = self.downloadFile()
        if not utils.openByDefaultEditor(filePath):
            utilsUi.popWarning(self.qtParent, 'Unable to open file!')

    def downloadFile(self):
        statingPath = self.widgetQtObj.text() or self.fieldStringInterface
        newFilePath = utilsUi.getDirectoryFileToSaveSystem(None, statingPath=statingPath)
        if not self.currentValue:
            utilsUi.popWarning(self.qtParent, 'Unable to save the file!')
        filePath = str(newFilePath)
        utils.unpackFile(self.currentValue, filePath)
        return filePath

    def editField(self):
        filePath = utilsUi.getFileFromSystem('Open', '')
        if not os.path.exists(filePath):
            return
        fileContent = utils.packFile(str(filePath))
        self.currentValue = fileContent
        self.fieldStringInterface = os.path.split(filePath)[1]
        self.widgetQtObj.setText(self.fieldStringInterface)

    def clearField(self):
        self.currentValue = ''
        self.fieldStringInterface = ''
        self.widgetQtObj.setText('')

    def valueChanged(self, val):
        utils.logDebug('To implement valueChanged changed for binary', 'valueChanged')
        self.valueTemplateChanged()

    def setValue(self, newVal, fileName='', viewType='form'):
        self.currentValue = newVal
        if self.xmlWidget == 'image':
            self.pixmap = QtGui.QPixmap()
            if newVal:
                self.pixmap.loadFromData(base64.b64decode(newVal))
            self.pixmap = self.pixmap.scaled(self.imageWidth,
                                             self.imageHeight,
                                             #aspectRatioMode=QtCore.Qt.IgnoreAspectRatio,
                                             #transformMode=QtCore.Qt.FastTransformation
                                             )
            self.widgetQtObj.setPixmap(self.pixmap)
            self.widgetQtObj.resize(self.imageWidth, self.imageHeight)
        else:
            text = fileName or self.fieldPyDefinition.get('help', 'File Content')
            self.widgetQtObj.setText(text)
            self.fieldStringInterface = text

    def setReadonly(self, val=False):
        if self.xmlWidget != 'image':
            super(Binary, self).setReadonly(val)
            self.widgetQtObj.setEnabled(False)
            self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE + constants.READONLY_STYLE)
            self.buttonClear.setHidden(val)
            self.buttonEdit.setHidden(val)
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Binary, self).setInvisible(val)
        if self.labelQtObj:
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
        