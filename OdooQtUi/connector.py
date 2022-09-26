'''
Created on 02 feb 2017

@author: Daniel Smerghetto
'''
import logging

from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.RPC.rpc import RpcConnection
from OdooQtUi.views.search_obj import TemplateSearchView
from OdooQtUi.views.form_obj import TemplateFormView
from OdooQtUi.views.tree_tree_obj import TemplateTreeTreeView
from OdooQtUi.views.tree_list_obj import TemplateTreeListView
from OdooQtUi.interface.login import LoginDialComplete

logger = logging.getLogger()
logger.setLevel(utils.getDebugSeverity())


class ViewOdooObj(object):
    """
        view info container
    """
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

    def hasMatch(self,
                 localViewType, 
                 localOdooObjectName, 
                 localViewName, 
                 localViewId, 
                 localViewFilter, 
                 loginInfos, 
                 viewCheckBoxes, 
                 hideFormContent):
        if self.localViewType == localViewType and \
            self.localOdooObjectName == localOdooObjectName and \
            self.localViewName == localViewName and \
            self.localViewId == localViewId and \
            self.localViewFilter == localViewFilter and \
            self.loginInfos == loginInfos and \
            self.localViewCheckBoxes == viewCheckBoxes:
            self.hideFormContent == hideFormContent
            return True
        return False

    def __str__(self, *args, **kwargs):
        res = super(ViewOdooObj, self).__str__()
        return '[%s -- %s -- %s -- %s] ---- [%s]' % (self.odooModel, self.odooViewName, self.localViewType, self.odooViewId, res)


