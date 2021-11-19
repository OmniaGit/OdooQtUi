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
Created on 5 Nov 2021

@author: mboscolo
'''
import os
import copy
import logging
import socket
from requests import Session

class ClientController(object):

    def __init__(self, server, verify_ssl=True, pwsPath=''):
        super(ClientController, self).__init__()
        self.server = server
        self.session = Session()
        self.csrf_token = None
        self.verify_ssl = verify_ssl
        self.pwsPath = pwsPath
        
    def authenticate(self,
                     login,
                     password,
                     db=''):
        """
            authenticate to the server
            remarks: verify is for non check ssl
        """
        self.session.get(self.server + '/web/login',
                         params=dict(db=db),
                         verify=self.verify_ssl)
        args = dict(login=login, password=password, db=db)
        res = self.session.post(self.server + '/plm_document_upload/login',
                                args,
                                verify=self.verify_ssl)
        if res.status_code == 404:
            raise Exception("Some errors during calling plm document upload login [%r]" % (res.status_code))
        elif res.status_code != 200:
            raise Exception("Some errors during calling plm document upload login [%r] [%r]" % (res.status_code, res.text))
        logging.info('Plm login autenticated!')
        self.csrf_token = res.headers.get('x-csrf-token')
        return res.headers.get('x-csrf-token')

    def upload_document(self,
                        file_path,
                        ir_id,
                        csrf_token=None,
                        preview_path=False):
        csrf_token = copy.deepcopy(csrf_token)
        if not csrf_token:
            if self.csrf_token:
                csrf_token = self.csrf_token
        if not file_path:
            raise Exception('Unable to upload document ID %r and fileName %r' % (ir_id, file_path))
        url = self.server + '/plm_document_upload/upload'
        post_data = {'doc_id': ir_id,
                     'filename': os.path.split(file_path)[-1],
                     'hostpws': self.pwsPath,
                     'hostname': socket.gethostname(),
                     }
        if csrf_token:
            post_data['csrf_token'] = csrf_token
        logging.info('Start sending file %r with document %r' % (file_path, ir_id))
        files = {}
        with open(file_path, 'rb') as f:
            files['mod_file'] = f.read()
        if preview_path:
            with open(preview_path, 'rb') as f:
                files['preview'] = f.read()
        response = self.session.post(url,
                                     files=files,
                                     data=post_data,
                                     verify=self.verify_ssl)
        if response.status_code != 200:
            raise Exception("Some errors during calling plm document upload  [%r] [%r]" % (response.status_code, response.text))
        
    def upload_pdf(self,
                   file_path,
                   doc_id=False,
                   csrf_token=None):
        if not file_path:
            logging.warning('Unable to upload the PDF file %r' % file_path)
            return
        csrf_token = copy.deepcopy(csrf_token)
        if not csrf_token:
            if self.csrf_token:
                csrf_token = self.csrf_token
        url = self.server + '/plm_document_upload/upload_pdf'
        post_data = {'doc_id': doc_id, 'filename': os.path.split(file_path)[-1]}
        if csrf_token:
            post_data['csrf_token'] = csrf_token
        logging.info('Start sending pdf file %r with document %r' % (file_path, doc_id))
        with open(file_path, 'rb') as f:
            response = self.session.post(url,
                                         files={'file_stream': f.read()},
                                         data=post_data,
                                         verify=self.verify_ssl)
        if response.status_code != 200:
            raise Exception("Some errors during calling plm document upload_pdf  [%r] [%r]" % (response.status_code, response.text))
