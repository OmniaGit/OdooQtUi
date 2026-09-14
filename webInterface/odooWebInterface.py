# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

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
    sys.exit(app.exec())

