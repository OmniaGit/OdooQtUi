'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
from RPC.rpc import RpcConnection
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
        self.rpc =  self._getRpcInstance(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc.loginWithUser()

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def getViewLayout(self, viewType, odooObjectName, startingFieldValues={}, clientReadonlyFields={}, idsToLoad=[]):
        '''
        @viewType: tree_tree, tree_list, form, search
        @odooObjectName: product.product, mrp.bom, ...
        @startingFieldValues: {'description': val1, 'name': val2, ...}     [only search and form views]
        @clientReadonlyFields: ['description', 'name', ...]                [only for form view]

        tree_list and tree_tree views are always read only
        '''
        pass

if __name__ == '__main__':
    scheme = 'http'
    xmlrpcServerIP = '127.0.0.1'
    xmlrpcPort = 8069
    user = 'admin'
    password = 'admin'
    dbName = 'plm_9'
    loginType = 'xmlrpc'

#     scheme = 'http'
#     xmlrpcServerIP = '127.0.0.1'
#     xmlrpcPort = 8081
#     user = 'admin'
#     password = 'Maus2016'
#     dbName = 'Maus_real'
#     loginType = 'xmlrpc'
    connectorObj = MainConnector()
    connectorObj.loginWithUser(user, password, dbName, xmlrpcServerIP, xmlrpcPort, scheme, loginType)
    
    usersObj = 'res.users'
    partnerObj = 'res.partner'
    connectorObj.rpc.search(usersObj, [])
    connectorObj.rpc.read(usersObj, [], [1])
    connectorObj.rpc.fieldsGet(usersObj, [])
    connectorObj.rpc.readSearch(usersObj, [], [])
    connectorObj.rpc.create(partnerObj, {'name': 'Daniel'})
    
    
    