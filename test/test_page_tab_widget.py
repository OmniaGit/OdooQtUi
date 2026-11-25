# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A form's notebook is as high as the page it shows (2026-11-25): a
QTabWidget is as high as its tallest page, and a short page left an empty
band under it.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen, and no server.
"""

import os
import subprocess
import sys
import unittest

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

from OdooQtUi.widgets.page_tab_widget import PageTabWidget

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def page(lines):
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(widget)
    for _ in range(lines):
        layout.addWidget(QtWidgets.QLineEdit())
    return widget


class PageHigh(unittest.TestCase):

    def setUp(self):
        self.tabs = PageTabWidget()
        self.tabs.addTab(page(10), 'long')
        self.tabs.addTab(page(2), 'short')
        self.plain = QtWidgets.QTabWidget()
        self.plain.addTab(page(10), 'long')
        self.plain.addTab(page(2), 'short')

    def test_the_short_page_is_short(self):
        self.tabs.setCurrentIndex(1)
        self.assertLess(self.tabs.sizeHint().height(), self.plain.sizeHint().height())
        self.assertLess(self.tabs.minimumSizeHint().height(), self.plain.minimumSizeHint().height())

    def test_the_long_page_as_qt_has_it(self):
        self.tabs.setCurrentIndex(0)
        self.assertEqual(self.plain.sizeHint().height(), self.tabs.sizeHint().height())

    def test_a_hidden_tab_does_not_count(self):
        self.tabs.setTabVisible(0, False)
        self.tabs.setCurrentIndex(1)
        self.assertEqual(self.tabs.sizeHint().height(), self.tabs._onePage(
            QtWidgets.QTabWidget.sizeHint(self.tabs), lambda p: p.sizeHint()).height())


if __name__ == '__main__':
    unittest.main()
