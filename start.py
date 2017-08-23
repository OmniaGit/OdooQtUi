'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
import sys
from PyQt4 import QtGui
from PyQt4 import QtCore
from utils_odoo_conn import utils
from RPC.rpc import connectionObj
from views.search_obj import TemplateSearchView
from views.form_obj import TemplateFormView
from views.tree_tree_obj import TemplateTreeTreeView
from views.tree_list_obj import TemplateTreeListView
from interface.login import LoginDialComplete
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class MainConnector(object):

    def __init__(self):
        self.activeLanguage = 'en_US'
        self.userGroups = []    # Not Used
        self.loadedViews = {'form': [],
                            'tree_tree': [],
                            'tree_list': [],
                            'search': []}
        return object.__init__(self)

    def loginNoUser(self, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        connectionObj.initConnection(loginType, '', '', '', xmlrpcPort, scheme, xmlrpcServerIP)
        return connectionObj.loginNoUser()

    def loginWithUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        connectionObj.initConnection(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        res = connectionObj.loginWithUser()
        self.activeLanguage = connectionObj.contextUser.get('lang', 'en_US')
        return res

    def loginWithDial(self):
        loginDialInst = LoginDialComplete()
        loginDialInst.interfaceDial.exec_()
        if connectionObj.userLogged:
            self.activeLanguage = connectionObj.contextUser.get('lang', 'en_US')
            return True
        return False

    def computeUserGroups(self):
        # Not Used
        res = connectionObj.read('res.users', ['groups_id'], connectionObj.userId)
        for userDict in res:
            self.userGroups = userDict.get('groups_id', [])
            break

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def _getCommonLangAndRpc(self, activeLanguage='', rpcObj=None):
        if not activeLanguage:
            activeLanguage = self.activeLanguage
        if not rpcObj:
            rpcObj = connectionObj
        return activeLanguage, rpcObj
        
    def initTreeListViewObject(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', viewCheckBoxes={}, viewFilter=False):
        localLang, rpcObj = self._getCommonLangAndRpc(activeLanguage, rpcObj)
        oldView = self.checkAlreadyLoadedView('tree_list', rpcObj, odooObjectName, viewName, view_id)
        if oldView:
            return oldView
        templateViewObj = TemplateTreeListView(rpcObj, localLang, viewFilter)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id, viewCheckBoxes)
        self.appendLoadedView('tree_list', rpcObj, odooObjectName, viewName, view_id, templateViewObj)
        return templateViewObj

    def initTreeTreeViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage=''):
        localLang, rpcObj = self._getCommonLangAndRpc(activeLanguage, rpcObj)
        oldView = self.checkAlreadyLoadedView('tree_tree', rpcObj, odooObjectName, viewName, view_id)
        if oldView:
            return oldView
        templateViewObj = TemplateTreeTreeView(rpcObj, localLang)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        self.appendLoadedView('tree_tree', rpcObj, odooObjectName, viewName, view_id, templateViewObj)
        return templateViewObj

    def initFormViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False):
        localLang, rpcObj = self._getCommonLangAndRpc(activeLanguage, rpcObj)
        oldView = self.checkAlreadyLoadedView('form', rpcObj, odooObjectName, viewName, view_id)
        if oldView:
            return oldView
        templateViewObj = TemplateFormView(rpcObj, localLang, useHeader, useChatter)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        self.appendLoadedView('form', rpcObj, odooObjectName, viewName, view_id, templateViewObj)
        return templateViewObj

    def initSearchViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage=''):
        localLang, rpcObj = self._getCommonLangAndRpc(activeLanguage, rpcObj)
        oldView = self.checkAlreadyLoadedView('search', rpcObj, odooObjectName, viewName, view_id)
        if oldView:
            return oldView
        templateViewObj = TemplateSearchView(rpcObj, localLang)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        self.appendLoadedView('search', rpcObj, odooObjectName, viewName, view_id, templateViewObj)
        return templateViewObj

    def initViewObj(self, viewType, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False, viewCheckBoxes={}):
        '''
        @viewType: tree_tree, tree_list, form, search
        @odooObjectName: product.product, mrp.bom, ...
        @startingFieldValues: {'description': val1, 'name': val2, ...}     [only search and form views]
        @clientReadonlyFields: ['description', 'name', ...]                [only for form view]

        tree_list and tree_tree views are always read only
        '''
        localLang = self.activeLanguage
        if activeLanguage:
            localLang = activeLanguage
        if not rpcObj:
            rpcObj = connectionObj
        oldView = self.checkAlreadyLoadedView(viewType, rpcObj, odooObjectName, viewName, view_id)
        if oldView:
            return oldView
        if viewType == 'form':
            templateViewObj = TemplateFormView(rpcObj, localLang, useHeader, useChatter)
            templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        elif viewType == 'tree_tree':
            templateViewObj = TemplateTreeTreeView(rpcObj, localLang)
            templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        elif viewType == 'tree_list':
            templateViewObj = TemplateTreeListView(rpcObj, localLang)
            templateViewObj.initViewObj(odooObjectName, viewName, view_id, viewCheckBoxes={})
        elif viewType == 'search':
            templateViewObj = TemplateSearchView(rpcObj, localLang)
            templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        else:
            utils.logMessage('warning', 'View Type not supported: %r' % (viewType), 'initViewObj')
        self.appendLoadedView(viewType, rpcObj, odooObjectName, viewName, view_id, templateViewObj)
        return templateViewObj

    def appendLoadedView(self, viewType, rpcObj, odooObjectName, viewName, view_id, templateViewObj):
        self.loadedViews[viewType].append({
            'login': rpcObj.getLoginInfos(),
            'view_type': viewType,
            'object_name': odooObjectName,
            'view_name': viewName or '',
            'view_id': view_id,
            'TMP_VIEW_OBJ': templateViewObj,
            })

    def checkAlreadyLoadedView(self, viewType, rpcObj, odooObjectName, viewName, view_id):
        viewList = self.loadedViews.get(viewType, [])
        for viewDict in viewList:
            oldLogin = viewDict.get('login')
            if oldLogin == rpcObj.getLoginInfos():
                oldViewType = viewDict.get('view_type')
                oldObjectName = viewDict.get('object_name')
                oldViewName = viewDict.get('view_name')
                oldViewId = viewDict.get('view_id')
                if oldViewType == viewType and oldObjectName == odooObjectName and oldViewName == viewName and oldViewId == view_id:
                    return viewDict['TMP_VIEW_OBJ']
        return False

