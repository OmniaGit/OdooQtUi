# -*- coding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, ERP-PLM-CAD Open Source Solutions
#    Copyright (C) 2011-2021 https://OmniaSolutions.website
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this prograIf not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
'''
Created on 16 May 2021

@author: mboscolo
'''
import logging
import datetime
import sys
import site
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from urllib.parse import urljoin


class BaseWebForm(QWebEngineView):
    def __init__(self):
        super(BaseWebForm, self).__init__()
        self._baseUrl = 'http://localhost:8069/'  # in future load it from local setting

class FormYesNow(BaseWebForm):
    pass

class TreeYesNow(BaseWebForm):
    pass

class Login(BaseWebForm):
    def __init__(self):
        super(Login, self).__init__()
        self.load(QUrl(urljoin(self._baseUrl, r'web/database/login')))


        


if __name__ == '__main__':
    app = QApplication(sys.argv) 
    l = Login()
    l.show()   
    sys.exit(app.exec_())
    
    
    
    
    

