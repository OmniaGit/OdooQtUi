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


class One2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(One2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.viewObj = False
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.getQtObject()
        self.evaluatedIds = {}
        self.currentValue = []

    def getQtObject(self):
        self.mainLay = QtGui.QVBoxLayout()
        buttonsLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        buttonsLay.addWidget(self.labelQtObj)
        self.createButt = QtGui.QPushButton('Create')
        self.createButt.setStyleSheet(constants.BUTTON_STYLE)
        buttonsLay.addWidget(self.createButt)
        self.createButt.clicked.connect(self.createAndAdd)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(buttonsLay)

    def createAndAdd(self):

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
            res = self.rpc.create(self.relation, fieldVals)
            if res:
                rowCount = self.widgetQtObj.rowCount()
                orderedFields = self.viewObj.treeObj.orderedFields
                orderedFields.append('')
                for fieldName in orderedFields:
                    self.widgetQtObj.setRowCount(rowCount + 1)
                    colIndex = orderedFields.index(fieldName)
                    twItem = QtGui.QTableWidgetItem(fieldVals.get(fieldName, ''))
                    self.widgetQtObj.setItem(rowCount, colIndex, twItem)
                rowCount = rowCount + 1
                insertedRowDict = utils.getRowsFromTableWidget(self.widgetQtObj, 'dict', orderedFields)
                self.setRemoveButtons(self.widgetQtObj, insertedRowDict)

    def setValue(self, relIds):
        self.currentValue = relIds
        from start import MainConnector
        conn = MainConnector()
        self.viewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        self.viewObj.loadIds(relIds, {}, {}, {}, viewCheckBoxes=False)
        self.widgetQtObj = self.viewObj.treeObj.tableWidget
        self.widgetQtObj.setColumnCount(self.widgetQtObj.columnCount() + 1)
        fieldsToReadOrdered = self.viewObj.treeObj.orderedFields
        self.fieldsToReadOrdered = fieldsToReadOrdered
        fieldsToReadOrdered.append('')
        insertedRowDict = utils.getRowsFromTableWidget(self.widgetQtObj, 'dict', fieldsToReadOrdered)
        self.setRemoveButtons(self.widgetQtObj, insertedRowDict)
        self.setupTableWidgetLay(self.widgetQtObj)
        self.mainLay.addLayout(self.viewObj.layout)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        addAnItemLay = QtGui.QHBoxLayout()
        addAnItemLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(addAnItemLay)
        self.widgetLyQtObject.addLayout(self.mainLay)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)
        self.widgetQtObj.setHorizontalHeaderItem(self.widgetQtObj.columnCount() - 1, QtGui.QTableWidgetItem('Remove'))
        self.widgetQtObj.resizeColumnsToContents()

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

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(val)
        if self.viewObj:
            self.viewObj.treeObj.tableWidget.setDisabled(val)
            self.viewObj.buttToLeft.setDisabled(val)
            self.viewObj.buttToRight.setDisabled(val)
            self.viewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(One2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setHidden(val)
        if self.viewObj:
            self.viewObj.buttToLeft.setHidden(val)
            self.viewObj.buttToRight.setHidden(val)
            self.viewObj.treeObj.tableWidget.setHidden(val)
            self.viewObj.treeObj.widgetContents.setHidden(val)
        self.labelQtObj.setHidden(val)
        self.createButt.setHidden(val)
        super(One2many, self).setInvisible(val)
