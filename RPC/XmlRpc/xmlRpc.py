'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''

from utils import utils
import xmlrpclib


class XmlRpcConnection(object):

    def __init__(self, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1'):
        self.userName = userName
        self.userPassword = userPassword
        self.databaseName = databaseName
        self.xmlrpcPort = xmlrpcPort
        self.scheme = scheme
        self.xmlrpcServerIP = xmlrpcServerIP
        self.urlCommon = self.scheme + '://' + str(self.xmlrpcServerIP) + ':' + str(self.xmlrpcPort) + '/xmlrpc/'
        self.urlNoLogin = self.urlCommon + 'common'
        self.urlYesLogin = self.urlCommon + 'object'
        self.socketNoLogin = False
        self.socketYesLogin = False
        self.userId = False

    def loginNoUser(self):
        try:
            self.socketNoLogin = xmlrpclib.ServerProxy(self.urlNoLogin)
        except Exception, ex:
            utils.logMessage('error', 'Error during login without user: %r' % (ex), 'loginNoUser')
            return False
        utils.logMessage('info', 'Successfull connection to Odoo using login No User', 'loginNoUser')
        return True

    def loginWithUser(self):
        if not self.socketNoLogin:
            self.loginNoUser()
        try:
            self.userId = self.socketNoLogin.login(self.databaseName, self.userName, self.userPassword)
        except Exception, ex:
            utils.logMessage('error', 'Error during login with user: %r' % (ex), 'loginWithUser')
            return False
        try:
            self.socketYesLogin = xmlrpclib.ServerProxy(self.urlYesLogin)
        except Exception, ex:
            utils.logMessage('error', 'Error getting server proxy: %r' % (ex), 'loginWithUser')
            return False
        utils.logMessage('info', 'Successfull connection to Odoo with user %r and database %r' % (self.userName, self.databaseName), 'loginNoUser')
        return True

    def callOdooFunction(self, odooObj, functionName, parameters=[], kwargParameters={}):
        '''
            @odooObj: product.product, product.template ...
            @functionName: 'search', 'read', ...
            @parameters: [val1, val2, ...]
            @kwargParameters: {'context': {}, limit: val, 'order': val,...}
        '''
        return self.socketYesLogin.execute_kw(self.databaseName, self.userId, self.userPassword,
                                              odooObj,
                                              functionName,
                                              parameters,
                                              kwargParameters)
