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


class Text(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Text, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = ''
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QTextEdit()
        self.widgetQtObj.setStyleSheet(constants.TEXT_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.textChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.TEXT_STYLE)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self):
        self.currentValue = str(self.widgetQtObj.toPlainText())
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
        super(Text, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.READONLY_STYLE)
        elif self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.TEXT_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.TEXT_STYLE)
            else:
                self.widgetQtObj.setStyleSheet('background-color:white;')

    def setInvisible(self, val=False):
        super(Text, self).setInvisible(val)
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
