'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from objects.fieldTemplate import OdooFieldTemplate


class Integer(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Integer, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = 0
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QSpinBox()
        self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.valueChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.INTEGER_STYLE)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self, newValue):
        self.currentValue = int(unicode(newValue))
        self.valueTemplateChanged()

    def setValue(self, newVal):
        newVal = int(unicode(newVal))
        self.widgetQtObj.setValue(newVal)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Integer, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE + constants.READONLY_STYLE)
        else:
            self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE)

    def setInvisible(self, val=False):
        super(Integer, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue
