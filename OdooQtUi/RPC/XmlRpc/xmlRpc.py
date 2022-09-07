'''
Created on 3 Feb 2017

@author: Daniel Smerghetto
'''

from OdooQtUi.utils_odoo_conn import utils
import socket
try:
    import xmlrpc.client as xmlrpc
    import http.client as httplib
except Exception as ex:
    import xmlrpclib as xmlrpc
    import httplib
USE_INTERFACE = True
try:
    from OdooQtUi.utils_odoo_conn import utilsUi
except Exception as ex:
    utils.logError(ex, '')
    USE_INTERFACE = False



class XmlRpcConnection(object):

    def __init__(self,
                 userName,
                 userPassword,
                 databaseName,
                 xmlrpcPort=8069,
                 scheme='http',
                 xmlrpcServerIP='127.0.0.1',
                 secure=False):

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
        self.useInterface = USE_INTERFACE
        self.secure = secure
        self.timeout = 60
        self.login_timeout = 2
        self.serverVersion = 8
        self.max_timeout = 7200
        self.raise_error = False
        self.last_error = ''

    def _logError(self, ex, message='', function_name=''):
        message = message + ' Error: %r' % ex
        utils.logMessage('error',
                         message,
                         function_name)
        if self.raise_error:
            raise ex
        
    def timeoutTransport(self, force=False):
        t = TimeoutTransport()
        if force:
            t.set_timeout(force)
        else:
            t.set_timeout(self.timeout)
        return t

    def _assignServerVersion(self):
        """
            assign odoo server version
        """
        try:
            utils.logMessage('info', 'Trying to compute server version', '_assignServerVersion')
            odooVerInfo = xmlrpc.ServerProxy('{}2/common'.format(self.urlCommon), transport=self.timeoutTransport(self.login_timeout),allow_none=True)
            odooVerDict = odooVerInfo.version()
            serverVersion = odooVerDict.get('server_serie', '')
            if serverVersion == '':
                serverVersion = odooVerDict.get('server_version', '')
                serverVersion = serverVersion.split('-')[0]
                serverVersion = str(serverVersion).split("+")[0]
                serverVersion = serverVersion.replace('e', '')
            self.serverVersion =  int(float(serverVersion))
            utils.logMessage('info', 'Server version is %r' % (self.serverVersion), '_assignServerVersion')
        except Exception as ex:
            self._logError(ex, 'Unable to read server version', utils.getFunctionName())

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
                self.socketNoLogin = xmlrpc.ServerProxy(self.urlNoLogin, transport=self.timeoutTransport(self.login_timeout), allow_none=True)
            except Exception as ex:
                utils.logMessage('error', 'Error during login without user: %r' % (ex), 'loginNoUser')
                return False
        else:
            try:
                self.socketNoLogin = xmlrpc.ServerProxy(self.urlNoLogin, allow_none=True)
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
                self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin, transport=self.timeoutTransport(self.login_timeout), allow_none=True)
                self.socketYesLogin._ServerProxy__transport.timeout = self.timeout
            except Exception as ex:
                utils.logMessage('error', 'Error getting server proxy: %r' % (ex), 'loginWithUser')
                return False
        else:
            try:
                self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin, allow_none=True) 
            except Exception as ex:
                utils.logMessage('error', 'Unable to login with user on secure', 'loginWithUser')
                try:
                    self.xmlrpcType = '/xmlrpc/2/'
                    self.socketNoLogin = xmlrpc.ServerProxy(self.urlCommon, allow_none=True)
                    self.userId = self.socketNoLogin.authenticate(self.databaseName, self.userName, self.userPassword, {})
                    self.socketYesLogin = xmlrpc.ServerProxy(self.urlYesLogin, allow_none=True)
                except Exception as ex:
                    utils.logMessage('error', 'Unable to login with user on secure with autenticate', 'loginWithUser')
                    return False
        self._assignServerVersion()
        utils.logMessage('info', 'Successfull connection to Odoo with user %r and database %r' % (self.userName, self.databaseName), 'loginNoUser')
        return True

    def listDb(self):
        if not self.secure:
            try:
                return xmlrpc.ServerProxy(self.urlListDB, transport=self.timeoutTransport(self.login_timeout), allow_none=True).list()
            except Exception as ex:
                utils.logMessage('warning', 'Unable to list database. EX: %r' % (ex), 'listDb')
                if self.useInterface:
                    utilsUi.popWarning(None, 'Unable to get database list, please check your login settings.')
        else:
            try:
                proxy = xmlrpc.ServerProxy(self.urlListDB, allow_none=True)
                return proxy.list()
            except Exception as ex:
                utils.logMessage('warning', 'Secure try to read database list: %r' % (ex), 'listDb')
                if self.useInterface:
                    utilsUi.popWarning(None, 'Unable to get database list, please check your login settings.')
        return []

    def search(self, obj, filterList, limit=False, offset=False, order='', context={}):
        try:
            kargs = {'context': context}
            if limit or limit == 0:
                kargs['limit'] = limit
            if offset or offset == 0:
                kargs['offset'] = offset
            if order:
                kargs['order'] = order
            return self.callOdooFunction(obj, 'search', [filterList], kargs)
        except Exception as ex:
            msg = 'Error during search with values: object %r, filter %r, parameters %r.' % (obj, filterList, kargs)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def read(self, obj, fields=[], ids=[], limit=False, context={}, load='_classic_read'):
        try:
            kargs = {'context': context, 'load': load}
            return self.callOdooFunction(obj, 'read', [ids, fields], kargs)
        except Exception as ex:
            msg = 'Error during read with values: object %r, fields %r, ids %r.' % (obj, fields, ids)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def fieldsGet(self, obj, attributesToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'attributes': attributesToRead, 'context': context}
            return self.callOdooFunction(obj, 'fields_get', [], kargs)
        except Exception as ex:
            msg = 'Error during reading fields with values: object %r, kargs %r.' % (obj, kargs)
            self._logError(ex, msg, utils.getFunctionName())
        return {}

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'default_get', [fieldsToRead], kargs)
        except Exception as ex:
            msg = 'Error during reading fields with values: object %r, kargs %r.' % (obj, kargs)
            self._logError(ex, msg, utils.getFunctionName())
        return {}

    def readSearch(self, obj, fields, filterList, limit=False, order=False, context={}):
        try:
            kargs = {'fields': fields, 'context': context}
            if order:
                kargs['order'] = order
            return self.callOdooFunction(obj, 'search_read', [filterList], kargs)
        except Exception as ex:
            msg = 'Error during reading fields with values: object %r, kargs %r, filterList' % (obj, kargs)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def create(self, obj, values, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'create', [values], kargs)
        except Exception as ex:
            msg = 'Error during create with values: object %r, kargs %r, filterList %r.' % (obj, kargs, values)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def write(self, obj, values, idsToWrite, context={}, kargs={}):
        try:
            if 'context' not in kargs:
                kargs['context'] = context
            return self.callOdooFunction(obj, 'write', [idsToWrite, values], kargs)
        except Exception as ex:
            msg = 'Error during create with values: object %r, kargs %r, filterList %r.' % (obj, kargs, values)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def delete(self, obj, idsToDelete, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'unlink', [idsToDelete], kargs)
        except Exception as ex:
            msg = 'Error during create with values: object %r, kargs %r, idsToDelete %r.' % (obj, kargs, idsToDelete)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def searchCount(self, obj, filterList, context={}):
        try:
            kargs = {'context': context}
            return self.callOdooFunction(obj, 'search_count', [filterList], kargs)
        except Exception as ex:
            msg = 'Error during create with values: object %r, kargs %r, filterList %r.' % (obj, kargs, filterList)
            self._logError(ex, msg, utils.getFunctionName())
        return []

    def fieldsViewGet(self, odooObj, view_id=False, view_type='form', context={}):
        try:
            if not view_id:
                view_id = False
            kwargParameters = {'context': context}
            return self.callOdooFunction(odooObj, 'fields_view_get', [view_id, view_type], kwargParameters)
        except Exception as ex:
            self._logError(ex, 'Error during fields view get:', utils.getFunctionName())
        return {}

    def on_change(self, odooObj, activeIds, allVals, fieldName, allOnchanges, context):
        try:
            utils.logMessage('debug', 'Onchange field %r' % (fieldName), 'on_change')
            res = self.callOdooFunction(odooObj, 'onchange', [activeIds, allVals, fieldName, allOnchanges], {'context': context})
            if not res:
                return {}
            return res
        except Exception as ex:
            msg =  'Wrong on_change call with odooObj: %r, fieldName: %r, activeIds: %r, context: %r.' % (odooObj, fieldName, activeIds, context)
            self._logError(ex, msg, utils.getFunctionName())
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
            msg =  'Error during call Odoo Function execute with arguments: %r, %r, %r, %r' % (obj, method, args)
            self._logError(ex, msg, utils.getFunctionName())
            return False

    def sanitizeVersionFunction(self, functionName):
        if self.serverVersion==14:
            if functionName == 'context_get': 
                functionName = 'koo_context_get'
            if functionName == 'fields_view_get': 
                functionName = 'koo_fields_view_get'            
        return functionName
    
    #@utils.timeit
    def callOdooFunction(self, odooObj, functionName, parameters=[], kwargParameters={}, forceHideInterface=False, forceRaise_error=False):
        '''
            @odooObj: product.product, product.template ...
            @functionName: 'search', 'read', ...
            @parameters: [val1, val2, ...]
            @kwargParameters: {'context': {}, limit: val, 'order': val,...}
        '''
        if self.socketYesLogin in [None, False]:
            raise Exception("Socket not inizialized properly")
        self.last_error = ''
        try:
            functionName = self.sanitizeVersionFunction(functionName)
            return self.socketYesLogin.execute_kw(self.databaseName,
                                                  self.userId,
                                                  self.userPassword,
                                                  odooObj,
                                                  functionName,
                                                  parameters,
                                                  kwargParameters)
        except socket.error as err:
            if self.raise_error or forceRaise_error:
                raise err
            message = 'Unable to communicate with the server: %r calling %r on %r' % (err, functionName, odooObj)
            utils.logMessage('error', message, 'callOdooFunction')
            if self.useInterface and not forceHideInterface:
                utilsUi.popError(self, message)
            else:
                self._logError(err, message, utils.getFunctionName())
        except xmlrpc.Fault as err:
            if self.raise_error or forceRaise_error:
                raise err
            try:
                self.last_error = str(err)
                if self.useInterface and not forceHideInterface:
                    utilsUi.popError(self, err)
                    return None
                else:
                    err_str = err.faultString or err.faultCode
                    if err_str:
                        utils.logError(err_str, 'callOdooFunction')
                    return None
                return self.socketYesLogin.execute(self.databaseName,
                                                   self.userId,
                                                   self.userPassword,
                                                   odooObj,
                                                   functionName,
                                                   parameters)
            except Exception as ex:

                if self.raise_error or forceRaise_error:
                    raise err
                self.last_error = str(ex)
                utils.logMessage('error', ex, 'callOdooFunction')
                message = 'Unable to communicate with the server: %r' % ex.faultCode
                if self.useInterface and not forceHideInterface:
                    utilsUi.popError(None, message)
                else:
                    self._logError(ex, message, utils.getFunctionName())
        except Exception as ex:
            if self.raise_error or forceRaise_error:
                raise err
            self.last_error = str(ex)
            utils.logMessage('error', ex, 'callOdooFunction')
            utils.logMessage('error',
                             'Error during call Odoo Function with arguments: %r, %r, %r, %r' % (odooObj,
                                                                                                 functionName,
                                                                                                 parameters,
                                                                                                 kwargParameters),
                             'callOdooFunction')
            if self.useInterface and not forceHideInterface:
                utilsUi.popError(self, ex)
            else:
                self._logError(ex, '', utils.getFunctionName())
        return None


class TimeoutTransport(xmlrpc.Transport):
    timeout = 5.0

    def set_timeout(self, timeout):
        self.timeout = timeout

    def make_connection(self, host):
        h = httplib.HTTPConnection(host, timeout=self.timeout)
        return h
