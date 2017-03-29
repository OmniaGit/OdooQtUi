'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
import sys
from PyQt4 import QtGui
from utils_odoo_conn import utils
from RPC.rpc import RpcConnection
from views.search_obj import TemplateSearchView
from views.form_obj import TemplateFormView
from views.tree_tree_obj import TemplateTreeTreeView
from views.tree_list_obj import TemplateTreeListView
from interface.login import LoginDial
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class MainConnector(object):

    def __init__(self):
        self.rpc = False
        self.activeLanguage = 'en_US'
        self.userGroups = []    # Not Used
        return object.__init__(self)

    def _getRpcInstance(self, loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP):
        return RpcConnection(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)

    def loginNoUser(self, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, '', '', '', xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc.loginNoUser()

    def loginWithUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        res = self.rpc.loginWithUser()
        self.activeLanguage = self.rpc.contextUser.get('lang', 'en_US')
        return res

    def loginWithDial(self):
        loginDialInst = LoginDial(parent=self)
        loginDialInst.exec_()
        return loginDialInst.logged

    def computeUserGroups(self):
        # Not Used
        res = self.rpc.read('res.users', ['groups_id'], self.rpc.userId)
        for userDict in res:
            self.userGroups = userDict.get('groups_id', [])
            break

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def initTreeListViewObject(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', viewCheckBoxes=False):
        localLang = self.activeLanguage
        if activeLanguage:
            localLang = activeLanguage
        if not rpcObj:
            rpcObj = self.rpc
        templateViewObj = TemplateTreeListView(rpcObj, localLang)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id, viewCheckBoxes)
        return templateViewObj

    def initViewObj(self, viewType, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False):
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
            rpcObj = self.rpc
        if viewType == 'form':
            templateViewObj = TemplateFormView(rpcObj, localLang, useHeader, useChatter)
        elif viewType == 'tree_tree':
            templateViewObj = TemplateTreeTreeView(rpcObj, localLang)
        elif viewType == 'tree_list':
            templateViewObj = TemplateTreeListView(rpcObj, localLang)
        elif viewType == 'search':
            templateViewObj = TemplateSearchView(rpcObj, localLang)
        else:
            utils.logMessage('warning', 'View Type not supported: %r' % (viewType), 'initViewObj')
        templateViewObj.initViewObj(odooObjectName, viewName, view_id)
        return templateViewObj

if __name__ == '__main__':
    import time
    ts = time.time()
    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'odoo-9-clean'
    loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'odoo-9-clean'
    loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = 'www.odooplm.cloud'
    xmlrpcPort = 8066
    user = 'odooplm'
    password = 'odooplm'
    dbName = 'odoov9_0'
    loginType = 'xmlrpc'

    app = QtGui.QApplication(sys.argv)

    connectorObj = MainConnector()
    connectorObj.loginWithDial()

    connectorObj.loginWithDial()

#     connectorObj.loginWithUser(user, password, dbName, xmlrpcServerIP, xmlrpcPort, scheme, loginType)
#     dialog = QtGui.QDialog()
#     templateViewObj = connectorObj.initViewObj('form', 'product.product', '', False, useHeader=False)
#     qtInterface = templateViewObj.QtInterface
#     objIds = [257]
#     startingFieldValues = {}
#     readonlyFields = {}     # {'description': True}
#     invisibleFields = {}    # {'description': True, 'state': True}
#     templateViewObj.loadIds(objIds, startingFieldValues, readonlyFields, invisibleFields)
#     dialog.setLayout(qtInterface)
#     dialog.setStyleSheet('background-color:#893b74;')
#     dialog.resize(1200, 600)
#     dialog.move(100, 100)
#     dialog.show()
#     te = time.time()
#     print 'TOTAL = %2.2f sec' % (te - ts)
#     dialog.exec_()

    # Odoo calls
    usersObj = 'res.users'
    partnerObj = 'res.partner'
    prodProdObj = 'product.product'
    app.exec_()
