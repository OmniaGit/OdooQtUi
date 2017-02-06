'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
from RPC.rpc import RpcConnection
from views.templateView import TemplateView
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class MainConnector(object):

    def __init__(self):
        self.rpc = False
        return object.__init__(self)

    def _getRpcInstance(self, loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP):
        return RpcConnection(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)

    def loginNoUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc.loginNoUser()

    def loginWithUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        self.rpc = self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc.loginWithUser()

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def initViewObj(self, viewType, odooObjectName, viewName='', view_id=False, startingFieldValues={}, clientReadonlyFields={}, idsToLoad=[]):
        '''
        @viewType: tree_tree, tree_list, form, search
        @odooObjectName: product.product, mrp.bom, ...
        @startingFieldValues: {'description': val1, 'name': val2, ...}     [only search and form views]
        @clientReadonlyFields: ['description', 'name', ...]                [only for form view]

        tree_list and tree_tree views are always read only
        '''
        templateViewObj = TemplateView(self.rpc)
        templateViewObj.initViewObj(odooObjectName, viewName, view_id, viewType, startingFieldValues, clientReadonlyFields, idsToLoad)

if __name__ == '__main__':
#     scheme = 'http'
#     xmlrpcServerIP = '127.0.0.1'
#     xmlrpcPort = 8069
#     user = 'admin'
#     password = 'admin'
#     dbName = 'plm_9'
#     loginType = 'xmlrpc'

    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8081
    user = 'admin'
    password = 'Maus2016'
    dbName = 'Maus_real'
    loginType = 'xmlrpc'
    connectorObj = MainConnector()
    connectorObj.loginWithUser(user, password, dbName, xmlrpcServerIP, xmlrpcPort, scheme, loginType)
    
    
    connectorObj.initViewObj('form', 'product.product', '', False, {}, {}, [])
    
    
    
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
    