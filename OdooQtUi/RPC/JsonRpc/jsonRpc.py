# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 14 Aug 2026

JSON-RPC transport, drop-in replacement for RPC.XmlRpc.xmlRpc.XmlRpcConnection.
Talks to Odoo's generic /jsonrpc endpoint, which dispatches to the same
'common' / 'db' / 'object' services XML-RPC uses (see odoo/http.py:dispatch_rpc
and odoo/addons/base/controllers/rpc.py on the server).
'''

import socket
import threading
import traceback
import requests

from OdooQtUi.utils_odoo_conn import utils
import reprlib
from OdooQtUi.RPC.errors import OdooRpcError, OdooServerError, OdooConnectionError

_SHORT = reprlib.Repr()
_SHORT.maxstring = 200
_SHORT.maxother = 200
#: Kept for the code that still reads it: the RPC layer shows no window any more.
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
        # One Session per thread: without it every RPC opens a new TCP
        # connection (and a new TLS handshake on https), and a single save
        # makes ~55 of them. Per thread rather than shared, because
        # SaveStructure calls in from worker threads and a Session's cookie
        # jar is not meant to be written concurrently.
        self._local = threading.local()

    @property
    def session(self):
        session = getattr(self._local, 'session', None)
        if session is None:
            session = requests.Session()
            self._local.session = session
        return session

    def close(self):
        session = getattr(self._local, 'session', None)
        if session is not None:
            session.close()
            self._local.session = None

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
            response = self.session.post(self.urlCommon,
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
        utils.logMessage('debug', 'Onchange field %r' % (fieldName), 'on_change')
        return self.callOdooFunction(odooObj, 'onchange', [activeIds, allVals, fieldName, allOnchanges], {'context': context}) or {}

    def execute_kw(self, obj, method, *args, **kargs):
        return self.callOdooFunction(obj, method, args, kargs)

    def execute(self, obj, method, *args):
        """The positional `execute` of old, made through execute_kw: same answer, same errors."""
        if method == 'execute_kw':
            odooObj, functionName, parameters, kwargParameters = args
            return self.callOdooFunction(odooObj, functionName, parameters, kwargParameters)
        return self.callOdooFunction(obj, method, list(args), {})

    def sanitizeVersionFunction(self, functionName):
        if self.serverVersion==14:
            if functionName == 'context_get':
                functionName = 'koo_context_get'
        if functionName == 'fields_view_get':
            functionName = 'koo_fields_view_get'
        return functionName

    def callOdooFunction(self, odooObj, functionName, parameters=[], kwargParameters={}, forceHideInterface=False, forceRaise_error=False):
        """Call `functionName` on the model `odooObj` and answer what Odoo answers.

        :raise OdooServerError      Odoo refused the call (UserError, AccessError...)
        :raise OdooConnectionError  the call did not reach Odoo or did not come back
        :raise OdooRpcError         anything else, e.g. a value that cannot be sent

        Never shows a window. forceHideInterface and forceRaise_error are
        accepted for the callers of old and change nothing: every error raises.
        """
        if self.socketYesLogin in [None, False]:
            raise OdooConnectionError('Not logged in', odooObj, functionName)
        self.last_error = ''
        functionName = self.sanitizeVersionFunction(functionName)
        try:
            return self._call('object', 'execute_kw', [self.databaseName,
                                                        self.userId,
                                                        self.userPassword,
                                                        odooObj,
                                                        functionName,
                                                        parameters,
                                                        kwargParameters])
        except JsonRpcFault as err:
            cause = err
            self.last_error = str(err.faultString or err.faultCode)
            error = OdooServerError(self.last_error.strip().splitlines()[-1] if self.last_error.strip() else str(err),
                                    odooObj, functionName, err.faultCode, err.faultString)
        except OSError as err:
            cause = err
            self.last_error = str(err)
            error = OdooConnectionError('Unable to communicate with the server: %s' % err, odooObj, functionName)
        except Exception as err:
            cause = err
            self.last_error = str(err)
            error = OdooRpcError('%s: %s' % (type(err).__name__, err), odooObj, functionName)
        # Shortened: the arguments of a save carry whole files in base64.
        utils.logMessage('error', '%s -- arguments %s' % (error, _SHORT.repr((parameters, kwargParameters))), 'callOdooFunction')
        raise error from cause
