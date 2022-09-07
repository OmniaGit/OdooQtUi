'''
Created on 24 Mar 2017

@author: dsmerghetto
'''
import json
#
from PySide2 import QtWidgets
from PySide2.QtCore import QAbstractItemModel, Qt, QModelIndex
#
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.views.templateView import TemplateView
#
#
class TemplateTreeTreeView(TemplateView):

    def __init__(self,
                 odooConnector,
                 viewObject):
        super(TemplateTreeTreeView, self).__init__(odooConnector=odooConnector,
                                                   viewObj=viewObject)
        self.field_parent = ''
        self.viewType = 'tree'
        self.readonly = True
        self.activeIds = []

    def initViewObj(self,
                    odooObjectName,
                    viewName,
                    view_id):
        self.field_parent = self.fieldsViewDefinition.get('field_parent', '')
        self.addToObject()

class NodeComputed(object):
    def __init__(self,
                 attributes = {},
                 parent=None):
        """
        internal node representation of the tree structure
        :attributes of the current object suppose that the id parameter must be in the dictionary
        """
        self.id = attributes.get('id')
        if 'id' in attributes:
            del attributes['id']
        self.attributes = attributes
        self.parent = parent
        self.children = []
        self.setParent(parent)

    def setParent(self, parent):
        if parent is not None:
            self.parent = parent
            self.parent.appendChild(self)
        else:
            self.parent = None

    def appendChild(self, child):
        self.children.append(child)

    def childAtRow(self, row):
        return self.children[row]

    def rowOfChild(self, child):
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1
   
    def removeChild(self, row):
        value = self.children[row]
        self.children.remove(value)
        return True
       
    def __len__(self):
        return len(self.children)
    
    
class TreeTreeData(QAbstractItemModel):
    def __init__(self,
                 connectorObj,
                 objectName,
                 functionName,
                 ids=[]):
        """
        :connectorObj instance of RpcConnection 
        :objectName odoo object name
        :functionName function to call to get the data back *
        :ids    list of id of the specific odoo object model all this ids will be rendered at first level in the tree
        
        * the function name must return:
            headers, structure
            :heders dictionary like with value as header label {'engineering_code','Code', }
            :structure in form of parent child relation es [(id, attributes, children),..]
            
        """
        super(TreeTreeData, self).__init__(None)
        #
        self.connectorObj = connectorObj
        self.objectName = objectName
        #
        # call the server in  order to retrive all data
        #
        ret = self.connectorObj.callCustomMethod(self.objectName,
                                                 functionName,
                                                 parameters=ids)
        try:
            ret = json.loads(ret)
        except Exception:
            pass
        if not ret:
            #todo: mettere un pop up di errore o qualcosa ???
            return
        self.treeView = None  
        self.headers = list(ret[0].values())
        self.headersKey= list(ret[0].keys())
        self.columnsLen = len(self.headers)

        def addChilds(parentNode, childNodesAttributes):
            """
                add children node
            """
            for levelAttributes, childrenAttributes in childNodesAttributes:
                node = NodeComputed(levelAttributes, parent=parentNode)
                addChilds(node, childrenAttributes)
         
        self.root = NodeComputed({'name': 'RootNode'})
        addChilds(self.root, ret[1])

    def flags(self, index):
        defaultFlags = QAbstractItemModel.flags(self, index)
        if index.isValid():
            return defaultFlags
        else:
            return defaultFlags

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]

    def insertRow(self, row, parent):
        return self.insertRows(row, 1, parent)

    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent, row, (row + (count - 1)))
        self.endInsertRows()
        return True

    def removeRow(self, row, parentIndex):
        return self.removeRows(row, 1, parentIndex)

    def removeRows(self, row, count, parentIndex):
        self.beginRemoveRows(parentIndex, row, row)
        node = self.nodeFromIndex(parentIndex)
        node.removeChild(row)
        self.endRemoveRows()
        return True

    def index(self, row, column, parent):
        node = self.nodeFromIndex(parent)
        return self.createIndex(row, column, node.childAtRow(row))
        
    def data(self, index, role): 
        """
        main function to retrieve the data from the abstract model
        """     
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignTop | Qt.AlignLeft)
        if not index.isValid():
            return 
                        
        node = self.nodeFromIndex(index)
        
        if role != Qt.DisplayRole:
            return
        
        columnIndex = index.column()
        return node.attributes.get(self.headersKey[columnIndex],None)

    def columnCount(self, parent):
        return self.columnsLen

    def rowCount(self, parent):
        node = self.nodeFromIndex(parent)
        if node is None:
            return 0
        return len(node)

    def parent(self, child_index):
        if not child_index.isValid():
            return QModelIndex()

        node = self.nodeFromIndex(child_index)
       
        if node is None:
            return QModelIndex()

        parent = node.parent
           
        if parent is None:
            return QModelIndex()
       
        grandparent = parent.parent
        if grandparent is None:
            return QModelIndex()
        row = grandparent.rowOfChild(parent)
       
        assert row != -1
        return self.createIndex(row, 0, parent)

    def nodeFromIndex(self, index):
        if index.isValid():
            return index.internalPointer()
        else:
            return self.root  
 
    def appendChild(self, child):
        self.children.append(child)
       
    def childAtRow(self, row):
        return self.children[row]
   
    def rowOfChild(self, child):       
        for i, item in enumerate(self.children):
            if item == child:
                return i
        return -1

    def removeChild(self, row):
        value = self.children[row]
        self.children.remove(value)

        return True

    def __len__(self):
        return len(self.children)


class TreeTreeView(QtWidgets.QWidget):
    def __init__(self,
                 connectorObj,
                 objectName,
                 functionName,
                 showSearch=False):
        """
        :connectorObj  OdooQtUi.RPC.rpc (object)
        :objectName    Odoo model object name 
        :functionName  Odoo method that retrieve the structure this call must return an object like [(parentAttributes={}, [childrent])]
        :showSearch show the search view based on proxie model
        """
        super(TreeTreeView, self).__init__()
        self._connectorObj = connectorObj
        self._objectName = objectName
        self._functionName = functionName
        self.showSearch = showSearch
        self.abstractModel = None
        self._mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(self._mainLayout)    
        self._qTreeView = QtWidgets.QTreeView()
        self._qTreeView.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self._mainLayout.addWidget(self._qTreeView)
        
    def loadIds(self, ids):
        """
        :ids: list of first level ids
        """
        self.abstractModel = TreeTreeData(self._connectorObj,
                                          self._objectName,
                                          self._functionName,
                                          ids)
        self._qTreeView.setModel(self.abstractModel)
        self._qTreeView.header().setStyleSheet(constants.MANY_2_MANY_H_HEADER)
        #self._qTreeView.setStyleSheet(constants.TABLE_VIEW_LIST_LIST)

    def getSelectedNodes(self):
        nodes = []
        for index in self._qTreeView.selectionModel().selectedIndexes():
            node = self.abstractModel.nodeFromIndex(index)
            if node not in nodes:
                nodes.append(node)
        return nodes
    
    def getRootNode(self):
        return self.abstractModel.root
        
       
    
        
        
        
        
        
        