class MainConnector(object):
    def __init__(self,
                 parentWindow=None,
                 contextUser={},
                 app_name='OdooQtUi',
                 raise_error=False):
        """
        create the main odoo connector
        :parentWindow pySide2 main window
        :contextUser dict like context to be used for all the xml-rpc call
        :app_name str object that specifie the application name
        :raise_error in case of rpc call has an error rise an expception
        """
        self.rpc_connector = RpcConnection()
        self.rpc_connector.contextUser.update(contextUser)
        self.activeLanguage = 'en_US'
        self.app_name = app_name
        self.loadedViews = []
        self._parentWindow = parentWindow
        self._raise_error = raise_error
    
    @property
    def deltaTime(self):
        """
        return the delta time calculated from server to client machine time
        """
        return self.rpc_connector.deltaTime
    
    def loginNoUser(self, 
                    xmlrpcServerIP='127.0.0.1', 
                    xmlrpcPort=8069, 
                    scheme='http', 
                    loginType='xmlrpc'):
        """
        perform the login operation with blank user also reset the cached views
        this function is useful when you need to change the connection in order to reset all the data
        :xmlrpcServerIP='127.0.0.1' server ip address 
        :xmlrpcPort=8069 server port 
        :scheme='http' schema ['http', 'https']
        :loginType='xmlrpc' login type 
        """
        self.loadedViews = [] # reset the cashed view because you can change db
        self.rpc_connector.initConnection(loginType, '', '', '', xmlrpcPort, scheme, xmlrpcServerIP)
        return self.rpc_connector.loginNoUser()

    def loginWithUser(self, 
                      user, 
                      password, 
                      dbName, 
                      xmlrpcServerIP='127.0.0.1', 
                      xmlrpcPort=8069, 
                      scheme='http', 
                      loginType='xmlrpc',
                      context={}):
        """
        perform the login operation with given user
        remarks also perform the view cache to be cleened
        :user odoo login user
        :password odoo password
        :dbName odoo database
        :xmlrpcServerIP '127.0.0.1' server ip address 
        :xmlrpcPort 8069 server port 
        :scheme 'http' schema ['http', 'https']
        :loginType 'xmlrpc' login type 
        :context dict like object to be use to update the context for the given session
        """
        self.loadedViews = [] # reset the cashed view because you can change db 
        res = self.rpc_connector.loginWithUser(connectionType=loginType,
                                               userName=user,
                                               userPassword=password,
                                               databaseName=dbName,
                                               xmlrpcPort=xmlrpcPort, 
                                               scheme=scheme, 
                                               xmlrpcServerIP=xmlrpcServerIP)
        self.rpc_connector.contextUser.update(context)
        self.activeLanguage = self.rpc_connector.contextUser.get('lang', 'en_US')
        self.rpc_connector.setXmlRpcError(self._raise_error)
    
    def loginFromStorage(self):
        """
        perform the login operation from the storage file
        :return: True is logged, False is not logged         
        """
        try:
            dbName, username, userpass, serverIp, serverPort, scheme, connType, _dbList = utils.loadFromFile(self.app_name)
       
            self.loginWithUser(user=username,
                               password=userpass,
                               dbName=dbName,
                               xmlrpcServerIP=serverIp,
                               xmlrpcPort=serverPort,
                               scheme=scheme,
                               loginType=connType)
        except Exception as ex:
            logging.error("Unable to autologin %s" % ex)
        return self.userLogged
        
    @property
    def userLogged(self):
        """
        user is logged to rpc connectior
        """
        return self.rpc_connector.userLogged

    def loginWithDial(self, context={}):
        """
        Show the login dialog in order to perform the login operation
        :context dict like additional context for all the coll
        :return: True is logged, False not logged
        """
        loginDialInst = LoginDialComplete(app_name=self.app_name,
                                          odooConnector=self)
        loginDialInst.exec_()
        if self.userLogged:
            self.loadedViews = [] # reset the cashed view because you can change db
            self.rpc_connector.contextUser.update(context) 
            self.activeLanguage = self.rpc_connector.contextUser.get('lang', 'en_US')
            return True
        return False

    def setLogLevel(self, logInteger=logging.WARNING):
        """
        set the log level
        :logInteger logging.WARNING log level default WARNING
        """
        logger = logging.getLogger()
        logger.setLevel(logInteger)

    def _initView(self, 
                  viewType, 
                  odooObjectName, 
                  viewName, 
                  view_id, 
                  viewFilter=False, 
                  viewCheckBoxes={}, 
                  searchMode='ilike', 
                  useHeader=False, 
                  useChatter=False,
                  hideFormContent=False):
        try:
            viewObj = self.checkAlreadyLoadedView(viewType,
                                                  odooObjectName,
                                                  viewName,
                                                  view_id,
                                                  viewFilter,
                                                  viewCheckBoxes)
            if not viewObj:
                viewObj = self.appendLoadedView(viewType=viewType,
                                                odooObjectName=odooObjectName,
                                                viewName=viewName,
                                                view_id=view_id,
                                                viewFilter=viewFilter,
                                                viewCheckBoxes=viewCheckBoxes,
                                                searchMode=searchMode,
                                                useHeader=useHeader,
                                                useChatter=useChatter,
                                                hideFormContent=hideFormContent)
            utils.logMessage('info', 'Loading view %s' % (viewObj), '_initView')
            return viewObj
        except Exception as ex:
            logging.error(ex)
            raise ex

    def initTreeListViewObject(self,
                               odooObjectName,
                               viewName='',
                               view_id=False, 
                               viewCheckBoxes={}, 
                               viewFilter=False, 
                               deafult_filter=[],
                               remove_button=False):
        try:
            viewObjSearch = None
            viewObj = self._initView('tree_list',
                                     odooObjectName,
                                     viewName,
                                     view_id,
                                     viewFilter,
                                     viewCheckBoxes)
            if viewFilter:
                allFieldsDef = self.rpc_connector.fieldsGet(odooObjectName)
                viewObjSearch = self.initSearchViewObj(odooObjectName,
                                                       viewName='',
                                                       view_id='',
                                                       allFieldsDef=allFieldsDef)
            return TemplateTreeListView(odooConnector=self,
                                        viewObj=viewObj,
                                        searchObj=viewObjSearch,
                                        deafult_filter=deafult_filter,
                                        remove_button=remove_button)
        except Exception as ex:
            logging.error("Exception Ex %r" % ex)
            raise ex

    def initSearchViewObj(self,
                          odooObjectName,
                          viewName='',
                          view_id=False,
                          searchMode='ilike',
                          allFieldsDef={}):
        viewObj = self._initView(viewType='search',
                                 odooObjectName=odooObjectName,
                                 viewName=viewName,
                                 view_id=view_id,
                                 searchMode=searchMode)
        return TemplateSearchView(odooConnector=self,
                                  viewObject=viewObj,
                                  allFieldsDef=allFieldsDef)

    def initTreeTreeViewObj(self,
                            odooObjectName,
                            viewName='',
                            view_id=False):
        viewObj = self._initView(viewType='tree_tree',
                                 odooObjectName=odooObjectName,
                                 viewName=viewName,
                                 view_id=view_id)
        return TemplateTreeTreeView(odooConnector=self,
                                    viewObject=viewObj)

    def initFormViewObj(self,
                        odooObjectName, 
                        viewName='', 
                        view_id=False, 
                        useHeader=False, 
                        useChatter=False,
                        hideFormContent=False):
        """
        Initialize a odoo form view to be used
        """
        viewObj= self._initView(viewType='form',
                                odooObjectName=odooObjectName,
                                viewName=viewName, 
                                view_id=view_id, 
                                useHeader=useHeader, 
                                useChatter=useChatter,
                                hideFormContent=hideFormContent)
        return TemplateFormView(odooConnector=self,
                                viewObj=viewObj,
                                hideFormContent=hideFormContent)

    def appendLoadedView(self,
                         viewType,
                         odooObjectName,
                         viewName,
                         view_id,
                         viewFilter=False,
                         viewCheckBoxes={},
                         searchMode='ilike',
                         useHeader=False,
                         useChatter=False,
                         hideFormContent=False):
        odooArch, odooModel, odooViewName, odooViewId, odooFieldsNameTypeRel = self._getViewDefinition(odooObjectName=odooObjectName,
                                                                                                       viewType=viewType, 
                                                                                                       viewName=viewName,
                                                                                                       view_id=view_id)
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
        viewOdooObj.hideFormContent=hideFormContent
        viewOdooObj.loginInfos = self.rpc_connector.getLoginInfos()
        #
        self.loadedViews.append(viewOdooObj)
        #
        return viewOdooObj

    def checkAlreadyLoadedView(self,
                               viewType,
                               odooObjectName,
                               viewName,
                               view_id,
                               viewFilter=False,
                               viewCheckBoxes=False,
                               hideFormContent=False):
        loginInfos = self.rpc_connector.getLoginInfos()
        for viewObj in self.loadedViews:
            if viewObj.hasMatch(viewType, odooObjectName, viewName, view_id, viewFilter, loginInfos, viewCheckBoxes, hideFormContent):
                return viewObj
        return False

    def _searchForView(self, model, viewName, viewType):
        viewIds = self.rpc_connector.search('ir.ui.view', [('name', '=', viewName),
                                                           ('model', '=', model),
                                                           ('type', '=', viewType)])
        if viewIds:
            return viewIds[0]
        utils.logMessage('warning', 'View with name %r and model %r nor found' % (viewName, model), 'searchForView')
        return False

    def _getViewDefinition(self, odooObjectName, viewType='', viewName='', view_id=False):
        if viewType == 'tree_list':
            viewType = 'tree'
        if not view_id and viewName:
            view_id = self._searchForView(odooObjectName, viewName, viewType)
        fieldsViewDefinition = self.rpc_connector.fieldsViewGet(odooObjectName, view_id, viewType)
        if fieldsViewDefinition:
            arch = fieldsViewDefinition.get('arch', '')
            model = fieldsViewDefinition.get('model', '')
            viewName = fieldsViewDefinition.get('name', '')
            viewId = fieldsViewDefinition.get('view_id', False)
            fieldsNameTypeRel = fieldsViewDefinition.get('fields', '')
            return arch, model, viewName, viewId, fieldsNameTypeRel
        utils.logMessage('warning', 'Unable to read view definition for odooObjectName %r, viewName %r, view_id %r' % (odooObjectName, viewName, view_id), '_getViewDefinition')
        return '', '', '', False, ''

    def setXmlRpcError(self, value=False):
        """
        force the underline rpc soket to rise any error that occure
        """   
        self.rpc_connector.setXmlRpcError(value)
    
    def callButtonFunction(self,
                           model,
                           entity_id,
                           buttonType,
                           buttonName):
        ret = self.rpc_connector.callCustomMethod(model,  buttonName, [entity_id], forceRaise_error=True)
        if isinstance(ret , dict):
            action = ret.get('action')
            if action:
                pass
            else:
                pass
        return ret
        

        