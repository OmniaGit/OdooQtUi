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
        fieldsToReadOrdered = viewObj.treeObj.orderedFields
        res = self.rpc.read(self.relation, fieldsToReadOrdered, relIds)
        values = []
        flags = {}
        for recordDict in res:
            recordValList = []
            for fieldName in fieldsToReadOrdered:
                val = recordDict.get(fieldName)
                if isinstance(val, (list, tuple)):
                    if len(val) < 1:
                        val = ''
                    val = val[1]
                recordValList.append(unicode(val))
            recordValList.append('')
            flags[res.index(recordDict)] = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            values.append(recordValList)
        labelsOrdered = []
        for fieldName in fieldsToReadOrdered:
            fieldObj = viewObj.fields.__dict__.get(fieldName, None)
            if fieldObj:
                labelsOrdered.append(fieldObj.labelString)
            else:
                labelsOrdered.append(fieldName)
        labelsOrdered.append('')
        utils.commonPopulateTable(labelsOrdered, values, self.widgetQtObj, flags)
        rowCount = self.widgetQtObj.rowCount()
        colCount = self.widgetQtObj.columnCount()
        for rowCount in range(0, rowCount):
            btn = QtGui.QPushButton('Remove')
            btn.setStyleSheet(constants.BUTTON_ADD_AN_ITEM)
            self.widgetQtObj.setCellWidget(rowCount, colCount - 1, btn)
            btn.clicked.connect(self.removeItem)
        self.widgetQtObj.resizeColumnsToContents()
        self.widgetQtObj.setShowGrid(False)
        self.widgetQtObj.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.widgetQtObj.setRowCount(rowCount + 1)

    def removeItem(self):
        pass

    def addAnItem(self):
        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initViewObj('tree_list', self.relation, rpcObj=self.rpc)
        pass

    def valueChanged(self):
        self.valueTemplateChanged()

    def setReadonly(self, val=False):
        self.btnAddAnItem.setDisabled(val)
        super(Many2many, self).setReadonly(val)

    def setInvisible(self, val=False):
        self.btnAddAnItem.setHidden(val)
        super(Many2many, self).setInvisible(val)
