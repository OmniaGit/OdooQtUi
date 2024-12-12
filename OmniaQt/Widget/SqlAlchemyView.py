##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 22/lug/2014 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
#    info@omniasolutions.eu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
Created on 22/lug/2014

@author: mboscolo
'''
#
from PySide6 import QtCore, QtWidgets, QtGui
#
from sqlalchemy     import *
from sqlalchemy.orm import undefer,defer

from ...OmniaQt.Model.omniaModel import SqlAlchemyModel
from ...OmniaQt.Widget.omniaDataTable import OmniaDataTable,OmniaHorizontalHeader
from ...OmniaQt.Widget.delegates import SqlAlchemyQueyDelegateItem,SqlAlchemyEditDelegateItem,DelegateSwap
#
class SqlAlchemyFilterViewWidget(OmniaDataTable):
    """
        this class provide a search view for the sql alchemy 
    """
    def __init__(self,parent=None,session=None,sqlAlchemyObject=None,headers=[],filter=False):
        """
            Constructor
        """
        self.session=session
        self.sqlAlchemyObject=sqlAlchemyObject
        
        if len(headers)==0:
            self.headers=[str(a.key) for a in sqlAlchemyObject._sa_class_manager.attributes]
        else:
            self.headers=headers
        data=self.getAllData(filter)
        super(SqlAlchemyFilterViewWidget,self).__init__(parent, self.headers, data)
        self.tableObj.header=self.headers
        self.tableObj.data=data
        self.tableObj.computeFilterObj=self._refreshWithFilter
        
    def update(self,row,col,value):
        """
            update event from table
        """
        pass
    
    def delete(self,rowToDelete):
        """
            single row to delete
        """
        pass
        
    def setEditable(self,value):
        """
            
        """   
        if value:
            self.tableObj.model.update=self.update
            self.tableObj.model.delete=self.delete
            self.tableObj.model._flags=[QtCore.Qt.ItemIsEditable , QtCore.Qt.ItemIsEnabled , QtCore.Qt.ItemIsSelectable]
        else:
            self.tableObj.model._flags=[QtCore.Qt.ItemIsEnabled , QtCore.Qt.ItemIsSelectable]

    
    def _dataTableContextMenuEvent(self,event):
        contexMenu=QtWidgets.QMenu(self)
        #
        # Create Actions
        addAction = QtGui.QAction.triggered(self._newLibrary)
        addAction = QtGui.QAction.triggered(self._newLibrary)
        delAction = QtGui.QAction.triggered(self._addLibrary)
        #
        # Add action to the context menu   
        #
        contexMenu.addAction(addAction)
        contexMenu.addAction(delAction)
        #
        contexMenu.exec_(event.globalPos())
        del(contexMenu)       
        
    def _refreshWithFilter(self,objFilter):
        """
        """
        self.tableObj.data=[]
        flt=[]
        for columnFilter in objFilter._columnsFilter.values():
 
            for name,condition,value in  columnFilter.filterTuple:
                attribute=self.sqlAlchemyObject.__dict__.get(name,False)
                if attribute:
                    # if unicode(condition).lower() == 'like':
                    flt.append(attribute.like(value))
                    # else:
                    #     flt.append(attribute==value)
        self.tableObj.data=self.getAllData(tuple(flt))
        self.tableObj.populateModel()
      
    def getAllData(self,flt=False):
        """
            Get All the data from the db
        """    
        out=[]
        q=self.session.query(self.sqlAlchemyObject)
        if flt!=False:
            if isinstance(flt,(list,tuple)):
                for f in flt:
                    q=q.filter(f)
            else:
                q=q.filter(flt)
        for a in self.sqlAlchemyObject._sa_class_manager.attributes:
            if a.key in self.headers:
                q.options(undefer(a))
            else:    
                q.options(defer(a))
        for ent in q:
            out.append(ent)
        return out
    
    def getSelectedValue(self,fieldToReturn):    
        """
            return the selected value from the table
        """
        raise NotImplementedError("getSelectedValue")
        return []
    
class SqlAlchemyDialogEditView(QtWidgets.QDialog):
    def __init__(self,parent=None,session=None,sqlAlchemyObject=None,headers=[],filter=False):
        super(SqlAlchemyDialogEditView,self).__init__(parent)
        self.sqlAlchemyWidget=SqlAlchemyFilterViewWidget(self,
                                                         session=session,
                                                         sqlAlchemyObject=sqlAlchemyObject,
                                                         headers=headers,
                                                         filter=filter,
                                                         )
        verticalLayout = QtWidgets.QVBoxLayout(self)
        verticalLayout.addWidget(self.sqlAlchemyWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.on_buttonBox_rejected)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.on_buttonBox_accepted)
        verticalLayout.addWidget(self.buttonBox)
        self.sqlAlchemyWidget.tableObj.systemFilter=self.filterUpdated   
        self.filter=''
        self.rowSelectedValue=[]
        self.sqlAlchemyWidget.setEditable(True)

    def filterUpdated(self,newFilter): 
        """
            the filter condition is updated need recalculation
        """
        if self.filter!=newFilter:
            self.filter=newFilter
            self.sqlAlchemyWidget.getAllData()  

    def confirm(self,rowIndex):
        """
            confirm event with the given selected item
        """    
        self.nameSelected=self.sqlAlchemyWidget.getSelectedValue(rowIndex)
        self.accept()
        self.close()  
        
    @property    
    def values(self):
        """
            return the value selected
        """
        return self.rowSelectedValue
    
    
    def on_buttonBox_accepted(self):
        """
            implements the accept button
        """
        self.rowSelectedValue=self.sqlAlchemyWidget.selectedRows

        self.accept()
        try:
            self.close()
        except Exception as ex:
            print(ex)
                    
    
    def on_buttonBox_rejected(self):
        """
            implements the accept button
        """
        self.close()      
            
class SqlAlchemyDialogView(SqlAlchemyDialogEditView):
    def __init__(self,parent=None,session=None,sqlAlchemyObject=None,headers=[],filter=False):
        super(SqlAlchemyDialogView,self).__init__(
                                                  parent=parent,
                                                  session=session,
                                                  sqlAlchemyObject=sqlAlchemyObject,
                                                  headers=headers,
                                                  filter=filter
                                                  )
        self.sqlAlchemyWidget.setEditable(False)

class SqlAlchemyQTableView(QtWidgets.QTableView):
    def __init__(self,
                 session,
                 entityType,
                 visibleField=[],
                 editableField=[],
                 defaultVaues={},
                 headers_Description={},
                 relationDict={},
                 parent=None,
                 standardFilter=None,
                 deletebleRule={},
                 updatable=[],
                 automaticComputation=True):
        super(SqlAlchemyQTableView,self).__init__(parent=None)
        self.setTabKeyNavigation(False)
        self._standardFilter=standardFilter
        self.setModel(SqlAlchemyModel(session,
                                      entityType,
                                      headerData=visibleField,
                                      editableFields=editableField,
                                      headers_Description=headers_Description,
                                      defaultVaues=defaultVaues,
                                      flt=standardFilter,
                                      deletebleRule=deletebleRule,
                                      updatable=updatable,
                                      automaticComputation=automaticComputation))
#
        self.setSortingEnabled(True)
        self.setHorizontalHeader(OmniaHorizontalHeader())
        self.horizontalHeader().filterUpdate = self.filetrChange
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        refObjects=self.model()._sqlAlchemyObject
        if not isinstance(refObjects,list):
            refObjects=[refObjects]
        self._mappers=[]
        for refObj in refObjects:   
            self._mappers.append(inspect(refObj))
#
        self._itemDelegate={}
        for fieldName in editableField:
            indexFiled=visibleField.index(fieldName)
            if indexFiled>=0:
                relValue=relationDict.get(fieldName)
                if relValue:
                    toKey,sqlalkemyObject,preFilter=relValue
                    self._itemDelegate[indexFiled]=SqlAlchemyQueyDelegateItem(session,
                                              sqlalkemyObject,
                                              toValueRef=toKey,
                                              fromValueRef=fieldName,
                                              sqlAlchemyPreFilter=preFilter,)
                else:
                    self._itemDelegate[indexFiled]=SqlAlchemyEditDelegateItem()
        self.setItemDelegate(DelegateSwap(self._itemDelegate))            
        
    def deleteSelected(self):
        """
            delete selected items
        """
        reply = QtGui.QMessageBox.question(self, 'Attention !!','Sure you would like to delete ??', 
                      QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.model().removeRowFromIndexList(self.selectedIndexes())

    @property
    def selectedObject(self):
        """
            active selected objects
        """
        return self.model().sqlItemData(self.selectedIndexes())
     
    def filetrChange(self, objeFilters): 
        """
            change filter
        """
        outFilter = []
        for columnList in objeFilters._columnsFilter.values():
            for fileldHeaderName,filterCouse,filterValue in columnList.filterTuple:
                for m in self._mappers:
                    column=m.columns.get(fileldHeaderName,False)
                    if isinstance(column,bool) and not column : #non mi piace ma per inarca va bene cosi
                        column=m.columns.get("_"+fileldHeaderName)
                    if isinstance(column,Column):
                        if filterCouse=='Like':
                            condition = column.like("%"+filterValue+"%")
                        else:
                            condition = column==filterValue
                        outFilter.append(condition) 
        self.model().updateData(outFilter)

class SqlAlchemyDialogEditDialog(QtWidgets.QDialog):
    """
        widget dialog to manage an sqlalchemy object
    """
    def __init__(self,
                 session,
                 entityType,
                 visibleField=[],
                 editableField=[],
                 defaultVaues={},
                 headers_Description={},
                 relationDict={},
                 editable=False,
                 parent=None,
                 standardFilter=None,
                 deletebleRule={},
                 updatable=[],
                 automaticComputation=True):
        super(SqlAlchemyDialogEditDialog,self).__init__(parent)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        # TreeView
        self.treeView=SqlAlchemyQTableView(session,
                                           entityType,
                                           visibleField,
                                           editableField,
                                           defaultVaues=defaultVaues,
                                           headers_Description=headers_Description,
                                           relationDict=relationDict,
                                           standardFilter=standardFilter,
                                           deletebleRule=deletebleRule,
                                           updatable=updatable,
                                           automaticComputation=automaticComputation)
        self.editable=editable
        if self.editable:
            self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.treeView.customContextMenuRequested.connect(self.contextMenuTreeView)
            self.treeView.model().addFlags(QtCore.Qt.ItemIsEditable)
        self.verticalLayout.addWidget(self.treeView)
        # Button Box
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.on_buttonBox_rejected)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.on_buttonBox_accepted)
        self.verticalLayout.addWidget(self.buttonBox)        
    
    def contextMenuTreeView(self,position):
        menu = QtWidgets.QMenu()
        addAction = menu.addAction("Add New")
        deleteAction = menu.addAction("Delete")
        action = menu.exec_(self.treeView.mapToGlobal(position))
        if action == addAction:
            self.treeView.model().addNewEmptyItem()
        if action==deleteAction:
            self.treeView.deleteSelected()
    
    def on_buttonBox_rejected(self):
        self.close()
    
    def on_buttonBox_accepted(self):
        if self.editable:
            self.treeView.model().addCommitPendingEntities()
        self.accept()
        try:
            self.close()
        except Exception as ex:
            print(ex)
    
    @property
    def values(self):
        return self.treeView.selectedObject
    
