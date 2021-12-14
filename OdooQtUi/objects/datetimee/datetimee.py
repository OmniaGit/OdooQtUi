from datetime import datetime
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utilsUi

from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Datetime(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Datetime, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = ''
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtWidgets.QDateTimeEdit(self)
        self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.dateTimeChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.qtHorizontalWidget.addWidget(self.translateButton)

    def valueChanged(self, newDateTime):
        self.currentValue = newDateTime
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        pyqtDateTime = QtCore.QDateTime()
        if newVal:
            # year, month, day, hour, minute, second
            if not isinstance(newVal, str):
                datetimeVal = datetime.strptime(newVal.value, '%Y%m%dT%H:%M:%S')
            else:
                datetimeVal = datetime.strptime(newVal, '%Y-%m-%d %H:%M:%S')
            self.currentValue = datetimeVal
            pyqtDateTime = QtCore.QDateTime(datetimeVal.year, datetimeVal.month, datetimeVal.day, datetimeVal.hour, datetimeVal.minute, datetimeVal.second)
        self.widgetQtObj.setDateTime(pyqtDateTime)

    def setReadonly(self, val=False):
        super(Datetime, self).setReadonly(val)
        self.widgetQtObj.setEnabled(not val)
        if val:
            self.widgetQtObj.setStyleSheet(constants.DATE_STYLE + constants.READONLY_STYLE)
        elif self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
        else:
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.DATE_STYLE)
            else:
                self.widgetQtObj.setStyleSheet(constants.DATE_STYLE)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        super(Datetime, self).setInvisible(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        if self.currentValue:
            self.currentValue = str(self.widgetQtObj.dateTime().toString('yyyy-MM-dd hh:mm:ss'))
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)