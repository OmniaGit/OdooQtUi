'''
Created on Jan 18, 2019

@author: mboscolo
'''
import sys
import logging
from PySide2 import QtWidgets
from OdooQtUi.connector import MainConnector

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    odooConnector = MainConnector()
    import time
    ts = time.time()
    app = QtWidgets.QApplication(sys.argv)

    def do_test():
        connectorObj = MainConnector()
        connectorObj.loginWithDial()

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

        # tmplViewObj = tryForm('product.product', idToLoad=284, useChatter=True)
       # tmplViewObj = tryForm('product.product', idToLoad=1345, useChatter=False)
        # viewCheckBoxes = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
        tmplViewObj = tryListView('product.template', viewFilter=True)
        dialog = QtGui.QDialog()
        lay = QtGui.QVBoxLayout()
        lay.addWidget(tmplViewObj)
        dialog.setLayout(lay)
        dialog.resize(1200, 600)
        dialog.move(100, 100)
        dialog.show()
        dialog.exec_()
        time.sleep(2)
        dialog.exec_()
    while 1:
        do_test()
    app.exec_()
