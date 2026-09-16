# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import base64

from PySide6 import QtWidgets, QtCore, QtGui
from .parser.tree_list import TreeViewList
from .templateView import TemplateView
from OdooQtUi.RPC.errors import OdooRpcError
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from functools import partial
from OdooQtUi.utils_odoo_conn.utils import logWarning, logError


class RowSelectionDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(RowSelectionDelegate, self).__init__(parent)
        self.hoveredRow = -1
        if parent is not None:
            parent.setMouseTracking(True)
            parent.viewport().setMouseTracking(True)
            parent.viewport().installEventFilter(self)

    def eventFilter(self, watched, event):
        view = self.parent()
        if view is not None:
            if event.type() == QtCore.QEvent.MouseMove:
                newRow = view.indexAt(event.pos()).row()
                if newRow != self.hoveredRow:
                    self.hoveredRow = newRow
                    view.viewport().update()
            elif event.type() == QtCore.QEvent.Leave:
                if self.hoveredRow != -1:
                    self.hoveredRow = -1
                    view.viewport().update()
        return super(RowSelectionDelegate, self).eventFilter(watched, event)

    def paint(self, painter, option, index):
        try:
            # Remove focus rectangle
            option.state &= ~QtWidgets.QStyle.State_HasFocus
            if option.state & QtWidgets.QStyle.State_Selected:
                # Subtle gray selection highlight, matching the toolbar's gray theme
                painter.save()
                bg_color = QtGui.QColor("#e4e4e6")
                painter.fillRect(option.rect, bg_color)
                painter.restore()

                # Draw contents without default selection styling
                option.state &= ~QtWidgets.QStyle.State_Selected
                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
                option.state |= QtWidgets.QStyle.State_Selected
            elif index.row() == self.hoveredRow:
                # Light hover highlight across the whole row, cleared the instant
                # the mouse leaves it (tracked via eventFilter above)
                painter.save()
                painter.fillRect(option.rect, QtGui.QColor("#909090"))
                painter.restore()
                option.state &= ~QtWidgets.QStyle.State_MouseOver
                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
            else:
                QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)
        except Exception as ex:
            QtWidgets.QStyledItemDelegate.paint(self, painter, option, index)




