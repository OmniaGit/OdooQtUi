'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
from PySide2 import QtCore
from PySide2.QtCore import QObject


from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.views.parser.search_view import SearchView
from OdooQtUi.views.templateView import TemplateView


class TemplateSearchView(TemplateView, QtCore.QObject):
    filter_changed_signal = QtCore.Signal(list)         # Used by "SearchView" to return current filter
    out_filter_change_signal = QtCore.Signal(list)      # Used by parent view to get the current odoo list filter

    def __init__(self,
                 odooConnector,
                 viewObject,
                 allFieldsDef={}):
        #
        super(TemplateSearchView, self).__init__(odooConnector=odooConnector,
                                                 viewObj=viewObject)
        #
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
        utils.logDebug('New filter %r' % (filterList), '_filterChanged')
        self.out_filter_change_signal.emit(filterList)
