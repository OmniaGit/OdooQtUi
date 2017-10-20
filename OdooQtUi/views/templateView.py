'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import copy
from PyQt4 import QtGui
from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.RPC.rpc import connectionObj


class TemplateView(QtGui.QWidget):

    def __init__(self, rpcObject, viewObj, activeLanguageCode='en_US'):
        super(TemplateView, self).__init__()
        self.rpcObject = rpcObject
        self.viewObj = viewObj
        self.fields = Objects()    # fields.fieldName
        self.buttons = Objects()    # buttons.fieldName
        self.mappingInterface = {}   # {'fieldName' : fieldObj}
        self.activeLanguageCode = activeLanguageCode    # 'en_US'
        self.fieldsChanged = {}     # {'fieldName' : fieldObj}
        self.formVals = {}

    @property
    def viewFilter(self):
        return self.viewObj.localViewFilter
    
    @property
    def model(self):
        return self.viewObj.odooModel
        
    @property
    def arch(self):
        return self.viewObj.odooArch

    @property
    def viewName(self):
        return self.viewObj.odooViewName

    @property
    def viewCheckBoxes(self):
        return self.viewObj.localViewCheckBoxes
    
    @property
    def viewId(self):
        return self.viewObj.odooViewId
    
    @property
    def fieldsNameTypeRel(self):
        return self.viewObj.odooFieldsNameTypeRel

    @property
    def viewType(self):
        return self.viewObj.localViewType

    @property
    def searchMode(self):
        return self.viewObj.localSearchMode
    
    @property
    def useHeader(self):
        return self.viewObj.useHeader

    @property
    def useChatter(self):
        return self.viewObj.useChatter
    
#     def searchForView(self, model, viewName):
#         viewIds = connectionObj.search('ir.ui.view', [('name', '=', viewName), ('model', '=', model), ('type', '=', self.viewType)])
#         if viewIds:
#             return viewIds[0]
#         utils.logMessage('warning', 'View with name %r and model %r nor found' % (viewName, model), 'searchForView')
#         return False

#     def initViewObj(self, odooObjectName, viewName='', view_id=False):
#         if not view_id and viewName:
#             view_id = self.searchForView(odooObjectName, viewName)
#         self.fieldsViewDefinition = self.rpcObject.fieldsViewGet(odooObjectName, view_id, self.viewType)
#         if self.fieldsViewDefinition:
#             self.arch = self.fieldsViewDefinition.get('arch', '')
#             self.model = self.fieldsViewDefinition.get('model', '')
#             self.viewName = self.fieldsViewDefinition.get('name', '')
#             self.viewId = self.fieldsViewDefinition.get('view_id', '')
#             self.fieldsNameTypeRel = self.fieldsViewDefinition.get('fields', '')

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in self.mappingInterface.items():
            if key.startswith(fieldIdentifier):
                newKey = key.replace(fieldIdentifier, '')
                self.interfaceFieldsDict[newKey] = obj
            elif key.startswith(buttonIdentifier):
                newKey = key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = obj
        return True

    def cleanFields(self, fieldsToClean=[]):
        try:
            if not fieldsToClean:
                for fieldObj in self.interfaceFieldsDict.values():
                    if fieldObj:
                        fieldObj.eraseValue()
        except Exception, ex:
            utils.logMessage("error", unicode(ex), 'cleanFields')

    def setFieldValues(self, fieldsDict):
        for fieldName, fieldVal in fieldsDict.items():
            self.setValueField(fieldName, fieldVal)

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
    def loadIds(self, objIds=[], forceFieldValues={}, readonlyFields={}, invisibleFields={}, fieldsToRead=[], skipRemoveNootebook=False):
        self.activeIds = objIds
        if not fieldsToRead:
            fieldsToRead = self.interfaceFieldsDict.keys()
        self.objectsInit = copy.copy(self.fields)

    def isReadonly(self):
        return self.readonly

    def setReadonly(self, val=False):
        for fieldObj in self.interfaceFieldsDict.values():
            fieldObj.setReadonly(val)
        if not val:
            self._setFieldModifiers()

#     @property
#     def QtInterface(self):
#         return self.layout

#     @property
#     def xmlOdooView(self):
#         return self.arch

    def getAllFieldsValues(self):
        outDict = {}
        for fieldName, fieldObject in self.interfaceFieldsDict.items():
            outDict[fieldName] = fieldObject.value
        return outDict

    def getAllRequiredFieldsValues(self):
        outDict = {}
        for fieldName, fieldObject in self.requiredFields.items():
            outDict[fieldName] = fieldObject.value
        return outDict

    @property
    def interfaceFieldsDict(self):
        return self.fields.__dict__

    def setUserLanguage(self, langCode):
        self.activeLanguageCode = langCode


class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()

    def getFieldObj(self, fieldName):
        return self.__dict__.get(fieldName)
