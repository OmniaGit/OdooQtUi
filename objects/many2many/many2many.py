'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils import utils
from utils import constants
from functools import partial
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.viewObj = False
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.getQtObject()
        self.evaluatedIds = {}

    def getQtObject(self):
        self.mainLay = QtGui.QVBoxLayout()
        buttonsLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        buttonsLay.addWidget(self.labelQtObj)
        self.createButt = QtGui.QPushButton('Create')
        self.createButt.setStyleSheet(constants.BUTTON_STYLE)
        buttonsLay.addWidget(self.createButt)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(buttonsLay)

    def setValue(self, relIds):
        self.currentValue = relIds
        from start import MainConnector
        conn = MainConnector()
        self.viewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        self.viewObj.loadIds(relIds, {}, {}, {}, viewCheckBoxes=False)
        self.widgetQtObj = self.viewObj.treeObj.tableWidget
        self.fieldsToReadOrdered = self.viewObj.treeObj.orderedFields
        insertedRowDict = utils.getRowsFromTableWidget(self.widgetQtObj, 'dict', self.fieldsToReadOrdered)
        self.setRemoveButtons(self.widgetQtObj, insertedRowDict)
        self.setupTableWidgetLay(self.widgetQtObj)
        self.mainLay.addLayout(self.viewObj.layout)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        self.btnAddAnItem = QtGui.QPushButton('Add an item')
        self.btnAddAnItem.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
        self.btnAddAnItem.clicked.connect(self.addAnItem)
        addAnItemLay = QtGui.QHBoxLayout()
        addAnItemLay.addWidget(self.btnAddAnItem)
        addAnItemLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(addAnItemLay)
        self.widgetLyQtObject.addLayout(self.mainLay)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def setupTableWidgetLay(self, tableWidget):
        tableWidget.resizeColumnsToContents()
        tableWidget.setShowGrid(False)
        tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

    def setRemoveButtons(self, tableWidget, insertedRowDict):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            rowDict = insertedRowDict.get(rowCount, {})
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowDict))

    def getOrderedFieldsStrings(self, orderedFields, fieldsDict):
        labelsOrdered = []
        for fieldName in orderedFields:
            fieldObj = fieldsDict.get(fieldName, None)
            if fieldObj:
                labelsOrdered.append(fieldObj.labelString)
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
                recordValList.append(unicode(val))
            recordValList.append('')
            values.append(recordValList)
        if checkBox:
            flags[0] = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        return values, flags

    def removeItem(self, rowDictVals):
        rowDictValsDict = utils.getRowsFromTableWidget(self.widgetQtObj, 'dict', self.fieldsToReadOrdered)
        for recordId, recordVals in self.viewObj.idValsRel.items():
            localDict = recordVals.copy()
            if 'id' in localDict:
                del localDict['id']
            if rowDictVals == localDict:
                if recordId in self.currentValue:
                    self.currentValue.remove(recordId)
                rowCount = False
                for rowIndex, rowDict in rowDictValsDict.items():
                    if rowDictVals == rowDict:
                        rowCount = rowIndex
                        break
                if rowCount is not False:
                    utils.removeRowFromTableWidget(self.widgetQtObj, rowCount)
                return

    def addAnItem(self):
        def acceptDial():
            dial.accept()

        def rejectDial():
            dial.reject()

        def commonMove():
            currRange = viewObj.currentRange
            currRangeTuple = tuple(currRange)
            if currRangeTuple not in self.evaluatedIds.keys():
                resIds = self.rpc.search(self.relation, [], limit=viewObj.passRange, offset=currRange[-1])
                self.evaluatedIds[currRangeTuple] = resIds
            else:
                resIds = self.evaluatedIds[currRangeTuple]
            viewObj.loadIds(resIds, {}, {}, {}, viewCheckBoxes=True)

        def toLeft():
            commonMove()

        def toRight():
            commonMove()

        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initTreeListViewObject(self.relation, rpcObj=self.rpc, viewCheckBoxes=True)
        viewObj.buttToLeft.clicked.connect(toLeft)
        viewObj.buttToRight.clicked.connect(toRight)
        resIds = self.rpc.search(self.relation, [], limit=viewObj.currentRange[-1], offset=viewObj.passRange)
        viewObj.loadIds(resIds, {}, {}, {}, viewCheckBoxes=True)
        dial = QtGui.QDialog()
        vlay = QtGui.QVBoxLayout()
        layButt, okButt, cancelButt = utils.getButtonBox('right')
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        okButt.clicked.connect(acceptDial)
        cancelButt.clicked.connect(rejectDial)
        vlay.addLayout(viewObj.layout)
        vlay.addLayout(layButt)
        dial.setLayout(vlay)
        dial.setStyleSheet('background-color:#893b74;')
        dial.resize(800, 500)
        if dial.exec_() == QtGui.QDialog.Accepted:
            checkedRows = []
            table = viewObj.treeObj.tableWidget
            for rowIndex in range(table.rowCount()):
                if table.item(rowIndex, 0).checkState() == QtCore.Qt.Checked:
                    checkedRows.append(rowIndex)
            rowsDict = utils.getRowsFromTableWidget(table, 'dict', self.fieldsToReadOrdered)
            valsToInsert = []
            for checkedIndex in checkedRows:
                valsToInsert.append(rowsDict.get(checkedIndex, {}))
            values, flags = self.convertDictToLists(valsToInsert, self.fieldsToReadOrdered, checkBox=False)
            utils.commonPopulateTable(self.viewObj.labelsOrdered, values, self.widgetQtObj, flags, add=True)
            rowsDict = utils.getRowsFromTableWidget(self.widgetQtObj, 'dict', self.fieldsToReadOrdered)
            self.setRemoveButtons(self.widgetQtObj, rowsDict)
            self.setupTableWidgetLay(self.widgetQtObj)
            for recordId, recordVals in viewObj.idValsRel.items():
                for rowVals in valsToInsert:
                    localDict = recordVals.copy()
                    if 'id' in localDict:
                        del localDict['id']
                    if localDict == rowVals:
                        self.currentValue.append(recordId)
                        self.viewObj.idValsRel[recordId] = rowVals

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        self.btnAddAnItem.setDisabled(val)
        self.widgetQtObj.setDisabled(val)
        self.viewObj.treeObj.tableWidget.setDisabled(val)
        self.viewObj.buttToLeft.setDisabled(val)
        self.viewObj.buttToRight.setDisabled(val)
        self.viewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        self.btnAddAnItem.setHidden(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
        self.viewObj.buttToLeft.setHidden(val)
        self.viewObj.buttToRight.setHidden(val)
        self.viewObj.treeObj.tableWidget.setHidden(val)
        self.viewObj.treeObj.widgetContents.setHidden(val)
        self.createButt.setHidden(val)
        super(Many2many, self).setInvisible(val)
