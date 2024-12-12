# -*- coding: utf-8 -*-
'''
Created on Jan 18, 2019

@author: mboscolo
'''
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from PySide6 import QtWidgets
from OdooQtUi.connector import MainConnector
from OdooQtUi.utils_odoo_conn import constants
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


app = QtWidgets.QApplication(sys.argv)

if __name__ == '__main__':
    constants.DEBUG = False
    odooConnector = MainConnector()
    import time
    ts = time.time()
    
    connectorObj = MainConnector(app_name="Test_odooQtUi",
                                 contextUser={'odooPLM': True})
    if not connectorObj.loginFromStorage():
        connectorObj.loginWithDial()

    def do_test():
        def tryForm(odooObjectName,
                    viewName='',
                    view_id=False,
                    useHeader=False,
                    useChatter=False,
                    idToLoad=False):
            tmplViewObj = connectorObj.initFormViewObj(odooObjectName=odooObjectName,
                                                       viewName=viewName,
                                                       view_id=view_id,
                                                       useHeader=useHeader,
                                                       useChatter=useChatter,
                                                       hideFormContent=False)
            if idToLoad:
                tmplViewObj.loadIds(idToLoad)
            return tmplViewObj

        def trySearchView(odooObjectName,
                          viewName='',
                          view_id=False, 
                          searchMode='ilike',
                          allFieldsDef={}):
            return connectorObj.initSearchViewObj(odooObjectName=odooObjectName,
                                                  viewName=viewName,
                                                  view_id=view_id, 
                                                  searchMode=searchMode,
                                                  allFieldsDef=allFieldsDef)

        def tryListView(odooObjectName,
                        viewName='',
                        view_id=False,
                        viewCheckBoxes={},
                        viewFilter=False,
                        readonlyFields={},
                        invisibleFields={},
                        forceFieldValues={},
                        forceIds=False):
            tmplViewObj = connectorObj.initTreeListViewObject(odooObjectName=odooObjectName,
                                                              viewName=viewName, view_id=view_id,
                                                              viewCheckBoxes=viewCheckBoxes,
                                                              viewFilter=viewFilter,
                                                              deafult_filter=[],
                                                              remove_button=False)
            if forceIds:
                tmplViewObj.loadIds(forceIds, forceFieldValues, readonlyFields, invisibleFields)
            else:
                tmplViewObj.loadForceEmptyIds(forceFieldValues, readonlyFields, invisibleFields)
            return tmplViewObj

        product_ids = connectorObj.rpc_connector.search(obj='product.template',
                                                        filterList=[('id','>',0)],
                                                        limit=1)
        tmplViewObj = tryForm(odooObjectName='product.product',
                              viewName='plm.base.component',
                              idToLoad=product_ids,
                              useHeader=True,
                              useChatter=True)
        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(tmplViewObj)
        scroll.setWidgetResizable(True)
        dialog = QtWidgets.QDialog()
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(scroll)
        #lay.setMargin(0)
        lay.setContentsMargins(20,20,20,20)
        dialog.setLayout(lay)
        dialog.resize(1200, 800)
        dialog.move(100, 100)
        dialog.exec()

    if connectorObj.userLogged:
        do_test()
