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
        self.treeViewObj = False
        self.currentValue = []
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
        self.createButt.clicked.connect(self.createAndAdd)
        buttonsLay.addWidget(self.createButt)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(buttonsLay)

    def createAndAdd(self):
        try:
            def acceptDial():
                dialog.accept()

            def rejectDial():
                dialog.reject()

            dialog = QtGui.QDialog()
            mainLay = QtGui.QVBoxLayout()
            from start import MainConnector
            conn = MainConnector()
            viewObjForm = conn.initViewObj('form', self.relation, rpcObj=self.rpc)
            mainLay.addLayout(viewObjForm.layout)
            dialog.setStyleSheet('background-color:#893b74;')
            dialog.resize(1200, 600)
            dialog.move(100, 100)
            buttLay, okButt, cancelButt = utils.getButtonBox('right')
            mainLay.addLayout(buttLay)
            dialog.setLayout(mainLay)
            okButt.clicked.connect(acceptDial)
            cancelButt.clicked.connect(rejectDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            if dialog.exec_() == QtGui.QDialog.Accepted:
                fieldVals = viewObjForm.getAllFieldsValues()
                objId = self.rpc.create(self.relation, fieldVals)
                if objId:
                    rowCount = self.widgetQtObj.rowCount()
                    orderedFields = self.treeViewObj.treeObj.orderedFields
                    orderedFields.append('')
                    self.widgetQtObj.setRowCount(rowCount + 1)
                    for fieldName in orderedFields:
                        if not fieldName:
                            continue
                        colIndex = orderedFields.index(fieldName)
                        fieldObj = viewObjForm.fields.getFieldObj(fieldName)
                        fieldVal = ''
                        if fieldObj:
                            fieldVal = fieldObj.valueInterface
                        twItem = QtGui.QTableWidgetItem(fieldVal)
                        self.widgetQtObj.setItem(rowCount, colIndex, twItem)
                    self.treeViewObj.idLineRel[rowCount] = objId
                    self.currentValue.append(objId)
                    rowCount = rowCount + 1
                    self.setRemoveButtons(self.widgetQtObj)
        except Exception, ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def setValue(self, relIds):
        self.currentValue = relIds
        from start import MainConnector
        conn = MainConnector()
        self.treeViewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        self.treeViewObj.loadIds(relIds, {}, {}, {}, viewCheckBoxes=False)
        self.widgetQtObj = self.treeViewObj.treeObj.tableWidget
        self.fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
        self.setRemoveButtons(self.widgetQtObj)
        self.setupTableWidgetLay(self.widgetQtObj)
        self.mainLay.addLayout(self.treeViewObj.layout)
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

    def setRemoveButtons(self, tableWidget):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

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

    def removeItem(self, rowIndex):
        found = False
        rowIndexes = self.treeViewObj.idLineRel.keys()
        for rowInd in rowIndexes:
            objId = self.treeViewObj.idLineRel[rowInd]
            if rowInd == rowIndex:
                if objId in self.currentValue:
                    self.currentValue.remove(objId)
                    utils.removeRowFromTableWidget(self.widgetQtObj, rowIndex)
                    self.setRemoveButtons(self.widgetQtObj)
                    del self.treeViewObj.idLineRel[rowInd]
                    found = True
            elif found:
                del self.treeViewObj.idLineRel[rowInd]
                self.treeViewObj.idLineRel[rowInd - 1] = objId
        print self.treeViewObj.idLineRel

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
            viewObj.treeObj.tableWidget.clear()
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
            localIndexId = {}
            table = viewObj.treeObj.tableWidget
            for rowIndex in range(table.rowCount()):
                if table.item(rowIndex, 0).checkState() == QtCore.Qt.Checked:
                    objId = viewObj.idLineRel.get(rowIndex, False)
                    if objId:
                        self.currentValue.append(objId)
                        localIndexId[rowIndex] = objId
                    checkedRows.append(rowIndex)
            rowsDict = utils.getRowsFromTableWidget(table, 'dict', self.fieldsToReadOrdered)
            rowPosition = self.widgetQtObj.rowCount()
            for checkedIndex in checkedRows:
                self.widgetQtObj.setRowCount(rowPosition + 1)
                valsToInsert = rowsDict.get(checkedIndex, {})
                for fieldName in self.fieldsToReadOrdered:
                    colIndex = self.fieldsToReadOrdered.index(fieldName)
                    colVal = valsToInsert.get(fieldName, '')
                    twItem = QtGui.QTableWidgetItem(colVal)
                    font = QtGui.QFont()
                    font.setPointSize(constants.FONT_SIZE_LIST_WIDGET)
                    twItem.setFont(font)
                    self.widgetQtObj.setItem(rowPosition, colIndex, twItem)
                self.treeViewObj.idLineRel[rowPosition] = localIndexId[checkedIndex]
                rowPosition = rowPosition + 1
            self.setRemoveButtons(self.widgetQtObj)
            self.setupTableWidgetLay(self.widgetQtObj)
        print self.treeViewObj.idLineRel

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        self.btnAddAnItem.setDisabled(val)
        self.widgetQtObj.setDisabled(val)
        self.treeViewObj.treeObj.tableWidget.setDisabled(val)
        self.treeViewObj.buttToLeft.setDisabled(val)
        self.treeViewObj.buttToRight.setDisabled(val)
        self.treeViewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        self.btnAddAnItem.setHidden(val)
        self.labelQtObj.setHidden(val)
        self.widgetQtObj.setHidden(val)
        self.treeViewObj.buttToLeft.setHidden(val)
        self.treeViewObj.buttToRight.setHidden(val)
        self.treeViewObj.treeObj.tableWidget.setHidden(val)
        self.treeViewObj.treeObj.widgetContents.setHidden(val)
        self.createButt.setHidden(val)
        super(Many2many, self).setInvisible(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue
