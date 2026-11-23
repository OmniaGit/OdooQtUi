# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.
"""AdvancedErrorPopUP's auto_close_msecs: an info or a warning closes by
itself, an error never does, and a user who opens More keeps the dialog."""
import os
import subprocess
import sys
import time
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_PROBE = subprocess.call(
    [sys.executable, '-c',
     'import os;os.environ.setdefault("QT_QPA_PLATFORM","offscreen");'
     'from PySide6 import QtWidgets;QtWidgets.QApplication([])'],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@unittest.skipIf(_PROBE, "no Qt that can open a window here")
class AutoClose(unittest.TestCase):

    def setUp(self):
        from PySide6 import QtCore, QtWidgets
        from OdooQtUi.utils_odoo_conn import utilsUi
        self.QtCore = QtCore
        self.application = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.utilsUi = utilsUi

    def dialog(self, kind, msecs, body='Checked-out recursively successfully'):
        return self.utilsUi.AdvancedErrorPopUP(None, messageBody=body, mess_type=kind,
                                               auto_close_msecs=msecs)

    def exec_for(self, dialog, give_up_msecs=3000):
        """How long exec() lasted; a dialog still open at give_up_msecs is
        closed from outside, and the time says so."""
        self.QtCore.QTimer.singleShot(give_up_msecs, dialog.reject)
        start = time.monotonic()
        dialog.exec()
        return time.monotonic() - start

    def test_info_closes_by_itself(self):
        self.assertLess(self.exec_for(self.dialog('INFO', 300)), 1.5)

    def test_warning_closes_by_itself(self):
        self.assertLess(self.exec_for(self.dialog('WARNING', 300)), 1.5)

    def test_lower_case_type_as_popMessage_passes_it(self):
        self.assertLess(self.exec_for(self.dialog('info', 300)), 1.5)

    def test_error_waits_for_close(self):
        self.assertGreaterEqual(self.exec_for(self.dialog('ERROR', 300)), 2.9)

    def test_default_waits_for_close(self):
        self.assertGreaterEqual(self.exec_for(self.dialog('INFO', 0)), 2.9)

    def test_more_stops_the_timer(self):
        dialog = self.dialog('WARNING', 600, body='x' * 400)
        self.QtCore.QTimer.singleShot(100, dialog.showMore)
        self.assertGreaterEqual(self.exec_for(dialog), 2.9)

    def test_copy_stops_the_timer(self):
        dialog = self.dialog('INFO', 600)
        self.QtCore.QTimer.singleShot(100, dialog.copyMessage)
        self.assertGreaterEqual(self.exec_for(dialog), 2.9)

    def test_popInfo_and_popWarning_pass_it_popError_cannot(self):
        import inspect
        self.assertIn('auto_close_msecs', inspect.signature(self.utilsUi.popInfo).parameters)
        self.assertIn('auto_close_msecs', inspect.signature(self.utilsUi.popWarning).parameters)
        self.assertNotIn('auto_close_msecs', inspect.signature(self.utilsUi.popError).parameters)


if __name__ == '__main__':
    unittest.main()
