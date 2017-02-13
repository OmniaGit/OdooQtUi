'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Boolean(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Boolean, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QCheckBox()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.stateChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def valueChanged(self, val):
        if val == QtCore.Qt.Unchecked:
            self.currentValue = False
        elif val == QtCore.Qt.Checked:
            self.currentValue = True
        else:
            self.currentValue = 'third-state'
        return super(Boolean, self).stateChanged(val)
