'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.getQtObject()

    def getQtObject(self):
        buttonsLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        buttonsLay.addWidget(self.labelQtObj)
        createButt = QtGui.QPushButton('Create')
        editButton = QtGui.QPushButton('Edit')
        addButton = QtGui.QPushButton('Add')
        removeButton = QtGui.QPushButton('Remove')
        createButt.setStyleSheet(constants.BUTTON_STYLE)
        editButton.setStyleSheet(constants.BUTTON_STYLE)
        addButton.setStyleSheet(constants.BUTTON_STYLE)
        removeButton.setStyleSheet(constants.BUTTON_STYLE)
        buttonsLay.addWidget(createButt)
        buttonsLay.addWidget(editButton)
        buttonsLay.addWidget(addButton)
        buttonsLay.addWidget(removeButton)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.widgetQtObj = QtGui.QTableWidget()
        self.widgetQtObj.setToolTip(self.tooltip)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def setValue(self, newVal):
        return
        self.widgetQtObj.setText(newVal)
