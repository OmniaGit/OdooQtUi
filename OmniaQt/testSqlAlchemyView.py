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
from __future__ import print_function
from builtins import map
import sys
from PySide6 import QtWidgets
# Sql Alchemy imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import mapper,relationship

#OmniaQt 
from OmniaQt.Widget.SqlAlchemyView import SqlAlchemyDialogEditDialog

#This code below is only for testing porpouse shuld be moved somewere else
Base = declarative_base()

class Entity(Base):
    __tablename__ = 'entitys'
    name         = Column(String, primary_key=True, nullable = False)
    desctiption  = Column(String, nullable = False)
    desctiption2  = Column(String, nullable = False)
    
    def __init__(self, name='', objType='' ):
        self.name = name
        self.desctiption=objType

    def __repr__(self):
        return "<Entity('%s','%s')>" % (self.name,self.desctiption)
    
    @property
    def columnsKey(self):
        return list(self.__table__.columns.keys())
    
    @property
    def toList(self):
        """
            convert the object value to a list
        """
        
        return list(map(self.__dict__.get,self.columnsKey))
    
    def getValueFromList(self,columnList):
        """
            return the value of the object from a list of value
        """
        return list(map(self.__dict__.get,columnList))



class Fields(Base):
    __tablename__ = 'fileds'
    name         = Column(String, primary_key=True, nullable = False)
           
def setup():
    Entity.metadata.create_all(engine) 
    Fields.metadata.create_all(engine) 
    e1  =   Entity("E1","D1") 
    e1.desctiption2="fff"
    e2  =   Entity("E2","D2")
    e2.desctiption2="fff"
    e3  =   Entity("E3","D3")
    e3.desctiption2="fff"
    session.add(e1)
    session.add(e2)
    session.add(e3) 
    f=Fields()
    f.name="f1"
    f1=Fields()
    f1.name="f2"
    f2=Fields()
    f2.name="f3"

    session.add(f)
    session.add(f1)
    session.add(f2)
    session.commit()    

    
def teardown():
    Entity.metadata.drop_all(engine)  

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
   
if __name__=='__main__':
    #db staff
    engine = create_engine('sqlite:///test.db')
    session=sessionmaker(bind=engine)() 
    #session.configure(bind=engine)
    import os
    if not os.path.exists('test.db'):
        setup() #use it the first time to create the db and the entity used for testing
    
    # gui staff
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('plastique')
    #dialog=SqlAlchemyDialogEditView(None,session,Entity,['name'])
    relDic={'desctiption':('name',Fields,False)}
    dialog=SqlAlchemyDialogEditDialog(session,Entity,['name','desctiption','desctiption2'],editableField=['name','desctiption'],relationDict=relDic,editable=True)
    dialog.exec()
    print("sr",dialog.values)
    sys.exit(app.exec())
        
