'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from parser.tree_list import TreeViewList
from templateView import TemplateView
from utils import utils
from utils import constants
from PyQt4 import QtGui
from PyQt4 import QtCore


class TemplateTreeTreeView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US'):
        super(TemplateTreeTreeView, self).__init__(rpcObject, activeLanguageCode)
        self.field_parent = ''
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []

    def initViewObj(self, odooObjectName, viewName, view_id):
        super(TemplateTreeTreeView, self).initViewObj(odooObjectName, viewName, view_id)
        self.field_parent = self.fieldsViewDefinition.get('field_parent', '')
        self.addToObject()