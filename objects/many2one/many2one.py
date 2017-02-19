'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2one(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2one, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.editButton = None
        self.canCreate = json.loads(self.fieldAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldAttributes.get('can_write', 'true'))
        self.relation = self.fieldDefinition.get('relation', '')
        self.availableItems = self.getItems()
        if self.canCreate:
            self.availableItems.append('Create and Edit...')
        if self.canWrite:
            self.availableItems.append('Edit...')
        self.hboxLay = self.getQtObject()

    def getItems(self):
        outVal = ['']
        if self.relation:
            for singleDict in self.rpc.readSearch(self.relation, ['name']):
                val = singleDict.get('name', '')
                if val:
                    outVal.append(val)
        return outVal
        
    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.hboxLay.addWidget(self.labelQtObj)
        
        if self.canWrite:
            self.editButton = QtGui.QPushButton('O')
            self.editButton.clicked.connect(self.editItem)
            self.hboxLay.addWidget(self.editButton)
        self.widgetQtObj = QtGui.QComboBox()
        self.widgetQtObj.currentIndexChanged.connect(self.indexChanged)
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
        
    def editItem(self, res=False):
        pass
        
    def indexChanged(self, res=False):
        currText = unicode(self.widgetQtObj.currentText())
        if currText == 'Edit...':
            if self.currentValue:
                pass
        elif currText == 'Create and Edit...':
            pass
        else:
            self.currentValue = currText
