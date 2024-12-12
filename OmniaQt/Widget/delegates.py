##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 12/mar/2015 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
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
Created on 12/mar/2015

@author: mboscolo
'''
from PySide6 import QtCore, QtWidgets, QtGui

class SqlAlchemyEditDelegateItem(QtGui.QItemDelegate):
    def __init__(self,
                 parent=None, 
                 *args):
        QtGui.QItemDelegate.__init__(self, parent, *args)
        self.cellValue=''
        
        
    def createEditor(self,parent,option,index):
        """ QWidget createEditor(
                         QWidget *parent,
                         const QStyleOptionViewItem  option ,
                         const QModelIndex  index 
                         ) 
        """
        self.activeWidget=QtWidgets.QLineEdit(parent)
        self.activeWidget.setText(str(self.cellValue))
        return self.activeWidget
            
    def setEditorData(self,editor,index):
        value = index.model().data(index,QtCore.Qt.DisplayRole)
        editor.setText(value.toString())
                
    def updateEditorGeometry(self,editor,option,index):
        """
            update position
        """
        editor.setGeometry(option.rect);
        
    def setModelData(self,editor,model,index):
        """
            get value
        """
        model.setData(index,str(editor.text()),QtCore.Qt.EditRole)
        
                 
class SqlAlchemyQueyDelegateItem(QtGui.QItemDelegate):
    def __init__(self,
                 sqlAlchemySession,
                 sqlAlchemyObject,
                 toValueRef,
                 fromValueRef, 
                 parent=None, 
                 sqlAlchemyPreFilter=None,
                 *args):
        QtGui.QItemDelegate.__init__(self, parent, *args)
        self._sqlAlchemySession=sqlAlchemySession
        self._sqlAlchemyObject=sqlAlchemyObject
        self._sqlAlchemyPreFilter=sqlAlchemyPreFilter
        self._latestValue=None
        self._fromValueRef=fromValueRef
        self._toValueRef=toValueRef
        self.value=None
        
        
    def createEditor(self,parent,option,index):
        """ QWidget createEditor(
                         QWidget *parent,
                         const QStyleOptionViewItem  option ,
                         const QModelIndex  index 
                         ) 
        """
        from OmniaQt.Widget.SqlAlchemyView import SqlAlchemyDialogEditDialog
        d=SqlAlchemyDialogEditDialog(self._sqlAlchemySession,
                                     self._sqlAlchemyObject,
                                     visibleField=[],
                                     editableField=[],
                                     parent=parent,
                                     standardFilter=self._sqlAlchemyPreFilter)
        if d.exec()==QtWidgets.QDialog.Accepted:
            def updateLatest(values):
                for sqlAlchemyObject in values:
                    if isinstance(sqlAlchemyObject,tuple):
                        for ss in sqlAlchemyObject:
                            try:
                                self._latestValue=unicode(getattr(ss, self._toValueRef))
                                self.setModelData(None,index.mode(),index)
                                return
                            except:
                                pass
                    self._latestValue=unicode(getattr(sqlAlchemyObject, self._toValueRef))
                    self.setModelData(None,index.model(),index)
                    return
            updateLatest(d.values)
        return None
    

        
    def setEditorData(self,editor,index):
        self.value = index.model().data(index,QtCore.Qt.DisplayRole)
        
    def setModelData(self,editor,model,index):
        """
            get value
        """
        if self._latestValue!=None or self._latestValue!=self.value:
            model.setData(index,self._latestValue,QtCore.Qt.EditRole)
    
        
class DelegateSwap(QtGui.QItemDelegate):
    def __init__(self,delegates={},parent=None,*args):
        QtGui.QItemDelegate.__init__(self, parent, *args)
        self._delegates=delegates
        self._activeDelegate=None

        
    def createEditor(self,parent,option,index):
        """
            overload of the function
        """
        rightDelegate=self._delegates.get(index.column())
        if rightDelegate:
            self._activeDelegate=rightDelegate
            return rightDelegate.createEditor(parent,option,index)
        return None
    
    def setModelData(self,editor,model,index):
        self._activeDelegate.setModelData(editor,model,index)
    
    def setEditorData(self,editor,index):
        self._activeDelegate.setEditorData(editor,index)
        
    def updateEditorGeometry(self,editor,option,index):
        """
            update position
        """
        editor.setGeometry(option.rect);       
        
            
            
               
        