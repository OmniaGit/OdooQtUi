'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PySide2 import QtGui
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Date(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Date, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = ''
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qDoubleSpinBoxValue = QtWidgets.QDateEdit(self)
        self.qDoubleSpinBoxValue.setStyleSheet(constants.DATE_STYLE)
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.dateChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, constants.DATE_STYLE)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        if self.translatable:
            self.connectTranslationButton()
            self.addWidget(self.translateButton)

    def valueChanged(self, newDate):
        self.currentValue = newDate.toString()
        self.valueTemplateChanged()

    @property
    def value(self):
        if self.currentValue:
            self.currentValue = str(self.qDoubleSpinBoxValue.date().toString('yyyy-MM-dd'))
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue('')
