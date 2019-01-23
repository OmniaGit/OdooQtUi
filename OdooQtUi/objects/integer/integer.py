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
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Integer, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = 0
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qDoubleSpinBoxValue = QtWidgets.QSpinBox()
        self.qDoubleSpinBoxValue.setStyleSheet(constants.INTEGER_STYLE)
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.valueChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, constants.INTEGER_STYLE)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(40, 40, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def valueChanged(self, newValue):
        self.currentValue = int(str(newValue))
        self.valueTemplateChanged()

    def setValue(self, newVal):
        newVal = int(str(newVal))
        self.qDoubleSpinBoxValue.setValue(newVal)
        self.currentValue = newVal

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(0)
