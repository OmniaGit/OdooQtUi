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
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Date, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtWidgets.QDateEdit(self)
        self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.dateChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.addWidget(self.translateButton)

    def valueChanged(self, newDate):
        self.currentValue = newDate
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        # To Be Implemented
        self.widgetQtObj
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Date, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.DATE_STYLE + constants.READONLY_STYLE)
        elif self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Date, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        if self.currentValue:
            self.currentValue = str(self.widgetQtObj.date().toString('yyyy-MM-dd'))
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
