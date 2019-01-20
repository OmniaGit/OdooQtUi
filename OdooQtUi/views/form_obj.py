'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import copy
from PySide2 import QtGui
from PySide2 import QtCore


from OdooQtUi.views.parser.form_view import FormView
from OdooQtUi.views.templateView import TemplateView
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi


class TemplateFormView(TemplateView):

    def __init__(self, rpcObject, viewObj, activeLanguageCode='en_US', odooConnector=None):
        super(TemplateFormView, self).__init__(rpcObject, viewObj, activeLanguageCode)
        self.requiredFields = {}
        self.readonlyFields = {}
        self.invisibleFields = {}
        self.odooConnector = odooConnector
        self.objectsInit = copy.deepcopy(self.fields)
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.skipOnChange = False
        self.readonly = False
        self.activeIds = []     # must be one
        self._initViewObj()

    def _initViewObj(self):
        if self.fieldsNameTypeRel:
            self.startingFieldValues = self.fieldsNameTypeRel.get('fields', {})
            self.formObj = FormView(self.arch,
                                    self.fieldsNameTypeRel,
                                    self.rpcObject,
                                    self.useHeader,
                                    self.useChatter,
                                    self.odooConnector)
            self.formObj.nootebook_changed_signal.connect(self.updateDataStructure)
            layout = self.formObj.computeArch()
            self.mappingInterface = self.formObj.globalMapping
            self.addToObject()
            self._setFieldModifiers()
            oldLay = self.layout()
            if oldLay:
                del oldLay
            self.setLayout(layout)
        else:
            utils.logMessage('warning', 'Unable to get fields view definition!', '_initViewObj')

    def updateDataStructure(self, pageIndex=0):
        utils.logDebug('compute Nootebook fields: %r' % (pageIndex), 'updateDataStructure')
        if pageIndex > 0 and pageIndex in self.formObj.nootebookFieldsToCompute:
            dictFieldsToUpdate = self.formObj.nootebookFieldsToCompute[pageIndex]
            fieldNamesToUpdate = list(dictFieldsToUpdate.keys())
            self.loadIds(self.activeIds, {}, {}, {}, fieldNamesToUpdate, True)

    def setDefaults(self, fieldsToRead=[]):
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        self.fieldDefaultVals = self.rpcObject.defaultGet(self.model, fieldsToRead)
        self.skipOnChange = True
        for fieldName, fieldVal in list(self.fieldDefaultVals.items()):
            self.setValueField(fieldName, fieldVal)
        self.skipOnChange = False

    def removeNootebookFields(self, fieldsToRead):
        mainDict = {}
        for fieldsDict in list(self.formObj.nootebookFieldsToCompute.values()):
            mainDict.update(fieldsDict)
        for fieldName in list(mainDict.keys()):
            if fieldName in fieldsToRead:
                fieldsToRead.remove(fieldName)
        return fieldsToRead

    @utils.timeit
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}, fieldsToRead=[], skipRemoveNootebook=False):
        if objIds is None or not objIds:
            objIds = []
        if isinstance(objIds, int):
            objIds = [objIds]
        self.activeIds = objIds
        if not fieldsToRead:
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        if not skipRemoveNootebook:
            fieldsToRead = self.removeNootebookFields(fieldsToRead)
        if len(objIds) > 1:
            utilsUi.launchMessage('You cannot load multiple ids on form or search view!', 'warning')
            return False
        formId = False
        if objIds:
            formId = objIds[0]
            formVals = self.rpcObject.read(self.model, fieldsToRead, [formId], {'lang': self.activeLanguageCode})
            if not formVals:
                utils.logMessage('warning', 'No values found for id %r and model %r' % (formId, self.model), 'loadIds')
                formId = False
                self.skipOnChange = True
                self.setDefaults()
                self.skipOnChange = False
            else:
                self.skipOnChange = True
                self.formVals = formVals[0]
                for fieldName, fieldVal in list(self.formVals.items()):
                    self.setValueField(fieldName, fieldVal)
                    self.setFieldParentAttrs(fieldName)
                self.skipOnChange = False
        else:
            self.setDefaults(fieldsToRead)
        for fieldName, fieldVal in list(forceFieldValues.items()):
            self.setValueField(fieldName, fieldVal)
        self._setFieldModifiers()
        for readonlyField, fieldAttr in list(readonlyFields.items()):
            self.setReadonlyField(readonlyField, fieldAttr)
        for invisibleField, fieldAttr in list(invisibleFields.items()):
            self.setInvisibleField(invisibleField, fieldAttr)
        self._setButtonsModifiers()
        self.objectsInit = copy.copy(self.fields)

    def setFieldParentAttrs(self, fieldName):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            fieldObj.setParentAttrs(self.activeIds, self.model)

    def _setFieldModifiers(self):
        fieldDict = self.interfaceFieldsDict
        for fieldObj in list(fieldDict.values()):
            readonlyModif = fieldObj.modifiers.get('readonly', {})
            invisibleModif = fieldObj.modifiers.get('invisible', {})
            if readonlyModif:
                val = utils.evaluateAttrs(fieldDict, readonlyModif)
                fieldObj.setReadonly(val)
                self.commonEval(val, self.readonlyFields, fieldObj)
            if invisibleModif:
                val = utils.evaluateAttrs(fieldDict, invisibleModif)
                fieldObj.setInvisible(val)
                self.commonEval(val, self.invisibleFields, fieldObj)
            if fieldObj.required:
                self.requiredFields[fieldObj.fieldName] = fieldObj

    def checkRequiredFieldsEvaluated(self, showMessage=False):
        fieldsToEvaluate = []
        message = 'These required fields needs to be evaluated:'
        for fieldObject in list(self.requiredFields.values()):
            if not fieldObject.value and not isinstance(fieldObject.value, (int, float)):
                fieldsToEvaluate.append(fieldObject.fieldStringInterface)
                message = message + '\n %r' % (fieldObject.fieldStringInterface)
        if showMessage and fieldsToEvaluate:
            utilsUi.launchMessage(message, 'warning')
        return fieldsToEvaluate

    def setInvisibleField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setInvisibleField')
            return
        fieldObj.setInvisible(val)
        self.commonEval(val, self.invisibleFields, fieldObj)

    def setReadonlyField(self, fieldName, val=False):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setReadonlyField')
            return
        fieldObj.setReadonly(val)
        self.commonEval(val, self.readonlyFields, fieldObj)

    def commonEval(self, val, localDict, fieldObj):
        if val:
            localDict[fieldObj.fieldName] = fieldObj
        else:
            if fieldObj.fieldName in list(localDict.keys()):
                del localDict[fieldObj.fieldName]

    def getAllOnChange(self):
        outDict = {}
        for fieldName, fieldObject in list(self.interfaceFieldsDict.items()):
            outDict[fieldName] = fieldObject.on_change
        return outDict

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

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in list(self.mappingInterface.items()):
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
                obj.value_changed_signal.connect(self._valueChanged)
                obj.translation_clicked.connect(self.translationDial)
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def _valueChanged(self, fieldName):
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in interfacefieldsdict' % (fieldName), '_valueChanged')
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        for fieldNameFromServer, fieldValueFromServer in list(changedValues.items()):
            fieldObj1 = self.interfaceFieldsDict.get(str(fieldNameFromServer))
            fieldObj1.setValue(fieldValueFromServer)
        self.fieldsChanged[fieldName] = fieldObj
        self._setFieldModifiers()

    def translationDial(self, fieldName):
        if not self.activeIds:
            utilsUi.launchMessage('Translations are available only on already created records.', 'warning')
            return
        fieldName = str(fieldName)
        fieldObj = self.interfaceFieldsDict.get(fieldName)

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
        translationName = str(model + ',' + fieldName)
        filterList = [('res_id', '=', self.activeIds[0]),
                      ('name', '=', translationName)
                      ]
        headers = ['Source value', 'Translated Value', 'Language', 'Name']
        fieldNames = ['source', 'translated', 'lang', 'name']
        values = []
        translationObj = 'ir.translation'
        res = self.rpcObject.readSearch(translationObj, ['src', 'value', 'lang'], filterList)
        if not res:
            res = []
            installedLangs = self.rpcObject.readSearch('res.lang', ['code', 'name'], [('active', '=', True)])
            for resDict in installedLangs:
                code = resDict.get('code', '')
                createDict = {
                    'type': 'model',
                    'value': fieldObj.value,
                    'state': 'translated',
                    'module': '',
                    'res_id': self.activeIds[0],
                    'name': translationName,
                    'src': fieldObj.value,
                    'lang': code,
                }
                transId = self.rpcObject.create(translationObj, createDict)
                createDict['id'] = transId
                res.append(createDict)
        for elemDict in res:
            src = elemDict.get('src', '')
            value = elemDict.get('value', '')
            lang = elemDict.get('lang', '')
            values.append([src, value, lang, translationName])
        tableFlags = {1: QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable,
                      }
        utilsUi.commonPopulateTable(headers, values, tableWidget, tableFlags)
        mainLay.addWidget(tableWidget)
        layButtons, okButt, cancelButt = utilsUi.getButtonBox()
        okButt.clicked.connect(acceptTransDial)
        cancelButt.clicked.connect(rejectTransDial)
        mainLay.addLayout(layButtons)
        translationDial.setLayout(mainLay)
        translationDial.resize(800, 400)
        tableWidget.resizeColumnsToContents()
        tableWidget.horizontalHeader().setStretchLastSection(True)
        if translationDial.exec_() == QtGui.QDialog.Accepted:
            rowsDict = utils.getRowsFromTableWidget(tableWidget, 'dict', fieldNames)
            for rowDict in list(rowsDict.values()):
                elemId = False
                translated = str(rowDict.get('translated', ''))
                source = str(rowDict.get('source', ''))
                lang = str(rowDict.get('lang', ''))
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

