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

from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineCore import QWebEngineProfile 
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtNetwork import QNetworkCookie

# class QtOdoo(QObject):
#
#     _storedRecord={}
#
#     @Slot(str, str)
#     def onRecordSaved(self,
#                       model_name,
#                       datas):
#         """
#         Event fired by odoo framework on record saved
#         :model_name odoo table name
#         :datas json dict_like with the all the record values
#         """
#         print("onRecordSaved")
#         record_datas = json.loads(datas)
#         datas_id = record_datas.get('id')
#
#         if datas_id in self._storedRecord[model_name]:
#             self._storedRecord[model_name][datas_id]= record_datas
#         else:
#             self._storedRecord[model_name] = {datas_id: record_datas}
#
#     @Slot(str, result=str)
#     def getRef(self, o):
#         print("inside getRef", o)
#         #py_obj = json.loads(o)
#         #py_obj["c"] = ("Hello", "from", "Ppython")
#         #return "json.dumps(py_obj)"
#         return "{'message':{'id':5}}"
#
#     @Slot(str)
#     def printRef(self, o):
#         print("printRef Called")
#         py_obj = json.loads(o)
#         #print("inside printRef", py_obj)
#         pass
    
# class MainWindow(QMainWindow):
#
#     def __init__(self, *args, **kwargs):
#         super(MainWindow,self).__init__(*args, **kwargs)
#         self.qtodoo = QtOdoo()
#         self.webchannel = QWebChannel(self)
#         self.browser = QWebEngineView()#
#         #self.profile = QWebEngineProfile('odooPLM', self.browser)
#         #self.profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
#         #cookie_store = self.profile.cookieStore()
#         #cookie_store.loadAllCookies()
#         #cookie_store.cookieAdded.connect(self.onCookieAdded)
#         self.cookies = []
#         self.page = self.browser.page()
#         self.browser
#         #self.page.profile().setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
#         self.page.setWebChannel(self.webchannel)
#         self.webchannel.registerObject("qtodoo", self.qtodoo)
#
#         #self.browser.setUrl(QUrl("https://www.v15.odooplm.cloud/"))
#         #self.browser.setUrl(QUrl("http://localhost:8069/"))
#         self.browser.setUrl(QUrl("http://localhost:8069/web?debug=assets#id=647&cids=1&menu_id=217&action=398&model=product.product&view_type=form"))
#         #self.browser.setUrl(QUrl("http://localhost:8069"))
#         self.browser.loadFinished.connect(self.on_load_finished)
#         #
#         self.reload_button = QPushButton("Reload", self)
#         self.reload_button.setToolTip("reload")
#         self.reload_button.clicked.connect(lambda: self.browser.reload())
#         #
#         layout = QVBoxLayout()
#         layout.addWidget(self.browser)
#         layout.addWidget(self.reload_button)
#
#         container = QWidget()
#         container.setLayout(layout)
#
#         self.setCentralWidget(container)
#         #
#
#     def on_load_finished(self,*args,**karg):
#         self.load_custom_client_js()
#
#     def onCookieAdded(self, cookie):
#         for c in self.cookies:
#             if c.hasSameIdentifier(cookie):
#                 return
#         self.cookies.append(QNetworkCookie(cookie))
#         self.toJson()
#
#     def load_custom_client_js(self):
#         #
#         # Load custom qt javascript
#         #
#         with open('./src/qwebchannel.js') as f:
#             content= f.read()
#             self.page.runJavaScript(content)
#         self.load_custom_client_js()
#         print("Javascript executed form python code")

from OdooQtUiWeb.web_odoo import QtOdooUiDilog

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
            odoo_id=,
            odoo_object='product.product',
            odoo_action_id=
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
    sys.exit(ret)

if __name__ == "__main__":
    main()

    
    # def on_load_finished(self,*args,**karg):
    #     java ="""
    #     const loadJs = document.createElement("script");
    #     loadJs.type="text/javascript";
    #     loadJs.src="qrc:/src/qwebchannel.js";
    #     document.head.appendChild(loadJs);
    #     """    
 #     /*
    #     setTimeout(function(){
    #
    #
    #     var aa = document.querySelector("[name='action_confirm']");
    #     console.error("aa");
    #     console.error(aa);
    #     console.error("aa");
    #     if(aa){
    #     aa.addEventListener('click', function(args){
    #         console.error("Before");
    #         new QWebChannel(qt.webChannelTransport, function(channel) {
    #             console.error("inside");
    #             backend = channel.objects.backend;
    #             var x = {a: "1000", b: ["Hello", "From", "JS"]}
    #             backend.getRef(JSON.stringify(x), function(y) {
    #             js_obj = JSON.parse(y);
    #             js_obj["f"] = false;
    #             backend.printRef(JSON.stringify(js_obj));
    #     });
    # });
    #     })
    #     }
    #     else{
    #     console.error("event is null");
    #     }
    #     },10000)
    #     */
    #     """
        #self.page.runJavaScript(java)
    # promise.then(function(data){
    #     console.log(window)
    #     if("QWebChannel" in window){
    #         new QWebChannel(qt.webChannelTransport, function(channel) {
    #             const backend = channel.objects.backend;
    #             console.error("url");
    #             console.error(url);
    #             console.error("params");
    #             console.error(JSON.stringify(params)); 
    #             console.error("settings");
    #             console.error(JSON.stringify(settings));
    #             backend.printRef(JSON.stringify(url));
    #         });
    #     }
    #     return Promise.resolve(data);
    # }).catch(function(ex){
    #    console.error("Rpc Error", ex) 
    # });
    