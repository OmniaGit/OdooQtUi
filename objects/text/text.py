'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from objects.fieldTemplate import OdooFieldTemplate


class Text(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Text, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QVBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QTextEdit()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.textChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def valueChanged(self):
        self.currentValue = unicode(self.widgetQtObj.toPlainText())
        self.valueTemplateChanged()

    def setValue(self, newVal):
        if isinstance(newVal, bool):
            utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')
            newVal = ''
        self.widgetQtObj.setText(newVal)

    def setReadonly(self, val=False):
        self.widgetQtObj.setEnabled(not val)
