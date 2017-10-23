'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json
from PyQt4 import QtGui, QtCore
from functools import partial
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc, odooConnector=None):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.btnAddAnItem = None
        self.odooConnector = odooConnector
        self.currentValue = []
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.getQtObject()
        self.evaluatedIds = {}
        self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                  viewName='',
                                                  view_id=False,
                                                  rpcObj=self.rpc,
                                                  activeLanguage='',
                                                  viewCheckBoxes={0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled},
                                                  viewFilter=False)

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
        utilsUi.setLayoutMarginAndSpacing(self.mainLay)

    def createAndAdd(self):
        def acceptFormDial():
            fieldVals = tmpviewObjForm.getAllFieldsValues()
            for requiredFieldStr, requiredFieldObj in tmpviewObjForm.requiredFields.items():
                fieldVal = fieldVals.get(requiredFieldStr, '')
                if not fieldVal and not isinstance(fieldVal, (int, float)):
                    utilsUi.launchMessage('Field %r need a value' % (requiredFieldObj.labelString), 'error')
                    return
            formdialog.accept()
            
        def rejectFormDial():
            formdialog.reject()

        try:
            tmpviewObjForm = self.odooConnector.initFormViewObj(self.relation, rpcObj=self.rpc)
            tmpviewObjForm.loadIds([])
            formdialog = QtGui.QDialog()
            mainLay = QtGui.QVBoxLayout()
            mainLay.addWidget(tmpviewObjForm)
            formdialog.setStyleSheet('background-color:#893b74;')
            formdialog.resize(1200, 600)
            formdialog.move(100, 100)
            buttLay, okButt, cancelButt = utilsUi.getButtonBox('right')
            mainLay.addLayout(buttLay)
            formdialog.setLayout(mainLay)
            okButt.clicked.connect(acceptFormDial)
            cancelButt.clicked.connect(rejectFormDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            if formdialog.exec_() == QtGui.QDialog.Accepted:
                fieldVals = tmpviewObjForm.getAllFieldsValues()
                objId = self.rpc.create(self.relation, fieldVals)
                if objId:
                    self.currentValue.append(objId)
                    self.setValue(self.currentValue)
        except Exception, ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def setValue(self, relIds):
        self.currentValue = relIds
        self.treeViewObj.loadIds(relIds, {}, {}, {})
        self.widgetQtObj = self.treeViewObj.treeObj.tableWidget
        self.fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
        self.setRemoveButtons(self.widgetQtObj)
        self.setupTableWidgetLay(self.widgetQtObj)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, '')
        if not self.btnAddAnItem:
            self.btnAddAnItem = QtGui.QPushButton('Add an item')
            self.btnAddAnItem.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            self.btnAddAnItem.clicked.connect(self.addAnItem)
            addAnItemLay = QtGui.QHBoxLayout()
            addAnItemLay.addWidget(self.btnAddAnItem)
            addAnItemLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
            self.mainLay.addLayout(addAnItemLay)
            self.widgetLyQtObject.addLayout(self.mainLay)
        self.mainLay.addWidget(self.treeViewObj)

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

        viewObj = self.odooConnector.initTreeListViewObject(self.relation, rpcObj=self.rpc, viewCheckBoxes={0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled})
        viewObj.buttToLeft.clicked.connect(toLeft)
        viewObj.buttToRight.clicked.connect(toRight)
        resIds = self.rpc.search(self.relation, [], limit=viewObj.currentRange[-1], offset=viewObj.currentRange[0])
        viewObj.loadIds(resIds, {}, {}, {})
        dial = QtGui.QDialog()
        vlay = QtGui.QVBoxLayout()
        utilsUi.setLayoutMarginAndSpacing(vlay)
        layButt, okButt, cancelButt = utilsUi.getButtonBox('right')
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        okButt.clicked.connect(acceptDial)
        cancelButt.clicked.connect(rejectDial)
        vlay.addWidget(viewObj)
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
            self.setValue(self.currentValue)
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

    def eraseValue(self):
        self.setValue([])
