# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

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
        
