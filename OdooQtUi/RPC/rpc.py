# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 02 feb 2017

@author: Daniel
'''
import json
import socket
import logging
import requests
#
from OdooQtUi.RPC.XmlRpc.xmlRpc import XmlRpcConnection
from OdooQtUi.RPC.JsonRpc.jsonRpc import JsonRpcConnection
from OdooQtUi.RPC.errors import OdooRpcError, OdooServerError, OdooConnectionError
from OdooQtUi.utils_odoo_conn.utils import timeit


#
class RpcConnection(object):

    def __init__(self):
        self.userId = False
        self.availableConnTypes = ['jsonrpc', 'secure-jsonrpc', 'xmlrpc', 'secure-xmlrpc']
        self.sockInstance = False
        self.contextUser = {}
        self.useInterface = True
        self.db_from_field = ''
        self.userName = ''
        self.userPassword = ''
        self.databaseName = ''
        self.xmlrpcPort = ''
        self.scheme = ''
        self.xmlrpcServerIP = ''
        self.connectionType = ''
        self.hostname = socket.gethostname()
        self._session_id = False
        # The companies the logged user may work in, [{'id': 1, 'name': '...'}],
        # and the user's own default one: see loadUserCompanies.
        self.userCompanies = []
        self.userDefaultCompanyId = False
        self.clearCache()
        return super(RpcConnection, self).__init__()

    def __str__(self, *args, **kwargs):
        return "UID: %s DB: %s URL %s" % (self.userName,
                                          self.databaseName,
                                          self.xmlrpcServerIP)

    def clearCache(self):
        self._cache_search = {}
        self._cache_search_condition = {}
        self._cache_align_table = {}
        self._cache_read = {}

    def logout(self):
        self.userName = ''
        self.userPassword = ''
        self.sockInstance = False
        self.contextUser.pop('allowed_company_ids', None)
        self.userCompanies = []
        self.userDefaultCompanyId = False

    @property
    def serverVersion(self):
        return self.sockInstance.serverVersion

    def getCleanServer(self):
        return '%s://%s:%s' % (self.scheme, self.xmlrpcServerIP, self.xmlrpcPort)

    def initConnection(self,
                       connectionType,
                       userName,
                       userPassword,
                       databaseName,
                       xmlrpcPort=8069,
                       scheme='http',
                       xmlrpcServerIP='127.0.0.1'):
        old_socket = self.sockInstance
        if old_socket and hasattr(old_socket, 'close'):
            try:
                old_socket.close()
            except Exception as ex:
                logging.warning('Unable to close the previous connection: %r' % ex)
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
        elif connectionType == 'jsonrpc':
            self.sockInstance = JsonRpcConnection(userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP)
            self.sockInstance.useInterface = self.useInterface
        elif connectionType == 'secure-jsonrpc':
            self.sockInstance = JsonRpcConnection(userName, userPassword, databaseName, xmlrpcPort, scheme, xmlrpcServerIP, secure=True)
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
        # The companies of whoever was logged before are not this user's:
        # sent along, Odoo refuses every call with "Access to unauthorized or
        # invalid companies".
        self.contextUser.pop('allowed_company_ids', None)
        self.userCompanies = []
        self.userDefaultCompanyId = False
        res = self.sockInstance.loginWithUser()
        self.userId = self.sockInstance.userId
        if self.userId:
            self.computeUserLanguage()
            self.computeUserCompanies()
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
        try:
            res = self.callCustomMethod('res.users', 'context_get')
        except OdooRpcError as ex:
            # A login is not refused for the language: the context stays empty.
            logging.warning('Unable to get user context: %s' % ex)
            res = {}
        if not res:
            logging.warning('Unable to get user context.')
            res = {}
        self.contextUser.update(res.copy())

    def computeUserCompanies(self):
        """
        load the user's companies and start in the default one, as the web client does

        Odoo keeps no active company per session: every call works in the
        first company of its context key allowed_company_ids, or in the
        user's default company when the key is missing. So the active company
        lives here, in contextUser, and travels with every call.
        """
        try:
            self.loadUserCompanies()
        except OdooRpcError as ex:
            # A login is not refused for the companies: Odoo falls back on the
            # user's default company when the context names none.
            logging.warning('Unable to get user companies: %s' % ex)
            return
        if self.userDefaultCompanyId:
            self.contextUser['allowed_company_ids'] = [self.userDefaultCompanyId]

    def loadUserCompanies(self):
        """
        read the companies the logged user may work in
        :return: [{'id': 1, 'name': 'My Company'}, ...] in the order Odoo lists them
        """
        if not self.userId:
            return []
        users = self.read('res.users', ['company_id', 'company_ids'], [self.userId])
        if not users:
            return []
        user = users[0]
        defaultCompany = user.get('company_id')
        self.userDefaultCompanyId = defaultCompany[0] if defaultCompany else False
        companyIds = user.get('company_ids') or []
        companies = self.readSearch('res.company', ['name'], [('id', 'in', companyIds)]) if companyIds else []
        self.userCompanies = [{'id': company['id'], 'name': company['name']} for company in companies]
        return self.userCompanies

    @property
    def companyId(self):
        """The company the calls work in: the first allowed one, as env.company on the server."""
        allowed = self.contextUser.get('allowed_company_ids')
        if allowed:
            return allowed[0]
        return self.userDefaultCompanyId

    @property
    def companyName(self):
        companyId = self.companyId
        for company in self.userCompanies:
            if company['id'] == companyId:
                return company['name']
        return ''

    @property
    def isMultiCompany(self):
        """The user has more than one company to choose from."""
        return len(self.userCompanies) > 1

    def getCompanyId(self, company):
        """
        the id of one of the user's companies
        :company the company name or its id
        :raise ValueError: the user has no such company, or two with that name
        """
        if isinstance(company, int):
            matches = [c for c in self.userCompanies if c['id'] == company]
        else:
            matches = [c for c in self.userCompanies if c['name'] == company]
        if not matches:
            raise ValueError('The user %r has no company %r' % (self.userName, company))
        if len(matches) > 1:
            raise ValueError('The user %r has more companies named %r: use the id' % (self.userName, company))
        return matches[0]['id']

    def updateCompany(self, company):
        """
        switch the company every following call works in
        :company the company name or its id, one of userCompanies
        :return: the id of the company now active
        :raise ValueError: the user has no such company
        """
        companyId = self.getCompanyId(company)
        self.contextUser['allowed_company_ids'] = [companyId]
        # What was read belongs to the company of before.
        self.clearCache()
        return companyId

    @timeit
    def callCustomMethod(self, odooObj, functionName, parameters=[], kwargParameters={}, context={}, forceHideInterface=False, forceRaise_error=False):
        # Copies, not the session's own dicts: a context given for one call
        # must not stay behind in every call that follows, and the default
        # kwargParameters is shared by every call that does not pass one.
        localContext = dict(self.contextUser)
        localContext.update(context)
        kwargParameters = dict(kwargParameters)
        if localContext:
            kwargParameters['context'] = localContext
        return self.sockInstance.callOdooFunction(odooObj, functionName, parameters, kwargParameters, forceHideInterface, forceRaise_error)

    def search(self, obj, filterList, limit=False, offset=False, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        res = self.sockInstance.search(obj, filterList, limit, offset, context=localContext)
        if not res:
            return []
        return res

    def read(self, obj, fields, ids, context={}, limit=False, load='_classic_read'):
        if not ids:
            return []
        localContext = dict(self.contextUser)
        localContext.update(context)
        if isinstance(ids, int):
            ids = [ids]
        return self.sockInstance.read(obj,
                                      fields,
                                      ids,
                                      limit,
                                      context=localContext,
                                      load=load)

    def readCached(self, obj, fields, ids, context={}, limit=False, load='_classic_read'):
        if obj not in self._cache_read:
            self._cache_read[obj] = {}
        for look_id in ids:
            if look_id not in self._cache_read[obj]:
                for item in self.read(obj, fields, ids, context, limit, load):
                    self._cache_read[obj][look_id] = item
        return [self._cache_read[obj][x] for x in ids]

    def readSearch(self, obj, fields, filterList=[], order=False, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.readSearch(obj,
                                            fields,
                                            filterList,
                                            order=order,
                                            context=localContext)

    def write(self, obj, values, idsToWrite, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.write(obj, values, idsToWrite, context=localContext)

    def writeSearch(self, obj, values, filterList, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        idsToWrite = self.search(obj, filterList)
        return self.write(obj, values, idsToWrite, context=localContext)

    def delete(self, obj, idsToUnlink, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.delete(obj, idsToUnlink, context=localContext)

    def deleteSearch(self, obj, filterList, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        idsToUnlink = self.search(obj, filterList)
        return self.delete(obj, idsToUnlink, context=localContext)

    def searchCount(self, obj, filterList, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.searchCount(obj, filterList, context=localContext)

    def create(self, obj, values, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.create(obj, values, context=localContext)

    def fieldsGet(self, obj, attributesToRead=None, context={}):
        '''
        @attributesToRead: ['string', 'help', 'type'], None means all attributes
        '''
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.fieldsGet(obj, attributesToRead, context=localContext)

    def defaultGet(self, obj, fieldsToRead=[], context={}):
        '''
        @attributesToRead: ['string', 'help', 'type']
        '''
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.defaultGet(obj, fieldsToRead, context=localContext)

    def fieldsViewGet(self, obj, view_id, view_type, context={}):
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.fieldsViewGet(obj, view_id, view_type, context=localContext)

    def on_change(self, obj, activeIds, allVals, fieldName, allOnchanges, context={}):
        """The onchange of Odoo 16 and earlier: one field name and its map."""
        localContext = dict(self.contextUser)
        localContext.update(context)
        return self.sockInstance.on_change(obj, activeIds, allVals, fieldName, allOnchanges, context=localContext)

    def onchange(self, obj, activeIds, values, fieldNames, fieldsSpec, context={}):
        """The onchange of Odoo 17 and later.

        :values     the record as the form holds it, {field: value}
        :fieldNames the fields that changed
        :fieldsSpec {field: {}} for the fields the answer may carry, and
                    {field: {'fields': {...}}} for a relational one
        :return     {'value': {...}, 'warning': {...}}, {} on failure

        Called with the arguments of 16 a server of 17 does not refuse: it
        answers {} and the form never learns what changed.
        """
        return self.callCustomMethod(obj, 'onchange',
                                     [list(activeIds or []), values, list(fieldNames), fieldsSpec],
                                     context=context) or {}

    def EnableException(self):
        """Kept for the callers of old: every failed call raises OdooRpcError now."""
        self.sockInstance.raise_error = True

    def DisableException(self):
        """Kept for the callers of old: errors cannot be turned into None any more."""
        self.sockInstance.raise_error = True

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
                          context={},
                          overWrite=False,
                          only_get=False):
        if not condition:
            raise Exception("You must provide a valid search condition")
        key = "%s_%s" % (objName, condition)
        if key not in self._cache_search_condition:
            res = self.search(objName,
                              condition,
                              context)
            if only_get:
                if not res:
                    return False
            else:
                if not res:
                    res = self.create(objName,
                                         objVals,
                                         context=context)
                    res = [res]
                else:
                    if overWrite:
                        self.write(objName,
                                   objVals,
                                   res,
                                   context=context)
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
                            mapAttributes={},
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
            att[self.db_from_field] = obj_id
            new_id = self.create(objName,
                                 att,
                                 context=context)
        if isinstance(new_id, (list, tuple)):
            for _id in new_id:
                return _id
        return new_id    
    
    def setXmlRpcError(self, value=False):
        """Kept for the callers of old: every failed call raises OdooRpcError, whatever the value."""
        if self.sockInstance:
            self.sockInstance.raise_error = value
    
    def loadSessionId(self):
        """
        load the odoo session id with the credential stored in the xml-rpc
        """
        self._session_id = self.getSessionId()
        
    def getSessionId(self, reload=False):
        """
        create a session id with the connection
        :reload force to reload even if the session id is olready present
        :return: session id
        """
        if not self._session_id or reload:
            payload = json.dumps({
                "jsonrpc": "2.0",
                "params": {"db": self.databaseName,
                           "login": self.userName,
                           "password": self.userPassword}
                })
            headers = {'Content-Type': 'application/json'}
            url = self.getCleanServer() + "/web/session/authenticate"
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()
            self._session_id = response.headers.get('Set-Cookie').split("session_id=")[1].split(";")[0]
        return self._session_id 

    def http_post(self,
                  url,
                  param={},
                  files={},
                  headers={},
                  data={}):
        """
        make an http/https call to odoo server with the xml-rep credential
        """ 
        out = False
        if not self._session_id:
            self.loadSessionId()
        headers['Cookie'] = 'session_id=' + self._session_id
        with requests.post(url=self.getCleanServer() + url,
                           headers=headers,
                           files=files,
                           params=param,
                           data=data) as r:
            r.raise_for_status()
            out = r
        return out
    
    def http_get(self,
                  url,
                  param={},
                  headers={},
                  data={}):
        """
        make an http/https call to odoo server with the xml-rep credential
        """ 
        out = False
        if not self._session_id:
            self.loadSessionId()
        headers['Cookie'] = 'session_id=' + self._session_id
        with requests.post(url=self.getCleanServer() + url,
                           headers=headers,
                           params=param,
                           data=data) as r:
            r.raise_for_status()
            out = r
        return out
    
    def action_archive(self, obj, obj_id):
        self.callCustomMethod(obj, 'plm_lite_archive', [obj_id])
    
    def isActive(self, obj, obj_id):
        for res in self.read(obj, ['active'], [obj_id]):
            return res.get('active')

connectionObj = RpcConnection()
