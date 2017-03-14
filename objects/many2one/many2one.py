'''
Created on 7 Feb 2017

@author: dsmerghetto
'''

from PyQt4 import QtGui
from PyQt4 import QtCore
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
        self.skipSearch = False
        self.currentValue = False
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.availableItems = self.getItems()
        self.getQtObject()

    def getItems(self, search=False):
        outVal = ['']
        if self.relation and search:
            print 'search for values'
            for singleDict in self.rpc.readSearch(self.relation, ['name']):
                val = singleDict.get('name', '')
                if val:
                    outVal.append(val)
                    self.itemToIdRel[val] = singleDict.get('id', False)
        if self.canCreate:
            outVal.append('Create and Edit...')
        return outVal

    def getQtObject(self):
        self.labelQtObj = QtGui.QLabel(self.labelString)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)

        self.widgetQtObj = QtGui.QWidget()
        self.childLay = QtGui.QHBoxLayout()
        self.widgetQtObj2 = QtGui.QComboBox()
        self.widgetQtObj2.currentIndexChanged.connect(self.indexChanged)
        self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)
        self.widgetQtObj2.addItems(self.availableItems)
        self.widgetQtObj2.setToolTip(self.tooltip)
        self.widgetQtObj2.editTextChanged.connect(self.comboActivated)
        self.widgetQtObj2.installEventFilter(self)
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
        self.widgetLyQtObject.addWidget(self.widgetQtObj)
        if self.translatable:
            self.connectTranslationButton()
            self.widgetLyQtObject.addWidget(self.translateButton)

    def comboActivated(self, val=False):
        if not self.skipSearch:
            print 'combo activated, %r, val %r' % (self.availableItems, val)
            self.skipSearch = True
            newItems = self.getItems(True)
            self.widgetQtObj2.clear()
            self.widgetQtObj2.addItems(newItems)
            self.availableItems = newItems

    def setValue(self, val=False):
        newTextVal = ''
        indexToSet = 0
        if isinstance(val, (list, tuple)):
            objId, newTextVal = val
            self.itemToIdRel[newTextVal] = objId
        elif isinstance(val, bool):
            self.widgetQtObj2.setCurrentIndex(0)
            newTextVal = ''
            return
        elif isinstance(val, int):
            res = self.rpc.read(self.relation, ['name'], [val])
            if res:
                newTextVal = res[0].get('name', '')
        elif isinstance(val, (unicode, str)):
            newTextVal = val
        if newTextVal in self.availableItems:
            indexToSet = self.availableItems.index(newTextVal)
        else:
            self.availableItems.append(newTextVal)
            self.widgetQtObj2.clear()
            self.widgetQtObj2.addItems(self.availableItems)
            indexToSet = self.availableItems.index(newTextVal)
        self.widgetQtObj2.setCurrentIndex(indexToSet)

    def setReadonly(self, val=False):
        super(Many2one, self).setReadonly(val)
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
        super(Many2one, self).setInvisible(val)
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
        # objIds = [self.itemToIdRel.get(self.currentValue)]
        viewObj.loadIds([self.currentValue])
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
            self.rpc.write(self.relation, valuesToUpdate, self.currentValue)
            if 'name' in valuesToUpdate:
                oldName = ''
                for val, objId in self.itemToIdRel.items():
                    if objId == self.currentValue:
                        oldName = val
                        break
                indexToReplace = self.availableItems.index(oldName)
                valToUpdate = unicode(valuesToUpdate['name'])
                self.availableItems[indexToReplace] = valToUpdate
                del self.itemToIdRel[oldName]
                self.itemToIdRel[valToUpdate] = self.currentValue
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
                for fieldName, fieldObj in viewObj.interfaceFieldsDict.items():
                    valuesToCreate[fieldName] = fieldObj.value
                res = self.rpc.create(self.relation, valuesToCreate)
                if res:
                    name = unicode(valuesToCreate.get('name', ''))
                    self.itemToIdRel[name] = res
                    self.availableItems = self.getItems(search=True)
                    self.widgetQtObj2.clear()
                    self.widgetQtObj2.addItems(self.availableItems)
                    if name in self.availableItems:
                        currentIndex = self.availableItems.index(name)
                        self.widgetQtObj2.setCurrentIndex(currentIndex)
                    self.currentValue = self.itemToIdRel.get(name, False)
                    self.valueTemplateChanged()
            else:
                self.widgetQtObj2.setCurrentIndex(0)
        elif not currText:
            self.widgetQtObj2.setCurrentIndex(0)
            self.currentValue = False
        else:
            self.currentValue = self.itemToIdRel.get(currText, False)
            if self.currentValue and self.editButton:
                self.editButton.setHidden(False)
            elif self.editButton:
                self.editButton.setHidden(True)
            self.valueTemplateChanged()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and not self.skipSearch:
            print 'event filter'
            self.comboActivated()
        return super(Many2one, self).eventFilter(object, event)
