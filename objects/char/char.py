'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Charachter(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Charachter, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.translatable = utils.evaluateBoolean(self.fieldDefinition.get('translate', False))
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QLineEdit()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.editingFinished.connect(self.valueChanged)
        self.hboxLay.addWidget(self.widgetQtObj)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj)
        return self.hboxLay

    def valueChanged(self):
        self.currentValue = unicode(self.widgetQtObj.text())
        return super(Charachter, self).editingFinished()
