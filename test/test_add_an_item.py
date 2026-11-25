# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A many2many's "Add an item" takes the rows the user picks (2026-11-25).

It took only the rows ticked in column 0, and the first column of project's
list is `sequence`, which Odoo hides: no box could be ticked, and a project
selected and confirmed was not added. Now the boxes sit in the first column
shown, the rows selected count as well, and a double click takes its row.

And a form's fields take less room: two pixels above and below a field, none
in a group's grid, whose rows are four pixels apart.

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

from PySide6 import QtCore, QtWidgets

from OdooQtUi.objects.many2many.many2many import Many2many
from OdooQtUi.utils_odoo_conn import constants
from OdooQtUi.views.form_obj import TemplateFormView
from OdooQtUi.views.tree_list_obj import TemplateTreeListView

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

CHECK = {0: QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled}
COLUMNS = {0: '<field name="sequence"/>', 1: '<button name="b" type="object"/>',
           2: '<field name="name"/>', 3: '<field name="user_id"/>'}


def listView(rows=3):
    view = TemplateTreeListView.__new__(TemplateTreeListView)
    view.treeObj = mock.Mock(tableWidget=QtWidgets.QTableWidget(rows, len(COLUMNS)),
                             widgets_to_add_in_line={i: ElementTree.fromstring(x)
                                                     for i, x in COLUMNS.items()})
    view.idLineRel = {row: 10 + row for row in range(rows)}
    view.__dict__['viewObj'] = mock.Mock(localViewCheckBoxes=CHECK)
    view._checkColumn = 0
    view.doubleClickCallback = None
    for row in range(rows):
        for col in range(len(COLUMNS)):
            item = QtWidgets.QTableWidgetItem('r%dc%d' % (row, col))
            view.treeObj.tableWidget.setItem(row, col, item)
    return view


class CheckColumn(unittest.TestCase):

    def test_moved_to_the_first_field_shown(self):
        view = listView()
        flags = view._checkBoxFlags(dict(CHECK), {0: True, 1: False, 2: False})
        self.assertEqual([1 + 1], list(flags))          # column 1 is a button
        self.assertEqual(2, view._checkColumn)

    def test_left_where_it_is_when_column_0_is_shown(self):
        view = listView()
        self.assertEqual(CHECK, view._checkBoxFlags(dict(CHECK), {0: False}))
        self.assertEqual(0, view._checkColumn)

    def test_no_boxes_no_change(self):
        self.assertEqual({}, listView()._checkBoxFlags({}, {0: True}))


class Picked(unittest.TestCase):

    def field(self):
        field = Many2many.__new__(Many2many)
        return field

    def test_the_rows_selected(self):
        view = listView()
        with mock.patch.object(type(view), 'viewCheckBoxes', new_callable=mock.PropertyMock,
                               return_value=CHECK):
            view.treeObj.tableWidget.item(2, 2).setSelected(True)
            view.treeObj.tableWidget.item(0, 2).setSelected(True)
            self.assertEqual([10, 12], self.field()._pickedIds(view))

    def test_the_rows_ticked_in_the_column_shown(self):
        view = listView()
        view._checkColumn = 2
        with mock.patch.object(type(view), 'viewCheckBoxes', new_callable=mock.PropertyMock,
                               return_value=CHECK):
            view.treeObj.tableWidget.item(1, 2).setCheckState(QtCore.Qt.Checked)
            self.assertEqual([11], self.field()._pickedIds(view))

    def test_the_row_double_clicked(self):
        view = listView()
        with mock.patch.object(type(view), 'viewCheckBoxes', new_callable=mock.PropertyMock,
                               return_value=CHECK):
            self.assertEqual([12], self.field()._pickedIds(view, [12]))

    def test_a_double_click_goes_to_the_callback(self):
        view = listView()
        taken = []
        view.doubleClickCallback = taken.append
        view.odooConnector = mock.Mock()
        view.doubleClickEvent(view.treeObj.tableWidget.model().index(1, 2))
        self.assertEqual([11], taken)
        view.odooConnector.initFormViewObj.assert_not_called()


class Field(QtWidgets.QWidget):
    def __init__(self):
        super(Field, self).__init__()
        self.qtHorizontalWidget = QtWidgets.QHBoxLayout(self)
        self.qtHorizontalWidget.setContentsMargins(6, 6, 6, 6)
        self.qtHorizontalWidget.addWidget(QtWidgets.QLineEdit())


class Spacing(unittest.TestCase):

    def test_a_grid_cell_has_no_margin(self):
        field = Field()
        TemplateFormView._fillCell(field)
        margins = field.qtHorizontalWidget.contentsMargins()
        self.assertEqual((0, 0, 0, 0), (margins.left(), margins.top(), margins.right(), margins.bottom()))

    def test_the_constants(self):
        self.assertEqual(4, constants.GROUP_ROW_SPACING)
        self.assertEqual(2, constants.FIELD_V_MARGIN)


if __name__ == '__main__':
    unittest.main()
