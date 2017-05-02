'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from parser.tree_list import TreeViewList
from templateView import TemplateView
from views.search_obj import TemplateSearchView
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from RPC.rpc import connectionObj
from PyQt4 import QtGui
from PyQt4 import QtCore


class TemplateTreeListView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US', viewFilter=False):
        super(TemplateTreeListView, self).__init__(rpcObject, activeLanguageCode)
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []
        self.idValsRel = {}
        self.idLineRel = {}
        self.labelsOrdered = []
        self.currentRange = [0, 40]
        self.passRange = 40
        self.viewFilter = viewFilter

    def initViewObj(self, odooObjectName, viewName='', view_id=False, viewCheckBoxes={}):
        super(TemplateTreeListView, self).initViewObj(odooObjectName, viewName, view_id)
        self.viewCheckBoxes = viewCheckBoxes
        self.layout = QtGui.QVBoxLayout()
        if self.viewFilter:
            self.searchObj = TemplateSearchView(self.rpcObject, self.activeLanguageCode)
            self.searchObj.initViewObj(odooObjectName)
            self.layout.addLayout(self.searchObj.layout)
        self.treeObj = TreeViewList(self.arch, self.fieldsNameTypeRel, self.rpcObject, viewCheckBoxes)
        self.mainLay = self.treeObj.computeArch()
        switchRecordsLay = QtGui.QHBoxLayout()
        self.buttToLeft = QtGui.QPushButton('<')
        self.buttToRight = QtGui.QPushButton('>')
        switchRecordsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        switchRecordsLay.addWidget(self.buttToLeft)
        switchRecordsLay.addWidget(self.buttToRight)
        self.buttToLeft.setStyleSheet(constants.BUTTON_STYLE)
        self.buttToRight.setStyleSheet(constants.BUTTON_STYLE)
        self.buttToLeft.clicked.connect(self.switchToLeft)
        self.buttToRight.clicked.connect(self.switchToRight)
        self.layout.addLayout(switchRecordsLay, 0)
        self.layout.addLayout(self.mainLay)
        self.mappingInterface = self.treeObj.globalMapping
        self.addToObject()
        self.currentRange = [0, 40]
        self.buttToLeft.setHidden(True)
        self.treeObj.tableWidget.setStyleSheet(constants.TABLE_LIST_LIST)
        self.treeObj.tableWidget.setMinimumHeight(200)

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
            objIds = connectionObj.search(self.model, []) # to check with many records if 40 stop will work, 40)
        fields = self.treeObj.orderedFields
        if len(objIds) < self.passRange:
            self.buttToRight.setHidden(True)
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
                self.labelsOrdered.append(fieldObj.labelString)
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
                record[fieldName] = val
                if fieldObj.fieldType == 'many2one':
                    if isinstance(val, bool):
                        val = ''
                    else:
                        val = val[1]
                localList.append(unicode(val))
            valuesList.append(localList)
            recordId = record.get('id', False)
            self.idValsRel[recordId] = record
            self.idLineRel[records.index(record)] = recordId
        utils.commonPopulateTable(self.labelsOrdered, valuesList, self.treeObj.tableWidget, flagsDict, fontSize=constants.FONT_SIZE_LIST_WIDGET)
        self.treeObj.tableWidget.resizeColumnsToContents()
        self.treeObj.tableWidget.setShowGrid(False)
        self.treeObj.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.treeObj.tableWidget.horizontalHeader().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
        self.treeObj.tableWidget.verticalHeader().setVisible(False)

    def _valueChanged(self, fieldName):
        fieldName = unicode(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        self.fieldsChanged[fieldName] = fieldObj

    def switchToRight(self):
        _start, to = self.currentRange
        self.currentRange = [to, to + self.passRange]
        self.buttToLeft.setHidden(False)

    def switchToLeft(self):
        start, _to = self.currentRange
        self.currentRange = [start - self.passRange, start]
        if self.currentRange[0] == 0:
            self.buttToLeft.setHidden(True)
        self.buttToRight.setHidden(False)

    def sortResults(self, fieldName='', filterMode='DESC'):
        utils.logMessage('warning', 'Sorting not implemented in tree list view', 'sortResults')
