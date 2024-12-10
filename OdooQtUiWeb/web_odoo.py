# -*- coding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, ERP-PLM-CAD Open Source Solution
#    Copyright (C) 2011-2023 https://OmniaSolutions.website
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
Created on 14 Nov 2023

@author: mboscolo
'''
import os
import sys
import json
import logging
from urllib.parse import urlencode

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineProfile 
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtNetwork import QNetworkCookie
#
#
#
def make_url(base_url, *uris, **params):
    url = base_url.rstrip('/')
    for uri in uris:
        _uri = uri.strip('/')
        url = '{}/{}'.format(url, _uri) if _uri else url
    if params:
        url = '{}?{}'.format(url, urlencode(params))
    return url
#
#
#
class QtOdoo(QObject):
   
    _storedRecord={}
        
    @Slot(str, str)
    def onRecordSaved(self,
                      model_name,
                      datas):
        """
        Event fired by odoo framework on record saved
        :model_name odoo table name
        :datas json dict_like with the all the record values
        """
        print("onRecordSaved")
        record_datas = json.loads(datas)
        datas_id = record_datas.get('id')
        
        if datas_id in self._storedRecord[model_name]:
            self._storedRecord[model_name][datas_id]= record_datas
        else:
            self._storedRecord[model_name] = {datas_id: record_datas}
    
    @Slot(str, result=str)
    def getRef(self, o):
        print("inside getRef", o)
        #py_obj = json.loads(o)
        #py_obj["c"] = ("Hello", "from", "Ppython")
        #return "json.dumps(py_obj)"
        return "{'message':{'id':5}}"

    @Slot(str)
    def printRef(self, o):
        print("printRef Called")
        py_obj = json.loads(o)
        #print("inside printRef", py_obj)
        pass

#
class QtOdooUiWeb(QWebEngineView):
    def __init__(self,
                 parent,
                 web_base_url='http://localhost:8069'):
        super(QtOdooUiWeb, self).__init__(parent)
        self.profile = QWebEngineProfile("odooQtUi", self)
        self._parent = parent
        self._web_base_url = web_base_url 
        self.urlChanged.connect(self._url_changed)
        self._application_starting_url = ''
        
    def _url_changed(self, url):
        if self._application_starting_url:
            if url.toString()!=self._application_starting_url:
                self.hide()
    
    def set_form(self,
                 model,
                 record_id,
                 menu_id,
                 action_id):
        #
        params={}
        if record_id:
            params['id']= record_id
        params['menu_id']=menu_id
        params['action']=action_id
        params['model']=model
        params['view_type']='form'
        #
        self._application_starting_url=False
        page = QWebEnginePage(self.profile, self)
        self.setPage(page)
        qtOdoochannel = QWebChannel(self)
        page.setWebChannel(qtOdoochannel)
        qtOdoochannel.registerObject("qtodoo", QtOdoo())
        url=make_url(self._web_base_url ,'web#',**params)
        self.setUrl(url)
        self.page().loadFinished.connect(self.on_load_finished_hide_form)
        # http://localhost:8069/web?debug=assets#menu_id=217&action=398&model=product.product&view_type=form
        # action=381&model=ir.attachment&view_type=kanban&cids=1&menu_id=222
    
    def save_button(self):
        self.page().runJavaScript("""save_form();""")
    
    def cancel_button(self):
        self.page().runJavaScript("""cancel_form();""")
    
    def on_load_finished_hide_form(self):
        print("on_load_finished_hide_form ")
        self.load_custom_client_js()
        self.page().runJavaScript("""hide_form_items();""")

    def set_login(self):
        page = self.page()
        self.setPage(page)
        qtOdoochannel = QWebChannel(self)
        page.setWebChannel(qtOdoochannel)
        qtOdoochannel.registerObject("qtodoo", QtOdoo())
        self._application_starting_url=make_url(self._web_base_url ,'web/login')
        page = QWebEnginePage(self.profile, self)
        self.setPage(page)
        self.setUrl(self._application_starting_url)
        self.loadFinished.connect(self.on_load_finished)
    
    def set_list(self,
                 model,
                 menu_id,
                 action_id):
        #
        params={}
        params['menu_id']=menu_id
        params['action']=action_id
        params['model']=model
        params['view_type']='list'
        #
        self._application_starting_url=False
        page = QWebEnginePage(self.profile, self)
        self.setPage(page)
        qtOdoochannel = QWebChannel(self)
        page.setWebChannel(qtOdoochannel)
        qtOdoochannel.registerObject("qtodoo", QtOdoo())
        url = make_url(self._web_base_url ,'web#',**params)
        self.setUrl(url)
        self.loadFinished.connect(self.on_load_finished)
        self.show()
    
    def on_load_finished(self, *args, **karg):
        print("on_load_finished ")
        self.load_custom_client_js()

    def load_custom_client_js(self):
        #
        # Load custom qt javascript
        #
        with open('./src/qwebchannel.js') as f:
            content= f.read()
            self.page().runJavaScript(content)
        logging.info("Javascript executed form python code")

class QtOdooUiDilog(QDialog):
    def __init__(self,
                 parent,
                 web_base_url='http://localhost:8069'):
        super(QtOdooUiDilog, self).__init__(parent)
        self._browser = QtOdooUiWeb(parent,
                                    web_base_url)
        self.v_layout = QVBoxLayout()
        self.v_layout.addWidget(self._browser)
        self.command_layout = QHBoxLayout()
        self.v_layout.addLayout(self.command_layout)
        container = QWidget()
        container.setLayout(self.v_layout)
        self.setLayout(self.v_layout)    
    
    def delete_commands(self):
        child = self.command_layout.takeAt(0)
        while child:
            child.widget().deleteLater()
            child = self.command_layout.takeAt(0)
        
    def show_form(self,
                  odoo_id,
                  odoo_object,
                  odoo_action_id):
        #
        self.delete_commands()
        save_button = QPushButton("Save", self)
        save_button.clicked.connect(lambda: self._browser.save_button() )
        cancel_button = QPushButton("Cancel", self)
        cancel_button.clicked.connect(lambda: self._browser.cancel_button())
        self.command_layout.addWidget(save_button)
        self.command_layout.addWidget(cancel_button)
        #
        self._browser.set_form('product.product',
                               menu_id=217,
                               record_id=0,
                               action_id=398)
        self.exec()
        
    def show_tree(self):

    
    