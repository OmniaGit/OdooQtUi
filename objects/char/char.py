'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate


class Charachter(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Charachter, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.translatable = utils.evaluateBoolean(self.fieldDefinition.get('translate', False))
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QLineEdit()
        self.widgetQtObj.setStyleSheet(constants.CHAR_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.editingFinished.connect(self.valueChanged)
        self.hboxLay.addWidget(self.widgetQtObj)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.CHAR_STYLE)
        return self.hboxLay

    def valueChanged(self):
        self.currentValue = unicode(self.widgetQtObj.text())
        self.valueTemplateChanged()

    def setValue(self, newVal):
        if isinstance(newVal, bool):
            utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')
            newVal = ''
        self.widgetQtObj.setText(newVal)

    def setReadonly(self, val=False):
        self.widgetQtObj.setEnabled(not val)

    def setInvisible(self, val=False):
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
