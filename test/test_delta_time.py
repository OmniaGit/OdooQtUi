# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""At the login the connection measures the server's clock less this PC's,
both in UTC (the user, 2026-10-17): what turns a file's time into the
server's. MainConnector.deltaTime read it, and nothing ever set it.

The server's time is the HTTP Date header of /jsonrpc common.version, which
every Odoo answers with no module.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No server: requests.post answers here.
"""

import datetime
import email.utils
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC import rpc as rpc_module
from OdooQtUi.RPC.rpc import RpcConnection


class Answer(object):
    def __init__(self, server_time):
        self.headers = {'Date': email.utils.format_datetime(server_time, usegmt=True)}


def connection():
    rpc = RpcConnection()
    rpc.scheme, rpc.xmlrpcServerIP, rpc.xmlrpcPort = 'http', 'server', 8069
    return rpc


class DeltaTime(unittest.TestCase):

    def measure(self, server_ahead):
        now = datetime.datetime.now(datetime.timezone.utc)
        rpc = connection()
        with mock.patch.object(rpc_module.requests, 'post',
                               return_value=Answer(now + server_ahead)) as post:
            rpc.computeDeltaTime()
        return rpc, post

    def test_a_server_ahead(self):
        rpc, post = self.measure(datetime.timedelta(minutes=5))
        self.assertLess(abs((rpc.deltaTime - datetime.timedelta(minutes=5)).total_seconds()), 1.5)
        self.assertEqual('http://server:8069/jsonrpc', post.call_args[0][0])

    def test_the_same_clock(self):
        rpc, _post = self.measure(datetime.timedelta(0))
        self.assertLess(abs(rpc.deltaTime.total_seconds()), 1.5)

    def test_no_answer_is_no_difference(self):
        rpc = connection()
        with mock.patch.object(rpc_module.requests, 'post', side_effect=OSError('down')):
            rpc.computeDeltaTime()
        self.assertEqual(datetime.timedelta(0), rpc.deltaTime)

    def test_none_before_the_login_and_after_the_logout(self):
        rpc = connection()
        self.assertEqual(datetime.timedelta(0), rpc.deltaTime)
        rpc.deltaTime = datetime.timedelta(minutes=5)
        rpc.logout()
        self.assertEqual(datetime.timedelta(0), rpc.deltaTime)


if __name__ == '__main__':
    unittest.main()
