'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from .templateView import TemplateView


class TemplateTreeTreeView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US'):
        super(TemplateTreeTreeView, self).__init__(rpcObject, activeLanguageCode)
        self.field_parent = ''
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []

    def initViewObj(self, odooObjectName, viewName, view_id):
        self.field_parent = self.fieldsViewDefinition.get('field_parent', '')
        self.addToObject()
