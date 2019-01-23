'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from PySide2 import QtGui
from PySide2 import QtWidgets
from .parser.tree_list import TreeViewList
from .templateView import TemplateView
from OdooQtUi.views.search_obj import TemplateSearchView
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.RPC.rpc import connectionObj


class TemplateTreeListView(TemplateView):

    def __init__(self, rpcObject, viewObj, activeLanguageCode='en_US', searchObj=None, odooConnector=None, deafult_filter=[]):
        super(TemplateTreeListView, self).__init__(rpcObject, viewObj, activeLanguageCode)
        self.readonly = True
        self.activeIds = []
        self.idValsRel = {}
        self.idLineRel = {}
        self.odooConnector = odooConnector
        self.searchObj = searchObj
        self.labelsOrdered = []
        self.deafult_filter = deafult_filter
        self.currentRange = [0, 40]
        self.passRange = 40
        self._initViewObj()

    def _initViewObj(self):
        mainLay = QtWidgets.QVBoxLayout()
        # Add arrow buttons
        switchRecordsLay = self._setupArrowButtons()
        mainLay.addLayout(switchRecordsLay, 0)
        if self.viewFilter:
            if not self.searchObj:
                utils.logMessage('warning', 'You have requested to view search view for this object but search view has not been passed!', '_initViewObj')
            else:
                self.searchObj.out_filter_change_signal.connect(self.filterChanged)
                mainLay.addWidget(self.searchObj)
        self.treeObj = TreeViewList(self, self.arch, self.fieldsNameTypeRel, self.rpcObject, self.viewCheckBoxes, self.odooConnector)
        self.treeObj.computeArch()
        mainLay.addWidget(self.treeObj)
        self.mappingInterface = self.treeObj.globalMapping
        self.addToObject()
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.setStyleSheet(constants.TABLE_LIST_LIST)
            self.treeObj.tableWidget.setMinimumHeight(200)
        self.setLayout(mainLay)

    def _setupArrowButtons(self):
        self.currentRange = [0, 40]
        switchRecordsLay = QtWidgets.QHBoxLayout()
        self.buttToLeft = QtWidgets.QPushButton('<')
        self.buttToRight = QtWidgets.QPushButton('>')
        switchRecordsLay.addSpacerItem(QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
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
        objIds = connectionObj.search(self.model, newFilter, limit=self.passRange, offset=self.currentRange[0])
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
        if not objIds:
            return
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    @utils.timeit
    def loadForceEmptyIds(self, forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        searchFilter = []
        if self.deafult_filter:
            searchFilter = self.deafult_filter
        objIds = connectionObj.search(self.model, searchFilter, self.passRange)  # to check with many records if 40 stop will work, 40)
        return self._loadIds(objIds, forceFieldValues, readonlyFields, invisibleFields)

    @utils.timeit
    def _loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        fields = self.treeObj.orderedFields
        if len(objIds) < self.passRange:
            self.buttToRight.setHidden(True)
        else:
            self.buttToRight.setHidden(False)
        records = self.rpcObject.read(self.model, fields, objIds)
        flagsDict = {}
        valuesList = []
        self.labelsOrdered = []
        fieldsToRemove = []
        for fieldName in fields:
            fieldObj = self.interfaceFieldsDict.get(fieldName, None)
            if fieldObj:
                if fieldObj.fieldType in ['many2many', 'one2many']:
                    fieldsToRemove.append(fieldName)
                    continue
                self.labelsOrdered.append(fieldObj.fieldStringInterface)
            else:
                self.labelsOrdered.append(fieldName)
        fields = [item for item in fields if item not in fieldsToRemove]
        if self.viewCheckBoxes:
            flagsDict = self.viewCheckBoxes
        for record in records:
            localList = []
            for fieldName in fields:
                val = record.get(fieldName, '')
                fieldObj = self.interfaceFieldsDict.get(fieldName, None)
                fieldObj.setValue(val)
                record[fieldName] = fieldObj.currentValue
                if fieldObj.fieldType == 'many2one':
                    if isinstance(val, bool):
                        val = ''
                    else:
                        val = val[1]
                localList.append(str(fieldObj.valueInterface))
            valuesList.append(localList)
            recordId = record.get('id', False)
            self.idValsRel[recordId] = record
            self.idLineRel[records.index(record)] = recordId
        utilsUi.commonPopulateTable(self.labelsOrdered, valuesList, self.treeObj.tableWidget, flagsDict, fontSize=constants.FONT_SIZE_LIST_WIDGET)
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.setShowGrid(False)
            self.treeObj.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.treeObj.tableWidget.horizontalHeader().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
            self.treeObj.tableWidget.verticalHeader().setVisible(False)
            self.treeObj.tableWidget.horizontalHeader().setStyleSheet('::section {background-color:#a2b0ff;color:black;font-weight:bold;}')
        self.refreshColumns()

    def refreshColumns(self):
        if self.treeObj.tableWidget:
            self.treeObj.tableWidget.resizeColumnsToContents()

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
        objIds = connectionObj.search(self.model, [], limit=self.passRange, offset=self.currentRange[0])
        self.loadIds(objIds)

    def switchToLeft(self):
        start, _to = self.currentRange
        self.currentRange = [start - self.passRange, start]
        if self.currentRange[0] == 0:
            self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)
        objIds = connectionObj.search(self.model, [], limit=self.passRange, offset=self.currentRange[0])
        self.loadIds(objIds)

    def sortResults(self, fieldName='', filterMode='DESC'):
        utils.logMessage('warning', 'Sorting not implemented in tree list view', 'sortResults')
