# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A login that did not reach Odoo keeps what stopped it, and the words for it
are the application's.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No server: the login goes to a local port nothing listens on.
"""

import os
import socket
import sys
import unittest

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC import errors
from OdooQtUi.RPC.JsonRpc.jsonRpc import JsonRpcConnection


def closed_port():
    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        return probe.getsockname()[1]


class TestConnectionExplainer(unittest.TestCase):

    def tearDown(self):
        errors.set_connection_explainer(None)

    def login_to_nothing(self):
        connection = JsonRpcConnection('admin', 'admin', 'db', closed_port(), 'http', '127.0.0.1')
        connection.session.trust_env = False
        self.assertFalse(connection.loginWithUser())
        return connection

    def test_a_login_that_did_not_reach_odoo_keeps_why(self):
        connection = self.login_to_nothing()
        self.assertIsInstance(connection.last_exception, OSError)
        # The requests error is kept behind it, for whoever explains it.
        self.assertIsInstance(connection.last_exception.__cause__,
                              requests.exceptions.ConnectionError)

    def test_without_an_explainer_the_error_speaks(self):
        connection = self.login_to_nothing()
        text = errors.explain_connection_error(connection.last_exception, connection.urlCommon)
        self.assertEqual(text, str(connection.last_exception))

    def test_the_explainer_of_the_application(self):
        seen = []

        def explainer(error, url):
            seen.append((error, url))
            return 'Odoo does not answer'
        errors.set_connection_explainer(explainer)
        connection = self.login_to_nothing()
        text = errors.explain_connection_error(connection.last_exception, connection.urlCommon)
        self.assertEqual(text, 'Odoo does not answer')
        self.assertEqual(seen[0][1], connection.urlCommon)

    def test_an_error_that_is_not_about_the_connection(self):
        errors.set_connection_explainer(lambda error, url: None)
        self.assertIsNone(errors.connection_problem(ValueError('no'), 'http://x'))
        self.assertEqual(errors.explain_connection_error(OSError('down'), 'http://x'), 'down')

    def test_a_broken_explainer_does_not_hide_the_error(self):
        errors.set_connection_explainer(lambda error, url: 1 / 0)
        self.assertEqual(errors.explain_connection_error(OSError('down'), 'http://x'), 'down')


if __name__ == '__main__':
    unittest.main()
