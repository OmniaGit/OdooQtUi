'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''

from utils_odoo_conn import utils
import xmlrpclib
import httplib


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
        self.urlListDB = self.urlCommon + 'db'
        self.urlYesLogin = self.urlCommon + 'object'
        self.socketNoLogin = False
        self.socketYesLogin = False
        self.userId = False

    def loginNoUser(self):
        try:
            t = TimeoutTransport()
            t.set_timeout(4.0)
            # server = xmlrpclib.Server('http://time.xmlrpc.com/RPC2', transport=t)
            self.socketNoLogin = xmlrpclib.ServerProxy(self.urlNoLogin, transport=t)
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
            if not self.userId:
                return False
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

    def listDb(self):
        return xmlrpclib.ServerProxy(self.urlListDB).list()

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        try:
            kargs = {'context': context}
            if limit or limit == 0:
                kargs['limit'] = limit
            if offset or offset == 0:
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

    def execute_kw(self, obj, method, *args, **kargs):
        return self.callOdooFunction(obj, method, args, kargs)

    def execute(self, obj, method, *args):
        if method == 'execute_kw':
            odooObj, functionName, parameters, kwargParameters = args
            return self.callOdooFunction(odooObj, functionName, parameters, kwargParameters)
        try:
            return self.socketYesLogin.execute(self.databaseName, self.userId, self.userPassword,
                                              odooObj,
                                              functionName,
                                              parameters,
                                              kwargParameters)
        except Exception, ex:
            utils.logMessage('error', ex, 'execute')
            utils.logMessage('error', 'Error during call Odoo Function execute with arguments: %r, %r, %r, %r' % (obj, method, args), 'execute')
            return False

    @utils.timeit
    def callOdooFunction(self, odooObj, functionName, parameters=[], kwargParameters={}):
        '''
            @odooObj: product.product, product.template ...
            @functionName: 'search', 'read', ...
            @parameters: [val1, val2, ...]
            @kwargParameters: {'context': {}, limit: val, 'order': val,...}
        '''
        try:
            return self.socketYesLogin.execute_kw(self.databaseName, self.userId, self.userPassword,
                                                  odooObj,
                                                  functionName,
                                                  parameters,
                                                  kwargParameters)
        except Exception, ex:
            utils.logMessage('error', ex, 'callOdooFunction')
            utils.logMessage('error', 'Error during call Odoo Function with arguments: %r, %r, %r, %r' % (odooObj, functionName, parameters, kwargParameters), 'callOdooFunction')
            return False

class TimeoutTransport(xmlrpclib.Transport):
    timeout = 10.0
    def set_timeout(self, timeout):
        self.timeout = timeout
    def make_connection(self, host):
        h = httplib.HTTPConnection(host, timeout=self.timeout)
        return h

