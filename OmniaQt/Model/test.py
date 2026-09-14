# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

'''
Created on 27/ott/2014

@author: mboscolo
'''

import omniaModel

if __name__ == '__main__':
    from sqlalchemy import create_engine,and_
    from sqlalchemy.orm import relationship, backref
    engine = create_engine('sqlite:///:memory:', echo=True)
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Column, Integer, String
    Base = declarative_base()
    
    class User(Base):
        __tablename__ = 'users'
        
        id = Column(Integer, primary_key=True)
        name = Column(String)
        fullname = Column(String)
        password = Column(String)

        def __repr__(self):
            return "<User(name='%s', fullname='%s', password='%s')>" % (
                                self.name, self.fullname, self.password)
            
    class Role(Base):
        __tablename__ = 'role'
        
        id = Column(Integer, primary_key=True)
        roleName = Column(String)
        user = Column(String)
        def __repr__(self):
            return "<User(roleNames='%s')>" % (
                                self.roleName)           
    Base.metadata.create_all(engine)         
    from sqlalchemy.orm import sessionmaker
    s = sessionmaker(bind=engine)       
    s=s()        
    u=User()
    u.name='aaa'
    s.add(u)
    u=User()
    u.name='bbb'
    s.add(u)
    r=Role()
    r.roleName='Raaa'
    r.user=u.name
    s.add(r)
    
    s.commit()
    ff=and_(User.name==Role.user)+and_(User.name!='aaa')
    args=[User,Role]
    for qr in s.query(*args).filter(ff):
        print qr
        
    
    
            
            