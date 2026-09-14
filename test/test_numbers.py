# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The float and integer fields keep the number the server holds.

Their spin boxes had Qt's own range, 0 to 99.99 and 0 to 99: a 333.0 read from
Odoo showed as 99.99, a negative as 0, a sequence of 100 as 99 -- and the
clipped number was the one saved once the user touched the field.

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

# In a process of its own, as in test_status_bar: a Qt that cannot open a
# window does not raise, it aborts the whole run.
_PROBE = subprocess.call(
    [sys.executable, '-c',
     'import os;os.environ.setdefault("QT_QPA_PLATFORM","offscreen");'
     'from PySide6 import QtWidgets;QtWidgets.QApplication([])'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if _PROBE:
    raise unittest.SkipTest("no Qt that can open a window here")

from PySide6 import QtWidgets

from OdooQtUi.objects.float.float import Float
from OdooQtUi.objects.integer.integer import Integer

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def field(widgetClass, definition):
    xml = ElementTree.fromstring('<field name="amount"/>')
    return widgetClass(None, xml, {'amount': definition}, None)


class FloatField(unittest.TestCase):

    def test_large_and_negative_values_are_kept(self):
        amount = field(Float, {'type': 'float', 'string': 'Amount'})
        for number in (333.0, 1234567.89, -42.5):
            amount.setValue(number)
            self.assertEqual(amount.value, number)
            self.assertEqual(amount.widgetQtObj.value(), number)

    def test_decimals_come_from_the_digits_of_the_field(self):
        amount = field(Float, {'type': 'float', 'digits': [16, 4]})
        amount.setValue(0.1234)
        self.assertEqual(amount.widgetQtObj.decimals(), 4)
        self.assertEqual(amount.widgetQtObj.value(), 0.1234)

    def test_two_decimals_without_digits(self):
        amount = field(Float, {'type': 'float', 'digits': False})   # kept alive
        self.assertEqual(amount.widgetQtObj.decimals(), 2)

    def test_the_value_is_current_even_when_qt_emits_nothing(self):
        amount = field(Float, {'type': 'float'})
        amount.currentValue = 5.0       # stale, as after a missed signal
        amount.setValue(0.0)            # the spin box already shows 0.0
        self.assertEqual(amount.value, 0.0)

    def test_false_from_the_server_is_zero(self):
        amount = field(Float, {'type': 'float'})
        amount.setValue(False)
        self.assertEqual(amount.value, 0.0)


class IntegerField(unittest.TestCase):

    def test_large_and_negative_values_are_kept(self):
        sequence = field(Integer, {'type': 'integer'})
        for number in (100, 2000000000, -7):
            sequence.setValue(number)
            self.assertEqual(sequence.value, number)
            self.assertEqual(sequence.widgetQtObj.value(), number)

    def test_false_from_the_server_is_zero(self):
        sequence = field(Integer, {'type': 'integer'})
        sequence.setValue(False)
        self.assertEqual(sequence.value, 0)


if __name__ == '__main__':
    unittest.main()
