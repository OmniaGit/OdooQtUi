'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''
from form.form_view import FormView

class TemplateView(object):
    
    def __init__(self, rpcObject):
        self.rpcObject = rpcObject
        
    def getView(self, odooObjectName, viewName='', view_id=False, viewType='form', startingFieldValues=[], clientReadonlyFields=[], idsToLoad=[]):
        if not viewType:
            viewType = self.viewType
        fieldsViewDefinition = self.rpcObject.fieldsViewGet(odooObjectName, view_id, viewType)
        arch = fieldsViewDefinition.get('arch', '')
        model = fieldsViewDefinition.get('model', '')
        fields = fieldsViewDefinition.get('fields', {})
        viewName = fieldsViewDefinition.get('name', '')
        field_parent = fieldsViewDefinition.get('field_parent', '')
        if viewType == 'form':
            formObj = FormView(arch, model, fields, viewName, field_parent)
            formObj.computeArch()
        elif viewType == 'tree_tree':
            pass
        elif viewType == 'tree_list':
            pass
        elif viewType == 'search':
            pass
        
        
        
        