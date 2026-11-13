# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

from PySide6 import QtCore
from PySide6 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi

from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Datetime(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Datetime, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.labelQtObj = False
        self.widgetQtObj = False
        self.currentValue = False
        self.getQtObject()
    
    def __str__(self)->str:
        return f"<{self.fieldName}> : {self.value}"
    
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
        # shown in the user's timezone, kept as Odoo stores it: UTC
        self.currentValue = utils.userToUtc(newDateTime, self.odooConnector)
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        """newVal as Odoo answers it, in UTC; shown in the timezone of the
        user (their `tz` in Odoo, UTC when they have none)."""
        local = utils.utcToUser(newVal, self.odooConnector)
        pyqtDateTime = QtCore.QDateTime()
        if local:
            pyqtDateTime = QtCore.QDateTime(local.year, local.month, local.day,
                                            local.hour, local.minute, local.second)
        self.widgetQtObj.setDateTime(pyqtDateTime)
        # after the widget: its dateTimeChanged has already set a value
        self.currentValue = utils.odooDatetime(newVal).strftime(utils.ODOO_DATETIME_FORMAT) if local else False

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
        """The UTC string Odoo stores, False for none: what a write, a
        create and an onchange send."""
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)