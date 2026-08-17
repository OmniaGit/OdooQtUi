'''
Created on 14 Aug 2026

JSON-RPC transport, drop-in replacement for RPC.XmlRpc.xmlRpc.XmlRpcConnection.
Talks to Odoo's generic /jsonrpc endpoint, which dispatches to the same
'common' / 'db' / 'object' services XML-RPC uses (see odoo/http.py:dispatch_rpc
and odoo/addons/base/controllers/rpc.py on the server).
'''

import socket
import traceback
import requests

from OdooQtUi.utils_odoo_conn import utils
USE_INTERFACE = True
try:
    from OdooQtUi.utils_odoo_conn import utilsUi
except Exception as ex:
    utils.logError(ex, '')
    USE_INTERFACE = False


class JsonRpcFault(Exception):
    '''
    Mirrors the shape of xmlrpc.client.Fault so shared error-handling code
    (e.g. utilsUi.popError) can duck-type on faultCode/faultString regardless
    of which transport raised it.
    '''
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString
        super(JsonRpcFault, self).__init__(faultString)


class JsonRpcConnection(object):

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
        self.xmlrpcType = '/jsonrpc'
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
        self._request_id = 0

    def _logError(self, ex, message='', function_name=''):
        message = message + ' Error: %r' % ex
        utils.logMessage('error',
                         message,
                         function_name)
        if self.raise_error:
            raise ex

    @property
    def urlCommon(self):
        return self.scheme + '://' + str(self.xmlrpcServerIP) + ':' + str(self.xmlrpcPort) + self.xmlrpcType

    # kept for interface parity with XmlRpcConnection: everything goes through
    # the single /jsonrpc endpoint, service routing happens in the JSON body.
    @property
    def urlNoLogin(self):
        return self.urlCommon

    @property
    def urlListDB(self):
        return self.urlCommon

    @property
    def urlYesLogin(self):
        return self.urlCommon

    def _call(self, service, method, args, timeout=None):
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"service": service, "method": method, "args": args},
            "id": self._request_id,
        }
        try:
            response = requests.post(self.urlCommon,
                                     json=payload,
                                     timeout=timeout or self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as ex:
            raise socket.error(str(ex))
        if data.get('error'):
            err = data['error']
            err_data = err.get('data') or {}
            raise JsonRpcFault(err.get('code'), err_data.get('message') or err.get('message') or str(err))
        return data.get('result')

    def checkVersion(self):
        return self._call('common', 'version', [], timeout=self.login_timeout)

    def _assignServerVersion(self):
        """
            assign odoo server version
        """
        try:
            utils.logMessage('info', 'Trying to compute server version', '_assignServerVersion')
            odooVerDict = self.checkVersion()
            serverVersion = odooVerDict.get('server_serie', '')
            if serverVersion == '':
                serverVersion = odooVerDict.get('server_version', '')
                serverVersion = serverVersion.split('-')[0]
                serverVersion = str(serverVersion).split("+")[0]
                serverVersion = serverVersion.replace('e', '')
            self.serverVersion = int(float(serverVersion))
            utils.logMessage('info', 'Server version is %r' % (self.serverVersion), '_assignServerVersion')
        except Exception as ex:
            self._logError(ex, 'Unable to read server version', utils.getFunctionName())

    def loginNoUser(self):
        # JSON-RPC has no persistent proxy object to open; the endpoint is
        # stateless HTTP, so this just marks the transport ready.
        self.socketNoLogin = True
        utils.logMessage('info', 'Successfull connection to Odoo using login No User', 'loginNoUser')
        return True

    def loginWithUser(self):
        if not self.socketNoLogin:
            self.loginNoUser()
        try:
            self.userId = self._call('common', 'login', [self.databaseName, self.userName, self.userPassword])
            if not self.userId:
                return False
        except Exception as ex:
            utils.logMessage('error', 'Error during login with user: %r' % (ex), 'loginWithUser')
            return False
        self.socketYesLogin = True
        self._assignServerVersion()
        utils.logMessage('info', 'Successfull connection to Odoo with user %r and database %r' % (self.userName, self.databaseName), 'loginNoUser')
        return True

    def listDb(self):
        try:
            return self._call('db', 'list', [])
        except Exception as ex:
            print(traceback.format_exc())
            utils.logMessage('warning', 'Unable to list database. EX: %r' % (ex), 'listDb')
            if self.useInterface:
                utilsUi.popWarning(None, 'Unable to get the list of database available from the server. '
                                         'Ask your Odoo administrator the database name and write it '
                                         'to the following input box.')
        return []

    def search(self, obj, filterList, limit=False, offset=False, order='', context={}):
        kargs = {'context': context}
        if limit or limit == 0:
            kargs['limit'] = limit
        if offset or offset == 0:
            kargs['offset'] = offset
        if order:
            kargs['order'] = order
        return self.callOdooFunction(obj, 'search', [filterList], kargs)

    def read(self, obj, fields=[], ids=[], limit=False, context={}, load='_classic_read'):
        kargs = {'context': context, 'load': load}
        return self.callOdooFunction(obj, 'read', [ids, fields], kargs)

    def fieldsGet(self, obj, attributesToRead=None, context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}, None means all attributes
        '''
        kargs = {'attributes': attributesToRead, 'context': context}
        return self.callOdooFunction(obj, 'fields_get', [], kargs)

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: {'attributes': ['string', 'help', 'type']}
        '''
        kargs = {'context': context}
        return self.callOdooFunction(obj, 'default_get', [fieldsToRead], kargs)

    def readSearch(self, obj, fields, filterList, limit=False, order=False, context={}):
        kargs = {'fields': fields, 'context': context}
        if order:
            kargs['order'] = order
        return self.callOdooFunction(obj, 'search_read', [filterList], kargs)

    def create(self, obj, values, context={}):
        kargs = {'context': context}
        return self.callOdooFunction(obj, 'create', [values], kargs)

    def write(self, obj, values, idsToWrite, context={}, kargs={}):
        if 'context' not in kargs:
            kargs['context'] = context
        return self.callOdooFunction(obj, 'write', [idsToWrite, values], kargs)

    def delete(self, obj, idsToDelete, context={}):
        kargs = {'context': context}
        return self.callOdooFunction(obj, 'unlink', [idsToDelete], kargs)

    def searchCount(self, obj, filterList, context={}):
        kargs = {'context': context}
        return self.callOdooFunction(obj, 'search_count', [filterList], kargs)

    def fieldsViewGet(self, odooObj, view_id=False, view_type='form', context={}):
        if not view_id:
            view_id = False
        kwargParameters = {'context': context}
        return self.callOdooFunction(odooObj, 'fields_view_get', [view_id, view_type], kwargParameters)

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
            return self._call('object', 'execute', [self.databaseName,
                                                     self.userId,
                                                     self.userPassword,
                                                     obj,
                                                     method] + list(args))
        except Exception as ex:
            msg =  'Error during call Odoo Function execute with arguments: %r, %r, %r' % (obj, method, args)
            self._logError(ex, msg, utils.getFunctionName())
            return False

    def sanitizeVersionFunction(self, functionName):
        if self.serverVersion==14:
            if functionName == 'context_get':
                functionName = 'koo_context_get'
        if functionName == 'fields_view_get':
            functionName = 'koo_fields_view_get'
        return functionName

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
            return self._call('object', 'execute_kw', [self.databaseName,
                                                        self.userId,
                                                        self.userPassword,
                                                        odooObj,
                                                        functionName,
                                                        parameters,
                                                        kwargParameters])
        except socket.error as err:
            if self.raise_error or forceRaise_error:
                raise err
            message = 'Unable to communicate with the server: %r calling %r on %r' % (err, functionName, odooObj)
            utils.logMessage('error', message, 'callOdooFunction')
            if self.useInterface and not forceHideInterface:
                utilsUi.popError(self, message)
            else:
                self._logError(err, message, utils.getFunctionName())
        except JsonRpcFault as err:
            if self.raise_error or forceRaise_error:
                raise err
            self.last_error = str(err)
            if self.useInterface and not forceHideInterface:
                utilsUi.popError(None, err)
                return None
            else:
                err_str = err.faultString or err.faultCode
                if err_str:
                    utils.logError(err_str, 'callOdooFunction')
                return None
        except Exception as ex:
            if self.raise_error or forceRaise_error:
                raise ex
            self.last_error = str(ex)
            utils.logMessage('error', ex, 'callOdooFunction')
            utils.logMessage('error',
                             'Error during call Odoo Function with arguments: %r, %r, %r, %r' % (odooObj,
                                                                                                 functionName,
                                                                                                 parameters,
                                                                                                 kwargParameters),
                             'callOdooFunction')
            if self.useInterface and not forceHideInterface:
                utilsUi.popError(None, ex)
            else:
                self._logError(ex, '', utils.getFunctionName())
        return None
