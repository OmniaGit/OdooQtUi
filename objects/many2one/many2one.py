'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from utils import utils
from utils import constants
from objects.fieldTemplate import OdooFieldTemplate
import json


class Many2one(OdooFieldTemplate):
    def __init__(self, xmlField, fieldsDefinition, rpc):
        super(Many2one, self).__init__(xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.widgetQtObj = False
        self.editButton = QtGui.QPushButton()
        self.itemToIdRel = {}
        self.canCreate = json.loads(self.fieldAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldAttributes.get('can_write', 'true'))
        self.relation = self.fieldDefinition.get('relation', '')
        self.availableItems = self.getItems()
        self.hboxLay = self.getQtObject()

    def getItems(self):
        outVal = ['']
        if self.relation:
            for singleDict in self.rpc.readSearch(self.relation, ['name']):
                val = singleDict.get('name', '')
                if val:
                    outVal.append(val)
                    self.itemToIdRel[val] = singleDict.get('id', False)
        if self.canCreate:
            outVal.append('Create and Edit...')
        return outVal
        
    def getQtObject(self):
        self.hboxLay = QtGui.QHBoxLayout()
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.hboxLay.addWidget(self.labelQtObj)
        
        self.widgetQtObj = QtGui.QWidget()
        self.childLay = QtGui.QHBoxLayout()
        self.widgetQtObj2 = QtGui.QComboBox()
        self.widgetQtObj2.currentIndexChanged.connect(self.indexChanged)
        self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)
        self.widgetQtObj2.addItems(self.availableItems)
        self.widgetQtObj2.setToolTip(self.tooltip)
        if self.required:
            utils.setRequiredBackground(self.widgetQtObj2, constants.SELECTION_STYLE)
        self.childLay.addWidget(self.widgetQtObj2)
        if self.canWrite:
            self.editButton = QtGui.QPushButton('Edit')
            self.editButton.clicked.connect(self.editItem)
            self.editButton.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.childLay.addWidget(self.editButton)
            if not self.currentValue:
                self.editButton.setHidden(True)
        self.widgetQtObj.setLayout(self.childLay)
        self.hboxLay.addWidget(self.widgetQtObj)
        return self.hboxLay

    def setValue(self, val=False):
        indexToSet = 0
        newTextVal = ''
        if isinstance(val, (list, tuple)):
            _objId, newTextVal = val
        elif isinstance(val, bool):
            indexToSet = 0
            newTextVal = ''
        elif isinstance(val, int):
            res = self.rpc.read(self.relation, ['name'], [val])
            if res:
                newTextVal = res[0].get('name', '')
        elif isinstance(val, (unicode, str)):
            newTextVal = val
        if newTextVal in self.availableItems:
            indexToSet = self.availableItems.index(newTextVal)
        self.widgetQtObj2.setCurrentIndex(indexToSet)

    def setReadonly(self, val=False):
        self.widgetQtObj2.setEnabled(not val)
        self.widgetQtObj2.setEditable(not val)
        self.widgetQtObj2.setDisabled(val)
        if val:
            self.editButton.setHidden(True)
            self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE + constants.READONLY_STYLE)
        else:
            if self.currentValue:
                self.editButton.setHidden(False)
            else:
                self.editButton.setHidden(True)
            self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)

    def setInvisible(self, val=False):
        self.labelQtObj.setHidden(val)
        if self.widgetQtObj2:
            self.widgetQtObj2.setHidden(val)
        if self.currentValue and not val:
            self.editButton.setHidden(False)
        else:
            self.editButton.setHidden(True)
        
    def editItem(self, res=False):
        if not self.currentValue:
            return
        dialog = QtGui.QDialog()

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        from start import MainConnector
        conn = MainConnector()
        viewObj = conn.initViewObj('form', self.relation, rpcObj=self.rpc)
        objIds = [self.itemToIdRel.get(self.currentValue)]
        viewObj.loadIds(objIds)
        mainLay = viewObj.QtInterface
        lay, okButt, cancelButt = utils.getButtonBox()
        okButt.clicked.connect(accept)
        cancelButt.clicked.connect(reject)
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        mainLay.addLayout(lay)
        dialog.setLayout(mainLay)
        dialog.setStyleSheet('background-color:#893b74;')
        dialog.adjustSize()
        dialog.resize(800, dialog.height())
        if dialog.exec_() == QtGui.QDialog.Accepted:
            valuesToUpdate = {}
            for fieldName, fieldObj in viewObj.fieldsChanged.items():
                valuesToUpdate[fieldName] = fieldObj.value
            self.rpc.write(self.relation, valuesToUpdate, objIds)
            if 'name' in valuesToUpdate:
                indexToReplace = self.availableItems.index(self.currentValue)
                valToUpdate = unicode(valuesToUpdate['name'])
                self.availableItems[indexToReplace] = valToUpdate
                del self.itemToIdRel[self.currentValue]
                self.itemToIdRel[valToUpdate] = objIds[0]
                self.currentValue = valToUpdate
                self.widgetQtObj2.clear()
                self.widgetQtObj2.addItems(self.availableItems)
                self.widgetQtObj2.setCurrentIndex(indexToReplace)
                self.valueTemplateChanged()
        
    def indexChanged(self, res=False):
        currText = unicode(self.widgetQtObj2.currentText())
        if currText == 'Create and Edit...':
            dialog = QtGui.QDialog()
            def accept():
                dialog.accept()
    
            def reject():
                dialog.reject()

            from start import MainConnector
            conn = MainConnector()
            viewObj = conn.initViewObj('form', self.relation, rpcObj=self.rpc)
            viewObj.loadIds([])
            mainLay = viewObj.QtInterface
            lay, okButt, cancelButt = utils.getButtonBox()
            okButt.clicked.connect(accept)
            cancelButt.clicked.connect(reject)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            mainLay.addLayout(lay)
            dialog.setLayout(mainLay)
            dialog.setStyleSheet('background-color:#893b74;')
            dialog.adjustSize()
            dialog.resize(800, dialog.height())
            if dialog.exec_() == QtGui.QDialog.Accepted:
                valuesToCreate = {}
                for fieldName, fieldObj in viewObj.fields.__dict__.items():
                    valuesToCreate[fieldName] = fieldObj.value
                res = self.rpc.create(self.relation, valuesToCreate)
                if res:
                    name = unicode(valuesToCreate.get('name', ''))
                    self.itemToIdRel[name] = res
                    self.availableItems = self.getItems()
                    self.widgetQtObj2.clear()
                    self.widgetQtObj2.addItems(self.availableItems)
                    currentIndex = self.availableItems.index(name)
                    self.widgetQtObj2.setCurrentIndex(currentIndex)
                    self.currentValue = name
                    self.valueTemplateChanged()
            else:
                self.widgetQtObj2.setCurrentIndex(0)
        else:
            self.currentValue = currText
            if self.currentValue and self.editButton:
                self.editButton.setHidden(False)
            elif self.editButton:
                self.editButton.setHidden(True)
            self.valueTemplateChanged()

