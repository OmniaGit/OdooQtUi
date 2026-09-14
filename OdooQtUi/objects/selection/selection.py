# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 06 feb 2017

@author: Daniel
'''
import json
import logging
from PySide6 import QtCore
from PySide6 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate
from OdooQtUi.widgets.status_bar import StatusBar


class Selection(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, isChatterWidget=False):
        super(Selection, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.isChatterWidget = isChatterWidget
        self.selectionMapping = {}
        self.selectionMappingReverse = {}
        self.labels = []
        self.widgetQtObj = False
        self.currentValue = ''
        self.widget = self.fieldXmlAttributes.get('widget', '')
        self.statusbar_colors = {}
        self.statusbar_visible = []
        if self.widget == 'statusbar':
            # Both are optional, and both used to be read as if they were not:
            # json.loads('') raises, and ''.split(',') answers [''], which drew
            # a statusbar of one empty state. Odoo 17 does not send
            # statusbar_colors at all.
            try:
                self.statusbar_colors = json.loads(
                    self.fieldXmlAttributes.get('statusbar_colors') or '{}')
            except ValueError as ex:
                logging.warning("statusbar_colors of %s is not readable: %s"
                                % (self.fieldName, ex))
            self.statusbar_visible = [name.strip() for name
                                      in self.fieldXmlAttributes.get('statusbar_visible', '').split(',')
                                      if name.strip()]
        self.getQtObject()

        if self.widgetQtObj:
            # The bar is never disabled: it shows a state rather than taking
            # one, and a disabled widget answers no tooltip either.
            if self.widget != 'statusbar':
                self.widgetQtObj.setDisabled(self.readonly)
            if self.invisible:
                self.widgetQtObj.hide()

    def __str__(self)->str:
        return f"<{self.fieldName}> : {self.value}"
       
    def populateMapping(self, items):
        for odooName, interfaceName in items:
            odooName = str(odooName)
            interfaceName = str(interfaceName)
            self.selectionMapping[odooName] = interfaceName
            self.selectionMappingReverse[interfaceName] = odooName

    def statusBarStates(self):
        """The states to show, with the labels the server translated.

        From the field's own selection and not from `statusbar_visible`, which
        carries the technical values and was what the row of labels used to
        show -- `Draft`, not the label of the customer's own state. Where the
        view does name them, they are the ones always shown; Odoo adds the
        current one to that list whatever it says, so a record in a state
        nobody listed is not a bar with no state in it.
        """
        selection = [(str(value), str(label)) for value, label
                     in (self.fieldPyDefinition.get('selection') or [])]
        if not selection:
            return [(name, name.replace('_', ' ').title())
                    for name in self.statusbar_visible]
        if not self.statusbar_visible:
            return selection
        wanted = list(self.statusbar_visible)
        if self.currentValue and self.currentValue not in wanted:
            wanted.append(str(self.currentValue))
        return [(value, label) for value, label in selection if value in wanted]

    def statusBar(self):
        """The chevrons Odoo draws, filling the width they are given."""
        self.labels = []
        self.widgetQtObj = StatusBar(self, states=self.statusBarStates(),
                                     current=self.currentValue)
        self.widgetQtObj.setColours(self.statusbar_colors)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.layout().addWidget(self.widgetQtObj)
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)

    def getQtObject(self):
        if self.widget == 'statusbar':
            self.statusBar()
        else:
            self.getCombo()

    def getCombo(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.widgetQtObj = QtWidgets.QComboBox(self)
        self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)
        selectionVals = [('', '')]
        selectionVals.extend(self.fieldPyDefinition.get('selection', []))
        self.populateMapping(selectionVals)
        self.widgetQtObj.addItems(list(self.selectionMappingReverse.keys()))
        self.widgetQtObj.setToolTip(self.tooltip)
        self.widgetQtObj.currentIndexChanged.connect(self.valueChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

    def valueChanged(self, newIndex):
        currentValue = str(self.widgetQtObj.currentText())
        self.currentValue = self.selectionMappingReverse.get(currentValue)
        self.valueTemplateChanged()

    def setValue(self, newVal, viewType='form'):
        if isinstance(newVal, bool):
            if not newVal:
                newVal = ''
            else:
                newVal = ''
                utils.logMessage('warning', 'Boolean value %r is passed to char field %r, check better' % (newVal, self.fieldName), 'setValue')

        if self.widget == 'statusbar':
            self.currentValue = newVal
            if self.widgetQtObj:
                # The states as well: a view that lists only some of them shows
                # the current one too, and which one that is has just changed.
                self.widgetQtObj.setStates(self.statusBarStates())
                self.widgetQtObj.setCurrent(newVal)
            return
        allItems = tuple(self.selectionMapping.keys())
        if newVal not in allItems:
            utils.logMessage('warning', '[%r] Value %r not found in values: %r' % (self.fieldName, newVal, allItems), 'setValue')
            return
        newIndex = allItems.index(newVal)
        if newIndex:
            self.widgetQtObj.setCurrentIndex(newIndex)
        self.currentValue = newVal

    def setReadonly(self, val=False):
        super(Selection, self).setReadonly(val)
        if self.widget == 'statusbar':
            # Nothing to disable: the bar shows a state, it does not set one.
            # The buttons of the header are what move a record, and they carry
            # their own modifiers.
            return
        if self.widgetQtObj:
            self.widgetQtObj.setEnabled(not val)
            self.widgetQtObj.setEditable(not val)
            self.widgetQtObj.setDisabled(val)
            if val:
                self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE + constants.READONLY_STYLE)
            elif self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
            else:
                if self.required:
                    utilsUi.setRequiredBackground(self.widgetQtObj, constants.SELECTION_STYLE)
                else:
                    self.widgetQtObj.setStyleSheet(constants.SELECTION_STYLE)

    def setInvisible(self, val=False):
        try:
            if self.isChatterWidget:
                return
            if isinstance(val, (str,list, tuple,dict)):
                logging.warning(f'{val} not of supported type force to False')
                val=False
            super(Selection, self).setInvisible(val)
            if self.labelQtObj:
                self.labelQtObj.setContentsMargins(0,0,0,0)
                self.labelQtObj.setHidden(val)
            if self.widgetQtObj:
                self.widgetQtObj.setContentsMargins(0,0,0,0)
                self.widgetQtObj.setHidden(val)
        except Exception as ex:
            logging.error(f"Unable to set invisible {self.fieldName} due to errro {ex}")

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue(False)
