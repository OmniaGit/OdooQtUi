'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
from PySide2 import QtGui
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utilsUi

from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Integer(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Integer, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = 0
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.widgetQtObj = QtWidgets.QSpinBox()
        self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.valueChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.INTEGER_STYLE)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        if self.translatable:
            self.connectTranslationButton()
            self.qtHorizontalWidget.addWidget(self.translateButton)

    def valueChanged(self, newValue):
        self.currentValue = int(str(newValue))
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        newVal = int(str(newVal))
        self.widgetQtObj.setValue(newVal)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Integer, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE + constants.READONLY_STYLE)
        elif self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.INTEGER_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.INTEGER_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.INTEGER_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Integer, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(0)
