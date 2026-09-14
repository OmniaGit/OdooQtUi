# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A failed call raises, and the window is the business of the slot.

The RPC layer opened a modal dialog itself and answered None: a script with no
display waited for ever on the first refused call. Here the transports raise
OdooRpcError and show nothing, and utilsUi.rpcErrorBoundary tells the user once,
from the slot the action came through.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen, and no server.
"""

import os
import subprocess
import sys
import threading
import unittest
import xmlrpc.client

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC.errors import OdooRpcError, OdooServerError, OdooConnectionError
from OdooQtUi.RPC.XmlRpc.xmlRpc import XmlRpcConnection
from OdooQtUi.RPC.JsonRpc.jsonRpc import JsonRpcConnection, JsonRpcFault

TRACEBACK = ('Traceback (most recent call last):\n'
             '  File "odoo/service/model.py", line 97, in call_kw\n'
             'odoo.exceptions.UserError: The name is required.\n')


class XmlSocket(object):
    def __init__(self, error):
        self.error = error

    def execute_kw(self, *args):
        raise self.error


def xmlConnection(error):
    connection = XmlRpcConnection('admin', 'admin', 'db')
    connection.socketYesLogin = XmlSocket(error)
    return connection


def jsonConnection(error):
    connection = JsonRpcConnection('admin', 'admin', 'db')
    connection.socketYesLogin = True

    def call(*args, **kwargs):
        raise error
    connection._call = call
    return connection


class Transports(unittest.TestCase):

    def test_a_refusal_raises_what_odoo_said(self):
        for connection in (xmlConnection(xmlrpc.client.Fault(2, TRACEBACK)),
                           jsonConnection(JsonRpcFault(200, TRACEBACK))):
            with self.assertRaises(OdooServerError) as caught:
                connection.callOdooFunction('res.partner', 'write', [[7], {'name': ''}], {})
            error = caught.exception
            self.assertEqual((error.model, error.method), ('res.partner', 'write'))
            self.assertEqual(error.summary, 'odoo.exceptions.UserError: The name is required.')
            self.assertIn('Traceback', error.faultString)

    def test_a_lost_connection_raises_a_connection_error(self):
        for connection in (xmlConnection(ConnectionRefusedError('refused')),
                           jsonConnection(OSError('timed out'))):
            with self.assertRaises(OdooConnectionError):
                connection.callOdooFunction('res.partner', 'read', [[7]], {})

    def test_anything_else_is_still_an_rpc_error(self):
        with self.assertRaises(OdooRpcError) as caught:
            xmlConnection(TypeError('cannot marshal objects')).callOdooFunction('res.partner', 'read', [], {})
        self.assertIn('cannot marshal', str(caught.exception))
        self.assertIsInstance(caught.exception.__cause__, TypeError)

    def test_not_logged_in(self):
        connection = XmlRpcConnection('admin', 'admin', 'db')
        with self.assertRaises(OdooConnectionError):
            connection.callOdooFunction('res.partner', 'read', [], {})

    def test_the_old_flags_do_not_bring_back_a_none(self):
        connection = xmlConnection(xmlrpc.client.Fault(2, TRACEBACK))
        with self.assertRaises(OdooServerError):
            connection.callOdooFunction('res.partner', 'write', [], {}, forceHideInterface=True)


_PROBE = subprocess.call(
    [sys.executable, '-c',
     'import os;os.environ.setdefault("QT_QPA_PLATFORM","offscreen");'
     'from PySide6 import QtWidgets;QtWidgets.QApplication([])'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@unittest.skipIf(_PROBE, "no Qt that can open a window here")
class Boundary(unittest.TestCase):

    def setUp(self):
        from PySide6 import QtCore, QtWidgets
        from OdooQtUi.utils_odoo_conn import utilsUi
        self.QtCore = QtCore
        self.application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.utilsUi = utilsUi
        self.shown = []
        self.original = utilsUi.popMessage
        utilsUi.popMessage = lambda parent, body, kind, header='': self.shown.append((parent, kind, header))

        class Widget(QtWidgets.QPushButton):
            clicks = []

            @utilsUi.rpcErrorBoundary
            def buttonClicked(self):
                Widget.clicks.append('clicked')
                raise OdooServerError('The name is required.', 'res.partner', 'write',
                                      2, TRACEBACK)

        self.Widget = Widget

    def tearDown(self):
        self.utilsUi.popMessage = self.original

    def test_the_slot_tells_the_user_once_and_returns(self):
        button = self.Widget()
        self.assertIsNone(button.buttonClicked())
        self.assertEqual(len(self.shown), 1)
        parent, kind, header = self.shown[0]
        self.assertIs(parent, button)
        self.assertEqual(kind, 'ERROR')
        self.assertEqual(header, 'odoo.exceptions.UserError: The name is required.')

    def test_a_signal_with_more_arguments_than_the_slot_takes(self):
        button = self.Widget()
        button.clicked.connect(button.buttonClicked)     # clicked(bool)
        button.click()
        self.assertEqual(len(self.shown), 1)

    def test_other_exceptions_are_not_hidden(self):
        from PySide6 import QtWidgets

        class Broken(QtWidgets.QWidget):
            @self.utilsUi.rpcErrorBoundary
            def slot(self):
                raise KeyError('a bug')

        with self.assertRaises(KeyError):
            Broken().slot()

    def test_no_window_outside_the_gui_thread(self):
        answers = []
        error = OdooServerError('refused', 'res.partner', 'write')
        worker = threading.Thread(target=lambda: answers.append(self.utilsUi.showRpcError(None, error)))
        worker.start()
        worker.join()
        self.assertEqual(answers, [False])
        self.assertEqual(self.shown, [])


if __name__ == '__main__':
    unittest.main()
