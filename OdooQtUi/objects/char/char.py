'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

try:
    from PySide import QtGui
    from PySide import QtCore
except Exception as ex:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Charachter(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Charachter, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = ''
        self.translatable = utils.evaluateBoolean(self.fieldPyDefinition.get('translate', False))
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QLineEdit()
        self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.editingFinished.connect(self.valueChanged)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.widgetLyQtObject.setSpacing(10)
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)

    def valueChanged(self):
        self.currentValue = str(self.widgetQtObj.text())
        self.valueTemplateChanged()

    def setValue(self, newVal):
        if isinstance(newVal, bool):
            if not newVal:
                newVal = ''
            else:
                newVal = ''
                utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')
        self.widgetQtObj.setText(newVal)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Charachter, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE + constants.READONLY_STYLE)
        elif self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)

    def setInvisible(self, val=False):
        super(Charachter, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue('')
