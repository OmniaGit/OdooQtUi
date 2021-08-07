'''
Created on Jan 18, 2019

@author: mboscolo
'''
import os
import sys
import logging
import PySide2
from PySide2 import QtWidgets
from PySide2 import QtGui
from OdooQtUi.connector import MainConnector
from OdooQtUi.utils_odoo_conn import constants
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# dirname = os.path.dirname(PySide2.__file__)
# plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
# os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
#os.environ['QT_DEBUG_PLUGINS']='1'

app = QtWidgets.QApplication(sys.argv)

if __name__ == '__main__':
    constants.DEBUG = False
    odooConnector = MainConnector()
    import time
    ts = time.time()
    
    connectorObj = MainConnector()
    connectorObj.loginWithDial()

    def do_test():
        def tryForm(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False, idToLoad=False):
            tmplViewObj = connectorObj.initFormViewObj(odooObjectName, viewName, view_id, rpcObj, activeLanguage, useHeader, useChatter)
            if idToLoad:
                tmplViewObj.loadIds([idToLoad])
            return tmplViewObj

        def trySearchView(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', searchMode='ilike', allFieldsDef={}):
            return connectorObj.initSearchViewObj(odooObjectName, viewName, view_id, rpcObj, activeLanguage, searchMode, allFieldsDef)

        def tryListView(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', viewCheckBoxes={}, viewFilter=False, readonlyFields={}, invisibleFields={}, forceFieldValues={}, forceIds=False):
            tmplViewObj = connectorObj.initTreeListViewObject(odooObjectName, viewName, view_id, rpcObj, activeLanguage, viewCheckBoxes, viewFilter)
            if forceIds:
                tmplViewObj.loadIds(forceIds, forceFieldValues, readonlyFields, invisibleFields)
            else:
                tmplViewObj.loadForceEmptyIds(forceFieldValues, readonlyFields, invisibleFields)
            return tmplViewObj

        tmplViewObj = tryForm('sale.order', useChatter=False)
        #tmplViewObj = tryForm('product.product', 'plm.base.component', idToLoad=3572, useChatter=True)
        #tmplViewObj = tryListView('product.template', viewFilter=True)
#         lay = QtWidgets.QVBoxLayout()
#         lay.addWidget(tmplViewObj)
#         lay.setMargin(0)
#         lay.setContentsMargins(0,0,0,0)
#         dialog = QtWidgets.QDialog()
#         dialog.setLayout(lay)
#         dialog.exec_()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(tmplViewObj)
        scroll.setWidgetResizable(True)
        # tmplViewObj = tryForm('product.product', idToLoad=1345, useChatter=False)
        # viewCheckBoxes = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
        dialog = QtWidgets.QDialog()
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(scroll)
        #lay.setMargin(0)
        lay.setContentsMargins(20,20,20,20)
        dialog.setLayout(lay)
        dialog.resize(1200, 800)
        dialog.move(100, 100)
        dialog.exec_()

    do_test()
