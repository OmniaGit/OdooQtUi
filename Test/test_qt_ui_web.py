# -*- coding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, ERP-PLM-CAD Open Source Solution
#    Copyright (C) 2011-2024 https://OmniaSolutions.website
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
Created on 5 Oct 2024

@author: mboscolo
'''
import os
import sys
import json
import logging
from urllib.parse import urlencode

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtWebEngineWidgets import *
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide2.QtNetwork import QNetworkCookie
from ..OdooQtUiWeb.web_odoo import QtOdooUiDilog

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow,self).__init__(*args, **kwargs)
        self.qtOdooBrowser = QtOdooUiDilog(None)
        layout = QVBoxLayout()
        #
        show_login = QPushButton("Login", self)
        show_login.clicked.connect(lambda: self.show_login())
        layout.addWidget(show_login)
        #
        show_form = QPushButton("Form", self)
        show_form.clicked.connect(lambda: self.show_form())
        layout.addWidget(show_form)
        #
        show_list= QPushButton("List", self)
        show_list.clicked.connect(lambda: self.show_list())
        layout.addWidget(show_list)
        #
        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
    
    def show_login(self):
        self.qtOdooBrowser.show_login()
        
    def show_form(self):
        self.qtOdooBrowser.show_form(
            odoo_id='',
            odoo_object='product.product',
            odoo_action_id=''
            )


    def show_list(self):
        #http://localhost:8069/web#action=398&model=product.product&view_type=list&cids=1&menu_id=217
        self.qtOdooBrowser.set_list('product.product',
                                    menu_id=217,
                                    action_id=398)
        self.qtOdooBrowser.show()
        self.qtOdooBrowser.adjustSize()
 
def main():
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-logging --log-level=1 --remote-debugging-port=1234"
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    ret = app.exec()
    app.exec_(ret)
    # sys.exit(ret)

if __name__ == "__main__":
    main()
