# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""Modifiers, over the two generations of arch this client has to read.

Up to Odoo 16 the server computed the conditions into the arch as
`modifiers="{'invisible': [['state', '=', 'draft']]}"`, and `invisible` itself
was only ever "1" or "0". From Odoo 17 there are no modifiers at all: the node
carries `invisible="state != 'draft'"`, an expression over the record.

Read against an empty namespace -- which is what this client did until
2026-09-13 -- every one of those raises NameError and answers "not hidden". On a
v19 server that showed every button of a workflow in every state, and every
conditional field on every form.

The rules tested here are KOO's (Koo/Model/Record.py), because it is a client
that reads these views correctly today.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

No Qt and no server: utils imports neither.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OdooQtUi.utils_odoo_conn import utils


class _Field(object):
    """A field object as the views hold them: a name and a value."""

    def __init__(self, value):
        self.value = value


class _Widget(object):
    """A button or a field, as far as widgetModifier is concerned."""

    def __init__(self, modifiers=None, invisible=None, readonly=None):
        self.modifiers = modifiers or {}
        if invisible is not None:
            self.invisibleExpression = invisible
        if readonly is not None:
            self.readonlyExpression = readonly


class ConstantModifiers(unittest.TestCase):
    """What both generations write for "never" and "always"."""

    def test_the_constants_are_recognised(self):
        for value in (True, False, None, '', '0', '1', 'true', 'false', 'True', 'False'):
            self.assertTrue(utils.isConstantModifier(value), value)

    def test_an_expression_is_not_a_constant(self):
        for value in ("state != 'draft'", 'engineering_revision > 0',
                      "not id", "state in ['draft', 'confirmed']"):
            self.assertFalse(utils.isConstantModifier(value), value)

    def test_they_evaluate_without_a_record(self):
        self.assertIs(utils.evaluateExpression('1'), True)
        self.assertIs(utils.evaluateExpression('true'), True)
        self.assertIs(utils.evaluateExpression(True), True)
        self.assertIs(utils.evaluateExpression('0'), False)
        self.assertIs(utils.evaluateExpression('false'), False)
        self.assertIs(utils.evaluateExpression(''), False)
        self.assertIs(utils.evaluateExpression(None), False)
        self.assertIs(utils.evaluateExpression(False), False)


class Expressions(unittest.TestCase):
    """The Odoo 17 modifier: python, over the record's own values."""

    def test_the_record_decides(self):
        self.assertIs(utils.evaluateExpression("state != 'draft'",
                                               {'state': 'draft'}), False)
        self.assertIs(utils.evaluateExpression("state != 'draft'",
                                               {'state': 'released'}), True)

    def test_the_operators_a_view_really_uses(self):
        values = {'state': 'confirmed', 'engineering_revision': 2,
                  'linkeddocuments': [1, 2, 3], 'id': 7}
        self.assertIs(utils.evaluateExpression('engineering_revision > 0', values), True)
        self.assertIs(utils.evaluateExpression("state in ['draft', 'confirmed']", values), True)
        self.assertIs(utils.evaluateExpression("state not in ['draft']", values), True)
        self.assertIs(utils.evaluateExpression('not id', values), False)
        self.assertIs(utils.evaluateExpression('len(linkeddocuments) > 2', values), True)

    def test_a_name_the_record_has_not_got_hides_it(self):
        # KOO's answer, kept on purpose: `bool(expression)`, so a condition that
        # cannot be read hides the widget. A button shown by mistake is one the
        # user clicks and the server refuses; hidden by mistake, they go and
        # press it in Odoo. The first is the worse of the two.
        self.assertIs(utils.evaluateExpression('nothing_like_this > 0', {}), True)

    def test_the_context_is_there_to_be_read(self):
        self.assertIs(utils.evaluateExpression("context.get('show_all')", {},
                                               {'show_all': True}), True)
        self.assertIs(utils.evaluateExpression('uid == 2', {}, {'uid': 2}), True)

    def test_an_expression_cannot_reach_out_of_the_record(self):
        # It comes from the server, and it is still evaluated in this process.
        self.assertIs(utils.evaluateExpression("__import__('os').getcwd()", {}), True)
        self.assertIs(utils.evaluateExpression("open('/etc/passwd')", {}), True)


class RecordValues(unittest.TestCase):
    """The namespace an expression is read against -- KOO's rpcValues."""

    def test_a_many2one_is_its_id(self):
        # A read answers [id, name]; a view compares with the id.
        self.assertEqual(utils.recordValues({}, {'partner_id': [7, 'ACME']}),
                         {'partner_id': 7})

    def test_none_is_false(self):
        self.assertEqual(utils.recordValues({}, {'x': None}), {'x': False})

    def test_the_header_answers_under_the_plain_name(self):
        # The header keeps its fields as header_<name>, which is how
        # evaluateAttrs looks them up too.
        values = utils.recordValues({'header_state': _Field('draft')}, {})
        self.assertEqual(values['state'], 'draft')

    def test_what_the_form_holds_wins_over_what_was_read(self):
        # A modifier is about the record in front of the user, edits included.
        values = utils.recordValues({'state': _Field('released')},
                                    {'state': 'draft'})
        self.assertEqual(values['state'], 'released')


class WidgetModifiers(unittest.TestCase):
    """Which of the two generations answers, and when neither does."""

    def setUp(self):
        self.fields = {'state': _Field('draft')}
        self.values = utils.recordValues(self.fields, {})

    def test_the_old_modifiers_answer_when_the_server_sends_them(self):
        widget = _Widget(modifiers={'invisible': [['state', '=', 'draft']]})
        self.assertIs(utils.widgetModifier(widget, 'invisible', self.fields,
                                           self.values), True)

    def test_the_expression_answers_when_they_are_gone(self):
        widget = _Widget(invisible="state != 'draft'")
        self.assertIs(utils.widgetModifier(widget, 'invisible', self.fields,
                                           self.values), False)

    def test_a_constant_is_left_to_the_view(self):
        # Nothing to decide per record: the widget was built with it, and the
        # caller leaves it as the view drew it.
        self.assertIsNone(utils.widgetModifier(_Widget(invisible='1'),
                                               'invisible', self.fields, self.values))
        self.assertIsNone(utils.widgetModifier(_Widget(), 'invisible',
                                               self.fields, self.values))

    def test_a_workflow_shows_the_buttons_of_its_state(self):
        # The shape of the case this was written for: three buttons of a
        # statusbar, one state, and the two that are not for this state gone.
        buttons = {'confirm': _Widget(invisible="state != 'draft'"),
                   'release': _Widget(invisible="state != 'confirmed'"),
                   'obsolete': _Widget(invisible="state not in ['released']")}
        hidden = dict((name, utils.widgetModifier(widget, 'invisible',
                                                  self.fields, self.values))
                      for name, widget in buttons.items())
        self.assertEqual(hidden, {'confirm': False, 'release': True,
                                  'obsolete': True})


if __name__ == '__main__':
    unittest.main(verbosity=2)
