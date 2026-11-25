# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""A date, or a date and time, that can be empty, as an Odoo field can.

QDateTimeEdit always holds a date: a field Odoo left empty was shown as
01/01/2000 00:00, which reads as a value (2026-11-25). Here the empty value is
the minimum, drawn as blank, and the editor leaves it the way a user expects:

- the calendar opens on the current month, not on the minimum's;
- an arrow or the wheel starts from now, not from 1900;
- Delete or Backspace over the whole text makes it empty again.

One widget for both field types, the date one with a date-only format.
"""

from PySide6 import QtCore
from PySide6 import QtWidgets

#: The value that stands for "no date"; drawn as SPECIAL_TEXT.
EMPTY = QtCore.QDateTime(QtCore.QDate(1900, 1, 1), QtCore.QTime(0, 0, 0))
SPECIAL_TEXT = ' '


class EmptyDateTimeEdit(QtWidgets.QDateTimeEdit):

    def __init__(self, parent=None, dateOnly=False):
        super(EmptyDateTimeEdit, self).__init__(parent)
        if dateOnly:
            self.setDisplayFormat(QtCore.QLocale().dateFormat(QtCore.QLocale.ShortFormat))
        self.setMinimumDateTime(EMPTY)
        self.setSpecialValueText(SPECIAL_TEXT)
        self.setCalendarPopup(True)
        self.setEmpty()

    def isEmpty(self):
        return self.dateTime() <= self.minimumDateTime()

    def setEmpty(self):
        self.setDateTime(self.minimumDateTime())

    def _now(self):
        now = QtCore.QDateTime.currentDateTime()
        return QtCore.QDateTime(now.date(), QtCore.QTime(now.time().hour(), now.time().minute()))

    def stepBy(self, steps):
        if self.isEmpty():
            self.setDateTime(self._now())
            return
        super(EmptyDateTimeEdit, self).stepBy(steps)

    def mousePressEvent(self, event):
        empty = self.isEmpty()
        super(EmptyDateTimeEdit, self).mousePressEvent(event)
        calendar = self.calendarWidget()
        if empty and calendar is not None:
            today = QtCore.QDate.currentDate()
            calendar.setCurrentPage(today.year(), today.month())

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Delete, QtCore.Qt.Key_Backspace) \
                and self.lineEdit().selectedText() == self.lineEdit().text():
            self.setEmpty()
            return
        super(EmptyDateTimeEdit, self).keyPressEvent(event)
