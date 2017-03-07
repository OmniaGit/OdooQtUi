'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui, QtCore
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.getQtObject()

    def getQtObject(self):
        self.mainLay = QtGui.QVBoxLayout()
        buttonsLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        buttonsLay.addWidget(self.labelQtObj)
        createButt = QtGui.QPushButton('Create')
        createButt.setStyleSheet(constants.BUTTON_STYLE)
        buttonsLay.addWidget(createButt)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.widgetQtObj = QtGui.QTableWidget()
        self.widgetQtObj.horizontalHeader().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
        self.widgetQtObj.verticalHeader().setVisible(False)
        self.widgetQtObj.setToolTip(self.tooltip)
        self.mainLay.addLayout(buttonsLay)
        self.mainLay.addWidget(self.widgetQtObj)
        self.btnAddAnItem = QtGui.QPushButton('Add an item')
        self.btnAddAnItem.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
        self.btnAddAnItem.clicked.connect(self.addAnItem)
        addAnItemLay = QtGui.QHBoxLayout()
        addAnItemLay.addWidget(self.btnAddAnItem)
        addAnItemLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.mainLay.addLayout(addAnItemLay)
        self.widgetLyQtObject.addLayout(self.mainLay)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def setValue(self, relIds):
        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        self.fieldsToReadOrdered = viewObj.treeObj.orderedFields
        res = self.rpc.read(self.relation, self.fieldsToReadOrdered, relIds)
        values, flags = self.convertDictToLists(res, self.fieldsToReadOrdered, checkBox=False)
        self.labelsOrdered = self.getOrderedFieldsStrings(self.fieldsToReadOrdered, viewObj.fields.__dict__)
        utils.commonPopulateTable(self.labelsOrdered, values, self.widgetQtObj, flags)
        self.setRemoveButtons(self.widgetQtObj)
        self.setupTableWidgetLay(self.widgetQtObj)

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
            btn.clicked.connect(self.removeItem)

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

    def removeItem(self):
        pass

    def addAnItem(self):
        def acceptDial():
            dial.accept()

        def rejectDial():
            dial.reject()

        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initTreeListViewObject(self.relation, rpcObj=self.rpc, viewCheckBoxes=True)
        resIds = self.rpc.search(self.relation, [])
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
            utils.commonPopulateTable(self.labelsOrdered, values, self.widgetQtObj, flags, add=True)
            self.setRemoveButtons(self.widgetQtObj)
            self.setupTableWidgetLay(self.widgetQtObj)

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        self.btnAddAnItem.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        self.btnAddAnItem.setHidden(val)
        super(Many2many, self).setInvisible(val)
