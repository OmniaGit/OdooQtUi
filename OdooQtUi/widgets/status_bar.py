# -*- coding: utf-8 -*-
# SPDX-FileCopyrightText: 2011-2026 OmniaSolutions and the OdooQtUi contributors
# SPDX-License-Identifier: Apache-2.0
#
# This file is part of OdooQtUi, released under the Apache License 2.0.
# Redistributions must keep the attribution in the NOTICE file.
# See the LICENSE and NOTICE files at the root of the project.

"""The statusbar Odoo draws in a form header, in Qt.

A row of chevrons, one per state, pointing the way the record goes, with the
one it is in filled in. What it replaces was a row of QLabels carrying the
technical values -- `draft`, `confirmed` -- with two stylesheets and no
direction at all.

It is a widget and not a piece of the selection field on purpose: the same
thing belongs in any form that shows a state, and it knows nothing about Odoo.
It takes a list of `(value, label)` pairs and the value it is in.

    bar = StatusBar()
    bar.setStates([('draft', 'Draft'), ('confirmed', 'Confirmed')])
    bar.setCurrent('confirmed')

Display only by default. A state is changed by the buttons of the header, which
are the ones the server decides on, and a statusbar you can click is a state
written to the server without anybody asking -- `clickable=True` and the
`stateClicked` signal are there for the form that wants it.
"""

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets

from OdooQtUi import theme

#: How deep the chevron between two states is, and how much air there is above
#: and below it.
ARROW = 9
INSET = 5

#: One row, the height of a small button.
HEIGHT = 28

#: The corner of the bar, and how far the text keeps away from a chevron.
RADIUS = 4
PADDING = 10

#: What the thing is made of, read off Odoo's own: a white bar with a thin grey
#: border, the states written in grey, and the one the record is in boxed in the
#: accent colour with its text in near black. The chevron in front of the
#: current state carries the accent too -- it is the left edge of that box.
BACKGROUND = '#ffffff'
BORDER_COLOUR = '#d1d5db'
CURRENT_COLOUR = '#00a09d'
CURRENT_TEXT = '#111827'
DONE_TEXT = '#6b7280'
TODO_TEXT = '#9ca3af'

#: Odoo lets a view colour a state with `statusbar_colors`, whose values are
#: bootstrap names rather than colours. Applied to the box of the current one.
NAMED_COLOURS = {'red': '#d9534f', 'danger': '#d9534f',
                 'green': '#5cb85c', 'success': '#5cb85c',
                 'blue': '#337ab7', 'info': '#337ab7',
                 'orange': '#f0ad4e', 'warning': '#f0ad4e',
                 'grey': '#8f8f8f', 'gray': '#8f8f8f',
                 'black': '#000000', 'teal': CURRENT_COLOUR}


