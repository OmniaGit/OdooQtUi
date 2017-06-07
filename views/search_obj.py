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
from PyQt4.QtCore import QObject
import json


class TemplateSearchView(TemplateView, QObject):

    filter_changed_signal = QtCore.pyqtSignal(list)         # Used by "SearchView" to return current filter
    out_filter_change_signal = QtCore.pyqtSignal(list)      # Used by parent view to get the current odoo list filter

    def __init__(self, rpcObject, activeLanguageCode='en_US', searchMode='ilike'):
        super(TemplateSearchView, self).__init__(rpcObject, activeLanguageCode)
        self.viewType = 'search'
        self.readonly = True
        self.odooObjectName = ''
        self.viewName = ''
        self.viewId = False
        self.searchObj = None
        self.searchMode = searchMode
        self.currentFilterList = []
        self.filter_changed_signal.connect(self._filterChanged)

    def initViewObj(self, odooObjectName, viewName='', view_id=False, allFieldsDef={}):
        self.odooObjectName = odooObjectName
        self.viewName = viewName
        self.viewId = view_id
        super(TemplateSearchView, self).initViewObj(odooObjectName, viewName, view_id)
        self.allFieldsDef = allFieldsDef
        self.searchObj = SearchView(self.arch, self.fieldsNameTypeRel, parent=self, searchMode=self.searchMode, advancedFilterFields=allFieldsDef)
        self.layout = self.searchObj.computeArch()
        self.addToObject()

    def _filterChanged(self, filterList):
        self.currentFilterList = []
        currentFilterList = []
        operatorsOrdered = []
        for conditionTuple in filterList:
            if isinstance(conditionTuple, (str, unicode)):
                operatorsOrdered.append(conditionTuple)
            else:
                currentFilterList.append(conditionTuple)
        self.currentFilterList.extend(operatorsOrdered)
        self.currentFilterList.extend(currentFilterList)
        self.out_filter_change_signal.emit(self.currentFilterList)

