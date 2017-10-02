'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Boolean(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Boolean, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QCheckBox()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.stateChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self, val):
        if val == QtCore.Qt.Unchecked:
            self.currentValue = False
        elif val == QtCore.Qt.Checked:
            self.currentValue = True
        else:
            self.currentValue = 'third-state'
        self.valueTemplateChanged()

    def setValue(self, newVal):
        newVal = eval(unicode(newVal))
        self.widgetQtObj.setChecked(newVal)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Boolean, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.READONLY_STYLE)
        else:
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, '')
            else:
                self.widgetQtObj.setStyleSheet('background-color:white;')

    def setInvisible(self, val=False):
        super(Boolean, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
        