class StatusBar(QtWidgets.QWidget):
    """The states of a record, drawn as Odoo draws them."""

    #: The value of a state the user clicked. Only ever emitted when the widget
    #: was made clickable.
    stateClicked = QtCore.Signal(str)

    def __init__(self, parent=None, states=(), current='', clickable=False):
        super(StatusBar, self).__init__(parent)
        self._states = []
        self._current = ''
        self._colours = {}
        self._clickable = clickable
        # All the room there is, and no more height than a button: this is a
        # header, and the form under it is what the user came for.
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Fixed)
        self.setMinimumHeight(HEIGHT)
        self.setMaximumHeight(HEIGHT)
        self.setMouseTracking(True)
        self.setStates(states)
        self.setCurrent(current)

    # -- what it shows -----------------------------------------------------

    def setStates(self, states):
        """The states, in the order the record goes through them.

        :states a list of (value, label). A bare list of strings is taken as
                values that are their own labels, which is what a view that
                carries `statusbar_visible` and nothing else gives us.
        """
        self._states = []
        for state in states or []:
            if isinstance(state, (list, tuple)) and len(state) == 2:
                value, label = state
            else:
                value, label = state, str(state).replace('_', ' ').title()
            value = '' if value is None else str(value)
            if not value:
                continue
            self._states.append((value, str(label)))
        self.updateGeometry()
        self.update()

    def setCurrent(self, value):
        """The state the record is in. Anything else means none of them."""
        self._current = '' if value is None else str(value)
        self.update()

    def setColours(self, mapping):
        """`statusbar_colors`, as the view writes it: value -> colour name."""
        self._colours = dict(mapping or {})
        self.update()

    #: Odoo spells it the other way; both are here so a caller can use either.
    setColors = setColours

    def setClickable(self, value=True):
        self._clickable = bool(value)

    @property
    def states(self):
        return list(self._states)

    @property
    def current(self):
        return self._current

    # -- how it is laid out ------------------------------------------------

    def _bounds(self, width=None):
        """Where each chevron starts and ends, left to right.

        Kept apart from the painting, and answering plain numbers, because this
        is the part that can be wrong in a way a screenshot does not show: a
        rounding that loses a pixel per state leaves the last one short of the
        margin the user asked it to reach.
        """
        width = self.width() if width is None else width
        count = len(self._states)
        if count < 1 or width <= 0:
            return []
        out = []
        for index in range(count):
            start = round(index * width / float(count))
            end = round((index + 1) * width / float(count))
            out.append((int(start), int(end)))
        return out

    def _chevron(self, x, height):
        """The `>` that separates two states, as three points.

        The same shape does two jobs: drawn in grey it is a separator, drawn in
        the accent colour it is the left edge of the box around the current
        state -- which is what it is in Odoo, and why the one in front of the
        current state is coloured there too.
        """
        return [QtCore.QPointF(x, INSET),
                QtCore.QPointF(x + ARROW, height / 2.0),
                QtCore.QPointF(x, height - INSET)]

    def _currentPath(self, index, start, end, height):
        """The box around the state the record is in.

        Its left edge is the chevron of the state before it and its right edge
        the chevron into the state after -- unless it is the first or the last,
        where the edge is the border of the bar itself and follows its corner.
        """
        first = index == 0
        last = index == len(self._states) - 1
        half = height / 2.0
        path = QtGui.QPainterPath()
        top, bottom = 0.5, height - 0.5
        if first:
            path.moveTo(start + RADIUS, top)
        else:
            path.moveTo(start, top)
        if last:
            path.lineTo(end - RADIUS, top)
            path.quadTo(end, top, end, top + RADIUS)
            path.lineTo(end, bottom - RADIUS)
            path.quadTo(end, bottom, end - RADIUS, bottom)
        else:
            path.lineTo(end, top)
            path.lineTo(end + ARROW, half)
            path.lineTo(end, bottom)
        if first:
            path.lineTo(start + RADIUS, bottom)
            path.quadTo(start, bottom, start, bottom - RADIUS)
            path.lineTo(start, top + RADIUS)
            path.quadTo(start, top, start + RADIUS, top)
        else:
            path.lineTo(start, bottom)
            path.lineTo(start + ARROW, half)
            path.lineTo(start, top)
        return path

    def _accent(self):
        """The colour of the current state's box, which a view may choose."""
        named = self._colours.get(self._current, '')
        return QtGui.QColor(NAMED_COLOURS.get(named,
                                              theme.colour('accent', CURRENT_COLOUR)))

    def _textColour(self, index, value):
        """Near black for the state the record is in, grey for the others.

        A shade between the ones behind it and the ones ahead: Odoo does not
        make that distinction, and it costs nothing to say where the record has
        already been.
        """
        if value == self._current:
            return QtGui.QColor(theme.colour('text', CURRENT_TEXT))
        position = self._indexOf(self._current)
        if position >= 0 and index < position:
            return QtGui.QColor(theme.colour('muted', DONE_TEXT))
        return QtGui.QColor(TODO_TEXT)

    def _indexOf(self, value):
        for index, (state, _label) in enumerate(self._states):
            if state == value:
                return index
        return -1

    def _at(self, x):
        """The state under a point, or ''. The arrow belongs to the one behind."""
        for index, (start, end) in enumerate(self._bounds()):
            if start <= x < end:
                return self._states[index][0]
        return self._states[-1][0] if self._states else ''

    # -- and how it is drawn -----------------------------------------------

    def sizeHint(self):
        return QtCore.QSize(max(120 * len(self._states), 240), HEIGHT)

    def minimumSizeHint(self):
        return QtCore.QSize(60 * max(len(self._states), 1), HEIGHT)

    def paintEvent(self, event):
        if not self._states:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        height = self.height()
        bounds = self._bounds()
        current = self._indexOf(self._current)
        accent = self._accent()

        # The bar itself: white, with the thin border that holds it together.
        frame = QtCore.QRectF(0.5, 0.5, self.width() - 1, height - 1)
        painter.setPen(QtGui.QPen(QtGui.QColor(theme.colour('border', BORDER_COLOUR)), 1))
        painter.setBrush(QtGui.QColor(theme.colour('surface', BACKGROUND)))
        painter.drawRoundedRect(frame, RADIUS, RADIUS)

        # The separators, every one that is not an edge of the current state:
        # those two are drawn with the box, in its colour.
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.setPen(QtGui.QPen(QtGui.QColor(theme.colour('border', BORDER_COLOUR)), 1))
        for index, (start, _end) in enumerate(bounds):
            if not index or index in (current, current + 1):
                continue
            painter.drawPolyline(QtGui.QPolygonF(self._chevron(start, height)))

        # The box around the state the record is in.
        if 0 <= current < len(bounds):
            start, end = bounds[current]
            painter.setPen(QtGui.QPen(accent, 1.4))
            painter.drawPath(self._currentPath(current, start, end, height))

        # And the labels, inside their own chevron and out of the next one's.
        metrics = painter.fontMetrics()
        for index, (start, end) in enumerate(bounds):
            value, label = self._states[index]
            font = painter.font()
            font.setBold(index == current)
            painter.setFont(font)
            painter.setPen(self._textColour(index, value))
            box = QtCore.QRect(start + PADDING, 0,
                               max(end - start - 2 * PADDING, 1), height)
            painter.drawText(box, QtCore.Qt.AlignCenter,
                             metrics.elidedText(label, QtCore.Qt.ElideRight,
                                                box.width()))
        painter.end()

    # -- what it answers to ------------------------------------------------

    def mouseMoveEvent(self, event):
        """The whole label, for a state too narrow to show it."""
        value = self._at(event.position().x() if hasattr(event, 'position')
                         else event.x())
        index = self._indexOf(value)
        self.setToolTip(self._states[index][1] if index >= 0 else '')
        super(StatusBar, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._clickable and event.button() == QtCore.Qt.LeftButton:
            value = self._at(event.position().x() if hasattr(event, 'position')
                             else event.x())
            if value and value != self._current:
                self.stateClicked.emit(value)
        super(StatusBar, self).mouseReleaseEvent(event)
