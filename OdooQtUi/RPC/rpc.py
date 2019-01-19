'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
from OdooQtUi.RPC.XmlRpc.xmlRpc import XmlRpcConnection


class RpcConnection(object):

    def __init__(self):
        self.userId = False
        self.availableConnTypes = ['xmlrpc', 'secure-xmlrpc']
        self.sockInstance = False
        self.contextUser = {}
        self.userLogged = False
        self.useInterface = True
        return super(RpcConnection, self).__init__()

    def initConnection(self, connectionType, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1'):
        self.userName = userName
        self.userPassword = userPassword
        self.databaseName = databaseName
        self.xmlrpcPort = xmlrpcPort
        self.scheme = scheme
        self.xmlrpcServerIP = xmlrpcServerIP
        self.connectionType = connectionType
        if connectionType == 'xmlrpc':
            self.sockInstance = XmlRpcConnection(userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
            self.sockInstance.useInterface = self.useInterface
        elif connectionType == 'secure-xmlrpc':
            self.sockInstance = XmlRpcConnection(userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP, secure=True)
            self.sockInstance.useInterface = self.useInterface

    def getLoginInfos(self):
        return [self.userName,
                self.userPassword,
                self.databaseName,
                self.xmlrpcPort,
                self.scheme,
                self.xmlrpcServerIP,
                self.connectionType]
    @property
    def url(self):
        return self.sockInstance.urlYesLogin

    def loginNoUser(self, connectionType, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1'):
        if not self.sockInstance:
            self.initConnection(connectionType, userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
            if not self.sockInstance:
                return False
        return self.sockInstance.loginNoUser()

    def loginWithUser(self, connectionType, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1'):
        if not self.sockInstance:
            self.initConnection(connectionType, userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
            if not self.sockInstance:
                return False
        res = self.sockInstance.loginWithUser()
        self.userId = self.sockInstance.userId
        if self.userId:
            self.userLogged = True
            self.computeUserLanguage()
        if not res:
            self.userLogged = False
        return res

    def listDb(self):
        return self.sockInstance.listDb()

    def computeUserLanguage(self):
        if not self.userId:
            return False
        res = self.callCustomMethod('res.users', 'context_get')
        if not res:
            logging.warning('Unable to get user context.')
            res = {}
        self.contextUser = res

    def callCustomMethod(self, odooObj, functionName, parameters=[], kwargParameters={}, context={}):
        localContext = self.contextUser
        localContext.update(context)
        if localContext:
            kwargParameters['context'] = localContext
        return self.sockInstance.callOdooFunction(odooObj, functionName, parameters, kwargParameters)

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        localContext = self.contextUser
        localContext.update(context)
        res = self.sockInstance.search(obj, filterList, limit, offset, context=localContext)
        if not res:
            return []
        return res

    def read(self, obj, fields, ids, context={}, limit=False):
        if not ids:
            return {}
        localContext = self.contextUser
        localContext.update(context)
        if isinstance(ids, int):
            ids = [ids]
        return self.sockInstance.read(obj, fields, ids, limit, context=localContext)

    def readSearch(self, obj, fields, filterList=[], context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.readSearch(obj, fields, filterList, context=localContext)

    def write(self, obj, values, idsToWrite, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.write(obj, values, idsToWrite, context=localContext)

    def writeSearch(self, obj, values, filterList, context={}):
        localContext = self.contextUser
        localContext.update(context)
        idsToWrite = self.search(obj, filterList)
        return self.write(obj, values, idsToWrite, context=localContext)

    def delete(self, obj, idsToUnlink, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.delete(obj, idsToUnlink, context=localContext)

    def deleteSearch(self, obj, filterList, context={}):
        localContext = self.contextUser
        localContext.update(context)
        idsToUnlink = self.search(obj, filterList)
        return self.delete(obj, idsToUnlink, context=localContext)

    def searchCount(self, obj, filterList, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.searchCount(obj, filterList, context=localContext)

    def create(self, obj, values, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.create(obj, values, context=localContext)

    def fieldsGet(self, obj, attributesToRead=[], context={}):
        '''
        @attributesToRead: ['string', 'help', 'type']
        '''
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.fieldsGet(obj, attributesToRead, context=localContext)

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: ['string', 'help', 'type']
        '''
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.defaultGet(obj, fieldsToRead, context=localContext)

    def fieldsViewGet(self, obj, view_id, view_type, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.fieldsViewGet(obj, view_id, view_type, context=localContext)

    def on_change(self, obj, activeIds, allVals, fieldName, allOnchanges, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.on_change(obj, activeIds, allVals, fieldName, allOnchanges, context=localContext)

connectionObj = RpcConnection()
