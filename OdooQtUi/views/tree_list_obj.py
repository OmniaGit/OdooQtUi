'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from PySide2 import QtWidgets
from .parser.tree_list import TreeViewList
from .templateView import TemplateView
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from PySide2 import QtCore
from functools import partial
from OdooQtUi.utils_odoo_conn.utils import logWarning, logError


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
        self.passRange = 40
        self.remove_button = remove_button
        self._initViewObj()

    def _initViewObj(self):
        mainLay = QtWidgets.QVBoxLayout()
        mainLay.setSpacing(0)
        mainLay.setMargin(0)
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

    def filterChanged(self, newFilter):
        
        if self.deafult_filter:
            newFilter.extend(self.deafult_filter)
        objIds = self.odooConnector.rpc_connector.search(self.model, newFilter, limit=self.passRange, offset=0)
        self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)
        self._loadIds(objIds)

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
        self.idValsRel[recordID] = self.idValsRel[recordID].update(valuesDict)

    @utils.timeit
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        self.treeObj.tableWidget.clearContents()
        self.treeObj.tableWidget.setRowCount(0)
        self.row_widgets = {}
        self.idValsRel = {}
        self.idLineRel = {}
        if not objIds:
            return
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    @utils.timeit
    def loadForceEmptyIds(self, forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        searchFilter = []
        if self.deafult_filter:
            searchFilter = self.deafult_filter
        objIds = self.odooConnector.rpc_connector.search(self.model, searchFilter, self.passRange)  # to check with many records if 40 stop will work, 40)
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    @utils.timeit
    def _loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        self.labelsOrdered = self.treeObj.orderedFields
        if len(objIds) < self.passRange:
            self.buttToRight.setHidden(True)
        else:
            self.buttToRight.setHidden(False)
        objIds.sort()
        records = self.odooConnector.rpc_connector.read(self.model, self.labelsOrdered, objIds)
        flagsDict = {}
        fieldDict = {}
        valuesList = []
        headers = []
        self.row_widgets = {}
        if self.viewCheckBoxes:
            flagsDict = self.viewCheckBoxes
        for row_index, record in enumerate(records):
            if row_index not in self.row_widgets:
                self.row_widgets[row_index] = {}
            if row_index not in fieldDict:
                fieldDict[row_index] = {}
            localList = []
            for col_index, fieldName in enumerate(self.labelsOrdered):
                fieldPyDefinition = self.fieldsNameTypeRel.get(fieldName, {})
                val = record.get(fieldName, '')
                xml_obj = self.treeObj.widgets_to_add_in_line[col_index]
                if row_index == 0:
                    readonly = fieldPyDefinition.get('readonly', xml_obj.attrib.get('readonly', False))
                    readonly = utils.evaluateBoolean(readonly)
                    required = fieldPyDefinition.get('required', xml_obj.attrib.get('required', False))
                    required = utils.evaluateBoolean(required)
                    invisible = fieldPyDefinition.get('invisible', xml_obj.attrib.get('invisible', False))
                    invisible = utils.evaluateBoolean(invisible)
                    headers.append(fieldPyDefinition.get('string', fieldName))
                    self.treeObj.tableWidget.setColumnHidden(col_index, invisible)
                if xml_obj.tag == 'field':
                    if self.fieldsNameTypeRel.get(fieldName, {}).get('type')=='many2one':
                        tmp_val = record.get(fieldName, '')
                        if isinstance(tmp_val, (list,tuple)):
                            val=tmp_val[1]
                        else:
                            val=tmp_val
                    localList.append(val)
                else:
                    if row_index == 0:
                        headers.append('')
                    widget = self.treeObj.computeWidget(xml_obj)
                    widget.record = record
                    self.row_widgets[row_index][col_index] = widget
                    localList.append(widget)
            valuesList.append(localList)
            recordId = record.get('id', False)
            self.idValsRel[recordId] = record
            self.idLineRel[records.index(record)] = recordId
        if self.remove_button:
            headers.append('')
        utilsUi.commonPopulateTable(headers, valuesList, self.treeObj.tableWidget, flagsDict, fontSize=constants.FONT_SIZE_LIST_WIDGET)
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

    def doubleClickEvent(self, *args):
        try:
            model_index = args[0]
            row_index = model_index.row()
            obj_id = self.idLineRel.get(row_index, False)
            viewObj = self.odooConnector.initFormViewObj(self.model)
            viewObj.loadIds([obj_id])
            dialog = QtWidgets.QDialog()
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
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                valuesToUpdate = {}
                for fieldName, fieldObj in list(viewObj.fieldsChanged.items()):
                    valuesToUpdate[fieldName] = fieldObj.value
                self.odooConnector.rpc_connector.write(self.model, valuesToUpdate, obj_id)
        except Exception as ex:
            logError(ex)

    def _setFieldsModifiers(self, fieldDict):
        for _row_index, row_vals in fieldDict.items():
            for fieldName, widget in row_vals.items():
                try:
                    inv = utils.evaluateAttrs(row_vals, widget.invisible)
                    col_index = self.labelsOrdered.index(fieldName)
                    self.treeObj.tableWidget.setColumnHidden(col_index, inv)
                    ronly = utils.evaluateAttrs(row_vals, widget.readonly)
                    widget.setReadonly(ronly)
                except Exception as ex:
                    logWarning('Cannot set readonly and invisible attributes for field %r err %r' % (fieldName, ex), '_setFieldsModifiers')

    def _setButtonsModifiers(self, fieldDict):
        
        def hideButtonWithStyle(butt, flag):
            if butt:
                if flag:
                    butt.setStyleSheet('color:#dddddd; border:none;background-color:#dddddd;')
                else:
                    butt.setStyleSheet(constants.BUTTON_STYLE_REVERSED)
                butt.setDisabled(flag)

        for row_index, row_vals in self.row_widgets.items():
            for widget in row_vals.values():
                if widget.modifiers:
                    readonlyModif = widget.modifiers.get('readonly', {})
                    invisibleModif = widget.modifiers.get('invisible', {})
                    if readonlyModif:
                        val = utils.evaluateAttrs(fieldDict.get(row_index, {}), readonlyModif)
                        widget.setReadonly(val)
                    if invisibleModif:
                        val = utils.evaluateAttrs(fieldDict.get(row_index, {}), invisibleModif)
                        hideButtonWithStyle(widget, val)
                    if widget.readonly:
                        widget.setReadonly(True)
                    if widget.invisible:
                        hideButtonWithStyle(widget, val)

    def setRemoveButtons(self):
        rowCount = self.treeObj.tableWidget.rowCount()
        colCount = self.treeObj.tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtWidgets.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            self.treeObj.tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

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

    def switchToRight(self):
        _start, to = self.currentRange
        self.currentRange = [to, to + self.passRange]
        self.buttToLeft.setHidden(False)
        objIds = self.odooConnector.rpc_connector.search(self.model, self.deafult_filter, limit=self.passRange, offset=self.currentRange[0])
        if objIds:
            self.loadIds(objIds)
        else:
            self.buttToRight.setHidden(True)

    def switchToLeft(self):
        start, _to = self.currentRange
        self.currentRange = [start - self.passRange, start]
        if self.currentRange[0] <= 0:
            self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)
        objIds = self.odooConnector.rpc_connector.search(self.model, self.deafult_filter, limit=self.passRange, offset=self.currentRange[0])
        self.loadIds(objIds)

    def sortResults(self, fieldName='', filterMode='DESC'):
        utils.logMessage('warning', 'Sorting not implemented in tree list view', 'sortResults')

    def getSelectedIds(self):
        outIds = []
        selectedIndexes = self.treeObj.tableWidget.selectedItems()
        for index in selectedIndexes:
            outIds.append(self.idLineRel[index.row()])
        if not selectedIndexes:
            for rowIndex in range(self.treeObj.tableWidget.rowCount()):
                item = self.treeObj.tableWidget.item(rowIndex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    idd = self.idLineRel.get(rowIndex, False)
                    if idd:
                        outIds.append(idd)
        return list(set(outIds))
        