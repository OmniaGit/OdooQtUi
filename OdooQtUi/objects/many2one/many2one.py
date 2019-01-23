'''
Created on 7 Feb 2017

@author: dsmerghetto
'''
import json
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils, utilsUi
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.objects.fieldTemplate import OdooFieldTemplate


class Many2one(OdooFieldTemplate):
    def __init__(self, qtParent, xmlField, fieldsDefinition, rpc, odooConnector=None):
        super(Many2one, self).__init__(qtParent, xmlField, fieldsDefinition, rpc)
        self.labelQtObj = False
        self.qDoubleSpinBoxValue = False
        self.editButton = False
        self.itemToIdRel = {}
        self.skipSearch = False
        self.currentValue = False
        self.odooConnector = odooConnector
        self.relation = self.fieldPyDefinition.get('relation', '')
        self.canCreate = json.loads(self.fieldXmlAttributes.get('can_create', 'true'))
        self.canWrite = json.loads(self.fieldXmlAttributes.get('can_write', 'true'))
        self.availableItems = self.getItems()
        self.getQtObject()

    def getQtObject(self):
        self.labelQtObj = QtWidgets.QLabel(self.fieldStringInterface)
        self.labelQtObj.setStyleSheet(constants.LABEL_STYLE)
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qDoubleSpinBoxValue = QtWidgets.QWidget(self)
        self.widgetQtObj2 = QtWidgets.QComboBox(self)
        self.widgetQtObj2.setStyleSheet(constants.SELECTION_STYLE)
        self.widgetQtObj2.addItems(self.availableItems)
        self.widgetQtObj2.setToolTip(self.tooltip)
        self.widgetQtObj2.editTextChanged.connect(self.comboActivated)
        self.widgetQtObj2.installEventFilter(self)
        self.widgetQtObj2.currentIndexChanged.connect(self.indexChanged)
        if self.required:
            utilsUi.setRequiredBackground(self.widgetQtObj2, constants.SELECTION_STYLE)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj2)
        if self.canWrite:
            self.editButton = QtWidgets.QPushButton('Edit')
            self.editButton.clicked.connect(self.editItem)
            self.editButton.setStyleSheet(constants.BUTTON_STYLE_MANY_2_ONE)
            self.qtHorizontalWidget.addWidget(self.editButton)
            if not self.currentValue:
                self.editButton.setHidden(True)
        self.qtHorizontalWidget.addWidget(self.qDoubleSpinBoxValue)
        self.qtHorizontalWidget.insertSpacerItem(3, QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        if self.translatable:
            self.connectTranslationButton()
            self.addWidget(self.translateButton)

    def getItems(self, search=False):
        outVal = ['']
        if self.relation and search:
            for singleDict in self.rpc.readSearch(self.relation, ['name']):
                val = singleDict.get('name', '')
                if val:
                    outVal.append(val)
                    self.itemToIdRel[val] = singleDict.get('id', False)
        if self.canCreate:
            outVal.append('Create and Edit...')
        return outVal

    def comboActivated(self, val=False):
        if not self.skipSearch:
            self.skipSearch = True
            newItems = self.getItems(True)
            self.widgetQtObj2.clear()
            self.widgetQtObj2.addItems(newItems)
            self.availableItems = newItems

    def setValue(self, val=False):
        self.currentValue = val
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
            found = False
            for text, objId in list(self.itemToIdRel.items()):
                if objId == val:
                    found = True
                    newTextVal = text
                    self.currentValue = [objId, text]
            if not found:
                res = self.rpc.read(self.relation, ['name'], [val])
                if res:
                    relDict = res[0]
                    newTextVal = relDict.get('name', '')
                    self.itemToIdRel[newTextVal] = relDict.get('id', False)
                    self.currentValue = [relDict.get('id', False), newTextVal]
        elif isinstance(val, str):
            newTextVal = val
        if newTextVal in self.availableItems:
            indexToSet = self.availableItems.index(newTextVal)
        else:
            self.availableItems.append(newTextVal)
            self.widgetQtObj2.clear()
            self.widgetQtObj2.addItems(self.availableItems)
            indexToSet = self.availableItems.index(newTextVal)
        self.skipSearch = True
        self.widgetQtObj2.setCurrentIndex(indexToSet)
        self.skipSearch = False

    def editItem(self, res=False):
        if not self.currentValue:
            return
        dialog = QtWidgets.QDialog()

        def accept():
            dialog.accept()

        def reject():
            dialog.reject()

        self.setViewObject()
        self.viewObj.loadIds([self.currentValue[0]])
        mainLay = QtWidgets.QVBoxLayout()
        utilsUi.setLayoutMarginAndSpacing(mainLay)
        mainLay.addWidget(self.viewObj)
        lay, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(accept)
        cancelButt.clicked.connect(reject)
        okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
        cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
        lay.setParent(None)
        mainLay.addLayout(lay)
        dialog.setLayout(mainLay)
        dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
        dialog.adjustSize()
        dialog.resize(1000, 750)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            valuesToUpdate = {}
            for fieldName, fieldObj in list(self.viewObj.fieldsChanged.items()):
                valuesToUpdate[fieldName] = fieldObj.value
            self.rpc.write(self.relation, valuesToUpdate, self.currentValue[0])
            if 'name' in valuesToUpdate:
                oldName = ''
                for val, objId in list(self.itemToIdRel.items()):
                    if objId == self.currentValue[0]:
                        oldName = val
                        break
                indexToReplace = self.availableItems.index(oldName)
                valToUpdate = str(valuesToUpdate['name'])
                self.availableItems[indexToReplace] = valToUpdate
                del self.itemToIdRel[oldName]
                self.itemToIdRel[valToUpdate] = self.currentValue[0]
                self.widgetQtObj2.clear()
                self.widgetQtObj2.addItems(self.availableItems)
                self.widgetQtObj2.setCurrentIndex(indexToReplace)
                self.valueTemplateChanged()

    def setViewObject(self):
        self.viewObj = self.odooConnector.initFormViewObj(self.relation, rpcObj=self.rpc)

    def indexChanged(self, res=False):
        currText = str(self.widgetQtObj2.currentText())
        if currText == 'Create and Edit...':
            dialog = QtWidgets.QDialog()

            def accept():
                dialog.accept()

            def reject():
                dialog.reject()

            self.setViewObject()
            self.viewObj.loadIds([])
            mainLay = self.viewObj.layout()
            lay, okButt, cancelButt = utilsUi.getButtonBox()
            okButt.clicked.connect(accept)
            cancelButt.clicked.connect(reject)
            okButt.setStyleSheet(constants.BUTTON_STYLE_OK)
            cancelButt.setStyleSheet(constants.BUTTON_STYLE_CANCEL)
            lay.setParent(None)
            mainLay.addLayout(lay)
            dialog.setLayout(mainLay)
            dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
            dialog.adjustSize()
            dialog.resize(800, dialog.height())
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                valuesToCreate = {}
                for fieldName, fieldObj in list(self.viewObj.interfaceFieldsDict.items()):
                    valuesToCreate[fieldName] = fieldObj.value
                res = self.rpc.create(self.relation, valuesToCreate)
                if res:
                    name = str(valuesToCreate.get('name', ''))
                    self.itemToIdRel[name] = res
                    self.availableItems = self.getItems(search=True)
                    self.widgetQtObj2.clear()
                    self.widgetQtObj2.addItems(self.availableItems)
                    if name in self.availableItems:
                        currentIndex = self.availableItems.index(name)
                        self.widgetQtObj2.setCurrentIndex(currentIndex)
                    self.currentValue = [self.itemToIdRel.get(name, False), currText]
                    self.valueTemplateChanged()
            else:
                self.widgetQtObj2.setCurrentIndex(0)
        elif not currText:
            self.widgetQtObj2.setCurrentIndex(0)
            self.currentValue = False
            self.valueTemplateChanged()
        else:
            self.currentValue = [self.itemToIdRel.get(currText, False), currText]
            if self.currentValue and self.editButton:
                self.editButton.setHidden(False)
            elif self.editButton:
                self.editButton.setHidden(True)
            self.valueTemplateChanged()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and not self.skipSearch:
            self.comboActivated()
        return super(Many2one, self).eventFilter(object, event)

    @property
    def value(self):
        try:
            if isinstance(self.currentValue, int):
                return self.currentValue
            if self.currentValue:
                return self.currentValue[0]
            return self.currentValue
        except Exception as ex:
            utils.logMessage('error', 'Error during getting value from many2one field %r: %r' % (self.fieldName, ex), 'value')

    @property
    def valueInterface(self):
        if self.currentValue:
            return self.currentValue[1]
        return ''

    def eraseValue(self):
        self.setValue(False)
