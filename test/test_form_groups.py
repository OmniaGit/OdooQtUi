# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A form's groups laid out as Odoo lays them out (2026-11-25): a grid of
label | field with `col` and `colspan`, a title from `string`, groups of
groups side by side, `nolabel` honoured; and a date that can be empty.

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

from OdooQtUi.views.form_obj import TemplateFormView
from OdooQtUi.widgets.empty_date_edit import EmptyDateTimeEdit

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


class Field(QtWidgets.QWidget):
    """A field as the field types build one: its label first in its layout,
    then the input, then a stretch."""

    def __init__(self, name):
        super(Field, self).__init__()
        self.fieldName = name
        self.qtHorizontalWidget = QtWidgets.QHBoxLayout(self)
        self.labelQtObj = QtWidgets.QLabel(name.title())
        self.widgetQtObj = QtWidgets.QComboBox()
        self.qtHorizontalWidget.addWidget(self.labelQtObj)
        self.qtHorizontalWidget.addWidget(self.widgetQtObj)
        self.qtHorizontalWidget.addSpacerItem(QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))


def form():
    view = TemplateFormView.__new__(TemplateFormView)
    QtWidgets.QWidget.__init__(view)
    view.globalMapping = {}
    view.containerModifiers = []
    view.hideFormContent = False
    view.viewObj = mock.Mock(odooFieldsNameTypeRel={'weight': {'string': 'Weight'}})
    view.fields_made = {}

    def computeField(xml):
        field = Field(xml.attrib['name'])
        view.fields_made[field.fieldName] = field
        return field
    view.computeField = computeField
    return view


def lay(arch):
    view = form()
    layout = QtWidgets.QVBoxLayout(view)
    view._computeGroup(ElementTree.fromstring(arch), layout)
    return view, layout


def grids(layout):
    found = []
    for index in range(layout.count()):
        item = layout.itemAt(index)
        if isinstance(item.layout(), QtWidgets.QGridLayout):
            found.append(item.layout())
        elif item.layout() is not None:
            found.extend(grids(item.layout()))
    return found


def where(grid, widget):
    index = grid.indexOf(widget)
    return grid.getItemPosition(index) if index >= 0 else None


class Grid(unittest.TestCase):

    def test_one_field_a_row_label_then_field(self):
        view, layout = lay('<group><field name="a"/><field name="b"/></group>')
        grid = grids(layout)[0]
        a, b = view.fields_made['a'], view.fields_made['b']
        self.assertEqual((0, 0, 1, 1), where(grid, a.labelQtObj))
        self.assertEqual((0, 1, 1, 1), where(grid, a))
        self.assertEqual((1, 0, 1, 1), where(grid, b.labelQtObj))

    def test_col_four_two_fields_a_row(self):
        view, layout = lay('<group col="4"><field name="a"/><field name="b"/><field name="c"/></group>')
        grid = grids(layout)[0]
        self.assertEqual((0, 2, 1, 1), where(grid, view.fields_made['b'].labelQtObj))
        self.assertEqual((1, 0, 1, 1), where(grid, view.fields_made['c'].labelQtObj))

    def test_colspan_counts_the_label(self):
        view, layout = lay('<group col="6"><field name="code" colspan="4"/>'
                           '<field name="rev" colspan="2"/></group>')
        grid = grids(layout)[0]
        self.assertEqual((0, 1, 1, 3), where(grid, view.fields_made['code']))
        self.assertEqual((0, 5, 1, 1), where(grid, view.fields_made['rev']))

    def test_nolabel_takes_no_label_cell_and_hides_it(self):
        view, layout = lay('<group><field name="project_ids" nolabel="1" colspan="2"/></group>')
        grid = grids(layout)[0]
        field = view.fields_made['project_ids']
        self.assertEqual((0, 0, 1, 2), where(grid, field))
        self.assertIsNone(where(grid, field.labelQtObj))
        field.labelQtObj.setHidden(False)      # what a field's setInvisible does
        self.assertFalse(field.labelQtObj.isVisibleTo(view))

    def test_the_label_is_out_of_the_field(self):
        view, _layout = lay('<group><field name="a"/></group>')
        field = view.fields_made['a']
        self.assertEqual(-1, field.qtHorizontalWidget.indexOf(field.labelQtObj))

    def test_the_input_fills_the_cell(self):
        view, _layout = lay('<group><field name="a"/></group>')
        fieldLayout = view.fields_made['a'].qtHorizontalWidget
        spacers = [fieldLayout.itemAt(i).spacerItem() for i in range(fieldLayout.count())]
        self.assertEqual([None], [s for s in spacers if s is not None] or [None])
        self.assertEqual(1, fieldLayout.stretch(fieldLayout.indexOf(view.fields_made['a'].widgetQtObj)))

    def test_an_always_invisible_field_takes_no_cell(self):
        view, layout = lay('<group><field name="id" invisible="1"/><field name="a"/></group>')
        grid = grids(layout)[0]
        self.assertIsNone(where(grid, view.fields_made['id']))
        self.assertEqual((0, 0, 1, 1), where(grid, view.fields_made['a'].labelQtObj))

    def test_a_label_for_goes_beside_its_element(self):
        view, layout = lay('<group><label for="weight"/><div><field name="uom"/></div></group>')
        grid = grids(layout)[0]
        label = grid.itemAtPosition(0, 0).widget()
        self.assertEqual('Weight', label.text())
        self.assertIsNotNone(grid.itemAtPosition(0, 1))


class Groups(unittest.TestCase):

    def test_a_title(self):
        view, layout = lay('<group string="Material"><field name="a"/></group>')
        titles = [w.text() for w in view.findChildren(QtWidgets.QLabel) if w.text() == 'Material']
        self.assertEqual(['Material'], titles)

    def test_groups_of_groups_side_by_side(self):
        view, layout = lay('<group><group><field name="a"/></group><group><field name="b"/></group></group>')
        columns = layout.itemAt(0).layout()
        self.assertIsInstance(columns, QtWidgets.QHBoxLayout)
        self.assertEqual(2, columns.count())


class EmptyDate(unittest.TestCase):

    def test_starts_empty_and_shows_nothing(self):
        edit = EmptyDateTimeEdit()
        self.assertTrue(edit.isEmpty())
        self.assertEqual('', edit.text().strip())

    def test_a_value_then_empty_again(self):
        edit = EmptyDateTimeEdit()
        edit.setDateTime(QtCore.QDateTime(QtCore.QDate(2026, 11, 25), QtCore.QTime(10, 0)))
        self.assertFalse(edit.isEmpty())
        edit.setEmpty()
        self.assertTrue(edit.isEmpty())

    def test_an_arrow_from_empty_starts_today(self):
        edit = EmptyDateTimeEdit(dateOnly=True)
        edit.stepBy(1)
        self.assertEqual(QtCore.QDate.currentDate(), edit.date())


if __name__ == '__main__':
    unittest.main()
