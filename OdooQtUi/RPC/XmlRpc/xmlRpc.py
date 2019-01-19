'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''

from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.utils_odoo_conn import utilsUi
import xmlrpc.client as xmlrpc
import http.client as httplib
import socket


class XmlRpcConnection(object):

    def __init__(self, userName, userPassword, databaseName, xmlrpcPort=8069, scheme='http', xmlrpcServerIP='127.0.0.1', secure=False):
        self.userName = userName
        self.userPassword = userPassword
        self.databaseName = databaseName
        self.xmlrpcPort = xmlrpcPort
        self.scheme = scheme
        self.xmlrpcServerIP = xmlrpcServerIP
        self.xmlrpcType = '/xmlrpc/' # '/xmlrpc/2/' (no login is available)
        # self.urlCommon = self.scheme + '://' + str(self.xmlrpcServerIP) + ':' + str(self.xmlrpcPort) + self.xmlrpcType
        # self.urlNoLogin = self.urlCommon + 'common'
        # self.urlListDB = self.urlCommon + 'db'
        # self.urlYesLogin = self.urlCommon + 'object'
        self.socketNoLogin = False
        self.socketYesLogin = False
        self.userId = False
        self.useInterface = True
        self.secure = secure

    @property
    def urlNoLogin(self):
        return self.urlCommon + 'common'

    @property
    def urlListDB(self):
        return self.urlCommon + 'db'

    @property
    def urlYesLogin(self):
        return self.urlCommon + 'object'

    @property
    def urlCommon(self):
        return self.scheme + '://' + str(self.xmlrpcServerIP) + ':' + str(self.xmlrpcPort) + self.xmlrpcType
        
    def loginNoUser(self):
        if not self.secure:
            try:
                t = TimeoutTransport()
                t.set_timeout(2.5)
                self.socketNoLogin = xmlrpc.ServerProxy(self.urlNoLogin, transport=t)
            except Exception as ex:
                utils.logMessage('error', 'Error during login without user: %r' % (ex), 'loginNoUser')
                return False
        else:
            try:
                self.socketNoLogin = xmlrpc.ServerProxy(self.urlNoLogin)
            except Exception as ex:
                utils.logMessage('error', 'Error during login without user on secure: %r' % (ex), 'loginNoUser')
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
        except Exception as ex:
            utils.logMessage('error', 'Error during login with user: %r' % (ex), 'loginWithUser')
            return False
        if not self.secure:
            try:
                t = TimeoutTransport()
                t.set_timeout(2.5)
                self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin, transport=t)
            except Exception as ex:
                utils.logMessage('error', 'Error getting server proxy: %r' % (ex), 'loginWithUser')
                return False
        else:
            try:
                self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin) 
            except Exception as ex:
                utils.logMessage('error', 'Unable to login with user on secure', 'loginWithUser')
                try:
                    self.xmlrpcType = '/xmlrpc/2/'
                    self.socketNoLogin = xmlrpc.ServerProxy(self.urlCommon)
                    self.userId = self.socketNoLogin.authenticate(self.databaseName, self.userName, self.userPassword, {})
                    self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin)
                except Exception as ex:
                    utils.logMessage('error', 'Unable to login with user on secure with autenticate', 'loginWithUser')
                    return False
        utils.logMessage('info', 'Successfull connection to Odoo with user %r and database %r' % (self.userName, self.databaseName), 'loginNoUser')
        return True

    def listDb(self):
        if not self.secure:
            try:
                t = TimeoutTransport()
                t.set_timeout(2.5)
                return xmlrpc.ServerProxy(self.urlListDB, transport=t).list()
            except Exception as ex:
                utils.logMessage('warning', 'Unable to list database. EX: %r' % (ex), 'listDb')
                if self.useInterface:
                    utilsUi.launchMessage('Unable to get database list, please check your login settings.', 'warning')
        else:
            try:
                proxy = xmlrpc.ServerProxy(self.urlListDB)
                return proxy.list()
            except Exception as ex:
                utils.logMessage('warning', 'Secure try to read database list: %r' % (ex), 'listDb')
                if self.useInterface:
                    utilsUi.launchMessage('Unable to get database list, please check your login settings.', 'warning')
        return []

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        try:
            kargs = {'context': context}
            if limit or limit == 0:
                kargs['limit'] = limit
            if offset or offset == 0:
                kargs['offset'] = offset
            return self.callOdooFunction(obj, 'search', [filterList], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during search with values: object %r, filter %r, parameters %r. Error: %r' % (obj, filterList, kargs, ex), 'search')
        return []

    def read(self, obj, fields=[], ids=[], limit=False, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'read', [ids, fields], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during read with values: object %r, fields %r, ids %r. Error: %r' % (obj, fields, ids, ex), 'read')
        return []

    def fieldsGet(self, obj, attributesToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'attributes': attributesToRead, 'context': context}
            return self.callOdooFunction(obj, 'fields_get', [], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r. Error: %r' % (obj, kargs, ex), 'fieldsGet')
        return {}

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'default_get', [fieldsToRead], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r. Error: %r' % (obj, kargs, ex), 'fieldsGet')
        return {}

    def readSearch(self, obj, fields, filterList, limit=False, context={}):
        try:
            kargs = {'fields': fields, 'context': context}
            return self.callOdooFunction(obj, 'search_read', [filterList], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during reading fields with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, filterList, ex), 'readSearch')
        return []

    def create(self, obj, values, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'create', [values], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, values, ex), 'create')
        return []

    def write(self, obj, values, idsToWrite, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'write', [idsToWrite, values], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, values, ex), 'write')
        return []

    def delete(self, obj, idsToDelete, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'unlink', [idsToDelete], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, idsToDelete %r. Error: %r' % (obj, kargs, idsToDelete, ex), 'delete')
        return []

    def searchCount(self, obj, filterList, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'search_count', [filterList], kargs)
        except Exception as ex:
            utils.logMessage('error', 'Error during create with values: object %r, kargs %r, filterList %r. Error: %r' % (obj, kargs, filterList, ex), 'searchCount')
        return []

    def fieldsViewGet(self, odooObj, view_id=False, view_type='form', context={}):
        try:
            if not view_id:
                view_id = False
            kwargParameters = {'context': context}
            return self.callOdooFunction(odooObj, 'fields_view_get', [view_id, view_type], kwargParameters)
        except Exception as ex:
            utils.logMessage('error', 'Error during fields view get: %r' % (ex), 'fieldsViewGet')
        return {}

    def on_change(self, odooObj, activeIds, allVals, fieldName, allOnchanges, context):
        try:
            utils.logMessage('debug', 'Onchange field %r' % (fieldName), 'on_change')
            res = self.callOdooFunction(odooObj, 'onchange', [activeIds, allVals, fieldName, allOnchanges], {'context': context})
            if not res:
                return {}
            return res
        except Exception as ex:
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
        except Exception as ex:
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
        except socket.error as err:
            message = 'Unable to communicate with the server: %r' % err
            if self.useInterface:
                utilsUi.launchMessage(message, 'error')
            utils.logMessage('error', message, 'callOdooFunction')
        except xmlrpc.Fault as err:
            try:
                if err.faultString:
                    if self.useInterface:
                        utilsUi.launchMessage(err.faultString, 'error')
                return self.socketYesLogin.execute(self.databaseName, self.userId, self.userPassword, odooObj, functionName, parameters)
            except Exception as ex:
                message = 'Unable to communicate with the server: %r' % ex.faultCode
                if self.useInterface:
                    utilsUi.launchMessage(message, 'error')
                utils.logMessage('error', message, 'callOdooFunction')
        except Exception as ex:
            if self.useInterface:
                utilsUi.launchMessage(ex, 'error')
            utils.logMessage('error', ex, 'callOdooFunction')
            utils.logMessage('error', 'Error during call Odoo Function with arguments: %r, %r, %r, %r' % (odooObj, functionName, parameters, kwargParameters), 'callOdooFunction')
        return False


class TimeoutTransport(xmlrpc.Transport):
    timeout = 5.0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        h = httplib.HTTPConnection(host, timeout=self.timeout)
        return h
