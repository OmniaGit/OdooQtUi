'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from functools import partial
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.btnAddAnItem = None
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

    def acceptFormDial(self):
        fieldVals = self.tmpviewObjForm.getAllFieldsValues()
        for requiredFieldStr, requiredFieldObj in self.tmpviewObjForm.requiredFields.items():
            fieldVal = fieldVals.get(requiredFieldStr, '')
            if not fieldVal and not isinstance(fieldVal, (int, float)):
                utils.launchMessage('Field %r need a value' % (requiredFieldObj.labelString), 'error')
                return
        self.formdialog.accept()

    def rejectFormDial(self):
        self.formdialog.reject()

    def createAndAdd(self):
        try:
            from start import MainConnector
            conn = MainConnector()
            self.tmpviewObjForm = conn.initViewObj('form', self.relation, rpcObj=self.rpc)

            self.formdialog = QtGui.QDialog()
            mainLay = QtGui.QVBoxLayout()
            mainLay.addLayout(self.tmpviewObjForm.layout)
            self.formdialog.setStyleSheet('background-color:#893b74;')
            self.formdialog.resize(1200, 600)
            self.formdialog.move(100, 100)
            buttLay, okButt, cancelButt = utils.getButtonBox('right')
            mainLay.addLayout(buttLay)
            self.formdialog.setLayout(mainLay)
            okButt.clicked.connect(self.acceptFormDial)
            cancelButt.clicked.connect(self.rejectFormDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            if self.formdialog.exec_() == QtGui.QDialog.Accepted:
                fieldVals = self.tmpviewObjForm.getAllFieldsValues()
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
                        fieldObj = self.tmpviewObjForm.fields.getFieldObj(fieldName)
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
        self.treeViewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc, viewCheckBoxes={0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled})
        self.treeViewObj.loadIds(relIds, {}, {}, {})
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
            viewObj.loadIds(resIds, {}, {}, {})

        def toLeft():
            commonMove()

        def toRight():
            commonMove()

        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initTreeListViewObject(self.relation, rpcObj=self.rpc, viewCheckBoxes={0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled})
        viewObj.buttToLeft.clicked.connect(toLeft)
        viewObj.buttToRight.clicked.connect(toRight)
        resIds = self.rpc.search(self.relation, [], limit=viewObj.currentRange[-1], offset=viewObj.currentRange[0])
        viewObj.loadIds(resIds, {}, {}, {})
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
                    twItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                    self.widgetQtObj.setItem(rowPosition, colIndex, twItem)
                self.treeViewObj.idLineRel[rowPosition] = localIndexId[checkedIndex]
                rowPosition = rowPosition + 1
            self.setRemoveButtons(self.widgetQtObj)
            self.setupTableWidgetLay(self.widgetQtObj)
        print self.treeViewObj.idLineRel

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        if self.btnAddAnItem:
            self.btnAddAnItem.setDisabled(val)
        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(val)
        if self.treeViewObj:
            self.treeViewObj.treeObj.tableWidget.setDisabled(val)
            self.treeViewObj.buttToLeft.setDisabled(val)
            self.treeViewObj.buttToRight.setDisabled(val)
            self.treeViewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        if self.btnAddAnItem:
            if val:
                self.btnAddAnItem.hide()
            else:
                self.btnAddAnItem.show()
        if self.widgetQtObj:
            self.widgetQtObj.setHidden(val)
        if self.treeViewObj:
            if val:
                self.treeViewObj.buttToLeft.hide()
                self.treeViewObj.buttToRight.hide()
            else:
                self.treeViewObj.buttToLeft.show()
                self.treeViewObj.buttToRight.show()
            self.treeViewObj.treeObj.tableWidget.setHidden(val)
            self.treeViewObj.treeObj.widgetContents.setHidden(val)
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
        return self.currentValue
