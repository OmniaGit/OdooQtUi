# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The many2many field holds the rows of its list, and tells the form when
they change.

It read its ids from an 'ids' key its list never has, so it was always empty:
an item added with Add an item or Create vanished at once, and the form saved
no relation (the projects of a product, 2026-11-25). Adding or removing a row
did not tell the form either, so a product already in Odoo never had the
relation written.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen, and no server.
"""

import os
import subprocess
import sys
import unittest
from unittest import mock
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

from PySide6 import QtWidgets

from OdooQtUi.objects.many2many.many2many import Many2many
from OdooQtUi.views.tree_list_obj import TemplateTreeListView

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class Tree(QtWidgets.QWidget):
    """The list a many2many shows its records in: {row: id}, as the list view
    keeps it."""

    def __init__(self):
        super(Tree, self).__init__()
        self.idLineRel = {}
        self.on_rows_removed = None
        self.treeObj = mock.Mock(tableWidget=QtWidgets.QTableWidget(), orderedFields=[])
        self.buttToLeft = QtWidgets.QPushButton()
        self.buttToRight = QtWidgets.QPushButton()

    def loadIds(self, ids, *args, **kwargs):
        self.idLineRel = dict(enumerate(ids))
        self.treeObj.tableWidget.setRowCount(len(ids))


class Server(object):
    serverVersion = 20


class Connector(object):
    def __init__(self):
        self.rpc_connector = Server()
        self.trees = []

    def initTreeListViewObject(self, **kwargs):
        self.trees.append(Tree())
        return self.trees[-1]


def projects():
    xml = ElementTree.fromstring('<field name="project_ids"/>')
    definition = {'project_ids': {'type': 'many2many', 'relation': 'project.project',
                                  'string': 'Projects'}}
    parent = QtWidgets.QWidget()
    field = Many2many(parent, xml, definition, odooConnector=Connector())
    field._parent = parent          # kept alive with the field
    changes = []
    field.value_changed_signal.connect(changes.append)
    return field, changes


class TheValue(unittest.TestCase):

    def test_the_rows_of_the_list_in_their_order(self):
        field, _changes = projects()
        field.setValue([7, 3])
        self.assertEqual([7, 3], field.value)

    def test_empty(self):
        field, _changes = projects()
        self.assertEqual([], field.value)

    def test_a_value_set_by_the_form_is_not_a_change(self):
        field, changes = projects()
        field.setValue([7])
        self.assertEqual([], changes)


class AddingItems(unittest.TestCase):

    def test_an_item_added_stays_and_the_form_is_told(self):
        field, changes = projects()
        field.setValue([7])
        field.addIds([3])
        self.assertEqual([7, 3], field.value)
        self.assertEqual(['project_ids'], changes)

    def test_what_the_field_holds_already_is_not_added_twice(self):
        field, changes = projects()
        field.setValue([7])
        field.addIds([7, False])
        self.assertEqual([7], field.value)
        self.assertEqual([], changes)

    def test_create_adds_the_new_record(self):
        field, changes = projects()
        field.setValue([7])
        field.odooConnector.rpc_connector.create = mock.Mock(return_value=12)
        form = mock.Mock()
        form.getAllFieldsValues.return_value = {'name': 'P'}
        form.requiredFields = {}
        field.odooConnector.initFormViewObj = mock.Mock(return_value=QtWidgets.QWidget())
        field.odooConnector.initFormViewObj.return_value.loadIds = mock.Mock()
        field.odooConnector.initFormViewObj.return_value.getAllFieldsValues = form.getAllFieldsValues
        with mock.patch.object(QtWidgets.QDialog, 'exec', return_value=QtWidgets.QDialog.Accepted):
            field.createAndAdd()
        self.assertEqual([7, 12], field.value)
        self.assertEqual(['project_ids'], changes)


class RemovingItems(unittest.TestCase):

    def test_a_row_removed_tells_the_field_which_tells_the_form(self):
        field, changes = projects()
        field.setValue([7, 3, 5])
        tree = field.treeViewObj
        tree.setRemoveButtons = mock.Mock()
        TemplateTreeListView.removeItem(tree, 1)
        self.assertEqual([7, 5], field.value)
        self.assertEqual(['project_ids'], changes)

    def test_a_list_nobody_owns_removes_its_row_quietly(self):
        tree = Tree()
        tree.loadIds([7, 3])
        tree.setRemoveButtons = mock.Mock()
        TemplateTreeListView.removeItem(tree, 0)
        self.assertEqual({0: 3}, tree.idLineRel)


if __name__ == '__main__':
    unittest.main()
