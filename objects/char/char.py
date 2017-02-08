'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Charachter(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Charachter, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.translatable = utils.evaluateBoolean(self.fieldDefinition.get('translate', False))
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QLineEdit()
        self.widgetQtObj.setToolTip(self.fieldDefinition.get('help', ''))
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay
