from datetime import datetime
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Datetime(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc):
        super(Datetime, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.currentValue = ''
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qDoubleSpinBoxValue = QtWidgets.QDateTimeEdit(self)
        self.qDoubleSpinBoxValue.setStyleSheet(constants.DATE_STYLE)
        self.qDoubleSpinBoxValue.setToolTip(self.tooltip)
        self.qDoubleSpinBoxValue.dateTimeChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.qDoubleSpinBoxValue, constants.DATE_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        if self.translatable:
            self.connectTranslationButton()
            self.qtHorizontalWidget.addWidget(self.translateButton)

    def valueChanged(self, newDateTime):
        self.currentValue = newDateTime.toString()
        self.valueTemplateChanged()

    def setValue(self, newVal):
        pyqtDateTime = QtCore.QDateTime()
        if newVal:
            # year, month, day, hour, minute, second
            if not isinstance(newVal, str):
                datetimeVal = datetime.strptime(newVal.value, '%Y%m%dT%H:%M:%S')
            else:
                datetimeVal = datetime.strptime(newVal, '%Y-%m-%d %H:%M:%S')
            self.currentValue = datetimeVal
            pyqtDateTime = QtCore.QDateTime(datetimeVal.year, datetimeVal.month, datetimeVal.day, datetimeVal.hour, datetimeVal.minute, datetimeVal.second)
        self.qDoubleSpinBoxValue.setDateTime(pyqtDateTime)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        if self.currentValue:
            self.currentValue = str(self.qDoubleSpinBoxValue.dateTime().toString('yyyy-MM-dd hh:mm:ss'))
        return self.currentValue

    def eraseValue(self):
        self.setValue('')
