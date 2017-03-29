'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from parser.search_view import SearchView
from templateView import TemplateView
from utils_odoo_conn import utils
from utils_odoo_conn import constants
from PyQt4 import QtGui
from PyQt4 import QtCore


class TemplateSearchView(TemplateView):

    def __init__(self, rpcObject, activeLanguageCode='en_US'):
        super(TemplateSearchView, self).__init__(rpcObject, activeLanguageCode)
        self.viewType = 'search'
        self.readonly = True
        self.odooObjectName = ''
        self.viewName = ''
        self.viewId = False
        self.searchObj = None

    def initViewObj(self, odooObjectName, viewName, view_id):
        self.odooObjectName = odooObjectName
        self.viewName = viewName
        self.viewId = view_id
        super(TemplateSearchView, self).initViewObj(odooObjectName, viewName, view_id)
        self.fieldsViewDefinition
        self.searchObj = SearchView(self.arch, self.fieldsNameTypeRel)
        self.layout = self.searchObj.computeArch()
        self.addToObject()
