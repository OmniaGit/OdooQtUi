
from PyQt4 import QtGui
from objects.fieldTemplate import OdooFieldTemplate


class Datetime(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition):
        super(Datetime, self).__init__(xmlField, fieldsDefinition)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.hboxLay = self.getQtObject()

    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.hboxLay.addWidget(self.labelQtObj)
        self.widgetQtObj = QtGui.QDateTimeEdit()
        self.widgetQtObj.setToolTip(self.tooltip)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay
