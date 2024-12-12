'''
Created on 02 feb 2017

@author: Daniel Smerghetto
'''
import sys
import logging

from OdooQtUi.utils_odoo_conn import constants, utils
from OdooQtUi.RPC.rpc import connectionObj
from OdooQtUi.views.search_obj import TemplateSearchView
from OdooQtUi.views.form_obj import TemplateFormView
from OdooQtUi.views.tree_tree_obj import TemplateTreeTreeView
from OdooQtUi.views.tree_list_obj import TemplateTreeListView
from OdooQtUi.interface.login import LoginDialComplete

from PySide6 import QtWidgets

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class ViewOdooObj(object):

    def __init__(self):
        # Readed Odoo values
        self.odooArch = ''
        self.odooModel = ''
        self.odooViewName = ''
        self.odooViewId = False
        self.odooFieldsNameTypeRel = ''
        # Requested values
        self.localViewType = ''
        self.localOdooObjectName = ''
        self.localViewName = ''
        self.localViewId = False
        self.localViewFilter = False
        self.localSearchMode = ''
        self.useHeader = False
        self.useChatter = False
        self.loginInfos = {}
        self.localViewCheckBoxes = False

    def __str__(self, *args, **kwargs):
        res = super(ViewOdooObj, self).__str__()
        return '[%s -- %s -- %s -- %s] ---- [%s]' % (self.odooModel, self.odooViewName, self.localViewType, self.odooViewId, res)


class MainConnector(object):

    def __init__(self):
        self.activeLanguage = 'en_US'
        self.loadedViews = []
        return super(MainConnector, self).__init__()

    def loginNoUser(self, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        connectionObj.initConnection(loginType, '', '', '', xmlrpcPort, scheme, xmlrpcServerIP)
        return connectionObj.loginNoUser()

    def loginWithUser(self, user, password, dbName, xmlrpcServerIP='127.0.0.1', xmlrpcPort=8069, scheme='http', loginType='xmlrpc'):
        connectionObj.initConnection(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        res = connectionObj.loginWithUser(loginType, user, password, dbName, xmlrpcPort, scheme, xmlrpcServerIP)
        self.activeLanguage = connectionObj.contextUser.get('lang', 'en_US')
        return res

    def loginWithDial(self):
        loginDialInst = LoginDialComplete()
        loginDialInst.interfaceDial.exec()
        if connectionObj.userLogged:
            self.activeLanguage = connectionObj.contextUser.get('lang', 'en_US')
            return True
        return False

    def setLogLevel(self, logInteger=logging.WARNING):
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def _initView(self, viewType, rpcObj, activeLanguage, odooObjectName, viewName, view_id, viewFilter=False, viewCheckBoxes={}, searchMode='ilike', useHeader=False, useChatter=False):
        localLang, rpcObj = self._getCommonLangAndRpc(activeLanguage, rpcObj)
        viewObj = self.checkAlreadyLoadedView(viewType, rpcObj, odooObjectName, viewName, view_id, viewFilter, viewCheckBoxes)
        if not viewObj:
            viewObj = self.appendLoadedView(viewType, rpcObj, odooObjectName, viewName, view_id, viewFilter, viewCheckBoxes, searchMode, useHeader, useChatter)
        utils.logMessage('info', 'Loading view %s' % (viewObj), '_initView')
        return viewObj, localLang, rpcObj

    def initTreeListViewObject(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', viewCheckBoxes={}, viewFilter=False):
        viewObjSearch = None
        viewObj, localLang, rpcObj = self._initView('tree_list', rpcObj, activeLanguage, odooObjectName, viewName, view_id, viewFilter, viewCheckBoxes)
        if viewFilter:
            allFieldsDef = rpcObj.fieldsGet(odooObjectName)
            viewObjSearch = self.initSearchViewObj(odooObjectName, viewName='', view_id='', rpcObj=rpcObj, activeLanguage=activeLanguage, allFieldsDef=allFieldsDef)
        return TemplateTreeListView(rpcObj, viewObj, localLang, viewObjSearch, self)

    def initSearchViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', searchMode='ilike', allFieldsDef={}):
        viewObj, localLang, rpcObj = self._initView('search', rpcObj, activeLanguage, odooObjectName, viewName, view_id, searchMode=searchMode)
        return TemplateSearchView(rpcObj, viewObj, localLang, allFieldsDef)

    def initTreeTreeViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage=''):
        viewObj, localLang, rpcObj = self._initView('tree_tree', rpcObj, activeLanguage, odooObjectName, viewName, view_id)
        return TemplateTreeTreeView(rpcObj, viewObj, localLang)

    def initFormViewObj(self, odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False):
        viewObj, localLang, rpcObj = self._initView('form', rpcObj, activeLanguage, odooObjectName, viewName, view_id, useHeader=useHeader, useChatter=useChatter)
        return TemplateFormView(rpcObj, viewObj, localLang, self)

    def appendLoadedView(self, viewType, rpcObj, odooObjectName, viewName, view_id, viewFilter=False, viewCheckBoxes={}, searchMode='ilike', useHeader=False, useChatter=False):
        odooArch, odooModel, odooViewName, odooViewId, odooFieldsNameTypeRel = self._getViewDefinition(rpcObj, odooObjectName, viewType, viewName, view_id)
        viewOdooObj = ViewOdooObj()
        viewOdooObj.odooArch = odooArch
        viewOdooObj.odooModel = odooModel
        viewOdooObj.odooViewName = odooViewName
        viewOdooObj.odooViewId = odooViewId
        viewOdooObj.odooFieldsNameTypeRel = odooFieldsNameTypeRel

        viewOdooObj.localViewType = viewType
        viewOdooObj.localOdooObjectName = odooObjectName
        viewOdooObj.localViewName = viewName
        viewOdooObj.localViewId = view_id
        viewOdooObj.localViewFilter = viewFilter
        viewOdooObj.localViewCheckBoxes = viewCheckBoxes
        viewOdooObj.localSearchMode = searchMode
        viewOdooObj.useHeader = useHeader
        viewOdooObj.useChatter = useChatter

        viewOdooObj.loginInfos = rpcObj.getLoginInfos()

        self.loadedViews.append(viewOdooObj)
        return viewOdooObj

    def checkAlreadyLoadedView(self,
                               viewType,
                               rpcObj,
                               odooObjectName,
                               viewName,
                               view_id,
                               viewFilter=False,
                               viewCheckBoxes=False,
                               hideFormContent=False):
        loginInfos = rpcObj.getLoginInfos()
        for viewObj in self.loadedViews:
            if viewObj.hasMatch(viewType, odooObjectName, viewName, view_id, viewFilter, loginInfos, viewCheckBoxes, hideFormContent):
                return viewObj
        return False

    def _getCommonLangAndRpc(self, activeLanguage='', rpcObj=None):
        if not activeLanguage:
            activeLanguage = self.activeLanguage
        if not rpcObj:
            rpcObj = connectionObj
        return activeLanguage, rpcObj

    def _searchForView(self, model, viewName, viewType):
        viewIds = connectionObj.search('ir.ui.view', [('name', '=', viewName),
                                                      ('model', '=', model),
                                                      ('type', '=', viewType)])
        if viewIds:
            return viewIds[0]
        utils.logMessage('warning', 'View with name %r and model %r nor found' % (viewName, model), 'searchForView')
        return False

    def _getViewDefinition(self, rpcObj, odooObjectName, viewType='', viewName='', view_id=False):
        if viewType == 'tree_list':
            viewType = 'tree'
        if not view_id and viewName:
            view_id = self._searchForView(odooObjectName, viewName, viewType)
        fieldsViewDefinition, fieldsDetails = rpcObj.fieldsViewGet(odooObjectName, view_id, viewType)
        if fieldsViewDefinition:
            arch = fieldsViewDefinition.get('arch', '')
            model = fieldsViewDefinition.get('model', '')
            viewName = fieldsViewDefinition.get('name', '')
            if self.serverVersion > 16:
                viewId = fieldsViewDefinition.get('id', False)
                fieldsNameTypeRel = fieldsDetails
            else:
                viewId = fieldsViewDefinition.get('view_id', False)
                fieldsNameTypeRel = fieldsViewDefinition.get('fields', '')

            return arch, model, viewName, viewId, fieldsNameTypeRel
        utils.logMessage('warning', 'Unable to read view definition for odooObjectName %r, viewName %r, view_id %r' % (odooObjectName, viewName, view_id), '_getViewDefinition')
        return '', '', '', False, ''


if __name__ == '__main__':
    odooConnector = MainConnector()
    import time
    ts = time.time()

    app = QtWidgets.QApplication(sys.argv)

    @utils.timeit
    def do_test():
        connectorObj = MainConnector()
        if not connectorObj.loginWithDial():
            return do_test()
        connectorObj.loginWithUser('admin', 'admin', 'odoo-11', '127.0.0.1', '8069')
        # connectorObj.loginWithUser('admin', 'admin', 'v11_all', '192.168.99.16', '8069')

        def tryForm(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', useHeader=False, useChatter=False, idToLoad=False):
            tmplViewObj = connectorObj.initFormViewObj(odooObjectName, viewName, view_id, rpcObj, activeLanguage, useHeader, useChatter)
            if idToLoad:
                tmplViewObj.loadIds([idToLoad])
            return tmplViewObj

        def trySearchView(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', searchMode='ilike', allFieldsDef={}):
            return connectorObj.initSearchViewObj(odooObjectName, viewName, view_id, rpcObj, activeLanguage, searchMode, allFieldsDef)

        def tryListView(odooObjectName, viewName='', view_id=False, rpcObj=None, activeLanguage='', viewCheckBoxes={}, viewFilter=False, readonlyFields={}, invisibleFields={}, forceFieldValues={}, forceIds=False):
            tmplViewObj = connectorObj.initTreeListViewObject(odooObjectName, viewName, view_id, rpcObj, activeLanguage, viewCheckBoxes, viewFilter)
            if forceIds:
                tmplViewObj.loadIds(forceIds, forceFieldValues, readonlyFields, invisibleFields)
            else:
                tmplViewObj.loadForceEmptyIds(forceFieldValues, readonlyFields, invisibleFields)
            return tmplViewObj

        # tmplViewObj = tryForm('product.product', idToLoad=284, useChatter=True)
        tmplViewObj = tryForm('product.product', idToLoad=1, useChatter=True)
        # viewCheckBoxes = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
        dialog = QtWidgets.QDialog()
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(tmplViewObj)
        dialog.setLayout(lay)
        dialog.setStyleSheet(constants.VIOLET_BACKGROUND)
        dialog.resize(1200, 600)
        dialog.move(100, 100)
        dialog.show()
        dialog.exec()
        time.sleep(2)
        dialog.exec()
    while 1:
        do_test()

    app.exec()
