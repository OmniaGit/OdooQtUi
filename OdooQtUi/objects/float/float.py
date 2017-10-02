'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Float(OdooFieldTemplate):

    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Float, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = 0
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QDoubleSpinBox()
        self.widgetQtObj.setStyleSheet(constants.FLOAT_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.valueChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.FLOAT_STYLE)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self, newVal):
        self.currentValue = float(unicode(newVal))
        self.valueTemplateChanged()

    def setValue(self, newVal):
        newVal = float(unicode(newVal))
        self.widgetQtObj.setValue(newVal)

    def setReadonly(self, val=False):
        super(Float, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.FLOAT_STYLE + constants.READONLY_STYLE)
        elif self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.FLOAT_STYLE)
        else:
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, constants.FLOAT_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.FLOAT_STYLE)

    def setInvisible(self, val=False):
        super(Float, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(0.0)
