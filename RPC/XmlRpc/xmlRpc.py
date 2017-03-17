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

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        try:
            kargs = {'context': context}
            if limit:
                kargs['limit'] = limit
            if offset:
                kargs['offset'] = offset
            return self.callOdooFunction(obj, 'search', [filterList], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during search with values: object %r, filter %r, parameters %r. Error: %r' % (obj, filterList, kargs, ex), 'search')
        return []

    def read(self, obj, fields=[], ids=[], limit=False, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'read', [ids, fields], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during read with values: object %r, fields %r, ids %r. Error: %r' % (obj, fields, ids, ex), 'read')
        return []

    def fieldsGet(self, obj, attributesToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'attributes': attributesToRead, 'context': context}
            return self.callOdooFunction(obj, 'fields_get', [], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r. Error: %r' % (obj, kargs, ex), 'fieldsGet')
        return {}

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'default_get', [fieldsToRead], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r. Error: %r' % (obj, kargs, ex), 'fieldsGet')
        return {}

    def readSearch(self, obj, fields, filterList, limit=False, context={}):
        try:
            kargs = {'fields': fields, 'context': context}
            return self.callOdooFunction(obj, 'search_read', [filterList], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, filterList, ex), 'readSearch')
        return []

    def create(self, obj, values, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'create', [values], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, values, ex), 'create')
        return []

    def write(self, obj, values, idsToWrite, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'write', [idsToWrite, values], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, values, ex), 'write')
        return []

    def delete(self, obj, idsToDelete, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'unlink', [idsToDelete], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, idsToDelete %r. Error: %r' % (obj, kargs, idsToDelete, ex), 'delete')
        return []

    def searchCount(self, obj, filterList, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'search_count', [filterList], kargs)
        except Exception, ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, filterList, ex), 'searchCount')
        return []

    def fieldsViewGet(self, odooObj, view_id=False, view_type='form', context={}):
        try:
            kwargParameters = {'context': context}
            return self.callOdooFunction(odooObj, 'fields_view_get', [view_id, view_type], kwargParameters)
        except Exception, ex:
            utils.logMessage('error', 'Error during fields view get: %r' % (ex), 'fieldsViewGet')
        return {}

    def on_change(self, odooObj, activeIds, allVals, fieldName, allOnchanges, context):
        try:
            return self.callOdooFunction(odooObj, 'onchange', [activeIds, allVals, fieldName, allOnchanges, context])
        except Exception, ex:
            utils.logMessage('error', 'Wrong on_change call with odooObj: %r, fieldName: %r, activeIds: %r, context: %r. Error: %r' % (odooObj, fieldName, activeIds, context, ex), 'on_change')
        return {}

    @utils.timeit
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
