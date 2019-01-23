'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PySide2 import QtGui
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Charachter(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Charachter, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = ''
        self.translatable = utils.evaluateBoolean(self.fieldPyDefinition.get('translate', False))
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qDoubleSpinBoxValue = QtWidgets.QLineEdit()
        self.qDoubleSpinBoxValue.setStyleSheet(constants.CHAR_STYLE)
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.editingFinished.connect(self.valueChanged)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        if self.translatable:
            #self.setSpacing(10)
            self.connectTranslationButton()
            self.qtHorizontalWidget.addWidget(self.translateButton)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, constants.CHAR_STYLE)

    def valueChanged(self):
        self.currentValue = str(self.qDoubleSpinBoxValue.text())
        self.valueTemplateChanged()

    def setValue(self, newVal):
        if isinstance(newVal, bool):
            if not newVal:
                newVal = ''
            else:
                newVal = ''
                utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')
        self.qDoubleSpinBoxValue.setText(newVal)
        self.currentValue = newVal

    def setInvisible(self, val=False):
        super(Charachter, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.qDoubleSpinBoxValue.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue('')
