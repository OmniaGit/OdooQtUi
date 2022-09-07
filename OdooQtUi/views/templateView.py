'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
import copy
from PySide2 import QtWidgets
from OdooQtUi.utils_odoo_conn import utils


class TemplateView(QtWidgets.QWidget):

    def __init__(self,
                 odooConnector,
                 viewObj):
        super(TemplateView, self).__init__()
        self.odooConnector = odooConnector
        self.viewObj = viewObj
        self.fields = Objects()     # fields.fieldName
        self.buttons = Objects()    # buttons.fieldName
        self.mappingInterface = {}  # {'fieldName' : fieldObj}
        self.activeLanguage = odooConnector.activeLanguage    # 'en_US'
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

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, obj in list(self.mappingInterface.items()):
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
                for fieldObj in list(self.interfaceFieldsDict.values()):
                    if fieldObj:
                        fieldObj.eraseValue()
        except Exception as ex:
            utils.logMessage("error", str(ex), 'cleanFields')

    def setFieldValues(self, fieldsDict):
        for fieldName, fieldVal in list(fieldsDict.items()):
            self.setValueField(fieldName, fieldVal)

    def setValueField(self, fieldName, fieldVal):
        fieldObj = self.interfaceFieldsDict.get(fieldName, None)
        if not fieldObj:
            utils.logMessage('warning', 'Field %r not found in the local fields' % (fieldName), 'setValueField')
        else:
            if fieldObj.fieldType == 'binary':
                file_name = ''
                if fieldObj.fileName:
                    file_name = self.formVals.get(fieldObj.fileName, '')
                fieldObj.setValue(fieldVal, file_name)
                return
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
        for fieldObj in list(fieldDict.values()):
            readonlyModif = fieldObj.modifiers.get('readonly', {})
            invisibleModif = fieldObj.modifiers.get('invisible', {})
            if readonlyModif:
                fieldObj.setReadonly(utils.evaluateAttrs(fieldDict, readonlyModif))
            if invisibleModif:
                fieldObj.setInvisible(utils.evaluateAttrs(fieldDict, invisibleModif))

    def _setButtonsModifiers(self):
        fieldDict = self.interfaceFieldsDict
        for buttonObj in list(self.buttons.__dict__.values()):
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
            fieldsToRead = list(self.interfaceFieldsDict.keys())
        self.objectsInit = copy.copy(self.fields)

    def isReadonly(self):
        return self.readonly

    def setReadonly(self, val=False):
        for fieldObj in list(self.interfaceFieldsDict.values()):
            fieldObj.setReadonly(val)
        if not val:
            self._setFieldModifiers()

    def getAllFieldsValues(self):
        outDict = {}
        for fieldName, fieldObject in list(self.interfaceFieldsDict.items()):
            outDict[fieldName] = fieldObject.value
        return outDict

    def getFieldValue(self, fieldName):
        fieldObj = self.interfaceFieldsDict.get(fieldName)
        if fieldObj:
            return fieldObj.value
        return ''

    def getAllRequiredFieldsValues(self):
        outDict = {}
        for fieldName, fieldObject in list(self.requiredFields.items()):
            outDict[fieldName] = fieldObject.value
        return outDict

    @property
    def interfaceFieldsDict(self):
        return self.fields.__dict__

    def setUserLanguage(self, langCode):
        self.activeLanguage = langCode


class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()

    def getFieldObj(self, fieldName):
        return self.__dict__.get(fieldName)
