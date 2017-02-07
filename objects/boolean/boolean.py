'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from objects.fieldTemplate import OdooFieldTemplate


class Boolean(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Boolean, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        pass
