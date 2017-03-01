'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
import sys
from PyQt4 import QtGui
from utils import utils
from RPC.rpc import RpcConnection
from views.templateView import TemplateView
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class MainConnector(object):

    def __init__(self):
        self.rpc = False
        self.activeLanguage = 'en_US'
        self.availableLanguages = {'en_US': 'English'}
        return object.__init__(self)

    def _getRpcInstance(self, loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP):
        return RpcConnection(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)

    def loginNoUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc.loginNoUser()

    @utils.timeit
    def loginWithUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        res = self.rpc.loginWithUser()
        if res:
            self.computeAvailableLanguages()
            self.computeUserLanguage()
        return res

    def computeUserLanguage(self):
        res = self.rpc.readSearch('res.users', ['lang'], [('id', '=', self.rpc.userId)])
        if not res:
            logging.warning('Unable to get active user language.')
        for codeDict in res:
            langCode = codeDict.get('lang', '')
            self.activeLanguage = langCode
            break

    def computeAvailableLanguages(self):
        self.availableLanguages = {}
        res = self.rpc.readSearch('res.lang', ['name', 'code'], [])
        for codeDict in res:
            self.availableLanguages[codeDict.get('code', '')] = codeDict.get('name', '')

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def initViewObj(self, viewType, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', availableLanguages=[]):
        '''
        @viewType: tree_tree, tree_list, form, search
        @odooObjectName: product.product, mrp.bom, ...
        @startingFieldValues: {'description': val1, 'name': val2, ...}     [only search and form views]
        @clientReadonlyFields: ['description', 'name', ...]                [only for form view]

        tree_list and tree_tree views are always read only
        '''
        if not activeLanguage:
            activeLanguage = self.activeLanguage
        if not availableLanguages:
            availableLanguages = self.availableLanguages
        if rpcObj:
            templateViewObj = TemplateView(rpcObj, activeLanguage, availableLanguages)
        else:
            templateViewObj = TemplateView(self.rpc, activeLanguage, availableLanguages)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id, viewType)
        return templateViewObj

if __name__ == '__main__':
    import datetime
    import time
    ts = time.time()
    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'plm-9-enterprise'
    loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = '192.168.1.16'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'Maus_1'
    loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = 'www.odooplm.cloud'
    xmlrpcPort = 8066
    user = 'odooplm'
    password = 'odooplm'
    dbName = 'odoov9_0'
    loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'daniel'
    password = 'daniel'
    dbName = 'odoo-9-clean'
    loginType = 'xmlrpc'

    app = QtGui.QApplication(sys.argv)
    
    connectorObj = MainConnector()
    connectorObj.loginWithUser(user, password, dbName, xmlrpcServerIP, xmlrpcPort, scheme, loginType)
    
    #dialog = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
    dialog = QtGui.QDialog()
    templateViewObj = connectorObj.initViewObj('form', 'product.product', '', False)
    qtInterface = templateViewObj.QtInterface
    #objIds = [77540]
    objIds = [31]
    #startingFieldValues = {'description': 'non-settare'}
    startingFieldValues = {}
    readonlyFields = {}# {'description': True}
    invisibleFields = {}# {'description': True, 'state': True}
    
    templateViewObj.loadIds(objIds, startingFieldValues, readonlyFields, invisibleFields)
    templateViewObj.setReadonly(True)
    #dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    dialog.setLayout(qtInterface)
    dialog.setStyleSheet('background-color:#893b74;')
    dialog.resize(1000, 650)
    #dialog.adjustSize()
    dialog.show()
    te = time.time()
    print 'TOTAL = %2.2f sec' % (te-ts)
    dialog.exec_()
    
    # Odoo calls
    usersObj = 'res.users'
    partnerObj = 'res.partner'
    prodProdObj = 'product.product'
#     connectorObj.rpc.fieldsViewGet(prodProdObj, False, 'form')
#     
#     print 'Search result: %r' % (connectorObj.rpc.search(usersObj, []))
#     print 'Read result: %r' % (connectorObj.rpc.read(usersObj, [], [1]))
#     print 'Read search result: %r' % (unicode(connectorObj.rpc.readSearch(usersObj, [], [])))
#     print ''
#     print 'Write result %r' % (connectorObj.rpc.write(prodProdObj, {'description': 'ciaooo'}, [69, 70]))
#     print 'Search Write result %r' % (connectorObj.rpc.writeSearch(prodProdObj, {'description': 'ciao2'}, [('id', 'in', [69, 70])]))
#     print 'Fields get result: %r' % (connectorObj.rpc.fieldsGet(usersObj, []))
#     newId = connectorObj.rpc.create(partnerObj, {'name': 'Daniel'})
#     print 'Create result: %r' % (newId)
#     print 'Delete resut: %r' % (connectorObj.rpc.delete(prodProdObj, [newId]))
#     newId1 = connectorObj.rpc.create(partnerObj, {'name': 'Daniel_1'})
#     newId2 = connectorObj.rpc.create(partnerObj, {'name': 'Daniel_2'})
#     print 'Search Delete resut: %r' % (connectorObj.rpc.deleteSearch(partnerObj, [('id', 'in', [newId1, newId2])]))
#     print 'Search count res: %r' % (connectorObj.rpc.searchCount(partnerObj, [('name', 'ilike', 'daniel')]))
#     print 'Fields get res: %r' % (connectorObj.rpc.fieldsGet(partnerObj, []))
    app.exec_()