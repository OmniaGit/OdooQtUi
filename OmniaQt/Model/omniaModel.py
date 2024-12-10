##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 30/ott/2012 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
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
Created on 30/ott/2012
@author: mboscolo
'''

from PySide6 import QtWidgets 
from PySide6 import QtCore

from OmniaQt.util import OmniaEvent

class SqlAlchemyModel(QtCore.QAbstractTableModel):
    """
        abstract model to map sqlalchemy object
    """
    def __init__(self,
                 sqlAlchemySession,
                 sqlAlchemyObject, 
                 headerData={},
                 headers_Description={},
                 defaultVaues={},
                 editableFields=[],
                 flt=False, 
                 parent=None,
                 deletebleRule={},
                 updatable={},
                 automaticComputation=True,
                  *args): 
        QtCore.QAbstractTableModel.__init__(self, parent, *args)   
        self._editableFields=editableFields
        self._sqlAlchemyColumns=[]
        self._automaticComputation=automaticComputation
        def addColumns(sqlAlchemyObject):
            from sqlalchemy import inspect
            if not isinstance(sqlAlchemyObject,list):
                sqlAlchemyObject=[sqlAlchemyObject]
            for on in sqlAlchemyObject:    
                mapper=inspect(on)
            for c in mapper.columns:
                self._sqlAlchemyColumns.append(c.name)
            
        if isinstance(sqlAlchemyObject,list):
            for sao in sqlAlchemyObject:
                addColumns(sao)
        else:
            addColumns(sqlAlchemyObject)
        self._defaultvalue=defaultVaues
        self._headers_Description=headers_Description
        self._deletebleRule=deletebleRule
        self._updatable=updatable
        if len(headerData)>0:
            self._headerData=headerData
        else:
            self._headerData= self._sqlAlchemyColumns
        self._sqlAlchemySession=sqlAlchemySession
        self._sqlAlchemyObject=sqlAlchemyObject
        self._preFilter=flt
        self.updateData()
        flags=[]      
        flags.append(Qt.ItemIsSelectable)
        flags.append(Qt.ItemIsEnabled)
        self._flags=flags
        self._rowToCommit=[]
        self._automaticComputation=True
        
    def addCommitPendingEntities(self):
        """
            write modification to db
        """
        while len(self._rowToCommit):
            sqlItem= self._rowToCommit.pop()
            self._sqlAlchemySession.add(sqlItem)
        self._sqlAlchemySession.commit()
            
    def headerData(self, col, orientation, role):
        """
            data header overloads
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            if col <len(self._headerData):
                value=self._headers_Description.get(self._headerData[col],self._headerData[col])
                return value
        if orientation == QtCore.Qt.Horizontal and role == 111:
            return self._headerData[col]
        return 
    
    def addFlags(self,flag):  
        """Add Flag to the model"""
        self._flags.append(flag)
        
    def flags(self, index):
        """
            set the flag for the data model
        """
        flags = super(self.__class__,self).flags(index)
        for flag in self._flags:
            flags |= flag
        return flags

    def updateData(self,flt=[]):
        """
            update all the data from model
        """
        self.beginResetModel()
        self.reset()
        self._sqlAlchemyObjectRows=self.getAllData(flt)
        self.endResetModel()
        
    def getAllData(self,flt=[]):
        """
            Get All the data from the db
        """    
        from sqlalchemy.sql.expression  import BinaryExpression
        from sqlalchemy.sql.elements    import BooleanClauseList
        out=[]
        q=None
        if self._automaticComputation:
            if isinstance(self._sqlAlchemyObject,list):
                q=self._sqlAlchemySession.query(*self._sqlAlchemyObject)
            else:           
                q=self._sqlAlchemySession.query(self._sqlAlchemyObject)
            if isinstance(self._preFilter,(BooleanClauseList,BinaryExpression)):
                q=q.filter(self._preFilter)
            for f in flt:
                q=q.filter(f)
            for ent in q:
                out.append(ent)
        return out
        
    def rowCount(self,objParent): 
        """
            row count
        """
        return len(self._sqlAlchemyObjectRows) 

    def columnCount(self, parent): 
        """
            return the column count
        """
        return len(self._headerData) 
    
    def addNewEmptyItem(self):
        """
            add new empty editable row
        """
        newObject=self._sqlAlchemyObject()
        for column,defValue in  self._defaultvalue.items():
            setattr(newObject,column,defValue)
        count=len(self._sqlAlchemyObjectRows)
        self.beginInsertRows(QModelIndex(),count, count + 1)
        self._sqlAlchemyObjectRows.append(newObject)
        self._rowToCommit.append(newObject)
        self.endInsertRows()
        self.emit(SIGNAL('layoutChanged()'))
        
    def isDeletable(self,row):
        sqlObj=self._sqlAlchemyObjectRows[row]
        for field_name,values in self._deletebleRule.items():
            if getattr(sqlObj, field_name) in values:
                return False
        return True
        
    def removeRowFromIndexList(self, indexis):
        """
            remove row
        """
        self.beginRemoveRows(QModelIndex(), 0, len(self._sqlAlchemyObjectRows) - 1)
        deleted=[]
        for index in indexis:
            row=index.row()
            if not row in deleted: 
                deleted.append(row)
                if not self.isDeletable(row):
                    continue
                self._sqlAlchemySession.delete(self._sqlAlchemyObjectRows[row])
                del self._sqlAlchemyObjectRows[row]
        self._sqlAlchemySession.commit()
        self.endRemoveRows()
        self.emit(SIGNAL('layoutChanged()'))
        return True    

    def isUpdatable(self,field):
        if len(self._updatable)>0:
            return field in self._updatable
        return True
            
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        col = index.column()
        # if isinstance(value,QVariant):
        #     value=unicode(value.toString())
        if not self.isDeletable(row):
            if not self.isUpdatable(self._headerData[col]):
                return False
        setattr(self._sqlAlchemyObjectRows[row], self._headerData[col], value)
        self._sqlAlchemySession.flush()
        self.emit(SIGNAL('dataChanged()'))
        return True
    
    def data(self, index, role=None):
        value='' 
        if not index.isValid(): 
            return
        elif role != Qt.DisplayRole: 
            return
        try:
            storedRow=self._sqlAlchemyObjectRows[index.row()]
            if isinstance(storedRow,tuple):
                for stRow in storedRow:
                    try:
                        
                        value=getattr(stRow, self._headerData[index.column()])
                        return value
                    except:
                        pass
            else:
                return getattr(storedRow, self._headerData[index.column()])
        except:
            pass
        return value
    
    def sqlItemData(self,indexis):
        """
            retrive the inner sqlalchemy model
        """
        out={}
        for index in indexis:
            col=index.row()
            if not col in out.keys(): 
                out[col]=self._sqlAlchemyObjectRows[col]
        return out.values()
    
class OmniaModel(QtCore.QAbstractTableModel): 
    """
        abstract model for manage values
    """
    def __init__(self, datain, headerdata, parent=None, *args): 
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        
        if len(datain)==0:
            datain.append([None for h in headerdata])
        self.arraydata  = datain
        self.headerdata = headerdata 
        flags=[]      
        flags.append(QtCore.Qt.ItemIsSelectable)
        flags.append(QtCore.Qt.ItemIsEnabled)
        self._flags=flags
        self.changed=False
        self.delete=OmniaEvent()
        self.update=OmniaEvent()
        
    
    def rowCount(self,objParent): 
        """
            row count
        """
        return len(self.arraydata) 
    
    def addNewRow(self):
        """
            add a new empty row to the abstract model
        """
        newRow=[]
        newRow.append(False)
        for i in range(1,len(self.headerdata)):
            newRow.append('')
        self.insertRow(self.rowCount(None)+1,[newRow]) 

    def insertRow(self, pos, row):
        """
            insert row
        """
        self.insertRows(pos, 1, row)
  
  
    def insertRows(self, pos, count, rows):
        """
            insert rows
        """
        self.beginInsertRows(QModelIndex(), pos, pos + count - 1)
        for row in rows:
            self.arraydata.append(row)
        self.endInsertRows()
        self.emit(SIGNAL('layoutChanged()'))
        return True
    
    def removeRow(self, pos):
        """
            remove row
        """
        self.removeRows(pos, 1)
        return True
  
    def removeRows(self, row=-1, count=0, parent=QtCore.QModelIndex()):
        """
            remove rows
        """
        
        if row == -1:
            self.beginRemoveRows(QModelIndex(), 0, len(self.arraydata) - 1)
            self.delete(self.arraydata[:])
            del self.arraydata[:]
        else:
            self.beginRemoveRows(QModelIndex(), row, row + count - 1)
            self.delete(self.arraydata[row:row + count])
            del self.arraydata[row:row + count]
        self.endRemoveRows()
        self.emit(SIGNAL('layoutChanged()'))
        return True
    
    def columnCount(self, parent): 
        """
            return the column count
        """
        if len(self.arraydata)>0:
            return len(self.arraydata[0])
        return 0 
    
    def _rule(self,index):
        """
            this class must be overloaded in order to control the background color
        """
        return False
    
    def backgroudIndex(self,index):
        if self._rule(index):
            self.setData(index, QtCore.Qt.QColor(QtCore.Qt.red), QtCore.Qt.BackgroundColorRole)
    
    def data(self, index, role): 
        if not index.isValid(): 
            return
        elif role != QtCore.Qt.DisplayRole: 
            return 
        return self.arraydata[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal :
            if role == QtCore.Qt.DisplayRole or role==111:
                return self.headerdata[col]         
        return

    def flags(self, index):
        """
            set the flag for the data model
        """
        flags = super(self.__class__,self).flags(index)
        for flag in self._flags:
            flags |= flag
        return flags
    
    
    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = index.row()
        col = index.column()
        self.arraydata[row][col] = value
        self.emit(SIGNAL('dataChanged()'))
        self.update(row,col,unicode(value))
        return True
    
    def getRowData(self,row):
        return self.arraydata[row]
    
    def getRowDataHeader(self,row,columnsName=[]):
        outRow={}
        if len(columnsName)==0:
            columnsName=self.headerdata
        
        columnNameL=list(map(str.lower,columnsName))
        hederDataL=list(map(str.lower,self.headerdata))
        for srcColL in columnNameL:
            if srcColL in hederDataL:
                cursor=hederDataL.index(srcColL)
                outRow[self.headerdata[cursor]]=self.arraydata[row][cursor]
        return outRow
    
            