class TemplateTreeListView(TemplateView):
    """
    this class is a widget for managing the tree list view
    """
    def __init__(self,
                 viewObj,
                 searchObj=None,
                 odooConnector=None,
                 deafult_filter=[],
                 remove_button=False):
        super(TemplateTreeListView, self).__init__(odooConnector=odooConnector,
                                                   viewObj=viewObj)
        self.readonly = True
        self.activeIds = []
        self.idValsRel = {}
        self.idLineRel = {}
        self.row_widgets = {}
        self.searchObj = searchObj
        self.labelsOrdered = []
        self.deafult_filter = deafult_filter
        self.currentRange = [0, 40]
        #: The domain the user searched with, kept so the paging buttons search
        #: the same thing. None means nothing was searched and the default
        #: filter applies.
        self.currentFilter = None
        #: {(record id, field): base64} -- an image drawn once is not read again,
        #: and scrolling back up costs nothing.
        self._imageCache = {}
        self._image_rows_connected = False
        self.passRange = 40
        self.remove_button = remove_button
        # The form around the list, when the list is a one2many or a many2many
        # of it: what `parent.<field>` reads in a column expression.
        self.parentView = None
        self._initViewObj()

    def _initViewObj(self):
        mainLay = QtWidgets.QVBoxLayout()
        mainLay.setSpacing(0)
        mainLay.setContentsMargins(0, 0, 0, 0)
        mainLay.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        # Add arrow buttons
        recordSwitcher = self._setupArrowButtons()
        if self.viewFilter:
            if not self.searchObj:
                utils.logMessage('warning', 'You have requested to view search view for this object but search view has not been passed!', '_initViewObj')
            else:
                self.searchObj.out_filter_change_signal.connect(self.filterChanged)
                recordSwitcher.insertWidget(0, self.searchObj)

        mainLay.addLayout(recordSwitcher)
        self.treeObj = TreeViewList(qtParent=self,
                                    arch=self.arch,
                                    fieldsNameTypeRel=self.fieldsNameTypeRel,
                                    viewCheckBoxes=self.viewCheckBoxes,
                                    odooConnector=self.odooConnector)
        self.treeObj.computeArch()
        mainLay.addWidget(self.treeObj)
        self.mappingInterface = self.treeObj.globalMapping
        self.addToObject()
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.setAlternatingRowColors(True)
            self.treeObj.tableWidget.setStyleSheet(constants.TABLE_LIST_LIST)
            self.treeObj.tableWidget.horizontalHeader().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
            self.treeObj.tableWidget.setMinimumHeight(200)
            self.treeObj.tableWidget.setMouseTracking(True)
            self.treeObj.tableWidget.setItemDelegate(RowSelectionDelegate(self.treeObj.tableWidget))
        self.setLayout(mainLay)
        self.treeObj.tableWidget.doubleClicked.connect(self.doubleClickEvent)
        self.setStyleSheet(constants.BACKGROUND_WHITE)

    def _setupArrowButtons(self):
        self.currentRange = [0, 40]
        switchRecordsLay = QtWidgets.QHBoxLayout()
        switchRecordsLay.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.buttToLeft = QtWidgets.QPushButton('<')
        self.buttToRight = QtWidgets.QPushButton('>')
        spacer = QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        switchRecordsLay.addSpacerItem(spacer)
        switchRecordsLay.addWidget(self.buttToLeft)
        switchRecordsLay.addWidget(self.buttToRight)
        self.buttToLeft.setStyleSheet(constants.BUTTON_STYLE)
        self.buttToRight.setStyleSheet(constants.BUTTON_STYLE)
        self.buttToLeft.clicked.connect(self.switchToLeft)
        self.buttToRight.clicked.connect(self.switchToRight)
        self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(True)
        return switchRecordsLay

    @utilsUi.rpcErrorBoundary
    def filterChanged(self, newFilter):
        """The user searched: back to the first page, and remember what was asked.

        Both were bugs until 2026-09-16. The range was left where paging had put
        it, so a search made after paging showed its second or third page as if
        it were the first; and the domain was forgotten as soon as it had been
        used, so the paging buttons below searched the default filter instead --
        the user typed a code, paged once, and got the whole table back.
        """
        if self.deafult_filter:
            newFilter.extend(self.deafult_filter)
        self.currentFilter = newFilter
        self.currentRange = [0, self.passRange]
        objIds = self.odooConnector.rpc_connector.search(self.model, newFilter, limit=self.passRange, offset=0)
        self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)
        self._loadIds(objIds)

    def pagingFilter(self):
        """What the paging buttons search: the user's own domain when there is
        one, the default filter otherwise."""
        if self.currentFilter is None:
            return self.deafult_filter
        return self.currentFilter

    def forceRecordVals(self, recordID, valuesDict={}):
        if not valuesDict:
            return
        if recordID not in self.idValsRel:
            utils.logMessage('warning', 'Record with ID %r not found in rel dict %r' % (recordID, self.idValsRel), 'forceRecordVals')
            return
        for fieldName in valuesDict:
            fieldObj = self.interfaceFieldsDict.get(fieldName, None)
            if not fieldObj:
                utils.logMessage('warning', 'Field object %r not found in fields' % (fieldName), 'forceRecordVals')
                return
            fieldObj.setValue(valuesDict.get(fieldName))
        self.idValsRel[recordID] = self.idValsRel[recordID].update(valuesDict.copy())

    @utils.timeit
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        self.treeObj.tableWidget.clearContents()
        self.treeObj.tableWidget.setRowCount(0)
        self.row_widgets = {}
        self.idValsRel = {}
        self.idLineRel = {}
        if not objIds:
            if self.odooConnector.rpc_connector.serverVersion >= 17:
                # No rows, and the columns still the ones Odoo would show.
                headers, hidden = self._columnRules()
                self.treeObj.tableWidget.setColumnCount(len(headers))
                self.treeObj.tableWidget.setHorizontalHeaderLabels(headers)
                for col_index, is_hidden in hidden.items():
                    self.treeObj.tableWidget.setColumnHidden(col_index, is_hidden)
            return
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    @utils.timeit
    def loadForceEmptyIds(self, forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        searchFilter = []
        if self.deafult_filter:
            searchFilter = self.deafult_filter
        self.currentFilter = None
        self.currentRange = [0, self.passRange]
        objIds = self.odooConnector.rpc_connector.search(self.model, searchFilter, self.passRange)  # to check with many records if 40 stop will work, 40)
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    #: Field types that do not belong in the first read: the value is base64,
    #: it is big, and until 2026-09-16 it went into the cell as text, where it
    #: rendered as nothing at all -- a page of 40 products with `image_1920` was
    #: 325 KB against 14 KB without it. A column the view marks `widget="image"`
    #: is drawn now, but afterwards and only for the rows on screen.
    BINARY_TYPES = ('binary', 'image')

    #: The size an image column is drawn at, and the sibling field preferred for
    #: it: reading `image_1920` to show 60 pixels is 39 KB a row against 10.
    IMAGE_CELL_SIZE = 60
    SMALL_IMAGE_FIELDS = ('image_128', 'image_256')

    def _fieldsToRead(self):
        """The columns of the view, minus the ones the first read does not carry."""
        wanted = []
        for fieldName in self.labelsOrdered:
            definition = self.fieldsNameTypeRel.get(fieldName, {})
            if definition.get('type') in self.BINARY_TYPES:
                continue
            wanted.append(fieldName)
        return wanted

    def _imageColumns(self):
        """{column index: field to read} for the columns drawn as a picture.

        A column counts when the view asked for `widget="image"`, which is what
        Odoo's own list does. The field read is not always the one named: an
        image field of Odoo comes in sizes, and a 60 pixel cell is served by
        `image_128` -- 10 KB a row instead of 39.
        """
        columns = {}
        for col_index, fieldName in enumerate(self.labelsOrdered):
            element = self.treeObj.widgets_to_add_in_line.get(col_index)
            if element is None or element.tag != 'field':
                continue
            if element.attrib.get('widget') != 'image':
                continue
            columns[col_index] = self._imageFieldFor(fieldName)
        return columns

    def _imageFieldFor(self, fieldName):
        """The smallest sibling of an image field this model has, or the field."""
        if not fieldName.startswith('image_'):
            return fieldName
        for candidate in self.SMALL_IMAGE_FIELDS:
            if candidate in self.fieldsNameTypeRel:
                return candidate
        return fieldName

    @utils.timeit
    def _loadIds(self,
                 objIds=[],
                 forceFieldValues={},
                 readonlyFields={},
                 invisibleFields={}):
        """
        Load the ids passed reading it's values from odoo

        :objIds list of ids to load [<id1>,<id2>,...]
        :forceFieldValues
        :readonlyFields
        :invisibleFields
        """
        self.labelsOrdered = self.treeObj.orderedFields
        if len(objIds) < self.passRange:
            self.buttToRight.setHidden(True)
        else:
            self.buttToRight.setHidden(False)
        objIds.sort()
        records = self.odooConnector.rpc_connector.read(self.model,
                                                        self._fieldsToRead(),
                                                        objIds) or []
        flagsDict = {}
        fieldDict = {}
        valuesList = []
        headers = []
        self.row_widgets = {}
        if self.viewCheckBoxes:
            flagsDict = self.viewCheckBoxes
        hidden_columns = {}
        # From Odoo 17 a list tells a column from a cell: `column_invisible`
        # hides the column, `invisible` hides the value in one row and is an
        # expression over that row. Up to 16 the rules below, as they were.
        modern = self.odooConnector.rpc_connector.serverVersion >= 17
        if modern:
            headers, hidden_columns = self._columnRules()
            rowContext = dict(self.odooConnector.rpc_connector.contextUser)
        for row_index, record in enumerate(records):
            if row_index not in self.row_widgets:
                self.row_widgets[row_index] = {}
            fieldDict[row_index] = record
            localList = []
            rowValues = utils.recordValues({}, record) if modern else {}
            for col_index, fieldName in enumerate(self.labelsOrdered):
                fieldPyDefinition = self.fieldsNameTypeRel.get(fieldName, {})
                val = record.get(fieldName, '')
                xml_obj = self.treeObj.widgets_to_add_in_line[col_index]
                if modern:
                    cellInvisible = xml_obj.attrib.get('invisible')
                    if not utils.isConstantModifier(cellInvisible) \
                            and utils.evaluateExpression(cellInvisible, rowValues, rowContext):
                        localList.append('')
                        continue
                elif row_index == 0:
                    client_context = dict(self.odooConnector.rpc_connector.contextUser)
                    client_context.update(utils.evaluateContext(xml_obj.attrib.get('context', '{}'), record))
                    readonly = fieldPyDefinition.get('readonly', xml_obj.attrib.get('readonly', False))
                    readonly = utils.evaluateBoolean(readonly, context=client_context.copy())
                    required = fieldPyDefinition.get('required', xml_obj.attrib.get('required', False))
                    required = utils.evaluateBoolean(required, context=client_context.copy())
                    invisible = fieldPyDefinition.get('invisible', xml_obj.attrib.get('invisible', False))
                    invisible = utils.evaluateBoolean(invisible, context=client_context.copy())
                    if fieldName == 'is_checkout':
                        invisible = False
                    if xml_obj.tag == 'field':
                        headers.append(fieldPyDefinition.get('string', fieldName))
                    else:
                        headers.append(xml_obj.attrib.get('string', ''))
                    hidden_columns[col_index] = bool(invisible)
                if xml_obj.tag == 'field':
                    field_type = self.fieldsNameTypeRel.get(fieldName, {}).get('type')
                    if  field_type in ['many2one']:
                        tmp_val = record.get(fieldName, '')
                        if isinstance(tmp_val, (list,tuple)):
                            val=tmp_val[1]
                        else:
                            val=tmp_val
                    elif field_type in ['many2many','one2many']:
                        val=f"Record {len(val)}"
                    localList.append(val)
                else:
                    widget = self.treeObj.computeWidget(xml_obj)
                    if widget is None:
                        # A column this client does not draw: a <widget>, or a
                        # button that is not an object method. An empty cell,
                        # not the whole list refused.
                        localList.append('')
                        continue
                    widget.record = record
                    self.row_widgets[row_index][col_index] = widget
                    localList.append(widget)
            valuesList.append(localList)
            recordId = record.get('id', False)
            self.idValsRel[recordId] = record
            self.idLineRel[records.index(record)] = recordId
        if self.remove_button:
            headers.append('')
        utilsUi.commonPopulateTable(headers,
                                    valuesList,
                                    self.treeObj.tableWidget,
                                    flagsDict,
                                    fontSize=constants.FONT_SIZE_LIST_WIDGET)
        for col_index, is_hidden in hidden_columns.items():
            self.treeObj.tableWidget.setColumnHidden(col_index, is_hidden)
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.setShowGrid(False)
            self.treeObj.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.treeObj.tableWidget.horizontalHeader().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
            self.treeObj.tableWidget.verticalHeader().setVisible(False)
            self.treeObj.tableWidget.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self._setButtonsModifiers(fieldDict)
        if self.remove_button:
            self.setRemoveButtons()
        self.refreshColumns()
        self.treeObj.tableWidget.horizontalHeader().setStretchLastSection(True)
        self._loadVisibleImages()

    # -- the picture columns ---------------------------------------------------

    def _loadVisibleImages(self):
        """Draw the image columns of the rows on screen, and only those.

        The first read of a page carries no binaries: they are the bulk of it
        and the table is wanted now. The pictures follow, for what the user can
        actually see -- scrolling asks for the next ones -- and each one is kept,
        so a row drawn once is never read again.
        """
        columns = self._imageColumns()
        if not columns:
            return
        table = self.treeObj.tableWidget
        if not table:
            return
        table.setIconSize(QtCore.QSize(self.IMAGE_CELL_SIZE, self.IMAGE_CELL_SIZE))
        if not self._image_rows_connected:
            # Scrolling brings other rows into view; the ones already drawn cost
            # nothing, since _imageCache answers for them.
            table.verticalScrollBar().valueChanged.connect(self._loadVisibleImages)
            self._image_rows_connected = True
        wanted = {}
        for row_index in self._visibleRows():
            recordId = self.idLineRel.get(row_index)
            if not recordId:
                continue
            for col_index, fieldName in columns.items():
                if (recordId, fieldName) in self._imageCache:
                    self._drawImageCell(row_index, col_index, recordId, fieldName)
                else:
                    wanted.setdefault(fieldName, []).append((row_index, col_index, recordId))
        for fieldName, rows in wanted.items():
            ids = [recordId for _row, _col, recordId in rows]
            records = self.odooConnector.rpc_connector.read(self.model, [fieldName], ids) or []
            for record in records:
                self._imageCache[(record.get('id'), fieldName)] = record.get(fieldName) or ''
            for row_index, col_index, recordId in rows:
                self._drawImageCell(row_index, col_index, recordId, fieldName)

    def _visibleRows(self):
        """The rows the user can see, plus one page of margin above and below."""
        table = self.treeObj.tableWidget
        rows = table.rowCount()
        if not rows:
            return []
        first = table.rowAt(0)
        last = table.rowAt(table.viewport().height() - 1)
        if first < 0:
            first = 0
        if last < 0:
            last = rows - 1
        margin = max(1, last - first)
        return range(max(0, first - margin), min(rows, last + margin + 1))

    def _drawImageCell(self, row_index, col_index, recordId, fieldName):
        """The picture in its cell, scaled to the row, from the cache."""
        data = self._imageCache.get((recordId, fieldName))
        if not data:
            return
        item = self.treeObj.tableWidget.item(row_index, col_index)
        if item is None or not item.icon().isNull():
            return
        pixmap = QtGui.QPixmap()
        try:
            pixmap.loadFromData(base64.b64decode(data))
        except Exception as ex:
            utils.logMessage('warning', 'Image of %r: %r' % (recordId, ex), 'imageCell')
            return
        if pixmap.isNull():
            return
        item.setText('')
        item.setIcon(QtGui.QIcon(pixmap.scaled(self.IMAGE_CELL_SIZE, self.IMAGE_CELL_SIZE,
                                               QtCore.Qt.KeepAspectRatio,
                                               QtCore.Qt.SmoothTransformation)))
        if self.treeObj.tableWidget.rowHeight(row_index) < self.IMAGE_CELL_SIZE:
            self.treeObj.tableWidget.setRowHeight(row_index, self.IMAGE_CELL_SIZE + 4)

    def _columnRules(self):
        """Headers, and which columns are hidden, for Odoo 17 and later.

        A column is hidden by `column_invisible`, over the context and the
        parent record, or by `optional="hide"`, which Odoo shows only when the
        user asks for it. A constant `invisible` ("1") still hides the column:
        there is no row it could depend on.
        """
        context = dict(self.odooConnector.rpc_connector.contextUser)
        parentValues = self._parentValues()
        headers = []
        hidden = {}
        for col_index, fieldName in enumerate(self.treeObj.orderedFields):
            xml_obj = self.treeObj.widgets_to_add_in_line[col_index]
            attributes = xml_obj.attrib
            if xml_obj.tag == 'field':
                definition = self.fieldsNameTypeRel.get(fieldName, {})
                headers.append(attributes.get('string') or definition.get('string', fieldName))
            else:
                headers.append(attributes.get('string', ''))
            invisible = attributes.get('invisible')
            hidden[col_index] = attributes.get('optional') == 'hide' \
                or utils.evaluateColumnInvisible(attributes.get('column_invisible'), context, parentValues) \
                or (utils.isConstantModifier(invisible) and utils.evaluateExpression(invisible))
            if fieldName == 'is_checkout':
                hidden[col_index] = False
        return headers, hidden

    def _parentValues(self):
        parent = self.parentView
        if parent is None or not hasattr(parent, 'interfaceFieldsDict'):
            return {}
        formVals = getattr(parent, 'formVals', {})
        if getattr(parent, 'skipOnChange', False):
            # The form is still writing the record into its widgets, and the
            # ones it has not reached hold the previous record.
            return utils.recordValues({}, formVals)
        return utils.recordValues(parent.interfaceFieldsDict, formVals)

    @utilsUi.rpcErrorBoundary
    def doubleClickEvent(self, *args):
        try:
            model_index = args[0]
            row_index = model_index.row()
            obj_id = self.idLineRel.get(row_index, False)
            viewObj = self.odooConnector.initFormViewObj(self.model)
            viewObj.loadIds([obj_id])
            dialog = QtWidgets.QDialog()
            title = "Detail"
            if self.model == "ir.attachment":
                title = "Document Detail"
            elif self.model == "plm.box":
                title = "Box Detail"
            dialog.setWindowTitle(title)
            mainLay = QtWidgets.QVBoxLayout()
            utilsUi.setLayoutMarginAndSpacing(mainLay)
            scrollArea = QtWidgets.QScrollArea()
            scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
            scrollArea.setFrameShadow(QtWidgets.QFrame.Sunken)
            scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            scrollArea.setWidgetResizable(True)
            scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            scrollArea.setWidget(viewObj)
            mainLay.addWidget(scrollArea)
            lay, okButt, cancelButt = utilsUi.getButtonBox()
            okButt.clicked.connect(dialog.accept)
            cancelButt.clicked.connect(dialog.reject)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            lay.setParent(None)
            mainLay.addLayout(lay)
            dialog.setLayout(mainLay)
            dialog.setStyleSheet(constants.BACKGROUND_WHITE)
            dialog.adjustSize()
            dialog.resize(1000, 750)
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                valuesToUpdate = {}
                for fieldName, fieldObj in list(viewObj.fieldsChanged.items()):
                    valuesToUpdate[fieldName] = fieldObj.value
                self.odooConnector.rpc_connector.write(self.model, valuesToUpdate, obj_id)
        except OdooRpcError:
            raise           # told by rpcErrorBoundary
        except Exception as ex:
            logError(ex)

    def _setFieldsModifiers(self, fieldDict):
        for _row_index, row_vals in fieldDict.items():
            for fieldName, fieldObj in row_vals.items():
                try:
                    client_context = dict(self.odooConnector.rpc_connector.contextUser)
                    client_context.update(utils.evaluateContext(fieldObj.context, fieldDict))
                    inv = utils.evaluateAttrs(row_vals, fieldObj.invisible, client_context)
                    col_index = self.labelsOrdered.index(fieldName)
                    self.treeObj.tableWidget.setColumnHidden(col_index, bool(inv))
                    ronly = utils.evaluateAttrs(row_vals, fieldObj.readonly, client_context)
                    widget.setReadonly(ronly)
                except Exception as ex:
                    logWarning('Cannot set readonly and invisible attributes for field %r err %r' % (fieldName, ex), '_setFieldsModifiers')

    def _setButtonsModifiers(self, fieldDict):

        def hideButtonWithStyle(butt, flag):
            if butt:
                btn_text = str(butt.text()).strip()
                record = getattr(butt, 'record', {}) or {}
                is_checkout = record.get('is_checkout', False)
                if "out" in btn_text.lower():
                    # Left half of the capsule:
                    if is_checkout:
                        butt.setStyleSheet('background-color: #c0392b; color: #ffffff; border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; padding: 4px 10px; font-weight: bold; border: none; margin: 1px 0px 1px 4px; min-width: 75px;')
                    else:
                        butt.setStyleSheet('background-color: #333333; color: #ffffff; border-top-left-radius: 10px; border-bottom-left-radius: 10px; border-top-right-radius: 0px; border-bottom-right-radius: 0px; padding: 4px 10px; font-weight: bold; border: none; margin: 1px 0px 1px 4px; min-width: 75px;')
                    butt.setDisabled(False)
                elif "in" in btn_text.lower():
                    # Right half of the capsule (light gray background):
                    butt.setStyleSheet('QPushButton { background-color: #d1d5db; color: #333333; border-top-left-radius: 0px; border-bottom-left-radius: 0px; border-top-right-radius: 10px; border-bottom-right-radius: 10px; padding: 4px 10px; font-weight: bold; border: none; margin: 1px 1px 1px 0px; min-width: 75px; } QPushButton:disabled { background-color: #d1d5db; color: #666666; }')
                    butt.setDisabled(False)
                else:
                    if flag:
                        butt.setStyleSheet('background-color: #e5e7eb; color: #9ca3af; border: none; border-radius: 10px; padding: 4px 10px; font-weight: bold;')
                    else:
                        butt.setStyleSheet(constants.BUTTON_STYLE_REVERSED)
                    butt.setDisabled(flag)

        for row_index, row_vals in self.row_widgets.items():
            for fieldObj in row_vals.values():
                # Apply capsule style unconditionally first if it is a button
                if isinstance(fieldObj, QtWidgets.QPushButton) or getattr(fieldObj, 'butt_type', None):
                    hideButtonWithStyle(fieldObj, False)
                if fieldObj.modifiers:
                    readonlyModif = fieldObj.modifiers.get('readonly', {})
                    invisibleModif = fieldObj.modifiers.get('invisible', {})
                    client_context = dict(self.odooConnector.rpc_connector.contextUser)
                    client_context.update(utils.evaluateContext(fieldObj.context, fieldDict))
                    if readonlyModif:
                        val = utils.evaluateAttrs(fieldDict.get(row_index, {}), readonlyModif, client_context)
                        fieldObj.setReadonly(val)
                    if invisibleModif:
                        val = utils.evaluateAttrs(fieldDict.get(row_index, {}), invisibleModif, client_context)
                        hideButtonWithStyle(fieldObj, val)
                    if fieldObj.readonly:
                        fieldObj.setReadonly(True)
                    if fieldObj.invisible:
                        hideButtonWithStyle(fieldObj, val)

    def setRemoveButtons(self):
        rowCount = self.treeObj.tableWidget.rowCount()
        colCount = self.treeObj.tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtWidgets.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            self.treeObj.tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

    @utilsUi.rpcErrorBoundary
    def removeItem(self, rowIndex):
        found = False
        rowIndexes = list(self.idLineRel.keys())
        for rowInd in rowIndexes:
            objId = self.idLineRel[rowInd]
            if rowInd == rowIndex:
                utils.removeRowFromTableWidget(self.treeObj.tableWidget, rowIndex)
                self.setRemoveButtons()
                del self.idLineRel[rowInd]
                found = True
            elif found:
                del self.idLineRel[rowInd]
                self.idLineRel[rowInd - 1] = objId

    def refreshColumns(self):
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.resizeColumnsToContents()
            self.treeObj.tableWidget.setColumnWidth(0, 92)
            self.treeObj.tableWidget.setColumnWidth(1, 82)
            self.treeObj.tableWidget.horizontalHeader().setStretchLastSection(True)

    def setRowSelected(self, rowIndex):
        self.treeObj.tableWidget.selectRow(rowIndex)

    def setColumnSelected(self, colIndex):
        self.treeObj.tableWidget.selectColumn()

    def clearSelection(self):
        self.treeObj.tableWidget.clearSelection()

    def setAllItemsSelected(self):
        self.treeObj.tableWidget.selectAll()

    def getLineValues(self, lineIndex):
        recordId = self.idLineRel[lineIndex]
        recordObj = self.idValsRel.get(recordId, {})
        return recordObj

    def _valueChanged(self, fieldName):
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        self.fieldsChanged[fieldName] = fieldObj

    @utilsUi.rpcErrorBoundary
    def switchToRight(self):
        _start, to = self.currentRange
        self.currentRange = [to, to + self.passRange]
        self.buttToLeft.setHidden(False)
        objIds = self.odooConnector.rpc_connector.search(self.model, self.pagingFilter(), limit=self.passRange, offset=self.currentRange[0])
        if objIds:
            self.loadIds(objIds)
        else:
            self.buttToRight.setHidden(True)

    @utilsUi.rpcErrorBoundary
    def switchToLeft(self):
        start, _to = self.currentRange
        self.currentRange = [start - self.passRange, start]
        if self.currentRange[0] <= 0:
            self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)
        objIds = self.odooConnector.rpc_connector.search(self.model, self.pagingFilter(), limit=self.passRange, offset=self.currentRange[0])
        self.loadIds(objIds)

    def sortResults(self, fieldName='', filterMode='DESC'):
        utils.logMessage('warning', 'Sorting not implemented in tree list view', 'sortResults')

    def getSelectedIds(self):
        outIds = []
        if self.viewCheckBoxes:
            for rowIndex in range(self.treeObj.tableWidget.rowCount()):
                item = self.treeObj.tableWidget.item(rowIndex, 0)
                if item and item.checkState() == QtCore.Qt.Checked:
                    idd = self.idLineRel.get(rowIndex, False)
                    if idd:
                        outIds.append(idd)
        if not outIds:
            selectedIndexes = self.treeObj.tableWidget.selectedItems()
            for index in selectedIndexes:
                outIds.append(self.idLineRel[index.row()])
        return list(set(outIds))
        