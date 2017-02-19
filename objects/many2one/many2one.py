'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate


class Many2one(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2one, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.availableItems = self.getItems()
        self.availableItems.append('Create and Edit...')
        self.hboxLay = self.getQtObject()

    def getItems(self):
        return ['']
        
    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QComboBox()
        self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)
        self.widgetQtObj.addItems(self.availableItems)
        self.widgetQtObj.setToolTip(self.tooltip)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def setValue(self, newVal):
        return
        self.widgetQtObj.setText(newVal)

    def setReadonly(self, val=False):
        self.widgetQtObj.setEnabled(not val)
        self.widgetQtObj.setEditable(not val)
        self.widgetQtObj.setDisabled(val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE + constants.READONLY_STYLE)
        else:
            self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)

    def setInvisible(self, val=False):
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
