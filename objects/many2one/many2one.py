'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from objects.fieldTemplate import OdooFieldTemplate


class Many2one(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Many2one, self).__init__(xmlField, fieldsDefinition)
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
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QComboBox()
        self.widgetQtObj.addItems(self.availableItems)
        self.widgetQtObj.setToolTip(self.fieldDefinition.get('help', ''))
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay
