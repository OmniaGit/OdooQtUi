# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The context of a view node, and the session context it must not spoil.

On an Odoo 19 res.partner form a field carries
`context="{'default_country_id': country_id, 'default_parent_id': id}"`.
Evaluated over the widgets, the context held a Many2one widget and Python's
built-in `id`; merged into the session context, every later call failed with
"cannot marshal" and `form.loadIds([7])` never showed the record.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No Qt and no server.
"""

import os
import sys
import unittest
import xmlrpc.client

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.utils_odoo_conn import utils
from OdooQtUi.RPC.rpc import RpcConnection


class Widget(object):
    """What a field widget offers an expression: its value."""

    def __init__(self, value):
        self.value = value


class EvaluateContext(unittest.TestCase):

    CONTEXT = ("{'default_country_id': country_id, 'default_zip': zip, "
               "'default_parent_id': id, 'default_type': 'contact'}")

    def test_widgets_are_read_for_their_values(self):
        fields = {'country_id': Widget([110, 'Italy']), 'zip': Widget('30100')}
        context = utils.evaluateContext(self.CONTEXT, fields)
        self.assertEqual(context['default_country_id'], 110)
        self.assertEqual(context['default_zip'], '30100')
        self.assertEqual(context['default_type'], 'contact')

    def test_what_rpc_cannot_carry_is_left_out(self):
        fields = {'country_id': Widget(False), 'zip': Widget('')}
        context = utils.evaluateContext(self.CONTEXT, fields)
        self.assertNotIn('default_parent_id', context)
        xmlrpc.client.dumps((context,))   # does not raise

    def test_plain_values_work_too(self):
        context = utils.evaluateContext("{'x': partner_id}", {'partner_id': [3, 'A']})
        self.assertEqual(context, {'x': 3})

    def test_what_cannot_be_evaluated_is_empty(self):
        self.assertEqual(utils.evaluateContext("{'x': nowhere}", {}), {})
        self.assertEqual(utils.evaluateContext("[1, 2]", {}), {})


class SessionContext(unittest.TestCase):

    def test_a_call_context_does_not_stay_in_the_session(self):
        rpc = RpcConnection()
        rpc.contextUser = {'lang': 'en_US'}
        sent = []

        class Socket(object):
            def search(self, obj, filterList, limit, offset, context={}):
                sent.append(context)
                return [1]

        rpc.sockInstance = Socket()
        rpc.search('res.partner', [], context={'active_test': False})
        self.assertEqual(sent[0], {'lang': 'en_US', 'active_test': False})
        self.assertEqual(rpc.contextUser, {'lang': 'en_US'})


class OnchangeValues(unittest.TestCase):
    """What the onchange of Odoo 17 and later is sent, and what it answers."""

    def test_widget_values_are_sent_as_odoo_writes_them(self):
        import datetime
        self.assertEqual(utils.widgetValueToOnchange([3, 'Italy'], 'many2one'), 3)
        self.assertIs(utils.widgetValueToOnchange(None, 'char'), False)
        self.assertIs(utils.widgetValueToOnchange('', 'selection'), False)
        self.assertEqual(utils.widgetValueToOnchange('', 'char'), '')
        self.assertEqual(utils.widgetValueToOnchange(datetime.date(2026, 9, 14), 'date'), '2026-09-14')
        self.assertEqual(utils.widgetValueToOnchange(datetime.datetime(2026, 9, 14, 8, 5), 'datetime'),
                         '2026-09-14 08:05:00')

    def test_what_rpc_cannot_carry_is_refused(self):
        with self.assertRaises(ValueError):
            utils.widgetValueToOnchange(object(), 'char')

    def test_a_many2one_answer_becomes_the_pair_a_read_gives(self):
        self.assertEqual(utils.onchangeValueToWidget({'id': 109, 'display_name': 'Italy'}), [109, 'Italy'])
        self.assertIs(utils.onchangeValueToWidget({'id': False, 'display_name': ''}), False)
        self.assertIs(utils.onchangeValueToWidget(True), True)


if __name__ == '__main__':
    unittest.main()
