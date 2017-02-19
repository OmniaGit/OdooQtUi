'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate


class Float(OdooFieldTemplate):
    
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Float, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QDoubleSpinBox()
        self.widgetQtObj.setStyleSheet(constants.FLOAT_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.valueChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.FLOAT_STYLE)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def valueChanged(self, newVal):
        self.currentValue = float(unicode(newVal))
        self.valueTemplateChanged()

    def setValue(self, newVal):
        newVal = float(unicode(newVal))
        self.widgetQtObj.setValue(newVal)

    def setReadonly(self, val=False):
        self.widgetQtObj.setEnabled(not val)

    def setInvisible(self, val=False):
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
