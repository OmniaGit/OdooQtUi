'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
from form_view import FormView
from tree_list import TreeViewList
from utils import utils
from PyQt4 import QtGui
from PyQt4 import QtCore
import copy
import logging

# 
# 
# class Form(TemplateView):
#     pass
# 
# class Tree(TemplateView):
#     pass


class TemplateView(object):

    def __init__(self, rpcObject, activeLanguageCode='en_US', availableLanguages={'en_US': 'English'}):
        self.rpcObject = rpcObject
        self.arch = ''  # xml view...
        self.model = ''     # 'product.product' / ...
        self.viewName = ''
        self.fieldsNameTypeRel = {}
        self.fields = Objects()    # fields.fieldName
        self.buttons = Objects()    # buttons.fieldName
        self.mappingInterface = {}   # {'fieldName' : fieldObj}
        self.layout = QtGui.QVBoxLayout()
        self.activeLanguageCode = activeLanguageCode    # 'en_US'
        self.availableLanguages = availableLanguages    # {'en_US': 'English', ...}

    @utils.timeit
    def initViewObj(self, odooObjectName, viewName='', view_id=False):
        self.fieldsViewDefinition = self.rpcObject.fieldsViewGet(odooObjectName, view_id, self.viewType)
        self.arch = self.fieldsViewDefinition.get('arch', '')
        self.model = self.fieldsViewDefinition.get('model', '')
        self.viewName = self.fieldsViewDefinition.get('name', '')
        self.viewId = self.fieldsViewDefinition.get('view_id', '')
        self.fieldsNameTypeRel = self.fieldsViewDefinition.get('fields', '')

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in self.mappingInterface.items():
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
                obj.value_changed_signal.connect(self._valueChanged)
                obj.translation_clicked.connect(self.translationDial)
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def setValueField(self, fieldName, fieldVal):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            fieldObj.setValue(fieldVal)
        headerField = 'header_' + fieldName
        fieldObj = self.interfaceFieldsDict.get(headerField, None)
        if fieldObj:
            fieldObj.setValue(fieldVal)

    def setReadonlyField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setReadonlyField')
            return
        fieldObj.setReadonly(val)

    def setInvisibleField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setInvisibleField')
            return
        fieldObj.setInvisible(val)

    def _setFieldModifiers(self):
        fieldDict = self.interfaceFieldsDict
        for fieldObj in fieldDict.values():
            readonlyModif = fieldObj.modifiers.get('readonly', {})
            invisibleModif = fieldObj.modifiers.get('invisible', {})
            if readonlyModif:
                fieldObj.setReadonly(utils.evaluateAttrs(fieldDict, readonlyModif))
            if invisibleModif:
                fieldObj.setInvisible(utils.evaluateAttrs(fieldDict, invisibleModif))

    def _setButtonsModifiers(self):
        fieldDict = self.interfaceFieldsDict
        for buttonObj in self.buttons.__dict__.values():
            readonlyModif = buttonObj.modifiers.get('readonly', {})
            invisibleModif = buttonObj.modifiers.get('invisible', {})
            if readonlyModif:
                buttonObj.setReadonly(utils.evaluateAttrs(fieldDict, readonlyModif))
            if invisibleModif:
                buttonObj.setInvisible(utils.evaluateAttrs(fieldDict, invisibleModif))

    @utils.timeit
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        self.activeIds = objIds
        if self.viewType in ['form', 'search'] and len(objIds) > 1:
            utils.launchMessage('You cannot load multiple ids on form or search view!', 'warning')
            return False
        if self.viewType == 'form':
            formId = False
            if objIds:
                formId = objIds[0]
                formVals = self.rpcObject.read(self.model, self.interfaceFieldsDict.keys(), [formId], {'lang': self.activeLanguageCode})
                if not formVals:
                    utils.logMessage('warning', 'No values found for id %r and model %r' % (formId, self.model), 'loadIds')
                    formId = False
                    self.skipOnChange = True
                    self.setDefaults()
                    self.skipOnChange = False
                else:
                    self.skipOnChange = True
                    formVals = formVals[0]
                    for fieldName, fieldVal in formVals.items():
                        self.setValueField(fieldName, fieldVal)
                    self.skipOnChange = False
            for fieldName, fieldVal in forceFieldValues.items():
                self.setValueField(fieldName, fieldVal)
            self._setFieldModifiers()
            for readonlyField, fieldAttr in readonlyFields.items():
                self.setReadonlyField(readonlyField, fieldAttr)
            for invisibleField, fieldAttr in invisibleFields.items():
                self.setInvisibleField(invisibleField, fieldAttr)
            self._setButtonsModifiers()
        self.objectsInit = copy.copy(self.fields)

    def isReadonly(self):
        return self.readonly

    def setReadonly(self, val=False):
        for fieldObj in self.interfaceFieldsDict.values():
            if val:
                fieldObj.setReadonly(True)
            else:
                # Abilitare solo quelli che erano abilitati dall'inizio
                pass

    @property
    def QtInterface(self):
        return self.layout

    @property
    def xmlOdooView(self):
        return self.arch

    def getAllFieldsValues(self):
        outDict = {}
        for fieldName, fieldObject in self.interfaceFieldsDict.items():
            outDict[fieldName] = fieldObject.currentValue
        return outDict

    def getAllOnChange(self):
        outDict = {}
        for fieldName, fieldObject in self.interfaceFieldsDict.items():
            outDict[fieldName] = fieldObject.on_change
        return outDict

    def _valueChanged(self, fieldName):
        fieldName = unicode(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in interfacefieldsdict' % (fieldName), '_valueChanged')
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        for fieldNameFromServer, fieldValueFromServer in changedValues.items():
            fieldObj1 = self.interfaceFieldsDict.get(unicode(fieldNameFromServer))
            fieldObj1.setValue(fieldValueFromServer)
        self.fieldsChanged[fieldName] = fieldObj

    @property
    def interfaceFieldsDict(self):
        return self.fields.__dict__

    def _on_change(self, fieldName):
        '''
            [
            [id],
            {all values},
            launcher field name,
            {All form on_changes},
            {context},
            ]
        '''
        if self.skipOnChange:
            return {}
        allVals = self.getAllFieldsValues()
        allOnchanges = self.getAllOnChange()
        return self.rpcObject.on_change(self.model, self.activeIds, allVals, fieldName, allOnchanges, {})

    def setLanguage(self, langCode):
        if langCode not in self.availableLanguages:
            logging.warning('langCode %r not present in available languages.' % (langCode))
            return
        self.activeLanguageCode = langCode
        logging.info('Forced language as %r' % (self.availableLanguages.get(langCode, '')))

    def translationDial(self, fieldName):
        fieldName = unicode(fieldName)
        def acceptTransDial():
            translationDial.accept()

        def rejectTransDial():
            translationDial.reject()

        translationDial = QtGui.QDialog()
        mainLay = QtGui.QVBoxLayout()
        tableWidget = QtGui.QTableWidget()
        model = self.model
        if model == 'product.product':
            model = 'product.template'
        translationName = unicode(model + ',' + fieldName)
        filterList = [('res_id', '=', self.activeIds[0]),
                      ('name', '=', translationName)
                      ]
        headers = ['Source value', 'Translated Value', 'Language', 'Name']
        fieldNames = ['source', 'translated', 'lang', 'name']
        values = []
        translationObj = 'ir.translation'
        res = self.rpcObject.readSearch(translationObj, ['src', 'value', 'lang'], filterList)
        for elemDict in res:
            src = elemDict.get('src', '')
            value = elemDict.get('value', '')
            lang = elemDict.get('lang', '')
            values.append([src, value, lang, translationName])
        tableFlags = {0: QtCore.Qt.ItemIsEnabled,
                      2: QtCore.Qt.ItemIsEnabled,
                      3: QtCore.Qt.ItemIsEnabled,
                      }
        utils.commonPopulateTable(headers, values, tableWidget, tableFlags)
        mainLay.addWidget(tableWidget)
        layButtons, okButt, cancelButt = utils.getButtonBox()
        okButt.clicked.connect(acceptTransDial)
        cancelButt.clicked.connect(rejectTransDial)
        mainLay.addLayout(layButtons)
        translationDial.setLayout(mainLay)
        translationDial.resize(800, 400)
        tableWidget.resizeColumnsToContents()
        tableWidget.horizontalHeader().setStretchLastSection(True)
        if translationDial.exec_() == QtGui.QDialog.Accepted:
            rowsDict = utils.getRowsFromTableWidget(tableWidget, 'dict', fieldNames)
            for rowDict in rowsDict.values():
                elemId = False
                translated = unicode(rowDict.get('translated', ''))
                source = unicode(rowDict.get('source', ''))
                lang = unicode(rowDict.get('lang', ''))
                for elem in res:
                    sourceRel = elem.get('src', '')
                    langRel = elem.get('lang', '')
                    if source == sourceRel and lang == langRel:
                        elemId = elem.get('id', False)
                        break
                if elemId:
                    self.rpcObject.write(translationObj, {'value': translated}, [elemId])
                    if lang == self.activeLanguageCode:
                        self.setValueField(fieldName, translated)


class TemplateSearchView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US', availableLanguages={'en_US': 'English'}):
        super(TemplateSearchView, self).__init__(rpcObject, activeLanguageCode, availableLanguages)
        self.viewType = 'search'
        self.readonly = True

    def initViewObj(self, odooObjectName, viewName, view_id):
        super(TemplateSearchView, self).initViewObj(odooObjectName, viewName, view_id)
        self.addToObject()


class TemplateFormView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US', availableLanguages={'en_US': 'English'}):
        super(TemplateFormView, self).__init__(rpcObject, activeLanguageCode, availableLanguages)
        self.requiredFields = []    # ['field1', 'field2']
        self.readonlyFields = []     # ['field1', 'field2']
        self.viewType = 'form'
        self.objectsInit = copy.deepcopy(self.fields)
        self.fieldsChanged = {}     # {'fieldName' : fieldObj}
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.skipOnChange = False
        self.readonly = False
        self.activeIds = []     # must be one

    def initViewObj(self, odooObjectName, viewName, view_id):
        super(TemplateFormView, self).initViewObj(odooObjectName, viewName, view_id)
        self.startingFieldValues = self.fieldsViewDefinition.get('fields', {})
        formObj = FormView(self.arch, self.fieldsNameTypeRel, self.rpcObject)
        self.layout = formObj.computeArch()
        self.mappingInterface = formObj.globalMapping
        self.addToObject()

    @utils.timeit
    def setDefaults(self):
        self.fieldDefaultVals = self.rpcObject.defaultGet(self.model, self.interfaceFieldsDict.keys())
        for fieldName, fieldVal in self.fieldDefaultVals.items():
            self.setValueField(fieldName, fieldVal)


class TemplateTreeTreeView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US', availableLanguages={'en_US': 'English'}):
        super(TemplateTreeTreeView, self).__init__(rpcObject, activeLanguageCode, availableLanguages)
        self.field_parent = ''
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []

    def initViewObj(self, odooObjectName, viewName, view_id):
        super(TemplateTreeTreeView, self).initViewObj(odooObjectName, viewName, view_id)
        self.field_parent = self.fieldsViewDefinition.get('field_parent', '')
        self.addToObject()


class TemplateTreeListView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US', availableLanguages={'en_US': 'English'}):
        super(TemplateTreeListView, self).__init__(rpcObject, activeLanguageCode, availableLanguages)
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []

    def initViewObj(self, odooObjectName, viewName, view_id):
        super(TemplateTreeListView, self).initViewObj(odooObjectName, viewName, view_id)
        self.treeObj = TreeViewList(self.arch, self.fieldsNameTypeRel, self.rpcObject)
        self.layout = self.treeObj.computeArch()
        self.mappingInterface = self.treeObj.globalMapping
        self.addToObject()


class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()
