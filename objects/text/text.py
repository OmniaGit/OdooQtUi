'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from objects.fieldTemplate import OdooFieldTemplate


class Text(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Text, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QVBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QTextEdit()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay
