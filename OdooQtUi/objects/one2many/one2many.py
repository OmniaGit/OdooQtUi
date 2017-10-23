'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json

from PyQt4 import QtGui, QtCore
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from functools import partial
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class One2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc, odooConnector=None):
        super(One2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.treeViewObj = False
        self.odooConnector = odooConnector
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.getQtObject()
        self.evaluatedIds = {}
        self.currentValue = []
        self.treeViewObj = self.odooConnector.initTreeListViewObject(odooObjectName=self.relation,
                                                  viewName='',
                                                  view_id=False,
                                                  rpcObj=self.rpc,
                                                  activeLanguage='',
                                                  viewCheckBoxes={},
                                                  viewFilter=False)

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
        try:
            def acceptDial():
                dialog.accept()
    
            def rejectDial():
                dialog.reject()
    
            dialog = QtGui.QDialog()
            mainLay = QtGui.QVBoxLayout()
            viewObjForm = self.odooConnector.initFormViewObj(self.relation, rpcObj=self.rpc)
            mainLay.addWidget(viewObjForm)
            dialog.setStyleSheet('background-color:#893b74;')
            dialog.resize(1200, 600)
            dialog.move(100, 100)
            buttLay, okButt, cancelButt = utilsUi.getButtonBox('right')
            mainLay.addLayout(buttLay)
            dialog.setLayout(mainLay)
            okButt.clicked.connect(acceptDial)
            cancelButt.clicked.connect(rejectDial)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
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
                        fieldVal = viewObjForm.fields.getFieldObj(fieldName).valueInterface
                        twItem = QtGui.QTableWidgetItem(fieldVal)
                        self.widgetQtObj.setItem(rowCount, colIndex, twItem)
                    self.treeViewObj.idLineRel[rowCount] = objId
                    rowCount = rowCount + 1
                    self.setRemoveButtons(self.widgetQtObj)
        except Exception, ex:
            utils.logMessage('error', '%r' % (ex), 'createAndAdd')

    def computeFieldVal(self, val):
        outStrVal = ''
        if isinstance(val, (list, tuple)):
            _objId, outStrVal = val
        elif isinstance(val, bool):
            outStrVal = ''
        elif isinstance(val, int):
            outStrVal = ''
        elif isinstance(val, (str, unicode, QtCore.QString)):
            outStrVal = unicode(val)
        return outStrVal

    def setValue(self, relIds):
        self.currentValue = relIds
        self.treeViewObj.loadIds(relIds, {}, {}, {})
        self.widgetQtObj = self.treeViewObj.treeObj.tableWidget
        self.widgetQtObj.setColumnCount(self.widgetQtObj.columnCount() + 1)
        fieldsToReadOrdered = self.treeViewObj.treeObj.orderedFields
        self.fieldsToReadOrdered = fieldsToReadOrdered
        self.setRemoveButtons(self.widgetQtObj)
        self.setupTableWidgetLay(self.widgetQtObj)
        self.mainLay.addWidget(self.treeViewObj)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj, '')
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

    def setRemoveButtons(self, tableWidget):
        rowCount = tableWidget.rowCount()
        colCount = tableWidget.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            tableWidget.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(partial(self.removeItem, rowCount))

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

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setDisabled(val)
        if self.treeViewObj:
            self.treeViewObj.treeObj.tableWidget.setDisabled(val)
            self.treeViewObj.buttToLeft.setDisabled(val)
            self.treeViewObj.buttToRight.setDisabled(val)
            self.treeViewObj.treeObj.widgetContents.setDisabled(val)
        self.createButt.setDisabled(val)
        super(One2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        if self.widgetQtObj:
            self.widgetQtObj.setHidden(val)
        if self.treeViewObj:
            self.treeViewObj.buttToLeft.setHidden(val)
            self.treeViewObj.buttToRight.setHidden(val)
            self.treeViewObj.treeObj.tableWidget.setHidden(val)
            self.treeViewObj.treeObj.widgetContents.setHidden(val)
        self.labelQtObj.setHidden(val)
        self.createButt.setHidden(val)
        super(One2many, self).setInvisible(val)

    @property
    def value(self):
        return self.currentValue

    @property
    def valueInterface(self):
        return self.currentValue

    def eraseValue(self):
        self.setValue([])
