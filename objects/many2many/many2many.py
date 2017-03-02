'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2many(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2many, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.relation = self.fieldDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldAttributes.get('can_write', 'true'))
        self.getQtObject()

    def getQtObject(self):
        mainLay = QtGui.QVBoxLayout()
        buttonsLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        buttonsLay.addWidget(self.labelQtObj)
        createButt = QtGui.QPushButton('Create')
        editButton = QtGui.QPushButton('Edit')
        createButt.setStyleSheet(constants.BUTTON_STYLE)
        editButton.setStyleSheet(constants.BUTTON_STYLE)
        buttonsLay.addWidget(createButt)
        buttonsLay.addWidget(editButton)
        buttonsLay.addSpacerItem(QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum))
        self.widgetQtObj = QtGui.QTableWidget()
        self.widgetQtObj.setToolTip(self.tooltip)
        mainLay.addLayout(buttonsLay)
        mainLay.addWidget(self.widgetQtObj)
        self.widgetLyQtObject.addLayout(mainLay)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj, '')
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def setValue(self, relIds):
        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        fieldsToReadOrdered = viewObj.treeObj.orderedFields
        res = self.rpc.read(self.relation, fieldsToReadOrdered, relIds)
        values = []
        for recordDict in res:
            recordValList = []
            for fieldName in fieldsToReadOrdered:
                val = recordDict.get(fieldName)
                if isinstance(val, (list, tuple)):
                    if len(val) < 1:
                        val = ''
                    val = val[1]
                recordValList.append(unicode(val))
            values.append(recordValList)
        utils.commonPopulateTable(fieldsToReadOrdered, values, self.widgetQtObj)
        rowCount = self.widgetQtObj.rowCount()
        self.widgetQtObj.setRowCount(rowCount + 1)
        btn = QtGui.QPushButton('Add an item')
        btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
        self.widgetQtObj.setCellWidget(rowCount, 0, btn)
        btn.clicked.connect(self.addAnItem)
        self.widgetQtObj.resizeColumnsToContents()
        self.widgetQtObj.setShowGrid(False)

        colCount = self.widgetQtObj.columnCount()
        self.widgetQtObj.setColumnCount(colCount + 1)
        for rowCount in range(0, rowCount):
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            self.widgetQtObj.setCellWidget(rowCount, colCount, btn)
            btn.clicked.connect(self.removeItem)

    def removeItem(self):
        pass

    def addAnItem(self):
        pass

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        super(Many2many, self).setInvisible(val)
