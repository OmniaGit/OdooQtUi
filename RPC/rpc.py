'''
Created on 02 feb 2017

@author: Daniel
'''
from utils import utils
import xmlrpclib


class RpcConnection(object):
    
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
            self.socketNoLogin = xmlrpclib.ServerProxy (self.urlNoLogin)
        except Exception, ex:
            return False
            pass
        utils.logMessage('info', 'Successfull connection to Odoo using login No User', 'loginNoUser')
        return True
        
    def loginWithUser(self):
        if not self.socketNoLogin:
            self.loginNoUser()
        try:
            self.userId = self.socketNoLogin.login(self.databaseName, self.userName, self.userPassword)
        except Exception, ex:
            return False
            pass
        try:
            self.socketYesLogin = xmlrpclib.ServerProxy(self.urlYesLogin)
        except Exception, ex:
            return False
            pass
        utils.logMessage('info', 'Successfull connection to Odoo with user %r and database %r' % (self.userName, self.databaseName), 'loginNoUser')
        return True
        
        
        
        