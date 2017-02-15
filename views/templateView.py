'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
from form_view import FormView
from utils import utils
from PyQt4 import QtGui
import copy
from docutils.nodes import field


class TemplateView(object):

    def __init__(self, rpcObject):
        self.rpcObject = rpcObject
        self.arch = ''  # xml view...
        self.model = ''     # 'product.product' / ...
        self.viewName = ''
        self.field_parent = ''
        self.viewtype = ''  # 'form' / 'search' / ...
        self.readonlyFields = []     # ['field1', 'field2']
        self.requiredFields = []    # ['field1', 'field2']
        self.fieldsNameTypeRel = {}
        self.fields = Objects()    # fields.fieldName
        self.buttons = Objects()    # buttons.fieldName
        self.objectsInit = copy.deepcopy(self.fields)
        self.fieldsChanged = {}     # {'fieldName' : fieldObj}
        self.mappingInterface = {}   # {'fieldName' : fieldObj}
        self.fieldDefaultVals = {}  # {'fieldName' : fieldval}
        self.readonly = False
        self.layout = QtGui.QHBoxLayout()
        self.activeIds = []

    def initViewObj(self, odooObjectName, viewName='', view_id=False, viewType='form'):
        if not viewType:
            viewType = self.viewType
        fieldsViewDefinition = self.rpcObject.fieldsViewGet(odooObjectName, view_id, viewType)
        self.arch = fieldsViewDefinition.get('arch', '')
        self.model = fieldsViewDefinition.get('model', '')
        self.startingFieldValues = fieldsViewDefinition.get('fields', {})
        self.viewName = fieldsViewDefinition.get('name', '')
        self.field_parent = fieldsViewDefinition.get('field_parent', '')
        self.fieldsNameTypeRel = self.rpcObject.fieldsGet(self.model, [])
        self.viewType = viewType
        if viewType == 'form':
            formObj = FormView(self.arch, self.fieldsNameTypeRel, self.rpcObject)
            self.layout = formObj.computeArch()
            self.mappingInterface = formObj.globalMapping
        elif viewType == 'tree_tree':
            pass
        elif viewType == 'tree_list':
            pass
        elif viewType == 'search':
            pass
        self.addToObject()
        self.setDefaults()

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in self.mappingInterface.items():
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
                obj.value_changed_signal.connect(self._valueChanged)
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def setDefaults(self):
        self.fieldDefaultVals = self.rpcObject.defaultGet(self.model, self.interfaceFieldsDict.keys())
        for fieldName, fieldVal in self.fieldDefaultVals.items():
            self.setValueField(fieldName, fieldVal)
        
    def setValueField(self, fieldName, fieldVal):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
            return
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
            utils.evaluateAttrs(fieldDict, readonlyModif)
            utils.evaluateAttrs(fieldDict, invisibleModif)
        
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}):
        if self.viewType in ['form', 'search'] and len(objIds) > 1:
            utils.launchMessage('You cannot load multiple ids on form or search view!', 'warning')
            return False
        if self.viewType == 'form':
            formId = False
            if objIds:
                formId = objIds[0]
                formVals = self.rpcObject.read(self.model, self.interfaceFieldsDict.keys(), [formId])
                for fieldName, fieldVal in formVals.items():
                    self.setValueField(fieldName, fieldVal)
            for fieldName, fieldVal in forceFieldValues.items():
                self.setValueField(fieldName, fieldVal)
            self._setFieldModifiers()
            for readonlyField, fieldAttr in readonlyFields.items():
                self.setReadonlyField(readonlyField, fieldAttr)
            for invisibleField, fieldAttr in invisibleFields.items():
                self.setInvisibleField(invisibleField, fieldAttr)
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
        fieldObj = self.interfaceFieldsDict.get(unicode(fieldName))
        changeResult = self._on_change(fieldObj.fieldName)
        changedValues = changeResult.get('value', {})
        for fieldNameFromServer, fieldValueFromServer in changedValues.items():
            fieldObj1 = self.interfaceFieldsDict.get(unicode(fieldNameFromServer))
            fieldObj1.setValue(fieldValueFromServer)

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
        allVals = self.getAllFieldsValues()
        allOnchanges = self.getAllOnChange()
        return self.rpcObject.on_change(self.model, self.activeIds, allVals, fieldName, allOnchanges, {})


class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()
