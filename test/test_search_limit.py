# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""search sends a limit and an offset only when they are numbers.

False == 0 in Python, so `limit or limit == 0` sent limit=False. Most models
read that as no limit; ir.attachment._search in Odoo 19 reads any limit that is
not None as a batch size, turned it into 0 and answered nothing -- no document
was ever found by the CAD client (2026-09-15).

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No server.
"""

import os
import sys
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC.XmlRpc.xmlRpc import XmlRpcConnection
from OdooQtUi.RPC.JsonRpc.jsonRpc import JsonRpcConnection


def recorded(connection_class):
    """A connection whose calls are recorded instead of sent."""
    connection = connection_class('admin', 'admin', 'db')
    calls = []
    connection.callOdooFunction = lambda obj, method, args, kwargs, *rest: \
        calls.append((obj, method, args, kwargs)) or []
    return connection, calls


class SearchLimit(unittest.TestCase):

    def test_the_defaults_send_no_limit_and_no_offset(self):
        for connection_class in (XmlRpcConnection, JsonRpcConnection):
            connection, calls = recorded(connection_class)
            connection.search('ir.attachment', [('id', '=', 1)])
            kwargs = calls[0][3]
            self.assertNotIn('limit', kwargs, connection_class.__name__)
            self.assertNotIn('offset', kwargs, connection_class.__name__)

    def test_numbers_are_sent_zero_included(self):
        for connection_class in (XmlRpcConnection, JsonRpcConnection):
            connection, calls = recorded(connection_class)
            connection.search('ir.attachment', [], limit=0, offset=5)
            kwargs = calls[0][3]
            self.assertEqual((kwargs['limit'], kwargs['offset']), (0, 5),
                             connection_class.__name__)


if __name__ == '__main__':
    unittest.main()
