'''
Created on 24 Mar 2017

@author: dsmerghetto
'''

from PyQt4 import QtCore
from PyQt4.QtCore import QObject

from parser.search_view import SearchView
from templateView import TemplateView


class TemplateSearchView(TemplateView, QObject):

    filter_changed_signal = QtCore.pyqtSignal(list)         # Used by "SearchView" to return current filter
    out_filter_change_signal = QtCore.pyqtSignal(list)      # Used by parent view to get the current odoo list filter

    def __init__(self, rpcObject, viewObject, activeLanguageCode='en_US', allFieldsDef={}):
        super(TemplateSearchView, self).__init__(rpcObject, viewObject, activeLanguageCode)
        self.readonly = True
        self.currentFilterList = []
        self.filter_changed_signal.connect(self._filterChanged)
        self._initViewObj(allFieldsDef)

    def _initViewObj(self, allFieldsDef={}):
        self.allFieldsDef = allFieldsDef
        self.searchObj = SearchView(self.arch, self.fieldsNameTypeRel, parent=self, searchMode=self.searchMode, advancedFilterFields=allFieldsDef)
        layout = self.searchObj.computeArch()
        self.addToObject()
        self.setLayout(layout)

    def _filterChanged(self, filterList):
        print 'New filter %r' % (filterList)
        self.out_filter_change_signal.emit(filterList)

