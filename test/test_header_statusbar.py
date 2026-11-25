# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""useHeader='statusbar': of a form's header only the statusbar, no buttons --
where the record is, in an edit dialog that is not the place to move it
(2026-11-25). And the views a connector keeps are told apart by their header
and chatter too: a form built without them was handed back to whoever asked
for them.

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

from OdooQtUi.connector import ViewOdooObj
from OdooQtUi.views import form_obj
from OdooQtUi.views.form_obj import TemplateFormView, STATUSBAR_ONLY

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

HEADER = ElementTree.fromstring(
    '<header>'
    '<button name="action_confirm" type="object" string="Confirm"/>'
    '<field name="engineering_state" widget="statusbar"/>'
    '<field name="company_id"/>'
    '</header>')


class Field(QtWidgets.QWidget):
    def __init__(self, name, widget=''):
        super(Field, self).__init__()
        self.fieldName = name
        self.widget = widget


def header(useHeader):
    view = TemplateFormView.__new__(TemplateFormView)
    QtWidgets.QWidget.__init__(view)
    view.__dict__['model'] = 'product.product'
    view.odooConnector = mock.Mock()
    view.computeField = lambda xml: Field(xml.attrib['name'], xml.attrib.get('widget', ''))
    def make(**kw):
        made_button = QtWidgets.QPushButton(kw['xmlObject'].attrib['string'])
        made_button.buttonString = kw['xmlObject'].attrib['string']
        return made_button
    with mock.patch.object(form_obj.button, 'Button', side_effect=make) as made:
        mapping, _layout = TemplateFormView.computeHeader(view, HEADER, useHeader=useHeader)
    return mapping, made


class StatusbarOnly(unittest.TestCase):

    def test_only_the_statusbar(self):
        mapping, made = header(STATUSBAR_ONLY)
        self.assertEqual(['field_engineering_state'], sorted(mapping))
        made.assert_not_called()

    def test_the_whole_header_as_before(self):
        mapping, made = header(True)
        self.assertIn('field_engineering_state', mapping)
        self.assertIn('field_company_id', mapping)
        made.assert_called_once()


class ViewCache(unittest.TestCase):

    def view(self, useHeader=False, useChatter=False, hideFormContent=False):
        view = ViewOdooObj()
        view.localViewType, view.localOdooObjectName = 'form', 'product.product'
        view.localViewName = 'plm.base.component'
        view.useHeader, view.useChatter, view.hideFormContent = useHeader, useChatter, hideFormContent
        return view

    def match(self, view, **kw):
        return view.hasMatch('form', 'product.product', 'plm.base.component', False, False, {},
                             False, kw.get('hideFormContent', False),
                             kw.get('useHeader', False), kw.get('useChatter', False))

    def test_the_same_request_is_the_same_view(self):
        self.assertTrue(self.match(self.view(STATUSBAR_ONLY, True), useHeader=STATUSBAR_ONLY,
                                   useChatter=True))

    def test_another_header_is_another_view(self):
        self.assertFalse(self.match(self.view(False), useHeader=STATUSBAR_ONLY))
        self.assertFalse(self.match(self.view(True), useHeader=STATUSBAR_ONLY))

    def test_another_chatter_is_another_view(self):
        self.assertFalse(self.match(self.view(useChatter=False), useChatter=True))

    def test_a_new_view_object_hides_no_content(self):
        self.assertFalse(ViewOdooObj().hideFormContent)


if __name__ == '__main__':
    unittest.main()
