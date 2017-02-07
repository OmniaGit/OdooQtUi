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
        self.model = '' # 'product.product' / ...
        self.viewName = ''  
        self.field_parent = ''  
        self.viewtype = ''  # 'form' / 'search' / ...
        self.readonlyFields = []     # ['field1', 'field2']
        self.requiredFields = []    # ['field1', 'field2']
        self.fieldsNameTypeRel = {}
        self.objects = Objects()    # objects.fieldName
        self.objectsInit = copy.deepcopy(self.objects)
        self.fieldsChanged = {} # {'fieldName' : fieldObj}
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
            formObj = FormView(self.arch, self.fieldsNameTypeRel)
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
        for key, val in self.mappingInterface.items():
            self.objects.__dict__[key] = val
        
    def loadIds(self, objIds):
        if self.viewType in ['form', 'search'] and len(objIds) > 1:
            utils.launchMessage('You cannot load multiple ids on form or search view!', 'warning')

    def isReadonly(self):
        return self.readonly

    def setReadonly(self, val=False):
        pass

    def getQtInterface(self):
        return self.layout
        
    def getXml(self):
        return self.arch

    def getRequiredFields(self):
        return self.requiredFields

    def getReadonlyFields(self):
        return self.readonlyFields

    def getStartingFieldValues(self):
        return self.startingFieldValues
    
class Objects(object):
    def __init__(self):
        return super(Objects, self).__init__()

    
