# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 02 feb 2017

@author: Daniel
'''
import json

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants


class OdooFieldTemplate(QtWidgets.QWidget):
    value_changed_signal = QtCore.Signal((str,))
    translation_clicked = QtCore.Signal((str,))

    def __init__(self,
                 qtParent,
                 xmlField,
                 fieldsDefinition,
                 odooConnector):
        super(OdooFieldTemplate, self).__init__(qtParent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum,
                           QtWidgets.QSizePolicy.Minimum)
        self.odooConnector=odooConnector
        self.fieldXmlAttributes = xmlField.attrib
        self.parentId = False
        self.odooId=False
        self.parentModel = ''
        self.context = self.fieldXmlAttributes.get('context', '{}')
        self.fieldName = self.fieldXmlAttributes.get('name', '')
        self.modifiers = json.loads(self.fieldXmlAttributes.get('modifiers', '{}'))
        self.on_change = self.fieldXmlAttributes.get('on_change', '')
        self.fieldPyDefinition = fieldsDefinition.get(self.fieldName, {})
        # Kept as they came as well as evaluated. From Odoo 17 these are python
        # expressions over the record -- `invisible="state != 'draft'"` -- and
        # there is no record here yet: read now, against nothing, they raise and
        # answer "not hidden", which is how every conditional field came to be
        # shown in every state. What depends on the record is decided by the
        # modifier pass, once the record has been read -- see
        # utils.widgetModifier, and KOO's Record.isFieldInvisible before it.
        self.readonlyExpression = self.fieldPyDefinition.get('readonly', self.fieldXmlAttributes.get('readonly', False))
        self.readonly = utils.evaluateExpression(self.readonlyExpression) \
            if utils.isConstantModifier(self.readonlyExpression) else False
        self.requiredExpression = self.fieldPyDefinition.get('required', self.fieldXmlAttributes.get('required', False))
        self.required = utils.evaluateExpression(self.requiredExpression) \
            if utils.isConstantModifier(self.requiredExpression) else False
        self.invisibleExpression = self.fieldPyDefinition.get('invisible', self.fieldXmlAttributes.get('invisible', False))
        # False while it depends on the record, and the modifier pass decides
        # once there is one. Not hidden-until-told, which is what the buttons
        # do: the list view reads this attribute straight as a column rule
        # (`setColumnHidden` in tree_list_obj._setFieldsModifiers), where there
        # is no record to evaluate anything against, and a column that vanishes
        # from Search is a worse answer than one shown a moment early. In a form
        # nothing shows before the modifier pass anyway -- every field is built
        # hidden, two lines below.
        self.invisible = utils.evaluateExpression(self.invisibleExpression) \
            if utils.isConstantModifier(self.invisibleExpression) else False
        self.tooltip = self.fieldPyDefinition.get('help', '')
        self.fieldType = self.fieldPyDefinition.get('type', '')
        self.labelString = self.fieldPyDefinition.get('string', '')
        self.fieldStringInterface = self.fieldXmlAttributes.get('string', self.labelString)
        self.change_default = utils.evaluateBoolean(self.fieldPyDefinition.get('change_default', False))
        self.searchable = utils.evaluateBoolean(self.fieldPyDefinition.get('searchable', True))
        self.manual = utils.evaluateBoolean(self.fieldPyDefinition.get('manual', False))
        self.depends = self.fieldPyDefinition.get('depends', [])
        self.related = self.fieldPyDefinition.get('related', [])
        self.company_dependent = utils.evaluateBoolean(self.fieldPyDefinition.get('company_dependent', False))
        self.sortable = utils.evaluateBoolean(self.fieldPyDefinition.get('sortable', True))
        self.store = utils.evaluateBoolean(self.fieldPyDefinition.get('store', True))
        self.translatable = self.fieldXmlAttributes.get('translate', self.fieldPyDefinition.get('translate', False))
        self.labelQtObj = None
        self.widgetQtObj = None
        self.initVal = ''
        self.changed = False
        self.translateButton = False
        self.invisibleConditions, self.readonlyConditions = utils.evaluateModifiers(self.modifiers)
        self.qtHorizontalWidget = QtWidgets.QHBoxLayout(self)
        utilsUi.setLayoutMarginAndSpacing(self.qtHorizontalWidget)
        self.hide()
        if constants.DEBUG:
            self.setStyleSheet("border: 2px solid black;")
        return self

    @property
    def qtObject(self):
        return self.qtHorizontalWidget

    def setParentAttrs(self, parentId, parentModel):
        self.parentId = parentId
        self.parentModel = parentModel

    def connectTranslationButton(self):
        self.translateButton = QtWidgets.QPushButton('T')
        self.translateButton.setStyleSheet(constants.BUTTON_STYLE)
        self.translateButton.clicked.connect(self.translateDialog)
        # self.qtHorizontalWidget.setSpacing(10)

    def valueTemplateChanged(self):
        self.value_changed_signal.emit(self.fieldName)

    def setValue(self, newVal, viewType='form'):
        utils.logMessage('warning', 'setValue not implemented for field: %r' % (self.fieldName), 'setValue')

    def hideTranslateButton(self, val):
        if self.translateButton:
            self.translateButton.setHidden(val)

    def valueChanged(self):
        utils.logMessage('warning', 'valueChanged not implemented for field: %r' % (self.fieldName), 'valueChanged')

    def translateDialog(self):
        self.translation_clicked.emit(self.fieldName)

    def setReadonly(self, val):
        self.setEnabled(not val)
        self.hideTranslateButton(val)

    def setInvisible(self, val):
        utilsUi.setLayoutMarginAndSpacing(self.qtHorizontalWidget, 0)
        self.hideTranslateButton(val)
        if val:
            self.hide()
        else:
            self.show()

    def showChatterWidget(self):
        pass