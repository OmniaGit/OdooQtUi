'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Boolean(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Boolean, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.widgetQtObj = QtWidgets.QCheckBox()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.stateChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, '')
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.addWidget(self.translateButton)

    def valueChanged(self, val):
        if val == QtCore.Qt.Unchecked:
            self.currentValue = False
        elif val == QtCore.Qt.Checked:
            self.currentValue = True
        else:
            self.currentValue = 'third-state'
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        newVal = eval(str(newVal))
        self.widgetQtObj.setChecked(newVal)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Boolean, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.READONLY_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, '')
            else:
                self.widgetQtObj.setStyleSheet('background-color:white;')

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
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
        