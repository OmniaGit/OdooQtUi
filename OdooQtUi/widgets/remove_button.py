# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The button that takes a row off a list: a bin, as Odoo draws it
(2026-11-25; it was a "Remove" written in blue).

The bin is painted here, not read from a file or from the icon theme: a
theme may have no such icon on Windows, and nothing else needs shipping.
Grey, red under the mouse.
"""

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

GREY = '#6b7280'
RED = '#dc2626'
SIZE = 16


def binPixmap(color, size=SIZE):
    """A bin, size pixels square, drawn in color."""
    ratio = 2       # drawn at twice the size: sharp on a high-dpi screen too
    pixmap = QtGui.QPixmap(size * ratio, size * ratio)
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    pen = QtGui.QPen(QtGui.QColor(color), 1.4)
    pen.setCapStyle(QtCore.Qt.RoundCap)
    pen.setJoinStyle(QtCore.Qt.RoundJoin)
    painter.setPen(pen)
    unit = size / 16.0
    # lid and handle
    painter.drawLine(QtCore.QPointF(2.5 * unit, 4 * unit), QtCore.QPointF(13.5 * unit, 4 * unit))
    painter.drawPolyline([QtCore.QPointF(6 * unit, 4 * unit), QtCore.QPointF(6.5 * unit, 2 * unit),
                          QtCore.QPointF(9.5 * unit, 2 * unit), QtCore.QPointF(10 * unit, 4 * unit)])
    # body
    painter.drawPolygon([QtCore.QPointF(4 * unit, 5.5 * unit), QtCore.QPointF(12 * unit, 5.5 * unit),
                         QtCore.QPointF(11.2 * unit, 14 * unit), QtCore.QPointF(4.8 * unit, 14 * unit)])
    # its ribs
    for x in (6.6, 9.4):
        painter.drawLine(QtCore.QPointF(x * unit, 7.5 * unit), QtCore.QPointF(x * unit, 12 * unit))
    painter.end()
    return pixmap


def binIcon():
    """The bin grey, and red where the mouse is over it (QIcon.Active)."""
    icon = QtGui.QIcon()
    icon.addPixmap(binPixmap(GREY), QtGui.QIcon.Normal)
    icon.addPixmap(binPixmap(RED), QtGui.QIcon.Active)
    return icon


def removeButton(parent=None, tooltip='Remove'):
    """A flat bin button for a row of a list."""
    button = QtWidgets.QToolButton(parent)
    button.setIcon(binIcon())
    button.setIconSize(QtCore.QSize(SIZE, SIZE))
    button.setAutoRaise(True)
    button.setToolTip(tooltip)
    button.setCursor(QtCore.Qt.PointingHandCursor)
    button.setStyleSheet('QToolButton { border: none; background: transparent; padding: 2px; }')
    return button
