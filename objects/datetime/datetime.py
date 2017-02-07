
from PyQt4 import QtGui
from objects.fieldTemplate import OdooFieldTemplate


class Datetime(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Datetime, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        pass