odooConnector = MainConnector()

if __name__ == '__main__':
    import time
    ts = time.time()

    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'odoo_9_comm'
    loginType = 'xmlrpc'

#     scheme = 'http'
#     xmlrpcServerIP = 'www.odooplm.cloud'
#     xmlrpcPort = 8066
#     user = 'odooplm'
#     password = 'odooplm'
#     dbName = 'odoov9_0'
#     loginType = 'xmlrpc'

#     scheme = 'http'
#     xmlrpcServerIP = '192.168.99.16'
#     xmlrpcPort = 8069
#     user = 'admin'
#     password = 'admin'
#     dbName = 'Maus_2'
#     loginType = 'xmlrpc'
 
    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'all_v10'
    loginType = 'xmlrpc'

    app = QtGui.QApplication(sys.argv)

    @utils.timeit
    def do_test():
        connectorObj = MainConnector()
        #connectorObj.loginWithDial()
        connectorObj.loginWithDial()
        #res = connectorObj.loginWithUser(user, password, dbName, xmlrpcServerIP, xmlrpcPort, scheme, loginType)
        #tmplViewObj = connectorObj.initSearchViewObj('product.product')

        tmplViewObj = connectorObj.initFormViewObj('product.product', viewName='plm.base.component')
        #viewCheckBoxes = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
        #tmplViewObj = connectorObj.initTreeListViewObject('product.product', viewCheckBoxes=viewCheckBoxes)
        #tmplViewObj.loadIds([249])
        #tmplViewObj.sortResults('fieldName', 'filterMode')

        #tmplViewObj = connectorObj.initFormViewObj('product.product')

#         viewCheckBoxes = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
#         tmplViewObj = connectorObj.initTreeListViewObject('product.product', viewCheckBoxes=viewCheckBoxes, viewFilter=True)
#         tmplViewObj.loadIdsForceEmpty([])
        tmplViewObj.loadIds([])

        #tmplViewObj.sortResults('fieldName', 'filterMode')

        dialog = QtGui.QDialog()
        #tmplViewObj.QtInterface.setMargin(20)
        interf = tmplViewObj.QtInterface
        dialog.setLayout(interf)
        dialog.setStyleSheet('background-color:#893b74;')
        dialog.resize(1200, 600)
        dialog.move(100, 100)
        dialog.show()
        dialog.exec_()
        
    do_test()

    app.exec_()
