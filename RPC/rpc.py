'''
Created on 02 feb 2017

@author: Daniel
'''
from utils import utils
from XmlRpc.xmlRpc import XmlRpcConnection


class RpcConnection(object):

    def __init__(self, connectionType, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1'):
        self.userName = userName
        self.userPassword = userPassword
        self.databaseName = databaseName
        self.xmlrpcPort = xmlrpcPort
        self.scheme = scheme
        self.xmlrpcServerIP = xmlrpcServerIP
        self.socketNoLogin = False
        self.socketYesLogin = False
        self.userId = False
        self.connectionType = connectionType
        self.sockInstance = False
        if connectionType == 'xmlrpc':
            self.sockInstance = XmlRpcConnection(userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
        return super(RpcConnection, self).__init__()

    def loginNoUser(self):
        return self.sockInstance.loginNoUser()

    def loginWithUser(self):
        res = self.sockInstance.loginWithUser()
        self.userId = self.sockInstance.userId
        return res

    def search(self, obj, filterList):
        return self.sockInstance.search(obj, filterList)

    def read(self, obj, fields, ids, context={}):
        if isinstance(ids, int):
            ids = [ids]
        return self.sockInstance.read(obj, fields, ids, context)

    def readSearch(self, obj, fields, filterList=[]):
        return self.sockInstance.readSearch(obj, fields, filterList)

    def write(self, obj, values, idsToWrite):
        return self.sockInstance.write(obj, values, idsToWrite)

    def writeSearch(self, obj, values, filterList):
        idsToWrite = self.search(obj, filterList)
        return self.write(obj, values, idsToWrite)

    def delete(self, obj, idsToUnlink):
        return self.sockInstance.delete(obj, idsToUnlink)

    def deleteSearch(self, obj, filterList):
        idsToUnlink = self.search(obj, filterList)
        return self.delete(obj, idsToUnlink)

    def searchCount(self, obj, filterList):
        return self.sockInstance.searchCount(obj, filterList)
    
    def create(self, obj, values):
        return self.sockInstance.create(obj, values)
        
    def fieldsGet(self, obj, attributesToRead=[]):
        '''
        @attributesToRead: ['string', 'help', 'type']
        '''
        return self.sockInstance.fieldsGet(obj, attributesToRead)

    @utils.timeit
    def defaultGet(self, obj, fieldsToRead=[]):
        '''
        @attributesToRead: ['string', 'help', 'type']
        '''
        return self.sockInstance.defaultGet(obj, fieldsToRead)

    def fieldsViewGet(self, obj, view_id, view_type):
        return self.sockInstance.fieldsViewGet(obj, view_id, view_type)
        
    def on_change(self, obj, activeIds, allVals, fieldName, allOnchanges, context={}):
        return self.sockInstance.on_change(obj, activeIds, allVals, fieldName, allOnchanges, context)
        