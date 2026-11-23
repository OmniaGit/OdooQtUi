# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""Odoo keeps a datetime in UTC; the user sees and types it in their own
timezone, their `tz` in Odoo, and UTC when they have none (2026-10-17). The
widgets showed Odoo's UTC as it came, and sent back what the widget held --
a QDateTime or a datetime, which JSON-RPC cannot carry.

A date has no timezone. Its widget showed nothing: setValue only kept the
value.

    cd OdooQtUi && python -m unittest discover -s test -p "test_*.py"

Qt without a screen, and no server.
"""

import datetime
import json
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

from PySide6 import QtCore, QtWidgets

from OdooQtUi.objects.date.date import Date
from OdooQtUi.objects.datetimee.datetimee import Datetime
from OdooQtUi.utils_odoo_conn import utils

APPLICATION = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

BUENOS_AIRES = 'America/Argentina/Buenos_Aires'   # UTC-3, no summer time


class Rpc(object):
    def __init__(self, tz):
        self.contextUser = {'lang': 'en_US', 'tz': tz} if tz else {'lang': 'en_US'}


class Connector(object):
    def __init__(self, tz):
        self.rpc_connector = Rpc(tz)


def field(widgetClass, fieldType, tz=BUENOS_AIRES):
    xml = ElementTree.fromstring('<field name="when"/>')
    return widgetClass(None, xml, {'when': {'type': fieldType, 'string': 'When'}}, Connector(tz))


class Conversions(unittest.TestCase):

    def test_utc_to_the_user(self):
        self.assertEqual('2026-10-17 11:02:54',
                         utils.utcToUserText('2026-10-17 14:02:54', Connector(BUENOS_AIRES)))

    def test_the_user_to_utc(self):
        self.assertEqual('2026-10-17 14:02:54',
                         utils.userToUtc(datetime.datetime(2026, 10, 17, 11, 2, 54), Connector(BUENOS_AIRES)))

    def test_summer_time_follows_the_date(self):
        rome = Connector('Europe/Rome')
        self.assertEqual('2026-07-01 12:00:00', utils.utcToUserText('2026-07-01 10:00:00', rome))
        self.assertEqual('2026-01-01 11:00:00', utils.utcToUserText('2026-01-01 10:00:00', rome))

    def test_no_timezone_is_utc(self):
        self.assertEqual('2026-10-17 14:02:54', utils.utcToUserText('2026-10-17 14:02:54', Connector(None)))

    def test_the_rpc_connector_answers_too(self):
        self.assertEqual('2026-10-17 11:02:54',
                         utils.utcToUserText('2026-10-17 14:02:54', Rpc(BUENOS_AIRES)))

    def test_an_xmlrpc_datetime(self):
        import xmlrpc.client
        value = xmlrpc.client.DateTime('20261017T14:02:54')
        self.assertEqual('2026-10-17 11:02:54', utils.utcToUserText(value, Connector(BUENOS_AIRES)))

    def test_no_value(self):
        self.assertEqual('', utils.utcToUserText(False, Connector(BUENOS_AIRES)))
        self.assertFalse(utils.userToUtc(QtCore.QDateTime(), Connector(BUENOS_AIRES)))


class TheDatetimeWidget(unittest.TestCase):

    def test_shows_the_user_time_and_keeps_utc(self):
        widget = field(Datetime, 'datetime')
        widget.setValue('2026-10-17 14:02:54')
        self.assertEqual('2026-10-17 11:02:54', widget.widgetQtObj.dateTime().toString('yyyy-MM-dd hh:mm:ss'))
        self.assertEqual('2026-10-17 14:02:54', widget.value)

    def test_a_time_typed_goes_back_in_utc_and_as_text(self):
        widget = field(Datetime, 'datetime')
        widget.setValue('2026-10-17 14:02:54')
        widget.widgetQtObj.setDateTime(QtCore.QDateTime(2026, 10, 18, 9, 0, 0))
        self.assertEqual('2026-10-18 12:00:00', widget.value)
        self.assertEqual('"2026-10-18 12:00:00"', json.dumps(widget.value))   # JSON-RPC carries it

    def test_no_value(self):
        widget = field(Datetime, 'datetime')
        widget.setValue(False)
        self.assertFalse(widget.value)


class TheDateWidget(unittest.TestCase):

    def test_shows_the_date(self):
        widget = field(Date, 'date')
        widget.setValue('2026-10-17')
        self.assertEqual('2026-10-17', widget.widgetQtObj.date().toString('yyyy-MM-dd'))
        self.assertEqual('2026-10-17', widget.value)

    def test_a_date_typed_goes_back_as_text(self):
        widget = field(Date, 'date')
        widget.setValue('2026-10-17')
        widget.widgetQtObj.setDate(QtCore.QDate(2026, 12, 24))
        self.assertEqual('2026-12-24', widget.value)
        self.assertEqual('"2026-12-24"', json.dumps(widget.value))

    def test_no_timezone_moves_a_date(self):
        widget = field(Date, 'date', tz='Pacific/Kiritimati')   # UTC+14
        widget.setValue('2026-10-17')
        self.assertEqual('2026-10-17', widget.value)

    def test_no_value(self):
        widget = field(Date, 'date')
        widget.setValue(False)
        self.assertFalse(widget.value)


if __name__ == '__main__':
    unittest.main()
