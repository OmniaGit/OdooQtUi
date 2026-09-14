# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The many2one field asks the server what the user types, and nothing else.

It read every record of the related model -- no domain, no limit -- for every
many2one of a form each time the form was opened, and told the records apart
by name. Here a fake server counts what is asked.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen, and no server.
"""

import os
import subprocess
import sys
import unittest
from xml.etree import ElementTree

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_PROBE = subprocess.call(
    [sys.executable, '-c',
     'import os;os.environ.setdefault("QT_QPA_PLATFORM","offscreen");'
     'from PySide6 import QtWidgets;QtWidgets.QApplication([])'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if _PROBE:
    raise unittest.SkipTest("no Qt that can open a window here")

from PySide6 import QtCore, QtWidgets

from OdooQtUi.objects.many2one.many2one import Many2one, CREATE_ITEM

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class Server(object):
    serverVersion = 19

    def __init__(self):
        self.contextUser = {'lang': 'en_US', 'uid': 2}
        self.calls = []

    def read(self, model, fields, ids, *args, **kwargs):
        self.calls.append(('read', model, ids))
        return [{'id': ids[0], 'display_name': 'Record %d' % ids[0]}]

    def readSearch(self, *args, **kwargs):
        self.calls.append(('readSearch',) + args)
        return []

    def callCustomMethod(self, model, method, args=[], kwargs={}, context={}, **other):
        self.calls.append((method, model, kwargs, context))
        return [[11, 'Mario Rossi'], [1, 'My Company']]


class Connector(object):
    def __init__(self):
        self.rpc_connector = Server()


class Form(QtWidgets.QWidget):
    """What a many2one reads from its form: the fields and the record."""

    def __init__(self, values):
        super(Form, self).__init__()
        self.interfaceFieldsDict = {}
        self.formVals = values


def many2one(attributes, values={}):
    xml = ElementTree.fromstring('<field name="parent_id"/>')
    xml.attrib.update(attributes)
    connector = Connector()
    form = Form(values)
    field = Many2one(form, xml, {'parent_id': {'type': 'many2one', 'relation': 'res.partner'}}, connector)
    form.field = field      # kept alive with the form
    return field, connector.rpc_connector


class Loading(unittest.TestCase):

    def test_a_value_read_asks_nothing(self):
        field, server = many2one({})
        field.setValue([7, 'Cliente ABC'])
        self.assertEqual(server.calls, [])
        self.assertEqual(field.value, 7)
        self.assertEqual(field.widgetQtObj2.currentText(), 'Cliente ABC')

    def test_an_id_asks_for_its_name_only(self):
        field, server = many2one({})
        field.setValue(7)
        self.assertEqual(server.calls, [('read', 'res.partner', [7])])
        self.assertEqual(field.currentValue, [7, 'Record 7'])

    def test_false_empties_it(self):
        field, server = many2one({})
        field.setValue([7, 'Cliente ABC'])
        field.setValue(False)
        self.assertIs(field.value, False)
        self.assertEqual(field.widgetQtObj2.currentText(), '')


class Searching(unittest.TestCase):

    def test_the_search_carries_the_domain_over_the_record(self):
        field, server = many2one({'domain': "[('company_id', 'in', [company_id, False])]"},
                                 {'company_id': [3, 'Omnia']})
        field.widgetQtObj2.lineEdit().setText('ma')
        field._search()
        method, model, kwargs, _context = server.calls[-1]
        self.assertEqual((method, model), ('name_search', 'res.partner'))
        self.assertEqual(kwargs['name'], 'ma')
        self.assertEqual(kwargs['domain'], [('company_id', 'in', [3, False])])
        self.assertEqual(kwargs['limit'], 8)

    def test_a_domain_that_cannot_be_read_is_no_domain(self):
        field, _server = many2one({'domain': "[('x', '=', nowhere)]"})
        self.assertEqual(field.evaluatedDomain(), [])

    def test_a_proposal_is_chosen_by_id_and_the_form_is_told(self):
        field, _server = many2one({})
        told = []
        field.value_changed_signal.connect(told.append)
        field.widgetQtObj2.lineEdit().setText('m')
        field._search()
        field._proposalChosen(field._completerModel.index(1, 0))
        self.assertEqual(field.currentValue, [1, 'My Company'])
        self.assertEqual(told, ['parent_id'])

    def test_no_table_is_ever_read_whole(self):
        field, server = many2one({})
        field.setValue([7, 'Cliente ABC'])
        field.widgetQtObj2.lineEdit().setText('m')
        field._search()
        self.assertFalse([call for call in server.calls if call[0] == 'readSearch'])


class Attributes(unittest.TestCase):

    def test_python_false_from_odoo_17(self):
        field, _server = many2one({'can_create': 'False', 'can_write': 'False'})
        self.assertFalse(field.canCreate)
        self.assertFalse(field.canWrite)
        items = [field.widgetQtObj2.itemData(i) for i in range(field.widgetQtObj2.count())]
        self.assertNotIn(CREATE_ITEM, items)

    def test_json_true_up_to_16(self):
        field, _server = many2one({'can_create': 'true'})
        self.assertTrue(field.canCreate)

    def test_the_no_create_option(self):
        field, _server = many2one({'options': "{'no_create': True}"})
        self.assertFalse(field.canCreate)


if __name__ == '__main__':
    unittest.main()
