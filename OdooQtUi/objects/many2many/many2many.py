# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets

from functools import partial
from OdooQtUi.RPC.errors import OdooRpcError
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Many2many(OdooFieldTemplate):
    def __init__(self,
                 qtParent,
                 xmlField,
                 fieldsDefinition,
                 odooConnector=None,
                 isChatterWidget=False,
                 parent_view_type=''):
        super(Many2many, self).__init__(qtParent,
                                        xmlField,
                                        fieldsDefinition,
                                        odooConnector)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.btnAddAnItem = None
        self.qtParent = qtParent
        self.label_name_values = False
        self.isChatterWidget = isChatterWidget
        self.odooConnector = odooConnector
        self.relation = self.fieldPyDefinition.get('relation', '')
        if odooConnector.rpc_connector.serverVersion>=17:
            self.canCreate = self.fieldXmlAttributes.get('can_create', True)
            self.canWrite = self.fieldXmlAttributes.get('can_write', True)
        else:
            self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
            self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.qtVBoxLayout = QtWidgets.QVBoxLayout()
        self.evaluatedIds = {}
        self.loaded_ids = []
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtVBoxLayout.addWidget(self.labelQtObj)
        remove_button = True
        if self.readonly:
            remove_button = False
        #: Whether its rows may be removed at all; setReadonly takes the Remove
        #: buttons away while the form is read-only and gives them back after.
        self._removeAllowed = remove_button
        if parent_view_type != 'tree':
            qHl = self.getQtObject()
            self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                                         viewName='',
                                                                         view_id=False,
                                                                         viewCheckBoxes={},
                                                                         viewFilter=False,
                                                                         remove_button=remove_button)
            self.treeViewObj.parentView = qtParent
            # The list shows the records of the field, all of them: the paging
            # arrows a search list has are not for it.
            self._hidePaging()
            # A row taken off with its Remove button is a change of the field.
            self.treeViewObj.on_rows_removed = self.valueChanged
            self.qtVBoxLayout.addWidget(self.treeViewObj)
            self.qtVBoxLayout.addLayout(qHl)
        elif parent_view_type == 'tree':
            self.label_name_values = QtWidgets.QLabel('')
            self.qtVBoxLayout.addWidget(self.label_name_values)
        
        self.qtHorizontalWidget.addLayout(self.qtVBoxLayout)

    def __str__(self)->str:
        return f"<{self.fieldName}> : {self.relation}"

    @property
    def currentValue(self):
        """The ids the field holds: the rows of its list, in their order.

        idLineRel is {row: id}. It was read as if it held an 'ids' key, which
        it never does, so the field was always empty: an item added vanished
        at once and the form saved no relation at all."""
        if self.treeViewObj:
            rows = self.treeViewObj.idLineRel
            return [rows[row] for row in sorted(rows) if rows[row]]
        return list(self.loaded_ids)

    def addIds(self, ids):
        """Add ids to the field, those it does not hold yet, and tell the form
        the field changed, so that its save writes the relation."""
        value = self.currentValue
        added = [objId for objId in ids if objId and objId not in value]
        if not added:
            return
        self.setValue(value + added)
        self.valueChanged()

    def getQtObject(self):
        qhw = QtWidgets.QHBoxLayout()
        self.createButt = QtWidgets.QPushButton('Create', self)
        self.createButt.setStyleSheet(constants.BUTTON_STYLE_X2MANY_LINK)
        self.createButt.clicked.connect(self.createAndAdd)

        self.btnAddAnItem = QtWidgets.QPushButton('Add an item', self)
        self.btnAddAnItem.setStyleSheet(constants.BUTTON_STYLE_X2MANY_LINK)
        self.btnAddAnItem.clicked.connect(self.addAnItem)
            
        qhw.addWidget(self.createButt)
        qhw.addWidget(self.btnAddAnItem)
        
        qhw.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        return qhw

    @utilsUi.rpcErrorBoundary
    def createAndAdd(self):
        def acceptFormDial():
            fieldVals = tmpviewObjForm.getAllFieldsValues()
            for requiredFieldStr, requiredFieldObj in list(tmpviewObjForm.requiredFields.items()):
                fieldVal = fieldVals.get(requiredFieldStr, '')
                if not fieldVal and not isinstance(fieldVal, (int, float)):
                    utilsUi.popError(self.qtParent, 'Field %r need a value' % (requiredFieldObj.fieldStringInterface))
                    return
            formdialog.accept()

        def rejectFormDial():
            formdialog.reject()

        try:
            tmpviewObjForm = self.odooConnector.initFormViewObj(odooObjectName=self.relation)
            tmpviewObjForm.loadIds([])
            formdialog = QtWidgets.QDialog()
            mainLay = QtWidgets.QVBoxLayout()
            mainLay.addWidget(tmpviewObjForm)
            formdialog.setStyleSheet(constants.BACKGROUND_WHITE)
            formdialog.resize(1200, 600)
            formdialog.move(100, 100)
            buttLay, okButt, cancelButt = utilsUi.getButtonBox('right')
            mainLay.addLayout(buttLay)
            formdialog.setLayout(mainLay)
            okButt.clicked.connect(acceptFormDial)
            cancelButt.clicked.connect(rejectFormDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            if formdialog.exec() == QtWidgets.QDialog.Accepted:
                fieldVals = tmpviewObjForm.getAllFieldsValues()
                objId = self.odooConnector.rpc_connector.create(self.relation, fieldVals)
                if objId:
                    self.addIds([objId])
        except OdooRpcError:
            raise           # told by rpcErrorBoundary
        except Exception as ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def setValue(self, relIds, viewType='form'):
        if self.treeViewObj:
            self.treeViewObj.loadIds(relIds, {}, {}, {})
            self.widgetQtObj = self.treeViewObj.treeObj.tableWidget
            self.fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
            # self.setRemoveButtons(self.widgetQtObj)
            self.setupTableWidgetLay(self.widgetQtObj)
            self._hidePaging()
            if self.required:
                utilsUi.setRequiredBackground(self.widgetQtObj, '')
        elif self.label_name_values:
            self.loaded_ids = relIds
            str_to_display = ''
            for box_vals in self.odooConnector.rpc_connector.read(self.relation, ['display_name'], relIds):
                str_to_display += '%s | ' % (box_vals.get('display_name', ''))
            if str_to_display.endswith(' | '):
                str_to_display = str_to_display[:-2]
            self.label_name_values.setText(str_to_display)

    def setupTableWidgetLay(self, tableWidget):
        tableWidget.resizeColumnsToContents()
        tableWidget.setShowGrid(False)
        tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

    def setRemoveButtons(self, tableWidget):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtWidgets.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

    def getOrderedFieldsStrings(self, orderedFields, fieldsDict):
        labelsOrdered = []
        for fieldName in orderedFields:
            fieldObj = fieldsDict.get(fieldName, None)
            if fieldObj:
                labelsOrdered.append(fieldObj.fieldStringInterface)
            else:
                labelsOrdered.append(fieldName)
        labelsOrdered.append('')
        return labelsOrdered

    def convertDictToLists(self, readRes, orderedFields, checkBox=False):
        values = []
        flags = {}
        for recordDict in readRes:
            recordValList = []
            for fieldName in orderedFields:
                val = recordDict.get(fieldName)
                if isinstance(val, (list, tuple)):
                    if len(val) < 1:
                        val = ''
                    val = val[1]
                recordValList.append(str(val))
            recordValList.append('')
            values.append(recordValList)
        if checkBox:
            flags[0] = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return values, flags

    @utilsUi.rpcErrorBoundary
    def addAnItem(self):
        def acceptDial():
            dial.accept()

        def rejectDial():
            dial.reject()

        def commonMove():
            currRange = viewObj.currentRange
            currRangeTuple = tuple(currRange)
            if currRangeTuple not in list(self.evaluatedIds.keys()):
                resIds = self.odooConnector.rpc_connector.search(self.relation, [], limit=viewObj.passRange, offset=currRange[-1])
                self.evaluatedIds[currRangeTuple] = resIds
            else:
                resIds = self.evaluatedIds[currRangeTuple]
            viewObj.treeObj.tableWidget.clear()
            viewObj.loadIds(resIds, {}, {}, {})

        def toLeft():
            commonMove()

        def toRight():
            commonMove()

        #raise Exception('To be moved in list view with a flag')
        viewObj = self.odooConnector.initTreeListViewObject(self.relation,
                                                            viewCheckBoxes={0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled})
        viewObj.buttToLeft.clicked.connect(toLeft)
        viewObj.buttToRight.clicked.connect(toRight)
        resIds = self.odooConnector.rpc_connector.search(self.relation, [], limit=viewObj.currentRange[-1], offset=viewObj.currentRange[0])
        viewObj.loadIds(resIds, {}, {}, {})
        dial = QtWidgets.QDialog()
        vlay = QtWidgets.QVBoxLayout()
        utilsUi.setLayoutMarginAndSpacing(vlay)
        layButt, okButt, cancelButt = utilsUi.getButtonBox('right')
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        okButt.clicked.connect(acceptDial)
        cancelButt.clicked.connect(rejectDial)
        vlay.addWidget(viewObj)
        vlay.addLayout(layButt)
        dial.setLayout(vlay)
        dial.setStyleSheet(constants.VIOLET_BACKGROUND)
        dial.resize(800, 500)
        # The rows ticked, else the rows selected (Ctrl / Shift for several);
        # a double click takes its row at once.
        viewObj.treeObj.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        doubleClicked = []

        def takeRow(objId):
            doubleClicked.append(objId)
            dial.accept()
        viewObj.doubleClickCallback = takeRow
        if dial.exec() == QtWidgets.QDialog.Accepted:
            self.addIds(self._pickedIds(viewObj, doubleClicked))

    def _pickedIds(self, viewObj, extraIds=()):
        """The ids picked in the "Add an item" list, in the order of its
        rows: ticked or selected, and extraIds (the row double-clicked)."""
        picked = set(viewObj.getSelectedIds()) | set(extraIds)
        rows = viewObj.idLineRel
        return [rows[row] for row in sorted(rows) if rows[row] in picked]

    def valueChanged(self):
        self.valueTemplateChanged()

    def _hidePaging(self):
        if self.treeViewObj:
            self.treeViewObj.buttToLeft.setHidden(True)
            self.treeViewObj.buttToRight.setHidden(True)

    def setReadonly(self, val=False):
        if self.treeViewObj:
            removable = self._removeAllowed and not val
            if self.treeViewObj.remove_button != removable:
                # The rows drawn again with or without their Remove button.
                ids = self.currentValue
                self.treeViewObj.remove_button = removable
                self.setValue(ids)
        if self.btnAddAnItem:
            self.btnAddAnItem.setDisabled(val)
        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(val)
        if self.treeViewObj:
            self.treeViewObj.treeObj.tableWidget.setDisabled(val)
            self.treeViewObj.buttToLeft.setDisabled(val)
            self.treeViewObj.buttToRight.setDisabled(val)
            if self.treeViewObj.treeObj.widgetContents:
                self.treeViewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        if self.isChatterWidget:
            return
        if self.btnAddAnItem:
            if val:
                self.btnAddAnItem.hide()
            else:
                self.btnAddAnItem.show()
        if self.widgetQtObj:
            self.widgetQtObj.setHidden(val)
        if self.treeViewObj:
            self._hidePaging()
            self.treeViewObj.treeObj.tableWidget.setHidden(val)
            #self.treeViewObj.treeObj.widgetContents.setHidden(val)
        if self.label_name_values:
            self.label_name_values.setHidden(val)
        self.labelQtObj.setHidden(val)
        if val:
            self.createButt.hide()
        else:
            self.createButt.show()
        super(Many2many, self).setInvisible(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        if self.label_name_values:
            return self.label_name_values.text()
        return self.currentValue

    def eraseValue(self):
        self.setValue([])
