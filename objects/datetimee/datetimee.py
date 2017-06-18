from PyQt4 import QtCore
from PyQt4 import QtGui
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from objects.fieldTemplate import OdooFieldTemplate
from datetime import datetime


class Datetime(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Datetime, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = ''
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtGui.QDateTimeEdit()
        self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.dateTimeChanged.connect(self.valueChanged)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def valueChanged(self, newDateTime):
        self.currentValue = unicode(newDateTime)
        self.valueTemplateChanged()

    def setValue(self, newVal):
        # year, month, day, hour, minute, second
        datetimeVal = datetime.strptime(newVal, '%Y-%m-%d %H:%M:%S')
        self.currentValue = datetimeVal
        pyqtDateTime = QtCore.QDateTime(datetimeVal.year, datetimeVal.month, datetimeVal.day, datetimeVal.hour, datetimeVal.minute, datetimeVal.second)
        self.widgetQtObj.setDateTime(pyqtDateTime)

    def setReadonly(self, val=False):
        super(Datetime, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.DATE_STYLE + constants.READONLY_STYLE)
        else:
            if self.required:
                utils.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)

    def setInvisible(self, val=False):
        super(Datetime, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        if not self.currentValue:
            self.currentValue = self.widgetQtObj.dateTime().toString('yyyy-MM-dd hh:mm:ss')
        return self.currentValue
