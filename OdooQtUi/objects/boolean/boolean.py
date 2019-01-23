'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Boolean(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Boolean, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = False
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qDoubleSpinBoxValue = QtWidgets.QCheckBox()
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.stateChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, '')
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
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

    def setValue(self, newVal):
        newVal = eval(str(newVal))
        self.qDoubleSpinBoxValue.setChecked(newVal)
        self.currentValue = newVal

    def setInvisible(self, val=False):
        super(Boolean, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.qDoubleSpinBoxValue.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
