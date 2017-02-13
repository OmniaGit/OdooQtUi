'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
from form_view import FormView
from utils import utils
from PyQt4 import QtGui
import copy


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
        self.fields = Objects()    # objects.fieldName
        self.buttons = Objects()
        self.objectsInit = copy.deepcopy(self.fields)
        self.fieldsChanged = {}     # {'fieldName' : fieldObj}
        self.mappingInterface = {}   # {'fieldName' : fieldObj}
        self.readonly = False
        self.layout = QtGui.QHBoxLayout()

    def initViewObj(self, odooObjectName, viewName='', view_id=False, viewType='form', startingFieldValues=[], clientReadonlyFields=[], idsToLoad=[]):
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
            self.mappingInterface = formObj.globalMapping
            self.layout = formObj.computeArch()
        elif viewType == 'tree_tree':
            pass
        elif viewType == 'tree_list':
            pass
        elif viewType == 'search':
            pass
        self.addToObject()

    def addToObject(self):
        fieldIdentifier = 'field_'
        buttonIdentifier = 'button_'
        for key, val in self.mappingInterface.items():
            if key.startswith(fieldIdentifier):
                newKey =key.replace(fieldIdentifier, '')
                self.fields.__dict__[newKey] = val
            elif key.startswith(buttonIdentifier):
                newKey =key.replace(buttonIdentifier, '')
                self.buttons.__dict__[newKey] = val
        return True

    def loadIds(self, objIds):
        if self.viewType in ['form', 'search'] and len(objIds) > 1:
            utils.launchMessage('You cannot load multiple ids on form or search view!', 'warning')
            return False
        # Copy objects to self.objectsInit
        # Modify self.layout

    def isReadonly(self):
        return self.readonly

    def setReadonly(self, val=False):
        pass

    @property
    def QtInterface(self):
        return self.layout

    @property
    def xmlOdooView(self):
        return self.arch


class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()
