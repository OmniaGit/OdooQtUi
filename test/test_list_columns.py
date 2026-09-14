# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A list column from Odoo 17 on: `column_invisible` for the column.

`invisible` on a list field is about one row (`not is_account_reconcile` on
the move lines of a partner). Read as a column rule against the context alone,
it raised NameError, logged an ERROR and left the column shown; the real
column rule, `column_invisible`, was never read.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No Qt and no server.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.utils_odoo_conn import utils


class ColumnInvisible(unittest.TestCase):

    def test_no_rule_shows_the_column(self):
        self.assertFalse(utils.evaluateColumnInvisible(None))

    def test_constants(self):
        self.assertTrue(utils.evaluateColumnInvisible('True'))
        self.assertTrue(utils.evaluateColumnInvisible('1'))
        self.assertFalse(utils.evaluateColumnInvisible('0'))

    def test_the_parent_record_is_read_by_attribute(self):
        rule = "parent.state != 'draft'"
        self.assertTrue(utils.evaluateColumnInvisible(rule, {}, {'state': 'posted'}))
        self.assertFalse(utils.evaluateColumnInvisible(rule, {}, {'state': 'draft'}))

    def test_a_name_the_parent_does_not_hold_is_false(self):
        self.assertTrue(utils.evaluateColumnInvisible('not parent.company_id', {}, {}))

    def test_the_context(self):
        rule = "not context.get('show_cost')"
        self.assertTrue(utils.evaluateColumnInvisible(rule, {}, {}))
        self.assertFalse(utils.evaluateColumnInvisible(rule, {'show_cost': True}, {}))

    def test_what_cannot_be_evaluated_leaves_the_column_shown(self):
        self.assertFalse(utils.evaluateColumnInvisible('not is_account_reconcile', {}, {}))


class CellInvisible(unittest.TestCase):
    """The row's own `invisible`, over the row as a read answers it."""

    def test_evaluated_over_the_row(self):
        rule = 'not is_account_reconcile'
        row = utils.recordValues({}, {'is_account_reconcile': True, 'account_id': [5, 'Receivable']})
        self.assertFalse(utils.evaluateExpression(rule, row))
        row = utils.recordValues({}, {'is_account_reconcile': False})
        self.assertTrue(utils.evaluateExpression(rule, row))


if __name__ == '__main__':
    unittest.main()
