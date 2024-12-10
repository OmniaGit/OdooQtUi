##############################################################################
#
#    OmniaSolutions, Your own solutions
#    Copyright (C) 27/ott/2014 OmniaSolutions (<http://www.omniasolutions.eu>). All Rights Reserved
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
        
    
    
            
            