'''
Created on 02 feb 2017

@author: Daniel
'''
import logging
import socket
from OdooQtUi.RPC.XmlRpc.xmlRpc import XmlRpcConnection
from OdooQtUi.utils_odoo_conn.utils import timeit

class RpcConnection(object):
    def __init__(self):
        self.userId = False
        self.availableConnTypes = ['xmlrpc', 'secure-xmlrpc']
        self.sockInstance = False
        self.contextUser = {}
        self.useInterface = True
        self._cache_search = {}
        self._cache_search_condition = {}
        self._cache_align_table = {}
        self.db_from_field = ''
        self.userName = ''      
        self.userPassword = ''  
        self.databaseName = ''
        self.xmlrpcPort = ''
        self.scheme = ''
        self.xmlrpcServerIP = ''
        self.connectionType = ''
        self.hostname = socket.gethostname()
        return super(RpcConnection, self).__init__()
    
    def __str__(self, *args, **kwargs):
        return "UID: %s DB: %s URL %s" % (self.userName,
                                          self.databaseName,
                                          self.xmlrpcServerIP)

    def logout(self):
        self.userName = ''      
        self.userPassword = ''
        self.sockInstance = False

    @property
    def serverVersion(self):
        return self.sockInstance.serverVersion
 
    def getCleanServer(self):
        return self.url.split("/xmlrpc")[0]
        
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
        else:
            raise Exception("Missing value connectionType for initConnection function")

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
    
    def loginWithUser(self,
                      connectionType,
                      userName,
                      userPassword,
                      databaseName,
                      xmlrpcPort=8069,
                      scheme='http',
                      xmlrpcServerIP='127.0.0.1'):
        self.initConnection(connectionType, userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
        if not self.sockInstance:
            return False
        res = self.sockInstance.loginWithUser()
        self.userId = self.sockInstance.userId
        if self.userId:
            self.computeUserLanguage()
        if not res:
            self.userId = False
        return res

    @property
    def userLogged(self):
        if self.userId:
            return True
        return False

    def listDb(self):
        return self.sockInstance.listDb()

    def computeUserLanguage(self):
        if not self.userId:
            return False
        res = self.callCustomMethod('res.users', 'context_get')
        if not res:
            logging.warning('Unable to get user context.')
            res = {}
        self.contextUser.update(res)
    
    @timeit
    def callCustomMethod(self, odooObj, functionName, parameters=[], kwargParameters={}, context={},forceHideInterface=False, forceRaise_error=False):
        localContext = self.contextUser
        localContext.update(context)
        if localContext:
            kwargParameters['context'] = localContext
        return self.sockInstance.callOdooFunction(odooObj, functionName, parameters, kwargParameters, forceHideInterface, forceRaise_error)

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        localContext = self.contextUser
        localContext.update(context)
        res = self.sockInstance.search(obj, filterList, limit, offset, context=localContext)
        if not res:
            return []
        return res

    def read(self, obj, fields, ids, context={}, limit=False, load='_classic_read'):
        if not ids:
            return []
        localContext = self.contextUser
        localContext.update(context)
        if isinstance(ids, int):
            ids = [ids]
        return self.sockInstance.read(obj,
                                      fields,
                                      ids,
                                      limit,
                                      context=localContext,
                                      load=load)

    def readSearch(self, obj, fields, filterList=[], order=False, context={}):
        localContext = self.contextUser
        localContext.update(context)
        return self.sockInstance.readSearch(obj,
                                            fields,
                                            filterList,
                                            order=order,
                                            context=localContext)

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

    def EnableException(self):
        """
        enable at low level xml-rpc call exceprion
        """
        self.sockInstance.raise_error=True
    
    def DisableException(self):
        """
        diseble at low level xml-rpc call exceprion
        """
        self.sockInstance.raise_error=True

    def cacheSearch(self,
                    objName,
                    condition=[],
                    limit=False,
                    offset=False,
                    context={}):
        key = "%s_%s" % (objName, condition)
        if key not in self._cache_search_condition:
            self._cache_search_condition[key] = self.search(objName,
                                                                condition,
                                                                limit, 
                                                                offset, 
                                                                context)
        return self._cache_search_condition[key]
        
    def cacheSearchCreate(self,
                          objName,
                          objVals,
                          condition,
                          context={}):
        if not condition:
            raise Exception("You must provide a valid search condition")
        key = "%s_%s" % (objName, condition)
        if key not in self._cache_search_condition:
            res = self.search(objName,
                              condition,
                              context)

            if not res:
                res = self.create(objName,
                                     objVals,
                                     context=context)
                res = [res]
            self._cache_search_condition[key] = res
        return self._cache_search_condition[key]

    def searchObjectFromOldId(self,
                              objName,
                              OldID):
        ret = self._cache_search.get(objName, {}).get(OldID)
        if not ret:
            ret = self.search(objName, [(self.db_from_field, '=', OldID)])
            if not ret:
                return False
            if not objName in self._cache_search:
                self._cache_search[objName] = {}
            self._cache_search[objName][OldID] = ret[0]
        if isinstance(ret, int):
            return ret    
        return ret[0]

    def writeOrCreateObject(self,
                            objName,
                            attributes,
                            cleanAttributes=[],
                            mapAttributes = {},
                            context={}):
        att = attributes.copy()
        map = mapAttributes.copy()
        
        if 'id' in att:
            obj_id = att['id']
            del att['id']
        new_id = self.search(objName,
                             [(self.db_from_field, '=', obj_id)],
                             context=context)
        for befAtt, toAtt in map.items():
            att[toAtt] = att[befAtt]
        for aClean in cleanAttributes:
            del att[aClean]
        if new_id:
            self.write(objName, att, new_id, context=context)
        else:
            att[self.db_from_field]=obj_iRpcConnectiond
            new_id = self.create(objName,
                                 att,
                                 context=context)
        if isinstance(new_id, (list,tuple)):
            for _id in new_id:
                return _id
        return new_id    
    
    def setXmlRpcError(self, value=False):
        """
        force the underline rpc soket to rise any error that occure
        """   
        self.sockInstance.raise_error = value
        
connectionObj = RpcConnection()
