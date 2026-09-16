# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The active company of a user with more than one.

Odoo keeps no active company per session: every call works in the first id of
the context key allowed_company_ids, or in the user's default company when the
key is missing. The connection keeps it in contextUser, so it travels with
every call.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No Qt and no server.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.RPC.rpc import RpcConnection


class FakeSocket(object):
    """A server with the companies of users 2 and 3, recording the contexts it gets."""

    COMPANIES = {1: 'San Francisco', 2: 'Chicago', 3: 'Chicago'}
    USERS = {2: {'company_id': [1, 'San Francisco'], 'company_ids': [1, 2]},
             3: {'company_id': [2, 'Chicago'], 'company_ids': [2]}}

    def __init__(self, userId):
        self.userId = userId
        self.contexts = []

    def loginWithUser(self):
        return True

    def callOdooFunction(self, obj, functionName, parameters, kwargParameters, *args):
        return {'lang': 'en_US', 'uid': self.userId}

    def read(self, obj, fields, ids, limit, context={}, load=''):
        self.contexts.append(context)
        return [dict(self.USERS[ids[0]], id=ids[0])]

    def readSearch(self, obj, fields, filterList, order=False, context={}):
        self.contexts.append(context)
        ids = filterList[0][2]
        return [{'id': i, 'name': self.COMPANIES[i]} for i in ids]

    def search(self, obj, filterList, limit, offset, context={}):
        self.contexts.append(context)
        return [1]


def login(rpc, userId):
    rpc.initConnection = lambda *args: setattr(rpc, 'sockInstance', FakeSocket(userId))
    rpc.loginWithUser('xmlrpc', 'user', 'pass', 'db')
    return rpc.sockInstance


class ActiveCompany(unittest.TestCase):

    def test_login_starts_in_the_default_company(self):
        rpc = RpcConnection()
        login(rpc, 2)
        self.assertEqual(rpc.userCompanies, [{'id': 1, 'name': 'San Francisco'},
                                             {'id': 2, 'name': 'Chicago'}])
        self.assertTrue(rpc.isMultiCompany)
        self.assertEqual(rpc.contextUser['allowed_company_ids'], [1])
        self.assertEqual((rpc.companyId, rpc.companyName), (1, 'San Francisco'))

    def test_update_company_travels_with_every_call(self):
        rpc = RpcConnection()
        socket = login(rpc, 2)
        self.assertEqual(rpc.updateCompany('Chicago'), 2)
        rpc.search('res.partner', [])
        self.assertEqual(socket.contexts[-1]['allowed_company_ids'], [2])
        self.assertEqual(rpc.companyName, 'Chicago')
        self.assertEqual(rpc.updateCompany(1), 1)

    def test_a_company_of_someone_else_is_refused(self):
        rpc = RpcConnection()
        login(rpc, 2)
        with self.assertRaises(ValueError):
            rpc.updateCompany('Milano')
        with self.assertRaises(ValueError):
            rpc.updateCompany(3)
        self.assertEqual(rpc.companyId, 1)

    def test_the_next_user_does_not_inherit_the_company(self):
        rpc = RpcConnection()
        login(rpc, 2)
        rpc.updateCompany('Chicago')
        socket = login(rpc, 3)
        # Sent along, the old companies would make Odoo refuse the user's reads.
        self.assertNotIn('allowed_company_ids', socket.contexts[0])
        self.assertFalse(rpc.isMultiCompany)
        self.assertEqual(rpc.contextUser['allowed_company_ids'], [2])


if __name__ == '__main__':
    unittest.main()
